'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { ReportTab } from '@/components/project/report-tab'
import { getProjectReport, getProject } from '@/lib/api'

export default function ReportPage() {
  const { projectId } = useParams()
  const [markdown, setMarkdown] = useState("Loading report...")
  const [project, setProject] = useState<any>(null)

  useEffect(() => {
    getProject(projectId as string).then(setProject).catch(console.error)
    getProjectReport(projectId as string)
      .then(res => setMarkdown(res.markdown))
      .catch(err => {
        console.error(err)
        setMarkdown("Failed to load report.")
      })
  }, [projectId])

  return <div className="p-5 sm:p-8"><ReportTab markdown={markdown} project={project} /></div>
}
