import type { ApiError } from '../types';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

export class ApiClientError extends Error {
  constructor(
    public detail: string,
    public status_code?: number,
    public correlation_id?: string
  ) {
    super(detail);
    this.name = 'ApiClientError';
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(options.headers);

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
    throw new ApiClientError('Unauthorized', 401);
  }

  if (!response.ok) {
    let errorDetail = 'Request failed';
    let correlationId: string | undefined;
    try {
      const errorData: ApiError = await response.json();
      errorDetail = errorData.detail || errorDetail;
      correlationId = errorData.correlation_id;
    } catch {
      errorDetail = await response.text() || errorDetail;
    }
    throw new ApiClientError(errorDetail, response.status, correlationId);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
