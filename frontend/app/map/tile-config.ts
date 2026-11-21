// CDN base URL for map tiles — not a secret, committed to code.
// Set this to the "cloudfront_domain" output after running `terraform apply` in infra/.
// Override with NEXT_PUBLIC_TILES_CDN in .env.local to use locally generated tiles instead.
export const TILES_CDN =
  process.env.NEXT_PUBLIC_TILES_CDN ?? "https://d2f3wmk3a1imbc.cloudfront.net"

// Tile version — bumped automatically via PR by the deploy-map-tiles workflow on each release.
// Change this manually to roll back or forward to a different tile version.
export const MAP_TILE_VERSION = "map-v1"

// Full tile URL template passed to Leaflet. When TILES_CDN is empty, falls back to
// locally generated tiles at public/tiles/ (no version prefix).
export const TILE_URL_TEMPLATE =
  TILES_CDN && !TILES_CDN.startsWith("https://d2f3wmk3a1imbc")
    ? `${TILES_CDN}/tiles/${MAP_TILE_VERSION}/{z}/{x}/{y}.png`
    : `/tiles/{z}/{x}/{y}.png`
