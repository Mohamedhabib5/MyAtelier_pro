export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() ?? null;
  }
  return null;
}

export async function apiRequest<T>(input: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { ...(init?.headers as Record<string, string>) };
  
  if (!(init?.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  // Inject CSRF token from cookie
  const csrfToken = getCookie('myatelier_pro_csrf');
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }

  const response = await fetch(input, {
    credentials: 'include',
    ...init,
    headers,
  });

  if (!response.ok) {
    let detail = 'حدث خطأ غير متوقع';
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (payload.detail) {
        if (typeof payload.detail === 'string') {
          detail = payload.detail;
        } else {
          detail = JSON.stringify(payload.detail);
        }
      }
    } catch {
      detail = response.statusText || detail;
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/**
 * Trigger a file download by clicking a temporary anchor element.
 *
 * WHY synchronous (no async/await):
 * Browsers only allow programmatic downloads within a "user gesture context"
 * (i.e., the call stack initiated by the user's click). Using async/await
 * (e.g., awaiting fetch) breaks this context, causing the browser to
 * navigate to the URL/blob instead of saving to Downloads.
 *
 * Since the backend now sends a proper Content-Disposition header with the
 * correct filename, we can point the anchor directly at the API URL and let
 * the browser handle the download natively — same-origin, inside user gesture.
 */
export async function downloadFile(url: string): Promise<void> {
  console.log(`[Download] Initiating download for: ${url}`);
  try {
    const response = await fetch(url, {
      credentials: 'include',
      // No X-CSRF-Token needed for GET exports, avoids potential 403 mismatch
    });

    if (!response.ok) {
      throw new Error(`Download failed with status ${response.status}: ${response.statusText}`);
    }

    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = '';
    
    if (contentDisposition) {
      const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''([^;,\n]*)/i);
      if (filenameStarMatch && filenameStarMatch[1]) {
        filename = decodeURIComponent(filenameStarMatch[1]);
      } else {
        const filenameMatch = contentDisposition.match(/filename="?([^";,\n]*)"?/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }
    }

    if (!filename) {
      const parts = url.split('?')[0].split('/');
      filename = parts[parts.length - 1] || 'download';
    }

    if (!filename.includes('.')) {
      const contentType = response.headers.get('Content-Type');
      if (contentType?.includes('spreadsheetml')) filename += '.xlsx';
      else if (contentType?.includes('csv')) filename += '.csv';
      else if (contentType?.includes('pdf')) filename += '.pdf';
    }

    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    
    console.log(`[Download] Triggered: ${filename}`);

    // Increased timeout to 60s for maximum safety on slow systems
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
      if (a.parentNode) {
        document.body.removeChild(a);
      }
    }, 60000);
  } catch (error) {
    console.error('[Download] Error:', error);
    window.location.href = url;
  }
}
