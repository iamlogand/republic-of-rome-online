import regionsData from "./region-polygons.gen.json"

type LatLng = [number, number]

export interface Region {
  name: string
  polygons: LatLng[][][] // polygon[] → ring[] → [lat, lng]
  inset_polygons: (LatLng[][] | null)[] // per-polygon rings, shrunk inward; null for small islands
}

export const REGIONS = regionsData as unknown as Record<string, Region>
