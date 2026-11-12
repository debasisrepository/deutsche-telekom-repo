export interface User {
  id: number
  email: string
  username: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  user: User
}
