// CDN base URL for map tiles — not a secret, committed to code.
// Override with NEXT_PUBLIC_TILES_CDN in .env.local for local dev (set to empty string
// to fall back to locally generated tiles at public/tiles/).
const TILES_CDN =
  process.env.NEXT_PUBLIC_TILES_CDN ?? "https://d2f3wmk3a1imbc.cloudfront.net"

// Tile version — bumped automatically via PR by the deploy-map-tiles workflow on each release.
// Change this manually to roll back or forward to a different tile version.
export const MAP_TILE_VERSION = "map-v2"

// Full tile URL template passed to Leaflet.
export const MAP_TILE_URL_TEMPLATE = TILES_CDN
  ? `${TILES_CDN}/tiles/${MAP_TILE_VERSION}/{z}/{x}/{y}.png`
  : `/tiles/{z}/{x}/{y}.png`

// Overlay tile version — bumped automatically via PR by the deploy-overlay-tiles workflow on each release.
export const OVERLAY_TILE_VERSION = "overlay-v1"

// Overlay tile URL template (borders, labels, coastlines).
export const OVERLAY_MAP_TILE_URL_TEMPLATE =
  TILES_CDN && OVERLAY_TILE_VERSION !== "local"
    ? `${TILES_CDN}/tiles/${OVERLAY_TILE_VERSION}/{z}/{x}/{y}.png`
    : `/tiles/overlay/{z}/{x}/{y}.png`
