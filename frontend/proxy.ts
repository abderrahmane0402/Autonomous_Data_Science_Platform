import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // Try to get token from a cookie (if we switch to HTTP-only cookies)
  // Since we are using localStorage for this MVP, the middleware can't actually read localStorage.
  // Next.js middleware runs on the Edge, so we have to rely on a cookie, or we do a simple client-side check.
  
  // For a robust SaaS, we check if the user is trying to access protected routes
  const path = request.nextUrl.pathname
  const isProtectedRoute = path.startsWith('/dashboard') || path.startsWith('/projects')

  const token = request.cookies.get('token')?.value
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
