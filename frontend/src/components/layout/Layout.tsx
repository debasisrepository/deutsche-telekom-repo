import React from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-layout">
      <Header />
      <div className="flex flex-1 pt-12">
        <Sidebar />
        <main className="app-main p-8 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
}
