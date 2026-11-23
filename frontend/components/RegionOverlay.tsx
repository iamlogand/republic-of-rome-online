import { useEffect, useRef } from "react"

import type L from "leaflet"

type LatLng = [number, number]

interface RegionOverlayProps {
  leaflet: typeof L
  map: L.Map
  polygons: LatLng[][][]
  selected: boolean
  color: string | null
  onClick: () => void
}

// Weight that looks consistent relative to the map regardless of zoom.
// Each zoom level doubles the scale, so we double the pixel weight to match.
// Weight at max zoom in screen pixels. Each zoom level halves it so the
// border stays a constant size relative to the map.
const WEIGHT_AT_MAX_ZOOM = 32
const MAX_ZOOM = 6

function zoomWeight(zoom: number): number {
  return WEIGHT_AT_MAX_ZOOM * Math.pow(2, zoom - MAX_ZOOM)
}

function getStyle(
  selected: boolean,
  hovered: boolean,
  color: string | null,
  zoom: number,
): L.PathOptions {
  const active = selected || hovered
  return {
    stroke: active,
    color: "#fff",
    weight: active ? zoomWeight(zoom) : 0,
    fillColor: color ?? "#fff",
    fillOpacity: color ? 0.6 : 0,
  }
}

export default function RegionOverlay({
  leaflet,
  map,
  polygons,
  selected,
  color,
  onClick,
}: RegionOverlayProps) {
  const layerRef = useRef<L.Polygon | null>(null)
  const selectedRef = useRef(selected)
  const colorRef = useRef(color)
  selectedRef.current = selected
  colorRef.current = color

  // Create the layer once when polygons change.
  useEffect(() => {
    const latLngRings = polygons.map((rings) =>
      rings.map((ring) => ring.map(([lat, lng]) => leaflet.latLng(lat, lng))),
    )

    const zoom = map.getZoom()

    const layer = leaflet.polygon(
      latLngRings,
      getStyle(selectedRef.current, false, colorRef.current, zoom),
    )

    layer.on("mouseover", () =>
      layer.setStyle(
        getStyle(selectedRef.current, true, colorRef.current, map.getZoom()),
      ),
    )
    layer.on("mouseout", () =>
      layer.setStyle(
        getStyle(selectedRef.current, false, colorRef.current, map.getZoom()),
      ),
    )
    layer.on("click", onClick)

    const onZoom = () =>
      layer.setStyle(
        getStyle(selectedRef.current, false, colorRef.current, map.getZoom()),
      )
    map.on("zoomend", onZoom)

    layer.addTo(map)
    layerRef.current = layer

    return () => {
      map.off("zoomend", onZoom)
      layer.remove()
    }
  }, [leaflet, map, polygons])

  // Update style when selection or color changes without recreating the layer.
  useEffect(() => {
    if (layerRef.current) {
      layerRef.current.setStyle(getStyle(selected, false, color, map.getZoom()))
    }
  }, [selected, color, map])

  return null
}
