import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@sentinel/config", "@sentinel/shared", "@sentinel/ui"],
};

export default nextConfig;
