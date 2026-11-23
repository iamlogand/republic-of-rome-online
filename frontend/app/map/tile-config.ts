// CDN base URL for map tiles — not a secret, committed to code.
// Override with NEXT_PUBLIC_TILES_CDN in .env for local dev (set to empty string
// to fall back to locally generated tiles at public/tiles/).
const TILES_CDN =
  process.env.NEXT_PUBLIC_TILES_CDN ?? "https://d2f3wmk3a1imbc.cloudfront.net"

// Tile version — update manually after publishing a release and deploying new tiles.
export const BASE_TILE_VERSION = "map-base/v1"

// Full tile URL template passed to Leaflet.
export const MAP_TILE_URL_TEMPLATE = TILES_CDN
  ? `${TILES_CDN}/tiles/${BASE_TILE_VERSION}/{z}/{x}/{y}.png`
  : `/tiles/map-base/{z}/{x}/{y}.png`

// Overlay tile version — update manually after publishing a release and deploying new tiles.
export const OVERLAY_TILE_VERSION = "map-overlay/v1"

// Overlay tile URL template (borders, labels, coastlines).
export const OVERLAY_MAP_TILE_URL_TEMPLATE = TILES_CDN
  ? `${TILES_CDN}/tiles/${OVERLAY_TILE_VERSION}/{z}/{x}/{y}.png`
  : `/tiles/map-overlay/{z}/{x}/{y}.png`
