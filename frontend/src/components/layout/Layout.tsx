import { ReactNode } from 'react'
import { SkipToContent, Theme } from '@carbon/react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <Theme theme="white">
      <div className="app-layout">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header>
            <SkipToContent />
          </Header>
          <main className="app-main p-6 bg-gray-50" id="main-content">
            {children}
          </main>
        </div>
      </div>
    </Theme>
  )
}
