import { XMLParser } from "fast-xml-parser"
import { mkdirSync, readFileSync, writeFileSync } from "fs"
import Coordinate from "jsts/org/locationtech/jts/geom/Coordinate.js"
import GeometryFactory from "jsts/org/locationtech/jts/geom/GeometryFactory.js"
import OverlayOp from "jsts/org/locationtech/jts/operation/overlay/OverlayOp.js"
import Polygonizer from "jsts/org/locationtech/jts/operation/polygonize/Polygonizer.js"
import UnaryUnionOp from "jsts/org/locationtech/jts/operation/union/UnaryUnionOp.js"
import { dirname, join } from "path"
import svgPathParser from "svg-path-parser"
import { fileURLToPath } from "url"

const { parseSVG, makeAbsolute } = svgPathParser

const __dirname = dirname(fileURLToPath(import.meta.url))

// maxZoom 6, 256px tiles -> 2^6 = 64 pixels per CRS unit.
const PX_TO_CRS = 64.0

const factory = new GeometryFactory()

function parseSvgFile(svgPath) {
  const xml = readFileSync(svgPath, "utf-8")
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: "",
    ignoreDeclaration: true,
    isArray: (name) => name === "path",
  })
  const doc = parser.parse(xml)
  const svg = doc.svg

  const docWidth = parseFloat(String(svg.width).replace("px", ""))
  const docHeight = parseFloat(String(svg.height).replace("px", ""))

  const viewBox = svg.viewBox
  if (viewBox) {
    const parts = viewBox.split(/\s+/)
    const vbWidth = parseFloat(parts[2])
    const vbHeight = parseFloat(parts[3])
    if (
      Math.abs(vbWidth - docWidth) > 1 ||
      Math.abs(vbHeight - docHeight) > 1
    ) {
      console.warn(
        `WARNING: width/height (${docWidth}x${docHeight}) != viewBox (${vbWidth}x${vbHeight}). ` +
          `Coordinate frame may be broken.`,
      )
    }
  }

  const paths = new Map()
  const pathElements = svg.path ?? []
  for (const elem of pathElements) {
    const label = elem["inkscape:label"] ?? ""
    const d = elem.d ?? ""
    if (label && d) {
      paths.set(label, d)
    }
  }

  return { docWidth, docHeight, paths }
}

function pathToPolylines(dString) {
  const commands = makeAbsolute(parseSVG(dString))
  const polylines = []
  let current = []

  for (const cmd of commands) {
    const code = cmd.code.toUpperCase()

    if (code === "M") {
      if (current.length) polylines.push(current)
      current = [[cmd.x, cmd.y]]
    } else if (code === "Z") {
      if (current.length > 1) current.push(current[0])
      if (current.length) polylines.push(current)
      current = []
    } else if (code === "L" || code === "H" || code === "V") {
      current.push([cmd.x, cmd.y])
    } else {
      throw new Error(
        `Unsupported SVG segment type: ${cmd.command} (${cmd.code}). ` +
          `Only line segments are supported.`,
      )
    }
  }

  if (current.length) polylines.push(current)
  return polylines
}

function roundCoordinates(polylines, precision = 1) {
  const factor = 10 ** precision
  for (const line of polylines) {
    for (let i = 0; i < line.length; i++) {
      line[i] = [
        Math.round(line[i][0] * factor) / factor,
        Math.round(line[i][1] * factor) / factor,
      ]
    }
  }
}

function toLineString(points) {
  const coords = points.map(([x, y]) => new Coordinate(x, y))
  return factory.createLineString(coords)
}

function buildPolygons(allPolylines) {
  const lines = allPolylines.filter((pts) => pts.length >= 2).map(toLineString)

  if (!lines.length) return { polygons: [], dangles: [] }

  const collection = factory.createGeometryCollection(lines)
  const merged = UnaryUnionOp.union(collection)

  const polygonizer = new Polygonizer()
  polygonizer.add(merged)

  const polyCollection = polygonizer.getPolygons()
  const polygons = []
  for (let i = 0; i < polyCollection.size(); i++) {
    const geom = polyCollection.get(i)
    if (!geom.isEmpty()) polygons.push(geom)
  }

  const danglesCollection = polygonizer.getDangles()
  const danglesCount = danglesCollection?.size?.() ?? 0
  if (danglesCount > 0) {
    console.log(
      `  (${danglesCount} dangling edge(s) dropped — likely overshoots into the sea)`,
    )
  }

  return { polygons, dangles: danglesCollection }
}

// Assign each polygon to the province whose border paths share the most
// boundary overlap (>50% required).
function assignPolygonsToProvinces(polygons, provinceConfig, polylinesByLabel) {
  const provinceLines = new Map()
  for (const [provinceId, info] of Object.entries(provinceConfig)) {
    const lines = []
    for (const label of info.borders) {
      const polylines = polylinesByLabel.get(label)
      if (polylines) {
        for (const pts of polylines) {
          if (pts.length >= 2) lines.push(toLineString(pts))
        }
      }
    }
    if (lines.length) {
      const collection = factory.createGeometryCollection(lines)
      provinceLines.set(provinceId, UnaryUnionOp.union(collection))
    }
  }

  const assignments = new Map()
  const unassigned = []

  for (const polygon of polygons) {
    let bestProvince = null
    let bestOverlap = 0

    const boundary = polygon.getBoundary()
    const boundaryLength = boundary.getLength()

    for (const [provinceId, provinceGeometry] of provinceLines) {
      const intersection = OverlayOp.overlayOp(
        boundary,
        provinceGeometry,
        OverlayOp.INTERSECTION,
      )
      const overlap = intersection.getLength()
      const fraction = boundaryLength > 0 ? overlap / boundaryLength : 0
      if (fraction > bestOverlap) {
        bestOverlap = fraction
        bestProvince = provinceId
      }
    }

    if (bestProvince && bestOverlap > 0.5) {
      if (!assignments.has(bestProvince)) assignments.set(bestProvince, [])
      assignments.get(bestProvince).push(polygon)
    } else {
      unassigned.push({ polygon, bestProvince, bestOverlap })
    }
  }

  return { assignments, unassigned }
}

function polygonToGeoJsonCoords(polygon) {
  function ringToCrs(ring) {
    const coords = ring.getCoordinates()
    return coords.map((c) => [
      Math.round((c.x / PX_TO_CRS) * 100) / 100,
      Math.round((-c.y / PX_TO_CRS) * 100) / 100,
    ])
  }

  const rings = [ringToCrs(polygon.getExteriorRing())]
  for (let i = 0; i < polygon.getNumInteriorRing(); i++) {
    rings.push(ringToCrs(polygon.getInteriorRingN(i)))
  }
  return rings
}

function main() {
  const svgPath = join(__dirname, "regions.svg")
  const configPath = join(__dirname, "regions.json")
  const outputPath = join(__dirname, "..", "data", "region-polygons.gen.json")

  const config = JSON.parse(readFileSync(configPath, "utf-8"))
  const provinceConfig = config.provinces

  const { docWidth, docHeight, paths } = parseSvgFile(svgPath)
  console.log(`Document size: ${docWidth} x ${docHeight}`)
  console.log(`Found ${paths.size} labelled paths:`)
  for (const label of paths.keys()) {
    console.log(`  - ${label}`)
  }

  const allNeeded = new Set()
  for (const province of Object.values(provinceConfig)) {
    for (const border of province.borders) {
      allNeeded.add(border)
    }
  }
  const missing = [...allNeeded].filter((label) => !paths.has(label))
  if (missing.length) {
    console.warn("WARNING: config references labels not found in SVG:")
    for (const m of missing.sort()) {
      console.warn(`  - ${m}`)
    }
  }

  const polylinesByLabel = new Map()
  const allPolylines = []
  for (const [label, d] of paths) {
    const polylines = pathToPolylines(d)
    polylinesByLabel.set(label, polylines)
    allPolylines.push(...polylines)
    const totalPoints = polylines.reduce((sum, p) => sum + p.length, 0)
    console.log(
      `  ${label}: ${polylines.length} sub-path(s), ${totalPoints} points`,
    )
  }

  for (const polylines of [allPolylines, ...polylinesByLabel.values()]) {
    roundCoordinates(polylines)
  }

  console.log("\nBuilding polygons...")
  const { polygons } = buildPolygons(allPolylines)
  console.log(`Found ${polygons.length} polygon(s)`)

  for (let i = 0; i < polygons.length; i++) {
    const env = polygons[i].getEnvelopeInternal()
    const area = polygons[i].getArea()
    console.log(
      `  [${i}] area=${Math.round(area)} px²  ` +
        `bounds=(${Math.round(env.getMinX())}, ${Math.round(env.getMinY())})-` +
        `(${Math.round(env.getMaxX())}, ${Math.round(env.getMaxY())})`,
    )
  }

  const { assignments, unassigned } = assignPolygonsToProvinces(
    polygons,
    provinceConfig,
    polylinesByLabel,
  )

  console.log("\nProvince assignments:")
  for (const [provinceId, polys] of [...assignments.entries()].sort()) {
    const name = provinceConfig[provinceId].name
    const totalArea = polys.reduce((sum, p) => sum + p.getArea(), 0)
    console.log(
      `  ${name} (${provinceId}): ${polys.length} polygon(s), total area=${Math.round(totalArea)} px²`,
    )
  }

  if (unassigned.length) {
    console.log(`\nUnassigned polygons (${unassigned.length}):`)
    for (const { polygon, bestProvince, bestOverlap } of unassigned) {
      const env = polygon.getEnvelopeInternal()
      const area = polygon.getArea()
      const note =
        area < 1000 ? " (likely a sliver from overshooting lines)" : ""
      console.log(
        `  area=${Math.round(area)} px²  ` +
          `bounds=(${Math.round(env.getMinX())}, ${Math.round(env.getMinY())})-` +
          `(${Math.round(env.getMaxX())}, ${Math.round(env.getMaxY())})  ` +
          `best_match=${bestProvince} (${Math.round(bestOverlap * 100)}%)${note}`,
      )
    }
  }

  const features = []
  for (const [provinceId, polys] of [...assignments.entries()].sort()) {
    const name = provinceConfig[provinceId].name
    features.push({
      type: "Feature",
      properties: { id: provinceId, name, layer: "fill" },
      geometry: {
        type: "MultiPolygon",
        coordinates: polys.map(polygonToGeoJsonCoords),
      },
    })
  }

  const output = { type: "FeatureCollection", features }

  mkdirSync(dirname(outputPath), { recursive: true })
  writeFileSync(outputPath, JSON.stringify(output))

  console.log(`\nWrote ${outputPath}`)
  console.log("Done.")
}

main()
