import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiClient, AUTH_STORAGE_KEY } from './api-client'

interface User {
  id: number
  email: string
  username: string
  role: string
}

interface LoginResponse {
  access_token: string
  user: User
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)

  useEffect(() => {
    const token = localStorage.getItem(AUTH_STORAGE_KEY)
    if (token) {
      setIsAuthenticated(true)
      // User details will be loaded on first authenticated API call
      // or we could add a /me endpoint to fetch current user
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response = await apiClient.post<LoginResponse>('/auth/login', {
      email,
      password,
    })
    
    localStorage.setItem(AUTH_STORAGE_KEY, response.access_token)
    setUser(response.user)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
