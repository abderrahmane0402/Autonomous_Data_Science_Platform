'use client'

import { useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { Code2, Download, Package, Brain, BarChart3, Database } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getProject } from '@/lib/api'

export default function DeploymentsPage() {
  const { projectId } = useParams()
  const [project, setProject] = useState<any>(null)

  useEffect(() => {
    getProject(projectId as string).then(setProject).catch(console.error)
  }, [projectId])

  const isCompleted = project?.status === 'Completed'

  const leaderboard: any[] = Array.isArray(project?.leaderboard) ? project.leaderboard : []
  const sorted = [...leaderboard].sort((a, b) => b.score - a.score)
  const bestEntry = sorted[0]
  const bestScore = bestEntry?.score != null ? Number(bestEntry.score).toFixed(4) : 'N/A'
  const modelsCount = leaderboard.filter(m => m.model).length
  const qualityPct = project?.data_quality_score != null
    ? (project.data_quality_score * 100).toFixed(1) + '%'
    : 'N/A'
  const datasetName = project?.dataset_path
    ? project.dataset_path.split('/').pop().replace(/_engineered|_final/, '')
    : 'N/A'

  const stats = [
    { label: 'Best model', value: isCompleted ? (project?.best_model_name ?? 'N/A') : '—', sub: 'Selected by AutoML', icon: Brain },
    { label: 'Best score', value: isCompleted ? bestScore : '—', sub: 'R² / Accuracy', icon: BarChart3 },
    { label: 'Models trained', value: isCompleted ? String(modelsCount) : '—', sub: 'Candidate algorithms', icon: Package },
    { label: 'Data quality', value: isCompleted ? qualityPct : '—', sub: 'Missing-value score', icon: Database },
  ]

  return (
    <main className="min-h-screen bg-[#090b10] text-slate-100">
      <header className="flex h-16 items-center justify-between border-b border-white/8 px-4 sm:px-7">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold">{project ? project.name : 'Loading'}</span>
          <span className="text-xs text-slate-600">/ Deployments</span>
        </div>
        <Button
          onClick={() => {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            window.open(`${baseUrl}/${project?.deployment_zip_path || ''}`)
          }}
          disabled={!isCompleted}
          className="bg-indigo-500 hover:bg-indigo-400"
        >
          <Download className="mr-2 size-4" />Download Deployment ZIP
        </Button>
      </header>

      <div className="mx-auto max-w-6xl p-5 sm:p-8">
        <p className="text-xs uppercase tracking-[0.2em] text-indigo-300">Production operations</p>
        <h1 className="mt-2 text-3xl font-semibold">Deployments</h1>
        <p className="mt-2 text-sm text-slate-500">
          Package your trained model as a production-ready FastAPI service.
        </p>

        {/* Real stats from the project */}
        <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ label, value, sub, icon: Icon }) => (
            <Card key={label} className="border-white/8 bg-white/[0.03] shadow-none">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <p className="text-xs text-slate-500">{label}</p>
                  <Icon className="size-4 text-slate-700" />
                </div>
                <p className="mt-3 text-2xl font-semibold truncate" title={value}>{value}</p>
                <p className="mt-1 text-[11px] text-slate-600">{sub}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Download card */}
        <Card className="mt-8 border-white/8 bg-white/[0.03] shadow-none">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm">Production API Package</CardTitle>
              <Badge variant="outline" className={isCompleted ? 'border-emerald-400/20 text-emerald-300' : 'border-slate-400/20 text-slate-300'}>
                {isCompleted ? 'Ready' : 'Not Ready'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col gap-3 rounded-lg border border-white/8 bg-black/10 p-4 sm:flex-row sm:items-center">
              <Code2 className="size-4 shrink-0 text-indigo-300" />
              <code className="flex-1 text-xs text-slate-400">
                Download the ZIP to get a fully containerized <strong className="text-slate-300">FastAPI</strong> inference server, a <strong className="text-slate-300">Dockerfile</strong>, and the serialized <strong className="text-slate-300">{project?.best_model_name ?? 'model'}.pkl</strong>.
              </code>
              <Button
                onClick={() => {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            window.open(`${baseUrl}/${project?.deployment_zip_path || ''}`)
          }}
                disabled={!isCompleted}
                variant="outline"
                size="sm"
                className="w-fit border-white/10 bg-transparent text-xs"
              >
                <Download className="mr-1.5 size-3" />Download
              </Button>
            </div>

            {/* What's inside */}
            <div>
              <p className="mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">What's inside the ZIP</p>
              <div className="grid gap-2 sm:grid-cols-3">
                {[
                  ['deployment_api.py', 'FastAPI server with /predict endpoint'],
                  ['Dockerfile', 'Ready to docker build & run'],
                  ['model.pkl', `Serialized ${project?.best_model_name ?? 'best'} model`],
                ].map(([file, desc]) => (
                  <div key={file} className="rounded-lg border border-white/8 bg-black/10 p-3">
                    <p className="text-[11px] font-mono text-indigo-300">{file}</p>
                    <p className="mt-1 text-[11px] text-slate-500">{desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
