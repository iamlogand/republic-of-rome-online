"use client"

import { useEffect, useRef, useState } from "react"
import { TILE_URL_TEMPLATE } from "./tile-config"

// CRS.Simple coordinate system derived from the tile generation scheme.
//
// The source image is 24,576 × 16,384 px.  At MAX_ZOOM = 6 each tile covers
// exactly 256 × 256 pixels of the original, so the full image spans:
//   lng: 0 → 24576/64 = 384
//   lat: 0 → -(16384/64) = -256  (y increases downward, lat is negated)
const SW: [number, number] = [-256, 0]
const NE: [number, number] = [0, 384]

// CRS dimensions of the full image
const CRS_W = NE[1] - SW[1] // 220
const CRS_H = NE[0] - SW[0] // 144  (0 − (−144))

// Smallest zoomSnap-aligned zoom at which the image fills the viewport in
// both dimensions, calculated from raw DOM pixel dimensions to avoid any
// stale cached values inside Leaflet.
function coverZoom(container: HTMLElement, snap: number): number {
  const { clientWidth: w, clientHeight: h } = container
  const raw = Math.log2(Math.max(w / CRS_W, h / CRS_H))
  return Math.ceil(raw / snap) * snap
}

export default function MapPage() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<unknown>(null)
  const [zoom, setZoom] = useState<number | null>(null)
  const [cursor, setCursor] = useState<{ crsLat: number; crsLng: number } | null>(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    // Dynamic import keeps Leaflet out of SSR — it accesses `window` on load.
    Promise.all([import("leaflet"), import("leaflet/dist/leaflet.css")]).then(
      ([{ default: L }]) => {
        if (!containerRef.current || mapRef.current) return

        const SNAP = 0.25

        const map = L.map(containerRef.current, {
          crs: L.CRS.Simple,
          maxZoom: 6,
          zoomSnap: SNAP,
          zoomDelta: 0.5,
          attributionControl: false,
          zoomControl: false,
          maxBounds: [SW, NE],
          maxBoundsViscosity: 1.0,
        })

        L.tileLayer(TILE_URL_TEMPLATE, {
          tileSize: 256,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
        }).addTo(map)

        const center = L.latLng((SW[0] + NE[0]) / 2, (SW[1] + NE[1]) / 2)

        const applyMinZoom = () => {
          const cz = coverZoom(containerRef.current!, SNAP)
          map.setMinZoom(cz)
          if (map.getZoom() < cz) map.setZoom(cz)
        }

        applyMinZoom()
        map.setView(center, map.getMinZoom())

        map.on("resize", applyMinZoom)

        setZoom(map.getZoom())
        map.on("zoomend", () => setZoom(map.getZoom()))
        map.on("click", (e) => setCursor({ crsLat: e.latlng.lat, crsLng: e.latlng.lng }))

        mapRef.current = map
      },
    )

    return () => {
      if (mapRef.current) {
        ;(mapRef.current as { remove: () => void }).remove()
        mapRef.current = null
      }
    }
  }, [])

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <style>{`.leaflet-container,.leaflet-dragging .leaflet-container{cursor:default!important}`}</style>
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      {zoom !== null && (
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            zIndex: 1000,
            background: "rgba(0,0,0,0.6)",
            color: "white",
            fontFamily: "monospace",
            fontSize: 14,
            padding: "4px 8px",
            borderRadius: 4,
            userSelect: "text",
          }}
        >
          zoom: {zoom.toFixed(2)}
          {cursor && (
            <>
              <br />
              crs ({cursor.crsLng.toFixed(2)}, {cursor.crsLat.toFixed(2)})
            </>
          )}
        </div>
      )}
    </div>
  )
}
