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
/**
 * Trigger a file download using a secure, short-lived ticket.
 * 
 * WHY:
 * Previous blob-based downloads were fragile in strict security environments (CSP) 
 * and often failed to preserve filenames on Windows when intercepted by IDM.
 * The ticket system allows a native browser navigation download which is 
 * 100% compatible with all browsers and security policies while remaining secure.
 */
export async function downloadFile(url: string): Promise<void> {
  console.log(`[Download] Initiating ticket request for: ${url}`);
  try {
    // 1. Request a short-lived download ticket from the backend
    // This is a secure POST request that includes the user session and CSRF token.
    const ticketResult = await apiRequest<{ ticket: string; download_url: string }>(
      `/api/exports/tickets?target_path=${encodeURIComponent(url)}`,
      { method: 'POST' }
    );

    console.log(`[Download] Ticket received, triggering native download: ${ticketResult.ticket}`);
    
    // 2. Trigger native browser download via location redirection.
    // Since the download route has Content-Disposition and is exempted from restrictive CSP,
    // the browser will handle it perfectly (showing the Save As dialog with the correct name).
    window.location.href = ticketResult.download_url;

  } catch (error) {
    console.error('[Download] Ticket system error, falling back to direct URL:', error);
    // Fallback to direct URL if the ticket system fails for any reason
    window.location.href = url;
  }
}
