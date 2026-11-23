import type L from "leaflet"

type CanvasExtend = {
  extend: (o: object) => new (options?: L.RendererOptions) => L.Canvas
}

/**
 * Custom Leaflet Canvas renderer that clips strokes to the polygon interior,
 * producing an inset border effect (doubled stroke width + clip = only the
 * inner half is visible).
 */
export function createInsetBorderCanvas(leaflet: typeof L): L.Canvas {
  const InsetBorderCanvas = (leaflet.Canvas as unknown as CanvasExtend).extend({
    _fillStroke(
      ctx: CanvasRenderingContext2D,
      layer: { options: L.PathOptions },
    ) {
      const { options } = layer
      const fillRule = (options.fillRule || "evenodd") as CanvasFillRule

      if (options.fill) {
        ctx.globalAlpha = options.fillOpacity ?? 0.2
        ctx.fillStyle = (options.fillColor || options.color) as string
        ctx.fill(fillRule)
      }

      if (options.stroke && options.weight !== 0) {
        ctx.save()
        ctx.clip(fillRule)
        ctx.globalAlpha = options.opacity ?? 1
        ctx.lineWidth = (options.weight ?? 3) * 2
        ctx.strokeStyle = options.color as string
        ctx.lineCap = (options.lineCap as CanvasLineCap) || "round"
        ctx.lineJoin = (options.lineJoin as CanvasLineJoin) || "round"
        ctx.stroke()
        ctx.restore()
      }
    },
  })

  return new InsetBorderCanvas()
}
