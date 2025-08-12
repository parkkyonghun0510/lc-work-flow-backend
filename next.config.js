/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Ignore ESLint errors during builds to avoid blocking deployments.
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;

