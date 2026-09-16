/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  basePath: '/Autonomo',
  images: {
    unoptimized: true,
  },
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // Route to the backend Docker container directly
        destination: 'http://backend:8000/:path*',
      },
    ]
  },
}

export default nextConfig
