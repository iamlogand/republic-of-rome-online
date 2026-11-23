"use client"

import { useEffect, useRef, useState, useCallback } from "react"

import type L from "leaflet"

import { TILE_URL_TEMPLATE } from "../app/map/tile-config"
import { REGIONS, type Region } from "../data/regions"
import RegionOverlay from "./RegionOverlay"
import RegionColorPicker from "./RegionColorPicker"

function regionBounds(
  leaflet: typeof L,
  region: Region,
): L.LatLngBounds {
  const bounds = leaflet.latLngBounds([])
  for (const rings of region.polygons) {
    for (const ring of rings) {
      for (const [lat, lng] of ring) {
        bounds.extend([lat, lng])
      }
    }
  }
  return bounds
}

// CRS.Simple bounds derived from the source image (24,576 × 16,384 px).
// At maxZoom 6 each tile is 256 px, so the image spans:
//   lng: 0 → 24576/64 = 384
//   lat: 0 → -(16384/64) = -256  (y-down → negative lat)
const SW: [number, number] = [-256, 0]
const NE: [number, number] = [0, 384]

const CRS_W = NE[1] - SW[1]
const CRS_H = NE[0] - SW[0]

// Smallest snap-aligned zoom at which the image fills the viewport.
function coverZoom(container: HTMLElement, snap: number): number {
  const { clientWidth: w, clientHeight: h } = container
  const raw = Math.log2(Math.max(w / CRS_W, h / CRS_H))
  return Math.ceil(raw / snap) * snap
}

export default function GameMap() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const [leaflet, setLeaflet] = useState<typeof L | null>(null)
  const [map, setMap] = useState<L.Map | null>(null)
  const [zoom, setZoom] = useState<number | null>(null)
  const [cursor, setCursor] = useState<{
    crsLat: number
    crsLng: number
  } | null>(null)
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)
  const [regionColors, setRegionColors] = useState<Record<string, string | null>>({})

  const setRegionColor = useCallback((id: string, color: string | null) => {
    setRegionColors((prev) => ({ ...prev, [id]: color }))
  }, [])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    // Dynamic import keeps Leaflet out of SSR.
    Promise.all([import("leaflet"), import("leaflet/dist/leaflet.css")]).then(
      ([{ default: L }]) => {
        if (!containerRef.current || mapRef.current) return

        const SNAP = 0.25

        const renderer = L.svg()

        const leafletMap = L.map(containerRef.current, {
          crs: L.CRS.Simple,
          maxZoom: 6,
          zoomSnap: SNAP,
          zoomDelta: 0.5,
          attributionControl: false,
          zoomControl: false,
          maxBounds: [SW, NE],
          maxBoundsViscosity: 1.0,
          renderer,
        })

        // Low-res underlay kept permanently in the DOM so panning/zooming
        // never shows empty tiles while the sharp layer loads.
        L.tileLayer(TILE_URL_TEMPLATE, {
          tileSize: 256,
          minNativeZoom: 2,
          maxNativeZoom: 2,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
          keepBuffer: 1000,
        }).addTo(leafletMap)

        L.tileLayer(TILE_URL_TEMPLATE, {
          tileSize: 256,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
        }).addTo(leafletMap)

        const center = L.latLng((SW[0] + NE[0]) / 2, (SW[1] + NE[1]) / 2)

        const applyMinZoom = () => {
          const cz = coverZoom(containerRef.current!, SNAP)
          leafletMap.setMinZoom(cz)
          if (leafletMap.getZoom() < cz) leafletMap.setZoom(cz)
        }

        applyMinZoom()
        leafletMap.setView(center, leafletMap.getMinZoom())

        leafletMap.on("resize", applyMinZoom)

        setZoom(leafletMap.getZoom())
        leafletMap.on("zoomend", () => setZoom(leafletMap.getZoom()))
        leafletMap.on("click", (e) =>
          setCursor({ crsLat: e.latlng.lat, crsLng: e.latlng.lng }),
        )

        mapRef.current = leafletMap
        setLeaflet(L)
        setMap(leafletMap)
      },
    )

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [])

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <style>{`.leaflet-container,.leaflet-dragging .leaflet-container{cursor:default!important}`}</style>
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
      {leaflet &&
        map &&
        Object.entries(REGIONS).map(([id, region]) => (
          <RegionOverlay
            key={id}
            leaflet={leaflet}
            map={map}
            polygons={region.polygons}
            selected={selectedRegion === id}
            color={regionColors[id] ?? null}
            onClick={() => setSelectedRegion(selectedRegion === id ? null : id)}
          />
        ))}
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
          {leaflet && map && (
            <div style={{ marginTop: 8, borderTop: "1px solid rgba(255,255,255,0.3)", paddingTop: 6 }}>
              {Object.entries(REGIONS).map(([id, region]) => {
                const isSelected = selectedRegion === id
                return (
                  <div
                    key={id}
                    style={{
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      fontWeight: isSelected ? "bold" : "normal",
                      gap: 6,
                    }}
                  >
                    <RegionColorPicker
                      color={regionColors[id] ?? null}
                      onChange={(color) => setRegionColor(id, color)}
                    />
                    <span
                      onClick={() => {
                        setSelectedRegion(isSelected ? null : id)
                        map.flyToBounds(regionBounds(leaflet, region), { padding: [40, 40] })
                      }}
                      style={{ flex: 1 }}
                    >
                      {region.name}
                    </span>
                    {isSelected && (
                      <span
                        onClick={() => setSelectedRegion(null)}
                        style={{ cursor: "pointer", opacity: 0.7 }}
                      >
                        x
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
