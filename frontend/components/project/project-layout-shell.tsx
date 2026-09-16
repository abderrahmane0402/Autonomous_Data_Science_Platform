'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, ChevronRight, Database, Menu, X, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ProjectSidebar } from '@/components/project/project-sidebar'
import { ThemeToggle } from '@/components/theme-toggle'

export function ProjectLayoutShell({ projectId, children }: { projectId: string; children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const handleLogout = () => {
    localStorage.removeItem('token')
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    window.location.href = '/'
  }

  return (
    <main className="min-h-screen bg-[#090b10] text-slate-100">
      <header className="sticky top-0 z-50 flex min-h-16 items-center justify-between border-b border-white/8 bg-[#090b10] px-3 py-2 sm:px-6 lg:px-7 print:hidden">
        <div className="flex min-w-0 items-center gap-3">
          <Button 
            variant="ghost" 
            size="icon" 
            className="shrink-0 text-slate-400 lg:hidden" 
            onClick={() => setMobileNavOpen((open) => !open)} 
            aria-label={mobileNavOpen ? 'Close project navigation' : 'Open project navigation'}
          >
            {mobileNavOpen ? <X /> : <Menu />}
          </Button>
          <Link href="/dashboard" className="shrink-0 text-slate-500 hover:text-white" aria-label="Back to dashboard">
            <ArrowLeft className="size-4" />
          </Link>
          <span className="hidden text-sm font-semibold sm:inline">
            autonomo<span className="text-indigo-400">.ai</span>
          </span>
          <ChevronRight className="hidden size-4 text-slate-700 sm:inline" />
          <span className="flex min-w-0 items-center gap-2 truncate text-xs text-slate-400">
            <Database className="size-3 shrink-0 text-indigo-300" />
            Project workspace
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <ThemeToggle />
          <Button 
            onClick={handleLogout} 
            variant="ghost" 
            size="sm" 
            className="h-8 border border-white/8 text-xs text-slate-400 hover:border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-400"
            title="Disconnect from account"
          >
            <LogOut className="mr-1.5 size-3.5" />
            <span className="hidden sm:inline">Disconnect</span>
          </Button>
        </div>
      </header>
      <div className="mx-auto flex max-w-[1500px]">
        <ProjectSidebar projectId={projectId} mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
        <section className="min-w-0 flex-1">{children}</section>
      </div>
    </main>
  )
}
