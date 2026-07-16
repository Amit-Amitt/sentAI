import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: [
    "@sentinel/api-client",
    "@sentinel/config",
    "@sentinel/shared",
    "@sentinel/types",
    "@sentinel/ui",
  ],
};

export default nextConfig;
