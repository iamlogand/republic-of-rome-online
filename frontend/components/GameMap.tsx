"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import type { Feature, MultiPolygon } from "geojson"
import type L from "leaflet"

import {
  OVERLAY_MAP_TILE_URL_TEMPLATE,
  MAP_TILE_URL_TEMPLATE,
} from "../app/map/tile-config"
import {
  REGIONS_FC,
  REGION_INDEX,
  type RegionProperties,
} from "../data/regions"
import RegionColorPicker from "./RegionColorPicker"

type RegionFeature = Feature<MultiPolygon, RegionProperties>

// CRS.Simple bounds derived from the source image (24,576 x 16,384 px).
// At maxZoom 6 each tile is 256 px, so the image spans:
//   lng: 0 -> 24576/64 = 384
//   lat: 0 -> -(16384/64) = -256  (y-down -> negative lat)
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

const REGION_CSS = `.leaflet-container, .leaflet-dragging .leaflet-container { cursor: default !important }`

/** Lighten a hex colour by mixing it toward white. Amount is 0–1. */
function lightenColor(hex: string, amount: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const lr = Math.round(r + (255 - r) * amount)
  const lg = Math.round(g + (255 - g) * amount)
  const lb = Math.round(b + (255 - b) * amount)
  return `#${lr.toString(16).padStart(2, "0")}${lg.toString(16).padStart(2, "0")}${lb.toString(16).padStart(2, "0")}`
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
  const [regionColors, setRegionColors] = useState<
    Record<string, string | null>
  >({})

  const fillLayerRef = useRef<L.GeoJSON | null>(null)
  const regionColorsRef = useRef(regionColors)
  regionColorsRef.current = regionColors

  const setRegionColor = useCallback((id: string, color: string | null) => {
    setRegionColors((prev) => ({ ...prev, [id]: color }))
  }, [])

  const setAllRegionColors = useCallback((color: string | null) => {
    setRegionColors(
      Object.fromEntries(REGION_INDEX.map(({ id }) => [id, color])),
    )
  }, [])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    // Dynamic import keeps Leaflet out of SSR.
    Promise.all([import("leaflet"), import("leaflet/dist/leaflet.css")]).then(
      ([{ default: L }]) => {
        if (!containerRef.current || mapRef.current) return

        const SNAP = 0.25

        const leafletMap = L.map(containerRef.current, {
          crs: L.CRS.Simple,
          maxZoom: 6,
          zoomSnap: SNAP,
          zoomDelta: 0.5,
          attributionControl: false,
          zoomControl: false,
          maxBounds: [SW, NE],
          maxBoundsViscosity: 1.0,
        })

        // --- Tile layers -------------------------------------------------

        // Low-res underlay kept permanently in the DOM so panning/zooming
        // never shows empty tiles while the sharp layer loads.
        L.tileLayer(MAP_TILE_URL_TEMPLATE, {
          tileSize: 256,
          minNativeZoom: 2,
          maxNativeZoom: 2,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
          keepBuffer: 1000,
        }).addTo(leafletMap)

        L.tileLayer(MAP_TILE_URL_TEMPLATE, {
          tileSize: 256,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
        }).addTo(leafletMap)

        // --- Region fill layer -------------------------------------------

        const fillFeatures = {
          type: "FeatureCollection" as const,
          features: REGIONS_FC.features.filter(
            (f) => f.properties.layer === "fill",
          ),
        }

        const fillLayer = L.geoJSON(fillFeatures, {
          coordsToLatLng: ([lng, lat]) => L.latLng(lat, lng),
          style: () => ({
            stroke: false,
            fillColor: "#fff",
            fillOpacity: 0,
          }),
          onEachFeature: (feature: RegionFeature, layer) => {
            const regionId = feature.properties.id
            layer.on("mouseover", () => {
              const color = regionColorsRef.current[regionId] ?? null
              ;(layer as L.Path).setStyle(
                color
                  ? { fillColor: lightenColor(color, 0.3), fillOpacity: 0.6 }
                  : { fillOpacity: 0.4 },
              )
            })
            layer.on("mouseout", () => {
              const color = regionColorsRef.current[regionId] ?? null
              ;(layer as L.Path).setStyle({
                fillColor: color ?? "#fff",
                fillOpacity: color ? 0.6 : 0,
              })
            })
            layer.on("click", () => {
              setSelectedRegion((prev) => (prev === regionId ? null : regionId))
            })
          },
        })

        fillLayer.addTo(leafletMap)
        fillLayerRef.current = fillLayer

        // --- Map overlay tiles -------------------------------------------

        const mapOverlayPane = leafletMap.createPane("mapOverlay")
        mapOverlayPane.style.zIndex = "450"

        const TRANSPARENT_PIXEL =
          "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        L.tileLayer(OVERLAY_MAP_TILE_URL_TEMPLATE, {
          tileSize: 256,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
          pane: "mapOverlay",
          errorTileUrl: TRANSPARENT_PIXEL,
        }).addTo(leafletMap)

        // --- Viewport setup ----------------------------------------------

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

  // --- Sync fill colours with state ------------------------------------

  useEffect(() => {
    if (!fillLayerRef.current) return
    fillLayerRef.current.eachLayer((layer) => {
      const feature = (layer as L.GeoJSON & { feature: RegionFeature }).feature
      if (!feature) return
      const color = regionColors[feature.properties.id] ?? null
      ;(layer as L.Path).setStyle({
        fillColor: color ?? "#fff",
        fillOpacity: color ? 0.6 : 0,
      })
    })
  }, [regionColors])

  // --- Helpers for the sidebar -----------------------------------------

  const flyToRegion = useCallback(
    (regionId: string) => {
      if (!leaflet || !map || !fillLayerRef.current) return
      const bounds = leaflet.latLngBounds([])
      fillLayerRef.current.eachLayer((layer) => {
        const feature = (layer as L.GeoJSON & { feature: RegionFeature })
          .feature
        if (feature?.properties.id === regionId) {
          bounds.extend((layer as L.Polygon).getBounds())
        }
      })
      if (bounds.isValid()) map.flyToBounds(bounds, { padding: [40, 40] })
    },
    [leaflet, map],
  )

  const flyToAll = useCallback(() => {
    if (!leaflet || !map || !fillLayerRef.current) return
    const bounds = leaflet.latLngBounds([])
    fillLayerRef.current.eachLayer((layer) => {
      bounds.extend((layer as L.Polygon).getBounds())
    })
    if (bounds.isValid()) map.flyToBounds(bounds, { padding: [40, 40] })
  }, [leaflet, map])

  return (
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      <style>{REGION_CSS}</style>
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
          {leaflet && map && (
            <div
              style={{
                marginTop: 8,
                borderTop: "1px solid rgba(255,255,255,0.3)",
                paddingTop: 6,
              }}
            >
              <div
                style={{
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginBottom: 4,
                }}
              >
                <RegionColorPicker
                  color={
                    REGION_INDEX.length > 0 &&
                    REGION_INDEX.every(
                      ({ id }) =>
                        regionColors[id] === regionColors[REGION_INDEX[0].id],
                    )
                      ? (regionColors[REGION_INDEX[0].id] ?? null)
                      : null
                  }
                  onChange={setAllRegionColors}
                />
                <span
                  onClick={() => {
                    setSelectedRegion(null)
                    flyToAll()
                  }}
                  style={{ flex: 1 }}
                >
                  All regions
                </span>
              </div>
              {REGION_INDEX.map(({ id, name }) => {
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
                        flyToRegion(id)
                      }}
                      style={{ flex: 1 }}
                    >
                      {name}
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
