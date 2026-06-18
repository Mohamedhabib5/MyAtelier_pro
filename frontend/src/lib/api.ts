/**
 * @file api.ts
 * @description Core API utilities for MyAtelier Pro frontend.
 *
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║          ⚠️  CRITICAL: READ BEFORE MODIFYING downloadFile()  ⚠️         ║
 * ║                                                                          ║
 * ║  The downloadFile() function uses a specific 3-step approach that was   ║
 * ║  chosen after extensive debugging. DO NOT simplify it without           ║
 * ║  understanding WHY each step exists.                                     ║
 * ║                                                                          ║
 * ║  See: docs/EXPORT_SYSTEM.md for full technical details.                 ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 */

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
    if (response.status === 409) {
      if (typeof detail === 'string' && (detail.includes('تم تعديل') || detail === 'Conflict')) {
        detail = 'تم تعديل هذه البيانات بواسطة مستخدم آخر، يرجى تحديث الصفحة.';
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('optimistic-lock-error', { detail }));
        }
      }
    }

    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║                    downloadFile() - ARCHITECTURE NOTE                   ║
 * ╠══════════════════════════════════════════════════════════════════════════╣
 * ║                                                                          ║
 * ║  This function uses a 3-step fetch+blob approach. This is NOT           ║
 * ║  "over-engineering" — each step exists to solve a specific bug          ║
 * ║  that was encountered in production.                                     ║
 * ║                                                                          ║
 * ║  ❌ DO NOT REPLACE WITH: window.location.href = url                     ║
 * ║     → Browser ignores Content-Disposition header and uses the           ║
 * ║       UUID ticket ID from the URL as the filename.                      ║
 * ║       Result: Files saved as "a7960022-ccb1-4fee..." instead of        ║
 * ║               "bookings_branch_20260509.xlsx"                           ║
 * ║                                                                          ║
 * ║  ❌ DO NOT REPLACE WITH: anchor.href = url; anchor.download = ''        ║
 * ║     → anchor.download='' only hints to download; browser still uses    ║
 * ║       the URL path as filename for http: URLs. Same UUID problem.       ║
 * ║                                                                          ║
 * ║  ✅ CORRECT APPROACH: fetch() → blob → blob: URL → anchor.download     ║
 * ║     → We manually extract the filename from the Content-Disposition     ║
 * ║       response header (RFC 5987 format), then assign it explicitly     ║
 * ║       to anchor.download on a blob: URL. This is the ONLY method       ║
 * ║       that guarantees the server's filename is used.                    ║
 * ║                                                                          ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 *
 * @param url - The export API URL (e.g. /api/exports/bookings.xlsx?branch_id=...)
 */
export async function downloadFile(url: string): Promise<void> {
  const isDev = typeof import.meta !== 'undefined' && import.meta.env?.DEV;
  if (isDev) {
    console.log(`[Download] Initiating ticket request for: ${url}`);
  }
  try {
    // ── Step 1: Security ──────────────────────────────────────────────────
    // Request a secure, single-use download ticket from the backend.
    // The ticket expires immediately after use, preventing unauthorized access.
    const ticketResult = await apiRequest<{ ticket: string; download_url: string }>(
      `/api/exports/tickets?target_path=${encodeURIComponent(url)}`,
      { method: 'POST' }
    );

    if (isDev) {
      console.log(`[Download] Ticket received: ${ticketResult.ticket}`);
    }

    // ── Step 2: Fetch as blob ─────────────────────────────────────────────
    // Fetch the actual file content. We use fetch() (not location.href) so we
    // can programmatically access the response headers, specifically
    // Content-Disposition, which contains the real filename from the server.
    const response = await fetch(ticketResult.download_url, { credentials: 'include' });

    if (!response.ok) {
      throw new Error(`Download failed with status: ${response.status}`);
    }

    // ── Step 3: Extract filename from Content-Disposition ─────────────────
    // The server sends the filename in RFC 5987 format:
    //   Content-Disposition: attachment; filename="download.xlsx"; filename*=UTF-8''bookings_branch_20260509.xlsx
    //
    // We MUST read this ourselves because no browser navigation method
    // (href, anchor click) allows programmatic access to response headers.
    const disposition = response.headers.get('Content-Disposition') ?? '';
    let filename = 'download';

    // Prefer RFC 5987 encoded filename (supports Arabic/Unicode filenames)
    const filenameStar = disposition.match(/filename\*=UTF-8''([^;\s]+)/i);
    if (filenameStar) {
      try {
        filename = decodeURIComponent(filenameStar[1]);
      } catch {
        filename = filenameStar[1];
      }
    } else {
      // Fallback to plain ASCII filename
      const filenameMatch = disposition.match(/filename="?([^";\s]+)"?/i);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    if (isDev) {
      console.log(`[Download] Saving as: "${filename}"`);
    }

    // ── Step 4: Trigger download with correct filename ────────────────────
    // Create a temporary blob: URL. Unlike http: URLs, the browser WILL respect
    // anchor.download on blob: URLs, using whatever name we provide.
    // This is the KEY STEP that guarantees the correct filename is used.
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename; // ← Server-provided filename (NOT the UUID)
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();

    // Cleanup the temporary blob URL after the browser starts the download
    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
      if (link.parentNode) {
        document.body.removeChild(link);
      }
    }, 1000);

  } catch (error) {
    if (isDev) {
      console.error('[Download] Error downloading file:', error);
    }
    // Last-resort fallback: direct navigation (filename will be UUID, but file will download)
    window.location.href = url;
  }
}
