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
