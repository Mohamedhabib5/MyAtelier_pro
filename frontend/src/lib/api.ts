export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiRequest<T>(input: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { ...(init?.headers as Record<string, string>) };
  if (!(init?.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
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
export function downloadFile(url: string): void {
  const a = document.createElement('a');
  a.href = url;
  // Fallback filename hint — server's Content-Disposition takes precedence.
  const pathFilename = url.split('?')[0].split('/').pop() ?? 'download';
  a.download = pathFilename;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    if (a.parentNode) {
      document.body.removeChild(a);
    }
  }, 200);
}
