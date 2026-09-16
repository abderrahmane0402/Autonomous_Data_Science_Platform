'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { login, signup } from '@/lib/api'

export function LoginForm({ isSignUp }: { isSignUp: boolean }) {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (isSignUp) {
        await signup(email, password)
        const { access_token } = await login(email, password)
        localStorage.setItem('token', access_token)
        document.cookie = `token=${access_token}; path=/; max-age=604800; samesite=strict`
        router.push('/dashboard')
      } else {
        const { access_token } = await login(email, password)
        localStorage.setItem('token', access_token)
        document.cookie = `token=${access_token}; path=/; max-age=604800; samesite=strict`
        router.push('/dashboard')
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="flex flex-col gap-3.5" onSubmit={handleSubmit}>
      {error && (
        <div className="text-red-400 text-xs bg-red-900/20 border border-red-500/20 p-3 rounded-md">
          {error}
        </div>
      )}
      
      <div className="relative">
        <Mail className="absolute left-3 top-3.5 size-4 text-slate-500" />
        <Input 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your.email@example.com" 
          required
          className="h-11 border-white/10 bg-white/[0.04] pl-10 text-white placeholder:text-slate-500 text-xs" 
        />
      </div>
      
      <div className="relative">
        <LockKeyhole className="absolute left-3 top-3.5 size-4 text-slate-500" />
        <Input 
          type={showPassword ? 'text' : 'password'} 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password" 
          required
          className="h-11 border-white/10 bg-white/[0.04] pl-10 pr-10 text-white placeholder:text-slate-500 text-xs" 
        />
        <button 
          type="button" 
          aria-label="Toggle password visibility" 
          onClick={() => setShowPassword(!showPassword)} 
          className="absolute right-3 top-3.5 text-slate-500 hover:text-slate-300"
        >
          {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </button>
      </div>

      <Button 
        disabled={loading} 
        type="submit" 
        className="h-11 bg-indigo-500 text-white hover:bg-indigo-400 disabled:opacity-50 text-xs font-medium mt-1"
      >
        {loading ? 'Entering...' : (isSignUp ? 'Create Demo Account' : 'Enter Workspace Demo')} 
        <ArrowRight className="ml-1.5 size-3.5" />
      </Button>

      <p className="text-center text-[11px] text-slate-500">
        This is an interactive demo environment.
      </p>
    </form>
  )
}
