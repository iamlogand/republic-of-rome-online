"""
Build region polygon data from the master map SVG.

Reads regions.svg and regions.json, then:
1. Extracts SVG paths by their inkscape:label
2. Polygonizes enclosed regions
3. Assigns polygons to regions based on which border paths enclose them
4. Outputs a single JSON file with CRS.Simple coordinates for Leaflet

Usage:
    python build_provinces.py
"""

import json
import sys
import xml.etree.ElementTree as ET
import pathlib

from shapely.geometry import LineString, Polygon  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]
from svgelements import Close, Line, Move, Path as SVGPath  # type: ignore[import-untyped]

NS = {
    "svg": "http://www.w3.org/2000/svg",
    "inkscape": "http://www.inkscape.org/namespaces/inkscape",
}

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

# Pixel-to-CRS conversion factors for Leaflet CRS.Simple.
# The source image is 24,576 × 16,384 px.  At maxZoom 6 each tile is 256 px:
#   lng = px_x / 64        (0 → 384)
#   lat = -(px_y / 64)     (0 → -256, y-down becomes negative lat)
PX_TO_CRS = 64.0


def get_doc_size(root):
    """Get document width/height and check viewBox matches 1:1."""
    w = float(root.get("width", "0").replace("px", ""))
    h = float(root.get("height", "0").replace("px", ""))
    vb = root.get("viewBox", "")
    if vb:
        parts = vb.split()
        vb_w, vb_h = float(parts[2]), float(parts[3])
        if abs(vb_w - w) > 1 or abs(vb_h - h) > 1:
            print(
                f"WARNING: width/height ({w}x{h}) != viewBox ({vb_w}x{vb_h}). "
                f"Coordinate frame may be broken.",
                file=sys.stderr,
            )
    return w, h


def collect_paths(root):
    """Return dict of inkscape:label -> SVG 'd' attribute for all paths."""
    label_attr = f"{{{NS['inkscape']}}}label"
    paths = {}
    for elem in root.iter(f"{{{NS['svg']}}}path"):
        label = elem.get(label_attr, "")
        d = elem.get("d", "")
        if label and d:
            paths[label] = d
    return paths


def parse_path(d_string):
    """Convert an SVG path 'd' string to a list of polylines (lists of (x,y) tuples).

    Only supports lines (L/l/H/h/V/v) and moves (M/m). Each Move starts a new polyline.
    """
    path = SVGPath(d_string)
    polylines = []
    current = []

    for segment in path.segments():
        if isinstance(segment, Move):
            if current:
                polylines.append(current)
            current = [(segment.end.real, segment.end.imag)]
        elif isinstance(segment, Close):
            if current and len(current) > 1:
                current.append(current[0])
            if current:
                polylines.append(current)
            current = []
        elif isinstance(segment, Line):
            current.append((segment.end.real, segment.end.imag))
        else:
            raise ValueError(
                f"Unsupported SVG segment type: {type(segment).__name__}. "
                f"Only line segments are supported."
            )

    if current:
        polylines.append(current)
    return polylines


def round_coordinates(lines, precision=1):
    """Round all coordinates to eliminate floating-point accumulation drift."""
    for line in lines:
        for i in range(len(line)):
            x, y = line[i]
            line[i] = (round(x, precision), round(y, precision))


def build_polygons(all_polylines):
    """From a set of polylines, build enclosed polygons via shapely."""
    shapely_lines = []
    for pts in all_polylines:
        if len(pts) >= 2:
            shapely_lines.append(LineString(pts))

    if not shapely_lines:
        return []

    merged = unary_union(shapely_lines)
    polys, dangles, cuts, invalids = polygonize_full(merged)

    result = []
    for geom in polys.geoms if hasattr(polys, "geoms") else [polys]:
        if isinstance(geom, Polygon) and not geom.is_empty:
            result.append(geom)

    if dangles and not dangles.is_empty:
        n = len(dangles.geoms) if hasattr(dangles, "geoms") else 1
        print(f"  ({n} dangling edge(s) dropped — likely overshoots into the sea)")

    return result


def polygonize_full(geometry):
    """Wrapper around shapely polygonize_full."""
    from shapely.ops import polygonize_full as _polygonize_full

    return _polygonize_full(geometry)


def assign_polygons_to_provinces(polygons, province_borders, all_polylines_by_label):
    """Assign each polygon to the province whose border paths enclose it.

    Strategy: for each province, union its border lines into a geometry.
    A polygon belongs to a province if the polygon's boundary substantially
    overlaps (shares edges with) that province's border lines.
    """
    province_lines = {}
    for prov_id, info in province_borders.items():
        lines = []
        for label in info["borders"]:
            if label in all_polylines_by_label:
                for pts in all_polylines_by_label[label]:
                    if len(pts) >= 2:
                        lines.append(LineString(pts))
        if lines:
            province_lines[prov_id] = unary_union(lines)

    assignments = {}
    unassigned = []

    for poly in polygons:
        best_prov = None
        best_overlap = 0

        boundary = poly.boundary
        for prov_id, prov_geom in province_lines.items():
            overlap = boundary.intersection(prov_geom).length
            frac = overlap / boundary.length if boundary.length > 0 else 0
            if frac > best_overlap:
                best_overlap = frac
                best_prov = prov_id

        # Require that at least 50% of the polygon's boundary comes from
        # this province's borders for it to be a match
        if best_prov and best_overlap > 0.5:
            assignments.setdefault(best_prov, []).append(poly)
        else:
            unassigned.append((poly, best_prov, best_overlap))

    return assignments, unassigned


def polygon_to_geojson_coords(polygon):
    """Convert a shapely Polygon to GeoJSON-style coordinate rings in CRS.Simple.

    GeoJSON uses [lng, lat] order.  Returns [exterior, hole1, hole2, ...].
    """
    def ring_to_crs(ring):
        return [
            [round(x / PX_TO_CRS, 2), round(-y / PX_TO_CRS, 2)]
            for x, y in ring.coords
        ]

    rings = [ring_to_crs(polygon.exterior)]
    for interior in polygon.interiors:
        rings.append(ring_to_crs(interior))
    return rings




def main():
    svg_path = SCRIPT_DIR / "regions.svg"
    config_path = SCRIPT_DIR / "regions.json"
    repo_root = SCRIPT_DIR.parent
    output_path = repo_root / "frontend" / "data" / "region-polygons.gen.json"

    # Load config
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    province_config = config["provinces"]

    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()
    doc_w, doc_h = get_doc_size(root)
    print(f"Document size: {doc_w} x {doc_h}")

    # Collect all labelled paths
    label_to_d = collect_paths(root)
    print(f"Found {len(label_to_d)} labelled paths:")
    for label in label_to_d:
        print(f"  - {label}")

    # Check config references exist
    all_needed = set()
    for prov in province_config.values():
        for b in prov["borders"]:
            all_needed.add(b)
    missing = all_needed - set(label_to_d.keys())
    if missing:
        print(f"\nWARNING: config references labels not found in SVG:", file=sys.stderr)
        for m in sorted(missing):
            print(f"  - {m}", file=sys.stderr)

    # Linearize all paths
    all_polylines_by_label = {}
    all_polylines = []
    for label, d in label_to_d.items():
        polylines = parse_path(d)
        all_polylines_by_label[label] = polylines
        all_polylines.extend(polylines)
        total_pts = sum(len(p) for p in polylines)
        print(f"  {label}: {len(polylines)} sub-path(s), {total_pts} points")

    # Round coordinates to eliminate floating-point accumulation drift
    for polylines in [all_polylines] + list(all_polylines_by_label.values()):
        round_coordinates(polylines)

    # Build polygons
    print(f"\nBuilding polygons...")
    polygons = build_polygons(all_polylines)
    print(f"Found {len(polygons)} polygon(s)")

    for i, poly in enumerate(polygons):
        bx = poly.bounds
        area = poly.area
        print(
            f"  [{i}] area={area:.0f} px²  bounds=({bx[0]:.0f}, {bx[1]:.0f})-({bx[2]:.0f}, {bx[3]:.0f})"
        )

    # Assign polygons to provinces
    assignments, unassigned = assign_polygons_to_provinces(
        polygons, province_config, all_polylines_by_label
    )

    print(f"\nProvince assignments:")
    for prov_id, polys in sorted(assignments.items()):
        name = province_config[prov_id]["name"]
        total_area = sum(p.area for p in polys)
        print(
            f"  {name} ({prov_id}): {len(polys)} polygon(s), total area={total_area:.0f} px²"
        )

    if unassigned:
        print(f"\nUnassigned polygons ({len(unassigned)}):")
        for poly, best, overlap in unassigned:
            bx = poly.bounds
            area = poly.area
            note = ""
            if area < 1000:
                note = " (likely a sliver from overshooting lines)"
            print(
                f"  area={area:.0f} px²  bounds=({bx[0]:.0f}, {bx[1]:.0f})-"
                f"({bx[2]:.0f}, {bx[3]:.0f})  best_match={best} ({overlap:.0%}){note}"
            )

    # Build GeoJSON FeatureCollection.
    features = []
    for prov_id, polys in sorted(assignments.items()):
        name = province_config[prov_id]["name"]
        features.append({
            "type": "Feature",
            "properties": {"id": prov_id, "name": name, "layer": "fill"},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [polygon_to_geojson_coords(p) for p in polys],
            },
        })

    output = {
        "type": "FeatureCollection",
        "features": features,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f)

    print(f"\nWrote {output_path}")
    print("Done.")


if __name__ == "__main__":
    main()
