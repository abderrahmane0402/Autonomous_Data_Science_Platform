'use client'

import { ChangeEvent, useRef, useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { CloudUpload, Database, Upload, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { uploadDataset, runAIWorkflow, getUploadProgress, getProject, removeDataset } from '@/lib/api'

export default function UploadPage() {
  const params = useParams()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [progressStatus, setProgressStatus] = useState("Initializing...")
  const [progressPercent, setProgressPercent] = useState(0)
  const [redactPii, setRedactPii] = useState(false)
  const [existingDataset, setExistingDataset] = useState<string | null>(null)
  const [existingMetadata, setExistingMetadata] = useState<any>(null)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()
  
  const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
    // If the user selects a new file, clear the previous upload result
    setUploadResult(null)
  }
  
  useEffect(() => {
    if (params?.projectId) {
      getProject(params.projectId as string)
        .then(proj => {
          if (proj.dataset_path) {
            setExistingDataset(proj.dataset_path)
            if (proj.dataset_metadata) {
              setExistingMetadata(proj.dataset_metadata)
            }
          }
        })
        .catch(console.error)
    }
  }, [params?.projectId])
  
  useEffect(() => {
    let interval: any
    if (isUploading && selectedFile) {
        interval = setInterval(() => {
            getUploadProgress(selectedFile.name)
              .then(data => {
                  setProgressStatus(data.status || "Processing...")
                  setProgressPercent(data.percent || 0)
              })
              .catch(console.error)
        }, 1000)
    }
    return () => clearInterval(interval)
  }, [isUploading, selectedFile])
  
  const handleUpload = async () => {
    if (!selectedFile) return
    setIsUploading(true)
    setProgressPercent(0)
    setProgressStatus("Uploading file...")
    try {
      const result = await uploadDataset(selectedFile, params?.projectId as string, redactPii)
      setUploadResult(result)
    } catch (e: any) {
      alert(e.message || "Failed to upload dataset")
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveDataset = async () => {
    if (!confirm("Are you sure you want to detach and delete the dataset from this project?")) return;
    try {
      await removeDataset(params?.projectId as string)
      setExistingDataset(null)
      setExistingMetadata(null)
    } catch (e: any) {
      alert(e.message || "Failed to remove dataset")
    }
  }

  const handleRunAgents = async () => {
    if (!uploadResult || !params?.projectId) return

    // Start the AI workflow and redirect to the workflow tab
    try {
      await runAIWorkflow(uploadResult, params.projectId as string)
      router.push(`/projects/${params.projectId}/workflow`)
    } catch (e) {
      alert("Failed to start workflow")
    }
  }

  const hasStats = uploadResult?.metadata || existingMetadata;

  return <div className="p-5 sm:p-8"><p className="text-xs uppercase tracking-[0.2em] text-indigo-300">Data foundation</p><h1 className="mt-2 text-3xl font-semibold tracking-tight">Upload your dataset</h1><p className="mt-2 max-w-xl text-sm text-slate-500">Bring in a clean source of truth and let autonomo.ai profile, validate, and prepare it for modeling.</p>
  
  {existingDataset && !selectedFile && !uploadResult && (
    <div className="mt-6 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
      <p className="text-sm font-medium text-emerald-400">✅ Dataset already attached</p>
      <p className="mt-1 text-xs text-slate-300">
        This project is already using: <span className="font-mono text-emerald-300">{existingDataset}</span>
      </p>
      <p className="mt-2 text-xs text-slate-400">
        You can continue to the Workflow tab, or upload a new file below to overwrite it.
      </p>
      <div className="flex gap-3 mt-3">
        <Button onClick={() => router.push(`/projects/${params.projectId}/workflow`)} className="bg-emerald-600 hover:bg-emerald-500" size="sm">
          Go to Workflow
        </Button>
        <Button 
          onClick={async () => {
            if (!existingMetadata || !params?.projectId) return;
            try {
              const fakeUploadResult = { metadata: existingMetadata, saved_path: existingDataset };
              await runAIWorkflow(fakeUploadResult, params.projectId as string);
              router.push(`/projects/${params.projectId}/workflow`);
            } catch(e) {
              alert("Failed to start workflow");
            }
          }} 
          className="bg-indigo-600 hover:bg-indigo-500" size="sm"
        >
          <Play className="mr-2 size-4" /> Run AI Agents
        </Button>
        <Button onClick={handleRemoveDataset} variant="outline" className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300" size="sm">
          Remove Dataset
        </Button>
      </div>
    </div>
  )}

  <div className={`mt-8 grid gap-6 ${hasStats ? 'lg:grid-cols-2' : ''}`}>
  
  <Card className="border-dashed border-indigo-400/30 bg-indigo-500/[0.04] shadow-none h-full"><CardContent className="flex h-full flex-col items-center justify-center text-center p-6"><input ref={inputRef} type="file" accept=".csv,.xlsx,.parquet" onChange={handleFile} className="sr-only" aria-label="Choose dataset file" /><span className="grid size-16 place-items-center rounded-2xl bg-indigo-500/15 text-indigo-300"><CloudUpload className="size-7" /></span><h2 className="mt-5 text-lg font-medium">Drop CSV, Excel, or Parquet files here</h2><p className="mt-2 text-xs text-slate-500">Up to 5GB per file - encrypted in transit and at rest</p>
  
  <div className="flex gap-4 mt-5">
    <Button onClick={() => inputRef.current?.click()} className="bg-indigo-500 hover:bg-indigo-400"><Upload data-icon="inline-start" />{selectedFile ? 'Change file' : 'Choose file'}</Button>
    {selectedFile && (
      <Button onClick={() => { setSelectedFile(null); setUploadResult(null); if(inputRef.current) inputRef.current.value=''; }} variant="outline" className="border-indigo-400/20 text-slate-300 hover:bg-indigo-500/10 hover:text-white">
        Remove
      </Button>
    )}
    {selectedFile && !uploadResult && (
      <Button onClick={handleUpload} disabled={isUploading} className="bg-emerald-600 hover:bg-emerald-500">
        {isUploading ? (redactPii ? 'Analyzing NLP & Uploading...' : 'Uploading...') : 'Upload Dataset'}
      </Button>
    )}
    {uploadResult && (
      <Button onClick={handleRunAgents} className="bg-emerald-600 hover:bg-emerald-500">
        <Play className="mr-2 size-4" /> Run AI Agents
      </Button>
    )}
  </div>
  
  {selectedFile && !uploadResult && !isUploading && (
    <div className="mt-6 flex flex-col items-center gap-2 rounded-lg border border-indigo-400/20 bg-indigo-500/5 p-4 text-left max-w-md">
      <div className="flex items-center gap-3 w-full">
        <input 
          type="checkbox" 
          id="redactPii" 
          checked={redactPii} 
          onChange={(e) => setRedactPii(e.target.checked)} 
          className="size-4 rounded border-indigo-400/30 bg-black/20 text-indigo-500 focus:ring-indigo-500" 
        />
        <label htmlFor="redactPii" className="text-sm font-medium text-slate-200 cursor-pointer">
          🔒 Redact PII (English text only)
        </label>
      </div>
      <p className="text-[11px] text-slate-500 pl-7">
        Uses NLP to scan and anonymize Names, Emails, and Phone Numbers in free-text. Not recommended for non-English datasets as it may incorrectly redact valid words. (Warning: Taking this action on large files can take several minutes).
      </p>
    </div>
  )}
  
  {isUploading && (
    <div className="mt-6 w-full max-w-sm text-center">
      <Progress value={progressPercent} className="h-2 w-full bg-indigo-500/20" />
      <p className="mt-3 text-xs text-indigo-300">
        {progressStatus}<br/>
        This can take several minutes depending on hardware...
      </p>
    </div>
  )}
  
  {selectedFile && !uploadResult && !isUploading && <p className="mt-4 text-xs text-indigo-300">Selected: {selectedFile.name}</p>}
  {uploadResult && <p className="mt-4 text-xs text-emerald-400">Successfully Uploaded & Anonymized: {uploadResult.filename}</p>}
  </CardContent></Card>
  
  {hasStats && (
    <Card className="border-white/8 bg-white/[0.03] shadow-none h-full flex flex-col">
      <CardHeader><CardTitle className="text-sm">Dataset validation</CardTitle></CardHeader>
      <CardContent className="flex-1 flex flex-col justify-center">
        {(() => {
          const displayMeta = uploadResult?.metadata || existingMetadata;
          return (
            <>
              <div className="flex items-center gap-3"><Database className="size-4 text-indigo-300" /><div className="flex-1"><div className="flex justify-between text-xs"><span className="text-slate-300">Quality validation</span><span className="text-emerald-300">{displayMeta.quality_score * 100}%</span></div><Progress value={displayMeta.quality_score * 100} className="mt-2 h-1.5" /></div></div>
              <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4">
                {[
                  ['Rows', displayMeta.rows],
                  ['Columns', displayMeta.columns],
                  ['Missing', displayMeta.missing_values_percentage + '%'],
                  ['Memory', displayMeta.memory_usage_mb + ' MB']
                ].map(([a,b])=><div key={a as string} className="rounded-lg border border-white/8 bg-black/10 p-4 flex flex-col items-center justify-center text-center"><p className="text-[11px] text-slate-500">{a}</p><p className="mt-2 text-lg font-semibold">{b}</p></div>)}
              </div>
            </>
          )
        })()}
      </CardContent>
    </Card>
  )}
  
  </div>
  </div>
}
