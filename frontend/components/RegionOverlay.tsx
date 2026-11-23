import { useEffect, useRef } from "react"

import type L from "leaflet"

type LatLng = [number, number]

interface RegionOverlayProps {
  leaflet: typeof L
  map: L.Map
  polygons: LatLng[][][]
  insetPolygons: (LatLng[][] | null)[]
  selected: boolean
  color: string | null
  zoom: number
  onClick: () => void
}

// Weight at max zoom in screen pixels. Each zoom level halves it so the
// border stays a constant size relative to the map.
const WEIGHT_AT_MAX_ZOOM = 32
const MAX_ZOOM = 6

function zoomWeight(zoom: number): number {
  return WEIGHT_AT_MAX_ZOOM * Math.pow(2, zoom - MAX_ZOOM)
}

function getFillStyle(color: string | null): L.PathOptions {
  return {
    stroke: false,
    fillColor: color ?? "#fff",
    fillOpacity: color ? 0.6 : 0,
  }
}

function getBorderStyle(
  selected: boolean,
  hovered: boolean,
  zoom: number,
): L.PathOptions {
  const active = selected || hovered
  return {
    stroke: active,
    color: "#fff",
    weight: active ? zoomWeight(zoom) : 0,
    fill: false,
  }
}

function toLatLngRings(
  leaflet: typeof L,
  polygons: LatLng[][][],
): L.LatLng[][][] {
  return polygons.map((rings) =>
    rings.map((ring) => ring.map(([lat, lng]) => leaflet.latLng(lat, lng))),
  )
}

export default function RegionOverlay({
  leaflet,
  map,
  polygons,
  insetPolygons,
  selected,
  color,
  zoom,
  onClick,
}: RegionOverlayProps) {
  const fillRef = useRef<L.Polygon | null>(null)
  const borderRef = useRef<L.Polygon | null>(null)
  const selectedRef = useRef(selected)
  const colorRef = useRef(color)
  const zoomRef = useRef(zoom)
  selectedRef.current = selected
  colorRef.current = color
  zoomRef.current = zoom

  // Fill layer — uses original polygons for accurate hit-testing.
  useEffect(() => {
    const layer = leaflet.polygon(
      toLatLngRings(leaflet, polygons),
      getFillStyle(colorRef.current),
    )

    layer.on("mouseover", () => {
      if (borderRef.current) {
        borderRef.current.setStyle(
          getBorderStyle(selectedRef.current, true, zoomRef.current),
        )
      }
    })
    layer.on("mouseout", () => {
      if (borderRef.current) {
        borderRef.current.setStyle(
          getBorderStyle(selectedRef.current, false, zoomRef.current),
        )
      }
    })
    layer.on("click", onClick)

    layer.addTo(map)
    fillRef.current = layer

    return () => {
      layer.remove()
    }
  }, [leaflet, map, polygons])

  // Border layer — uses inset polygons so the stroke sits inside the fill.
  // Null entries (small islands) are skipped.
  useEffect(() => {
    const allRings = insetPolygons.filter(
      (p): p is LatLng[][] => p !== null,
    )

    const rings = toLatLngRings(leaflet, allRings)

    if (rings.length === 0) return

    const layer = leaflet.polygon(rings, {
      ...getBorderStyle(selectedRef.current, false, zoomRef.current),
      interactive: false,
    })

    layer.addTo(map)
    borderRef.current = layer

    return () => {
      layer.remove()
    }
  }, [leaflet, map, insetPolygons])

  // Update styles when selection, color, or zoom changes.
  useEffect(() => {
    if (fillRef.current) {
      fillRef.current.setStyle(getFillStyle(color))
    }
    if (borderRef.current) {
      borderRef.current.setStyle(getBorderStyle(selected, false, zoom))
    }
  }, [selected, color, zoom])

  return null
}
