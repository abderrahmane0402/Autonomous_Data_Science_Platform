'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Layers3, LogOut, Plus } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { ProjectCard } from '@/components/dashboard/project-card'
import { getProjects, createProject, deleteProject, getMe } from '@/lib/api'

export default function DashboardPage() {
  const [projects, setProjects] = useState<any[]>([])
  const [user, setUser] = useState<{ id: number; email: string } | null>(null)
  const router = useRouter()

  const loadProjects = () => {
    getProjects().then(data => {
      const mappedProjects = data.map((p: any) => ({
        id: p.id,
        name: p.name,
        desc: p.best_model_name ? `Best Model: ${p.best_model_name}` : 'Awaiting data upload',
        status: p.status,
        rows: p.dataset_path ? 'Uploaded' : 'Empty',
        quality: p.data_quality_score ? `${(p.data_quality_score * 100).toFixed(1)}%` : '-',
        time: new Date(p.created_at).toLocaleDateString(),
        color: 'from-indigo-500/25'
      }))
      setProjects(mappedProjects)
    }).catch(err => console.error('Failed to load projects', err))
  }

  useEffect(() => { 
    loadProjects()
    getMe().then(setUser).catch(console.error)
  }, [])

  const handleCreateProject = async () => {
    const name = prompt('Enter a name for the new project:')
    if (!name) return
    try {
      const newProject = await createProject(name)
      router.push(`/projects/${newProject.id}/upload`)
    } catch {
      alert('Failed to create project')
    }
  }

  const handleDeleteProject = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project? This will permanently delete its datasets and models.')) return
    try {
      await deleteProject(id)
      loadProjects()
    } catch {
      alert('Failed to delete project')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    router.push('/')
  }

  // Derive human-readable name & initials from email
  const rawHandle = user?.email ? user.email.split('@')[0] : 'User'
  const displayName = rawHandle
    .split(/[._-]/)
    .filter(Boolean)
    .map(p => p.charAt(0).toUpperCase() + p.slice(1))
    .join(' ') || 'User'

  const initials = displayName
    .split(' ')
    .filter(Boolean)
    .map(w => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'U'

  return (
    <main className="min-h-screen bg-[#090b10] text-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-50 flex min-h-16 items-center justify-between border-b border-white/8 bg-[#090b10] px-4 sm:px-8">
        <Link href="/dashboard" className="flex items-center gap-2 text-sm font-semibold">
          <span className="grid size-7 place-items-center rounded-md bg-indigo-500">
            <Layers3 className="size-4" />
          </span>
          autonomo<span className="text-indigo-400">.ai</span>
        </Link>

        {/* User profile & actions */}
        <div className="flex items-center gap-3">
          <ThemeToggle />

          {/* User badge */}
          <div className="flex items-center gap-2 rounded-full border border-white/8 bg-white/[0.03] py-1 pl-1 pr-3">
            <Avatar className="size-7">
              <AvatarFallback className="bg-indigo-500/20 text-[11px] font-semibold text-indigo-200">
                {initials}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs font-medium text-slate-200 max-w-[120px] truncate sm:max-w-[180px]">
              {displayName}
            </span>
          </div>

          {/* Disconnect button */}
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

      {/* Content */}
      <div className="mx-auto max-w-6xl p-5 sm:p-8">
        {/* Hero row */}
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-indigo-300">Workspace overview</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Welcome, <span className="text-indigo-300">{displayName}</span>
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              Manage and monitor every autonomous model lifecycle from one place.
            </p>
          </div>
          <Button onClick={handleCreateProject} className="hidden bg-indigo-500 hover:bg-indigo-400 sm:flex">
            <Plus className="mr-1.5 size-4" />New project
          </Button>
        </div>

        {/* Quick stats derived from real projects */}
        <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            ['Total projects', String(projects.length), 'In your workspace'],
            ['Completed', String(projects.filter(p => p.status === 'Completed').length), 'Fully trained & deployed'],
            ['In progress', String(projects.filter(p => p.status?.startsWith('Running')).length), 'Currently running'],
            ['Avg. quality', projects.length ? (projects.reduce((s, p) => s + (parseFloat(p.quality) || 0), 0) / projects.length).toFixed(1) + '%' : '—', 'Data quality score'],
          ].map(([label, value, detail]) => (
            <div key={label} className="rounded-xl border border-white/8 bg-white/[0.03] p-5">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="mt-3 text-2xl font-semibold">{value}</p>
              <p className="mt-1 text-[11px] text-indigo-300">{detail}</p>
            </div>
          ))}
        </div>

        {/* Projects grid */}
        <div className="mt-10 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold">Projects</h2>
            <p className="mt-1 text-xs text-slate-500">Click any project to continue working on it.</p>
          </div>
          <span className="text-xs text-slate-600">{projects.length} project{projects.length !== 1 ? 's' : ''}</span>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {projects.map(project => (
            <ProjectCard key={project.id} project={project} onDelete={handleDeleteProject} />
          ))}
        </div>

        {projects.length === 0 && (
          <div className="mt-16 flex flex-col items-center gap-3 text-center">
            <p className="text-sm text-slate-500">No projects yet.</p>
            <Button onClick={handleCreateProject} className="bg-indigo-500 hover:bg-indigo-400">
              <Plus className="mr-1.5 size-4" />Create your first project
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
