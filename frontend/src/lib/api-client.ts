const API_BASE = import.meta.env.VITE_API_URL ?? '/api'
const API_VERSION = '/v1'
const AUTH_STORAGE_KEY = 'access_token'

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(AUTH_STORAGE_KEY)
  const headers = new Headers(options.headers)
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const url = `${API_BASE}${API_VERSION}${path}`
  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    window.location.href = '/login'
    throw new ApiError(401, 'Unauthorized')
  }

  if (!response.ok) {
    let detail = 'Request failed'
    try {
      const errorData = await response.json()
      detail = errorData.detail || detail
    } catch {
      detail = await response.text() || detail
    }
    throw new ApiError(response.status, detail)
  }

  if (response.status === 204) {
    return null as T
  }

  return response.json() as Promise<T>
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
}

export { ApiError, AUTH_STORAGE_KEY }
