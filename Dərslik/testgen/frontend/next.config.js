/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    // Variant generation (25 questions, 5 concurrent) can take 30-40 minutes.
    // Default Next.js 16 rewrite proxy timeout is 30s — far too short.
    proxyTimeout: 2_700_000,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL || 'http://backend:8000'}/api/:path*`,
      },
    ]
  },
}
module.exports = nextConfig