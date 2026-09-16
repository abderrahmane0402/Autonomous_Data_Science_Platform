'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'
import { getProject } from '@/lib/api'

export default function ProjectPage() {
  const { projectId } = useParams()
  const router = useRouter()

  useEffect(() => {
    if (!projectId) return

    getProject(projectId as string)
      .then((project) => {
        if (project?.status === 'Completed') {
          router.replace(`/projects/${projectId}/report`)
        } else if (project?.status?.startsWith('Running')) {
          router.replace(`/projects/${projectId}/workflow`)
        } else {
          router.replace(`/projects/${projectId}/upload`)
        }
      })
      .catch((err) => {
        console.error('Failed to resolve project status for redirect:', err)
        router.replace(`/projects/${projectId}/upload`)
      })
  }, [projectId, router])

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
      <div className="flex flex-col items-center gap-3 text-slate-500">
        <Loader2 className="size-6 animate-spin text-indigo-400" />
        <p className="text-xs">Loading project workspace...</p>
      </div>
    </div>
  )
}
