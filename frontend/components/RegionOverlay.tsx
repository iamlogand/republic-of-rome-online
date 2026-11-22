import { useEffect, useRef } from "react"
import type L from "leaflet"

interface RegionOverlayProps {
  leaflet: typeof L
  map: L.Map
  bounds: L.LatLngBoundsExpression
  svg: string
}

export default function RegionOverlay({ leaflet, map, bounds, svg }: RegionOverlayProps) {
  const overlayRef = useRef<L.SVGOverlay | null>(null)

  useEffect(() => {
    let cancelled = false

    fetch(`/tiles/regions/${svg}`)
      .then((res) => res.text())
      .then((text) => {
        if (cancelled) return

        const doc = new DOMParser().parseFromString(text, "image/svg+xml")
        const svgElement = doc.documentElement as unknown as SVGElement

        // Let mouse events pass through empty areas to the map below.
        svgElement.style.pointerEvents = "none"

        const paths = svgElement.querySelectorAll("path")
        paths.forEach((path) => {
          path.setAttribute("fill-opacity", "0.1")
          path.style.pointerEvents = "auto"
          path.style.cursor = "pointer"
          path.style.transition = "fill-opacity 0.15s ease"

          // Hovering any path in a multi-path region highlights the whole region.
          path.addEventListener("mouseenter", () => {
            paths.forEach((p) => p.setAttribute("fill-opacity", "0.25"))
          })
          path.addEventListener("mouseleave", () => {
            paths.forEach((p) => p.setAttribute("fill-opacity", "0.1"))
          })
        })

        const overlay = leaflet.svgOverlay(svgElement, bounds, {
          interactive: true,
        })
        overlay.addTo(map)
        overlayRef.current = overlay
      })

    return () => {
      cancelled = true
      if (overlayRef.current) {
        overlayRef.current.remove()
      }
    }
  }, [leaflet, map, bounds, svg])

  return null
}
