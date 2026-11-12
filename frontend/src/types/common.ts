export interface ErrorResponse {
  detail: string
  status_code: number
}

export interface MessageResponse {
  message: string
}

export interface PaginationWrapper<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
