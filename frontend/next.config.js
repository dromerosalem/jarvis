/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Set the backend API URL for production and development
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000',
  },
  // Configure CORS for API requests
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
  // Disable source maps in production
  productionBrowserSourceMaps: false,
  // Enable static optimization
  experimental: {
    optimizeFonts: true,
  },
}

module.exports = nextConfig 