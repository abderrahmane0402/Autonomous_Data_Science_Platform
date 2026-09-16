'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Download, Rocket, Printer, FileDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useRouter } from 'next/navigation'

export function ReportTab({ markdown, project }: { markdown: string, project: any }) {
  const router = useRouter()
  if (!project) return <div className="p-8 text-slate-500 text-sm">Loading...</div>

  const quality = project.data_quality_score
    ? (project.data_quality_score * 100).toFixed(1) + '%'
    : 'N/A'

  const handlePrintPdf = () => {
    window.print()
  }

  const handleDownloadMarkdown = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${(project?.name || 'project').replace(/\s+/g, '_')}_final_report.md`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const components: any = {
    h1: ({ children }: any) => <h1 className="mt-8 mb-4 text-2xl font-bold text-slate-100 border-b border-white/10 pb-3 print:text-black print:border-slate-300">{children}</h1>,
    h2: ({ children }: any) => <h2 className="mt-8 mb-3 text-xl font-semibold text-slate-100 print:text-black">{children}</h2>,
    h3: ({ children }: any) => <h3 className="mt-6 mb-2 text-base font-semibold text-indigo-300 print:text-indigo-800">{children}</h3>,
    h4: ({ children }: any) => <h4 className="mt-4 mb-2 text-sm font-semibold text-slate-200 uppercase tracking-wider print:text-slate-800">{children}</h4>,
    p: ({ children, node }: any) => {
      // If this paragraph only wraps an image, render as div to avoid invalid nesting
      const hasImage = node?.children?.some((c: any) => c.tagName === 'img')
      if (hasImage) return <div className="mb-4">{children}</div>
      return <p className="mb-4 text-sm leading-7 text-slate-400 print:text-slate-800">{children}</p>
    },
    ul: ({ children }: any) => <ul className="mb-4 ml-4 space-y-1.5 list-disc marker:text-indigo-400 print:marker:text-slate-600">{children}</ul>,
    ol: ({ children }: any) => <ol className="mb-4 ml-4 space-y-1.5 list-decimal marker:text-indigo-400 print:marker:text-slate-600">{children}</ol>,
    li: ({ children }: any) => <li className="text-sm text-slate-400 leading-6 pl-1 print:text-slate-800">{children}</li>,
    strong: ({ children }: any) => <strong className="font-semibold text-slate-200 print:text-black">{children}</strong>,
    em: ({ children }: any) => <em className="italic text-slate-300 print:text-slate-800">{children}</em>,
    blockquote: ({ children }: any) => (
      <blockquote className="my-4 border-l-4 border-indigo-500 bg-indigo-500/5 pl-4 pr-3 py-3 rounded-r-lg text-sm text-slate-300 italic print:bg-slate-100 print:text-slate-900 print:border-indigo-600">
        {children}
      </blockquote>
    ),
    hr: () => <hr className="my-8 border-white/10 print:border-slate-300" />,
    code: ({ children, className }: any) => {
      const isBlock = className?.includes('language-')
      return isBlock
        ? <code className="block my-4 rounded-lg bg-black/30 border border-white/8 p-4 text-xs text-emerald-300 font-mono whitespace-pre-wrap overflow-x-auto print:bg-slate-50 print:text-slate-900 print:border-slate-300">{children}</code>
        : <code className="rounded bg-white/5 border border-white/10 px-1.5 py-0.5 text-xs text-emerald-300 font-mono print:bg-slate-100 print:text-slate-900 print:border-slate-300">{children}</code>
    },
    pre: ({ children }: any) => <pre className="my-4 rounded-lg bg-black/30 border border-white/8 p-4 overflow-x-auto print:bg-slate-50 print:border-slate-300">{children}</pre>,
    table: ({ children }: any) => (
      <div className="my-6 overflow-x-auto rounded-lg border border-white/8 print:border-slate-300">
        <table className="w-full text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }: any) => <thead className="bg-white/[0.03] border-b border-white/8 print:bg-slate-100 print:border-slate-300">{children}</thead>,
    tbody: ({ children }: any) => <tbody className="divide-y divide-white/5 print:divide-slate-200">{children}</tbody>,
    tr: ({ children }: any) => <tr className="hover:bg-white/[0.02] transition-colors print:hover:bg-transparent">{children}</tr>,
    th: ({ children }: any) => <th className="px-4 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-500 print:text-slate-700">{children}</th>,
    td: ({ children }: any) => <td className="px-4 py-3 text-xs text-slate-400 print:text-slate-800">{children}</td>,
    img: ({ src, alt }: any) => {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      return (
        <div className="my-6">
          <img src={`${baseUrl}/reports/${src}`} alt={alt} className="rounded-lg border border-white/8 max-w-full print:border-slate-300" />
          {alt && <div className="mt-2 text-center text-xs text-slate-500 print:text-slate-600">{alt}</div>}
        </div>
      )
    },
    a: ({ href, children }: any) => <a href={href} className="text-indigo-400 underline underline-offset-2 hover:text-indigo-300 print:text-indigo-600" target="_blank" rel="noreferrer">{children}</a>,
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_300px] print:block">
      {/* Main report */}
      <article className="rounded-xl border border-white/8 bg-white/[0.03] p-6 sm:p-8 min-h-[60vh] print:p-0 print:border-none print:bg-transparent">
        <div className="flex items-start justify-between mb-2">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-indigo-300 print:text-slate-500">Autonomous report</p>
            <h2 className="mt-1 text-2xl font-semibold text-slate-100 print:text-black">{project.name}</h2>
          </div>
          <div className="flex flex-wrap gap-2 print:hidden">
            <Button 
              onClick={handlePrintPdf} 
              variant="outline" 
              className="border-white/10 bg-transparent text-xs hover:bg-white/5"
              title="Print or Save as PDF"
            >
              <Printer className="mr-1.5 size-3 text-indigo-300" />Save / Print PDF
            </Button>
            <Button 
              onClick={handleDownloadMarkdown} 
              variant="outline" 
              className="border-white/10 bg-transparent text-xs hover:bg-white/5"
              title="Download raw markdown file"
            >
              <FileDown className="mr-1.5 size-3" />Markdown
            </Button>
            <Button 
              onClick={() => router.push(`/projects/${project.id}/deployments`)} 
              className="bg-indigo-600 hover:bg-indigo-500 text-xs"
            >
              <Rocket className="mr-1.5 size-3" />Deployments
            </Button>
          </div>
        </div>
        <div className="mt-6">
          <ReactMarkdown components={components} remarkPlugins={[remarkGfm]}>
            {markdown}
          </ReactMarkdown>
        </div>
      </article>

      {/* Sidebar stats */}
      <div className="flex flex-col gap-3 print:hidden">
        {([
          ['Data quality', quality, 'Based on missing values'],
          ['Best model', project.best_model_name || 'N/A', 'Ready for production'],
          ['Project status', project.status, 'Managed autonomously'],
          ['Recommendation', 'Deploy', 'Review final report'],
        ] as const).map(([label, value, sub]) => (
          <Card key={label} className="border-white/8 bg-white/[0.03] shadow-none">
            <CardContent className="p-5">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="mt-3 text-xl font-semibold text-slate-100 break-words">{value}</p>
              <p className="mt-1 text-[11px] text-indigo-300">{sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
