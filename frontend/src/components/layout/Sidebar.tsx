import { Link, useLocation } from 'react-router-dom'

const navigationItems = [
  { path: '/', label: 'Intake Queue' },
  { path: '/cases', label: 'Cases' },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="app-sidebar bg-gray-900 text-white p-4">
      <nav className="space-y-2">
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-2 rounded ${
                isActive
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
