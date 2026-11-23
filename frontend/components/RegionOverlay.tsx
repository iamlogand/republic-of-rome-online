import { useEffect, useRef } from "react"
import type L from "leaflet"

type LatLng = [number, number]

interface RegionOverlayProps {
  leaflet: typeof L
  map: L.Map
  polygons: LatLng[][][]
  selected: boolean
  onClick: () => void
}

export default function RegionOverlay({
  leaflet,
  map,
  polygons,
  selected,
  onClick,
}: RegionOverlayProps) {
  const layerRef = useRef<L.Polygon | null>(null)

  useEffect(() => {
    const latLngRings = polygons.map((rings) =>
      rings.map((ring) => ring.map(([lat, lng]) => leaflet.latLng(lat, lng))),
    )

    const baseOpacity = selected ? 0.4 : 0
    const hoverOpacity = selected ? 0.4 : 0.2

    const layer = leaflet.polygon(latLngRings, {
      stroke: false,
      fillColor: "#fff",
      fillOpacity: baseOpacity,
    })

    layer.on("mouseover", () => layer.setStyle({ fillOpacity: hoverOpacity }))
    layer.on("mouseout", () => layer.setStyle({ fillOpacity: baseOpacity }))
    layer.on("click", () => onClick())

    layer.addTo(map)
    layerRef.current = layer

    return () => {
      layer.remove()
    }
  }, [leaflet, map, polygons, selected])

  return null
}
