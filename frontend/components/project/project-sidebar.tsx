'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  BarChart3, 
  Database, 
  FileText, 
  Rocket, 
  Sparkles, 
  X, 
  Check, 
  Loader2, 
  AlertCircle, 
  Clock, 
  Circle 
} from 'lucide-react'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { getProject } from '@/lib/api'

const tabs = [
  { label: 'Upload data', suffix: '/upload', icon: Database, key: 'upload' },
  { label: 'AI workflow', suffix: '/workflow', icon: Sparkles, key: 'workflow' },
  { label: 'Leaderboard', suffix: '/leaderboard', icon: BarChart3, key: 'leaderboard' },
  { label: 'Report', suffix: '/report', icon: FileText, key: 'report' },
  { label: 'Deployments', suffix: '/deployments', icon: Rocket, key: 'deployments' },
] as const

export function ProjectSidebar({ 
  projectId, 
  mobileOpen = false, 
  onClose 
}: { 
  projectId: string
  mobileOpen?: boolean
  onClose?: () => void 
}) {
  const [project, setProject] = useState<any>(null)
  const pathname = usePathname()

  useEffect(() => {
    let interval: any
    const fetchStatus = () => {
      getProject(projectId)
        .then((p) => {
          setProject(p)
          // If still running, poll every 3s
          if (p?.status?.startsWith('Running')) {
            if (!interval) {
              interval = setInterval(fetchStatus, 3000)
            }
          } else if (interval) {
            clearInterval(interval)
            interval = null
          }
        })
        .catch(console.error)
    }

    fetchStatus()
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [projectId])

  const isCompleted = project?.status === 'Completed'
  const isRunning = project?.status?.startsWith('Running')
  const isFailed = project?.status?.startsWith('Failed')

  const getTabStatus = (key: string) => {
    if (!project) return null
    if (key === 'upload') {
      return project.dataset_path ? 'completed' : 'pending'
    }
    if (key === 'workflow') {
      if (isRunning) return 'running'
      if (isCompleted) return 'completed'
      return 'pending'
    }
    if (key === 'leaderboard') {
      return Array.isArray(project.leaderboard) && project.leaderboard.length > 0 ? 'completed' : 'pending'
    }
    if (key === 'report') {
      return isCompleted ? 'completed' : 'pending'
    }
    if (key === 'deployments') {
      return project.deployment_zip_path ? 'completed' : 'pending'
    }
    return 'pending'
  }

  return (
    <>
      {mobileOpen && (
        <button 
          aria-label="Close project navigation overlay" 
          className="fixed inset-0 top-16 z-40 bg-black/60 lg:hidden print:hidden" 
          onClick={onClose} 
        />
      )}
      <aside 
        className={`${mobileOpen ? 'flex' : 'hidden'} fixed inset-y-16 left-0 z-50 w-[min(86vw,18rem)] flex-col overflow-y-auto border-r border-white/10 bg-[#0c0f16] p-4 shadow-2xl lg:sticky lg:top-16 lg:flex lg:h-[calc(100vh-4rem)] lg:w-64 lg:shadow-none print:hidden`}
      >
        {/* Project Card with Live Status Indicator */}
        <div className="mb-6 rounded-xl border border-white/8 bg-white/[0.03] p-4">
          <p className="text-xs font-semibold text-slate-200 truncate">{project ? project.name : 'Loading...'}</p>
          <p className="mt-1 text-[10px] text-slate-500 font-mono">Project #{projectId}</p>
          
          <div className="mt-3 flex items-center gap-2 text-xs">
            {isCompleted && (
              <>
                <span className="relative flex size-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
                </span>
                <span className="font-medium text-emerald-400">Completed</span>
              </>
            )}
            {isRunning && (
              <>
                <Loader2 className="size-3 animate-spin text-amber-400" />
                <span className="font-medium text-amber-400 truncate">{project.status}</span>
              </>
            )}
            {isFailed && (
              <>
                <AlertCircle className="size-3 text-rose-400" />
                <span className="font-medium text-rose-400 truncate">Failed</span>
              </>
            )}
            {!isCompleted && !isRunning && !isFailed && (
              <>
                <Clock className="size-3 text-slate-500" />
                <span className="text-slate-400">Awaiting Run</span>
              </>
            )}
          </div>
        </div>

        {/* Navigation links with step status icons */}
        <nav className="flex flex-col gap-1">
          {tabs.map(({ label, suffix, icon: Icon, key }) => {
            const href = `/projects/${projectId}${suffix}`
            const isActive = pathname === href
            const stepStatus = getTabStatus(key)

            return (
              <Link
                key={label}
                href={href}
                onClick={onClose}
                className={`group flex min-h-11 items-center justify-between rounded-lg px-3 py-2.5 text-xs transition-colors ${
                  isActive
                    ? 'bg-indigo-500/10 text-indigo-300 font-medium'
                    : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`size-4 ${isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span>{label}</span>
                </div>

                {/* Status icon on the right side of nav item */}
                <div className="flex items-center pl-2">
                  {stepStatus === 'completed' && (
                    <span title="Ready / Completed" className="flex size-4 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
                      <Check className="size-2.5 stroke-[3]" />
                    </span>
                  )}
                  {stepStatus === 'running' && (
                    <span title="In Progress">
                      <Loader2 className="size-3 animate-spin text-amber-400" />
                    </span>
                  )}
                  {stepStatus === 'pending' && (
                    <Circle className="size-1.5 fill-slate-700 text-slate-700" />
                  )}
                </div>
              </Link>
            )
          })}
        </nav>

        <Separator className="my-6 bg-white/8" />
        <p className="px-3 text-[10px] leading-5 text-slate-500">
          Autonomous machine learning workspace. Track ingestion, modeling, reports, and production API packages.
        </p>

        <Button 
          variant="ghost" 
          size="sm" 
          className="mt-auto justify-start text-slate-500 lg:hidden" 
          onClick={onClose}
        >
          <X className="mr-2 size-3" />Close menu
        </Button>
      </aside>
    </>
  )
}
