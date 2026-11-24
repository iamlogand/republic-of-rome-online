"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import type { Feature, MultiPolygon } from "geojson"
import type L from "leaflet"

import {
  MAP_TILE_URL_TEMPLATE,
  OVERLAY_MAP_TILE_URL_TEMPLATE,
} from "../app/map/tile-config"
import { HOVER_COLORS } from "../data/colors"
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

export default function GameMap() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const [leaflet, setLeaflet] = useState<typeof L | null>(null)
  const [map, setMap] = useState<L.Map | null>(null)
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)
  const [regionColors, setRegionColors] = useState<
    Record<string, string | null>
  >({})
  const [colorIntensity, setColorIntensity] = useState<
    "low" | "medium" | "high"
  >("medium")
  const [settingsOpen, setSettingsOpen] = useState(false)
  const settingsRef = useRef<HTMLDivElement>(null)

  const INTENSITY_OPACITY = { low: 0.6, medium: 0.8, high: 1 } as const
  const fillOpacity = INTENSITY_OPACITY[colorIntensity]

  const fillLayerRef = useRef<L.GeoJSON | null>(null)
  const regionColorsRef = useRef(regionColors)
  regionColorsRef.current = regionColors
  const fillOpacityRef = useRef(fillOpacity)
  fillOpacityRef.current = fillOpacity
  const selectedRegionRef = useRef(selectedRegion)
  selectedRegionRef.current = selectedRegion

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
          doubleClickZoom: false,
          maxBounds: [SW, NE],
          maxBoundsViscosity: 1.0,
        })

        // Tile layers

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

        // Region fill layer

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
                  ? {
                      fillColor: HOVER_COLORS.get(color) ?? color,
                      fillOpacity: fillOpacityRef.current,
                    }
                  : { fillColor: "#fff", fillOpacity: 0.4 },
              )
            })
            layer.on("mouseout", () => {
              const color = regionColorsRef.current[regionId] ?? null
              const isSelected = selectedRegionRef.current === regionId
              ;(layer as L.Path).setStyle(
                color
                  ? {
                      fillColor: isSelected
                        ? (HOVER_COLORS.get(color) ?? color)
                        : color,
                      fillOpacity: fillOpacityRef.current,
                    }
                  : { fillColor: "#fff", fillOpacity: isSelected ? 0.4 : 0 },
              )
            })
            layer.on("click", () => {
              setSelectedRegion((prev) => (prev === regionId ? null : regionId))
            })
          },
        })

        fillLayer.addTo(leafletMap)
        fillLayerRef.current = fillLayer

        // Map overlay tiles

        const mapOverlayPane = leafletMap.createPane("mapOverlay")
        mapOverlayPane.style.zIndex = "450"

        L.tileLayer(OVERLAY_MAP_TILE_URL_TEMPLATE, {
          tileSize: 256,
          minZoom: 0,
          maxZoom: 6,
          noWrap: true,
          bounds: [SW, NE],
          pane: "mapOverlay",
        }).addTo(leafletMap)

        // Viewport setup

        const center = L.latLng((SW[0] + NE[0]) / 2, (SW[1] + NE[1]) / 2)

        const applyMinZoom = () => {
          const cz = coverZoom(containerRef.current!, SNAP)
          leafletMap.setMinZoom(cz)
          if (leafletMap.getZoom() < cz) leafletMap.setZoom(cz)
        }

        applyMinZoom()
        leafletMap.setView(center, leafletMap.getMinZoom())

        leafletMap.on("resize", applyMinZoom)

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

  // Sync fill colors with state

  useEffect(() => {
    if (!fillLayerRef.current) return
    fillLayerRef.current.eachLayer((layer) => {
      const feature = (layer as L.GeoJSON & { feature: RegionFeature }).feature
      if (!feature) return
      const color = regionColors[feature.properties.id] ?? null
      const isSelected = selectedRegion === feature.properties.id
      ;(layer as L.Path).setStyle(
        color
          ? {
              fillColor: isSelected
                ? (HOVER_COLORS.get(color) ?? color)
                : color,
              fillOpacity: fillOpacity,
            }
          : { fillColor: "#fff", fillOpacity: isSelected ? 0.4 : 0 },
      )
    })
  }, [regionColors, fillOpacity, selectedRegion])

  // Close settings on outside click

  useEffect(() => {
    if (!settingsOpen) return
    const handleClick = (e: MouseEvent) => {
      if (
        settingsRef.current &&
        !settingsRef.current.contains(e.target as Node)
      ) {
        setSettingsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [settingsOpen])

  // Helpers for the sidebar

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
    <div className="relative h-screen w-screen">
      <style>{REGION_CSS}</style>
      <div ref={containerRef} className="h-full w-full" />
      {leaflet && map && (
        <div className="absolute left-3 top-3 z-[1000] select-text bg-black/60 px-2 py-1 font-mono text-sm text-white">
          <div className="mb-1 flex cursor-pointer items-center gap-1.5">
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
              onClick={() => flyToAll()}
              className="cursor-pointer no-underline opacity-70"
              title="Fly to all regions"
            >
              🎯
            </span>
            <span onClick={() => setSelectedRegion(null)} className="flex-1">
              All regions
            </span>
          </div>
          <div className="my-1 border-t border-white/30" />
          {REGION_INDEX.map(({ id, name }) => {
            const isSelected = selectedRegion === id
            return (
              <div
                key={id}
                className={`flex cursor-pointer items-center gap-1.5 ${isSelected ? "font-bold" : "font-normal"}`}
              >
                <RegionColorPicker
                  color={regionColors[id] ?? null}
                  onChange={(color) => setRegionColor(id, color)}
                />
                <span
                  onClick={() => flyToRegion(id)}
                  className="cursor-pointer no-underline opacity-70"
                  title={`Fly to ${name}`}
                >
                  🎯
                </span>
                <span
                  onClick={() => setSelectedRegion(isSelected ? null : id)}
                  className={`flex-1 ${isSelected ? "underline" : "no-underline"}`}
                >
                  {name}
                </span>
              </div>
            )
          })}
        </div>
      )}

      {/* Settings */}
      <div ref={settingsRef} className="absolute right-3 top-3 z-[1000]">
        <button
          onClick={() => setSettingsOpen(!settingsOpen)}
          className="cursor-pointer border-none bg-black/60 px-2 py-1 font-mono text-sm text-white"
        >
          Settings
        </button>
        {settingsOpen && (
          <div className="absolute right-0 top-full mt-1 whitespace-nowrap bg-black/80 px-2 py-1 font-mono text-sm text-white">
            <div className="mb-1.5">Color intensity</div>
            {(["low", "medium", "high"] as const).map((level) => (
              <div
                key={level}
                onClick={() => setColorIntensity(level)}
                className={`cursor-pointer capitalize ${colorIntensity === level ? "font-bold underline" : "font-normal no-underline"}`}
              >
                {level}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
