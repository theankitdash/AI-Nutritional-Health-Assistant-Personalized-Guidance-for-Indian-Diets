/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone', // Enable standalone output for Docker
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`, // Proxy to FastAPI backend
            },
        ];
    },
};

export default nextConfig;
