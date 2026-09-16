'use client'

import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const [isLight, setIsLight] = useState(false)

  useEffect(() => {
    const saved = window.localStorage.getItem('autonomo-theme')
    const light = saved === 'light'
    document.documentElement.classList.toggle('light', light)
    document.documentElement.classList.toggle('dark', !light)
    setIsLight(light)
  }, [])

  function toggleTheme() {
    const nextIsLight = !isLight
    document.documentElement.classList.toggle('light', nextIsLight)
    document.documentElement.classList.toggle('dark', !nextIsLight)
    window.localStorage.setItem('autonomo-theme', nextIsLight ? 'light' : 'dark')
    setIsLight(nextIsLight)
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      aria-label={isLight ? 'Switch to dark theme' : 'Switch to light theme'}
      className="text-slate-400 hover:bg-white/10 hover:text-foreground"
    >
      {isLight ? <Moon data-icon="inline-start" /> : <Sun data-icon="inline-start" />}
    </Button>
  )
}
