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

function getStyle(
  selected: boolean,
  hovered: boolean,
  color: string | null,
): L.PathOptions {
  const active = selected || hovered
  return {
    stroke: active,
    color: "#fff",
    weight: active ? 4 : 0,
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

    const layer = leaflet.polygon(
      latLngRings,
      getStyle(selectedRef.current, false, colorRef.current),
    )

    layer.on("mouseover", () =>
      layer.setStyle(getStyle(selectedRef.current, true, colorRef.current)),
    )
    layer.on("mouseout", () =>
      layer.setStyle(getStyle(selectedRef.current, false, colorRef.current)),
    )
    layer.on("click", onClick)

    layer.addTo(map)
    layerRef.current = layer

    return () => {
      layer.remove()
    }
  }, [leaflet, map, polygons])

  // Update style when selection or color changes without recreating the layer.
  useEffect(() => {
    if (layerRef.current) {
      layerRef.current.setStyle(getStyle(selected, false, color))
    }
  }, [selected, color])

  return null
}
