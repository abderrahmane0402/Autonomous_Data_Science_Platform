import Link from 'next/link'
import { ArrowUpRight, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

export type Project = { id: string; name: string; desc: string; status: string; rows: string; quality: string; time: string; color?: string }

export function ProjectCard({ project, onDelete }: { project: Project, onDelete?: (id: string) => void }) {
  const targetUrl = project.status === 'Completed'
    ? `/projects/${project.id}/report`
    : project.status?.startsWith('Running')
    ? `/projects/${project.id}/workflow`
    : `/projects/${project.id}/upload`

  return <Link href={targetUrl}><Card className="group border-white/8 bg-white/[0.03] shadow-none transition hover:-translate-y-0.5 hover:border-indigo-400/30 relative"><CardContent className="p-5">
    
    {onDelete && (
      <button 
        onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(project.id); }}
        className="absolute top-3 right-3 p-1.5 rounded bg-black/40 text-slate-500 hover:text-red-400 hover:bg-black/60 z-10"
      >
        <Trash2 className="size-4" />
      </button>
    )}
    
    <div className={`h-24 rounded-lg bg-gradient-to-br ${project.color ?? 'from-indigo-500/20'} to-transparent`} /><div className="mt-5 flex items-start justify-between gap-3"><div><h3 className="text-sm font-medium group-hover:text-indigo-300">{project.name}</h3><p className="mt-1 text-xs leading-5 text-slate-500">{project.desc}</p></div><ArrowUpRight className="size-4 text-slate-600" /></div><div className="mt-5 flex items-center justify-between"><Badge variant="outline" className="border-emerald-400/20 text-[10px] text-emerald-300">{project.status}</Badge><span className="text-xs text-slate-500">{project.quality} quality</span></div><div className="mt-4 flex justify-between border-t border-white/8 pt-4 text-[10px] text-slate-600"><span>{project.rows} rows</span><span>{project.time}</span></div></CardContent></Card></Link>
}
