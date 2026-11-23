import type { FeatureCollection, MultiPolygon } from "geojson"

import regionsData from "./region-polygons.gen.json"

export interface RegionProperties {
  id: string
  name: string
  layer: "fill" | "border"
}

export type RegionFeatureCollection = FeatureCollection<
  MultiPolygon,
  RegionProperties
>

export const REGIONS_FC =
  regionsData as unknown as RegionFeatureCollection

/** Unique region IDs with their display names, derived from the fill features. */
export const REGION_INDEX = REGIONS_FC.features
  .filter((f) => f.properties.layer === "fill")
  .map((f) => ({ id: f.properties.id, name: f.properties.name }))
