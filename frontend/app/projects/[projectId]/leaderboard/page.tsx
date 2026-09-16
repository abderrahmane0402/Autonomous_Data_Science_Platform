'use client'

import { useParams, useRouter } from 'next/navigation'
import { Search, Scale, FileText } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { getProject } from '@/lib/api'

export default function LeaderboardPage() {
  const { projectId } = useParams()
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [project, setProject] = useState<any>(null)

  useEffect(() => {
    getProject(projectId as string).then(setProject).catch(console.error)
  }, [projectId])

  const leaderboard = Array.isArray(project?.leaderboard) ? project.leaderboard : []
  const sorted = [...leaderboard].sort((a: any, b: any) => b.score - a.score)
  const filtered = sorted.filter((r: any) => (r.model || '').toLowerCase().includes(query.toLowerCase()))

  return <main className="min-h-screen bg-[#090b10] text-slate-100"><header className="flex h-16 items-center justify-between border-b border-white/8 px-4 sm:px-7"><div className="flex items-center gap-3"><span className="text-sm font-semibold">{project ? project.name : 'Loading'}</span><span className="text-xs text-slate-600">/ Leaderboard</span></div><div className="flex gap-2"><Button variant="outline" className="border-white/10 bg-transparent text-xs"><Scale data-icon="inline-start" />Compare models</Button><Button onClick={() => router.push(`/projects/${projectId}/report`)} className="bg-indigo-600 hover:bg-indigo-500 text-xs"><FileText className="mr-2 size-4" />See AI generated report</Button></div></header><div className="mx-auto max-w-6xl p-5 sm:p-8"><p className="text-xs uppercase tracking-[0.2em] text-indigo-300">Model selection</p><h1 className="mt-2 text-3xl font-semibold">Leaderboard</h1><p className="mt-2 text-sm text-slate-500">AutoML models ranked by validation score.</p><Card className="mt-8 border-white/8 bg-white/[0.03] shadow-none"><CardHeader className="flex flex-col gap-4 border-b border-white/8 sm:flex-row sm:items-center sm:justify-between"><CardTitle className="text-sm">Candidate models</CardTitle><div className="relative"><Search className="absolute left-3 top-2.5 size-4 text-slate-600" /><Input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search models" className="h-9 border-white/10 bg-black/10 pl-9 text-xs" /></div></CardHeader><CardContent className="overflow-x-auto p-0"><Table><TableHeader><TableRow className="border-white/8 hover:bg-transparent">{['Rank','Model','Score (R2/Acc)','MAE','MSE','Status'].map((x,i)=><TableHead key={x+i} className="whitespace-nowrap text-[10px] uppercase tracking-wider text-slate-600">{x}</TableHead>)}</TableRow></TableHeader><TableBody>{filtered.map((r:any,i:number)=><TableRow key={r.model + i} className={`border-white/8 ${i===0?'bg-indigo-500/[0.06]':''}`}><TableCell className="whitespace-nowrap text-xs font-semibold text-indigo-300">{i+1}</TableCell><TableCell className="whitespace-nowrap text-xs font-medium text-slate-200">{r.model || 'Unknown / Error'}</TableCell><TableCell className="whitespace-nowrap text-xs text-slate-500">{r.score != null ? Number(r.score).toFixed(4) : 'N/A'}</TableCell><TableCell className="whitespace-nowrap text-xs text-slate-500">{r.mae != null ? Number(r.mae).toFixed(4) : 'N/A'}</TableCell><TableCell className="whitespace-nowrap text-xs text-slate-500">{r.mse != null ? Number(r.mse).toFixed(4) : 'N/A'}</TableCell><TableCell className="whitespace-nowrap text-xs text-slate-500"><Badge variant="outline" className={r.model ? "border-emerald-400/20 text-emerald-300" : "border-red-400/20 text-red-300"}>{r.model ? 'Ready' : 'Failed'}</Badge></TableCell></TableRow>)}</TableBody></Table></CardContent></Card></div></main>
}
