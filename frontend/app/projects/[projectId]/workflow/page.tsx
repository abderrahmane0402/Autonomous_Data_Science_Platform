'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Check, CircleDot, Clock3, Play, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { getProject } from '@/lib/api'

export default function WorkflowPage(){
  const { projectId } = useParams()
  const router = useRouter()
  const [project, setProject] = useState<any>(null)

  useEffect(() => {
    const interval = setInterval(() => {
        getProject(projectId as string).then(setProject).catch(console.error)
    }, 3000)
    getProject(projectId as string).then(setProject).catch(console.error)
    return () => clearInterval(interval)
  }, [projectId])

  const status = project?.status || ''
  const isCompleted = status === 'Completed' || status.startsWith('Failed')
  const isRunning = status.startsWith('Running')
  const isNotStarted = !isCompleted && !isRunning

  const phases = ['Supervisor', 'Analyst', 'Engineer', 'ML Engineer', 'Optimizer', 'Explainability', 'Report', 'Deployment']
  let currentIndex = -1
  if (isRunning) {
    const runningPhase = status.replace('Running: ', '')
    currentIndex = phases.indexOf(runningPhase)
    if (currentIndex === -1) currentIndex = 0
  } else if (isCompleted) {
    currentIndex = 99
  }

  const agents = [
      ['Supervisor Agent', currentIndex > 0 ? 'Completed' : (currentIndex === 0 ? 'Running' : 'Idle'), currentIndex > 0 ? 100 : (currentIndex === 0 ? 50 : 0), 'Orchestrating the workflow and validating handoffs.'],
      ['Data Analyst Agent', currentIndex > 1 ? 'Completed' : (currentIndex === 1 ? 'Running' : 'Idle'), currentIndex > 1 ? 100 : (currentIndex === 1 ? 50 : 0), 'Profiled distributions and detected predictive signal.'],
      ['Data Engineer Agent', currentIndex > 2 ? 'Completed' : (currentIndex === 2 ? 'Running' : 'Idle'), currentIndex > 2 ? 100 : (currentIndex === 2 ? 50 : 0), 'Built reproducible transformations and feature views.'],
      ['ML Engineer Agent', currentIndex > 4 ? 'Completed' : ((currentIndex === 3 || currentIndex === 4) ? 'Running' : 'Idle'), currentIndex > 4 ? 100 : ((currentIndex === 3 || currentIndex === 4) ? 50 : 0), 'Training and tuning candidate model families.'],
      ['Evaluation Agent', currentIndex > 7 ? 'Completed' : ((currentIndex >= 5 && currentIndex <= 7) ? 'Running' : 'Idle'), currentIndex > 7 ? 100 : ((currentIndex >= 5 && currentIndex <= 7) ? 50 : 0), 'Generating SHAP plots and creating final reports.']
  ]
  
  return <main className="min-h-screen bg-[#090b10] text-slate-100"><header className="flex h-16 items-center justify-between border-b border-white/8 px-4 sm:px-7"><div className="flex items-center gap-3"><span className="text-sm font-semibold">{project ? project.name : 'Loading'}</span><span className="text-xs text-slate-600">/ AI workflow</span></div>{isCompleted && <Button onClick={() => router.push(`/projects/${projectId}/leaderboard`)} className="bg-emerald-600 hover:bg-emerald-500"><Play data-icon="inline-start" />View Leaderboard</Button>}</header><div className="mx-auto max-w-6xl p-5 sm:p-8"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-xs uppercase tracking-[0.2em] text-indigo-300">Autonomous execution</p><h1 className="mt-2 text-3xl font-semibold">AI agent workflow</h1><p className="mt-2 text-sm text-slate-500">Five specialized agents are collaborating on {project?.name || 'the project'}.</p></div><Badge variant="outline" className={`w-fit ${isCompleted ? 'border-emerald-400/20 text-emerald-300' : (isRunning ? 'border-amber-400/20 text-amber-300' : 'border-slate-400/20 text-slate-300')}`}><CircleDot data-icon="inline-start" />{isCompleted ? 'Completed' : (isRunning ? status : 'Awaiting initialization')}</Badge></div><div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">{agents.map(([name,s,progress,description],i)=><Card key={name as string} className="relative border-white/8 bg-white/[0.03] shadow-none"><CardContent className="p-5"><div className="flex items-center justify-between"><span className="grid size-9 place-items-center rounded-xl bg-indigo-500/10 text-indigo-300"><Sparkles className="size-4" /></span><span className={`text-[10px] ${s==='Completed'?'text-emerald-300':s==='Running'?'text-amber-300':'text-slate-600'}`}>{s as string}</span></div><h2 className="mt-5 text-sm font-medium">{name as string}</h2><Progress value={progress as number} className="mt-4 h-1.5" /><div className="mt-3 flex items-center justify-between text-[10px] text-slate-600"><span>{progress as number}% complete</span><span><Clock3 className="mr-1 inline size-3" />{s === 'Idle' ? 'Waiting' : (s === 'Running' ? 'Active' : 'Done')}</span></div><p className="mt-5 text-xs leading-5 text-slate-500">{description as string}</p>{s !== 'Idle' && <div className="mt-5 border-t border-white/8 pt-4 text-[10px] text-slate-600">State: {s as string}</div>}</CardContent></Card>)}</div><Card className="mt-8 border-white/8 bg-white/[0.03] shadow-none"><CardContent className="p-5"><div className="flex items-center gap-3 text-sm"><Check className={`size-4 ${isNotStarted ? 'text-slate-600' : 'text-emerald-300'}`} />{isNotStarted ? 'Awaiting data and initialization' : 'Workflow context is healthy'}<span className="ml-auto text-xs text-slate-600">{status}</span></div></CardContent></Card></div></main>
}
