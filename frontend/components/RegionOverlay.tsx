import { useEffect, useRef } from "react"
import type L from "leaflet"

type LatLng = [number, number]

interface RegionOverlayProps {
  leaflet: typeof L
  map: L.Map
  polygons: LatLng[][][]
  onHover: (hovered: boolean) => void
}

export default function RegionOverlay({ leaflet, map, polygons, onHover }: RegionOverlayProps) {
  const layerRef = useRef<L.Polygon | null>(null)

  useEffect(() => {
    const latLngRings = polygons.map((rings) =>
      rings.map((ring) => ring.map(([lat, lng]) => leaflet.latLng(lat, lng))),
    )

    const layer = leaflet.polygon(latLngRings, {
      stroke: false,
      fillColor: "#fff",
      fillOpacity: 0,
    })

    layer.on("mouseover", () => {
      layer.setStyle({ fillOpacity: 0.4 })
      onHover(true)
    })
    layer.on("mouseout", () => {
      layer.setStyle({ fillOpacity: 0 })
      onHover(false)
    })

    layer.addTo(map)
    layerRef.current = layer

    return () => {
      layer.remove()
    }
  }, [leaflet, map, polygons])

  return null
}
