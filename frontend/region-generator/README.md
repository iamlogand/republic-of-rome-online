# Region generator

Reads `regions.svg` and `regions.json`, polygonizes the enclosed regions, and outputs CRS.Simple coordinates for Leaflet to `data/region-polygons.gen.json`.

```bash
cd frontend
npm run generate:regions
```
