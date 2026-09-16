'use client'

import { useState } from 'react'
import { BarChart3, Check, Zap } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { LoginForm } from '@/components/auth/login-form'

export default function HomePage() {
  const [isSignUp, setIsSignUp] = useState(false)

  return (
    <main className="min-h-screen bg-[#090b10] text-white lg:grid lg:grid-cols-[minmax(360px,0.9fr)_1.1fr]">
      {/* Left Column: Demo access & description */}
      <section className="flex min-h-screen flex-col justify-between border-r border-white/8 px-6 py-7 sm:px-10 lg:px-16">
        <header className="flex items-center justify-between gap-3 text-sm font-semibold tracking-tight">
          <span className="flex items-center gap-3">
            <span className="grid size-8 place-items-center rounded-lg bg-indigo-500 text-white">
              <BarChart3 className="size-4" />
            </span>
            autonomo<span className="text-indigo-400">.ai</span>
            <span className="rounded-full border border-indigo-400/20 bg-indigo-500/10 px-2 py-0.5 text-[10px] font-medium text-indigo-300">
              Interactive Demo
            </span>
          </span>
          <ThemeToggle />
        </header>

        <div className="mx-auto w-full max-w-md py-8">
          <div className="mb-6">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">
              AI Engineering Project
            </p>
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Autonomous Data Science <span className="text-indigo-400">Platform</span>
            </h1>
            <p className="mt-3 text-xs leading-5 text-slate-400">
              An end-to-end multi-agent AI pipeline that ingests raw datasets, automates feature engineering, trains candidate models, generates SHAP explainability insights, and packages production-ready FastAPI deployments.
            </p>
          </div>

          <div className="mb-5 flex rounded-lg bg-white/[0.04] p-1">
            <button 
              onClick={() => setIsSignUp(false)} 
              className={`flex-1 rounded-md py-2 text-xs font-medium transition ${!isSignUp ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
            >
              Sign in
            </button>
            <button 
              onClick={() => setIsSignUp(true)} 
              className={`flex-1 rounded-md py-2 text-xs font-medium transition ${isSignUp ? 'bg-white/10 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
            >
              Create account
            </button>
          </div>
          
          <LoginForm isSignUp={isSignUp} />
        </div>

        <footer className="pt-4 border-t border-white/8 text-xs text-slate-500">
          <p>Portfolio project demonstrating autonomous agentic workflows & machine learning automation.</p>
        </footer>
      </section>

      {/* Right Column: Live pipeline preview card */}
      <section className="relative hidden overflow-hidden bg-[#0d111a] lg:flex lg:items-center lg:justify-center p-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_35%,rgba(99,82,255,0.22),transparent_40%),radial-gradient(circle_at_30%_80%,rgba(27,148,255,0.08),transparent_35%)]" />
        
        <div className="relative w-full max-w-xl">
          <div className="mb-4 flex items-center justify-between text-xs text-slate-500">
            <span className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
              MULTI-AGENT PIPELINE
            </span>
            <span className="font-mono text-[11px] text-indigo-300">LIVE ORCHESTRATION</span>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#121722]/90 p-6 shadow-2xl shadow-indigo-950/40 backdrop-blur">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Sample Execution</p>
                <h2 className="mt-1 text-lg font-semibold text-slate-100">Predictive Modeling Workflow</h2>
              </div>
              <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300 font-medium">
                Active Agents
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-5">
              {[
                ['Supervisor', 'Orchestrates', 'LangGraph'],
                ['AutoML', '5+ Models', 'Scikit-Learn'],
                ['Explainability', 'SHAP Plots', 'Interpretability'],
              ].map(([label, value, detail]) => (
                <div key={label} className="rounded-xl border border-white/8 bg-white/[0.03] p-3.5">
                  <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
                  <p className="mt-2 text-base font-semibold text-slate-200">{value}</p>
                  <p className="mt-1 text-[10px] text-indigo-300">{detail}</p>
                </div>
              ))}
            </div>

            <div className="rounded-xl border border-white/8 bg-black/20 p-4">
              <div className="mb-3 flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium">Collaborating AI Agents</span>
                <span className="text-[11px] text-slate-500">Autonomous loop</span>
              </div>
              {[
                'Supervisor Agent · Problem formulation & routing',
                'Data Analyst Agent · Schema profiling & quality scoring',
                'Data Engineer Agent · Automated feature transformations',
                'ML Engineer Agent · Algorithm evaluation & leaderboard',
                'Explainability Agent · Feature attribution with SHAP',
                'Deployment Agent · Production FastAPI packaging',
              ].map((agent, index) => (
                <div key={agent} className="mb-2.5 flex items-center gap-2.5 last:mb-0">
                  <span className="grid size-5 shrink-0 place-items-center rounded-md bg-indigo-500/15 text-indigo-300">
                    <Check className="size-3 text-indigo-300" />
                  </span>
                  <span className="text-xs text-slate-300 truncate">{agent}</span>
                </div>
              ))}
            </div>
          </div>

          <p className="mt-4 text-center text-xs text-slate-500">
            Sign in with any email to test with your own CSV, Excel, or Parquet dataset.
          </p>
        </div>
      </section>
    </main>
  )
}
