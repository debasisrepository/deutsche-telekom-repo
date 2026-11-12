import { ReactNode } from 'react'
import { useAuth } from '../../lib/auth-context'

interface HeaderProps {
  children?: ReactNode
}

export function Header({ children }: HeaderProps) {
  const { user, logout } = useAuth()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      {children}
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-900">
          Deutsche Telekom IT Procurement
        </h1>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-gray-600">
              {user.username} ({user.role})
            </span>
          )}
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
