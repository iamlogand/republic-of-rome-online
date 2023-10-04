/** @type {import('next').NextConfig} */

if (typeof globalThis.AbortController === "undefined") {
  globalThis.AbortController = require("abort-controller")
}

const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
