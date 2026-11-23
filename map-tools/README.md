# Map tools

Scripts for generating map assets from the source Inkscape SVG.

## Prerequisites

1. Install Python 3 and `pip install -r requirements.txt`
2. Install [Docker](https://www.docker.com/) (for tile generation)

## Generate region polygons

Reads `regions.svg` and `regions.json`, polygonizes the enclosed regions, and outputs CRS.Simple coordinates for Leaflet to `frontend/data/region-polygons.gen.json`.

```bash
cd map-tools
python generate_regions.py
```

## Generate tiles

Slices a map PNG into tiles at zoom levels 0-6 and copies them into the frontend for local dev. Replace `<layer>` with `map-base` or `map-overlay`.

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "/path/to/map/directory:/data" \
  ghcr.io/osgeo/gdal:ubuntu-small-latest \
  gdal2tiles --profile raster --xyz --zoom=0-6 --processes=4 \
  /data/<layer>.png /data/<layer>-tiles

cp -r /path/to/map/directory/<layer>-tiles/{0,1,2,3,4,5,6} ../frontend/public/tiles/<layer>/
```

## Deploying tiles

1. Create a GitHub release and attach the image(s) as assets. Filenames must match `map-base-v<number>.png` or `map-overlay-v<number>.png`.
2. Publishing the release triggers the deploy-map-tiles workflow, which generates and uploads tiles to S3.
3. Update the version in `frontend/app/map/tile-config.ts` (e.g. `map-base/v3`) and merge.

## Using local tiles

To use local tiles in dev, set `NEXT_PUBLIC_TILES_CDN=` in `frontend/.env`.
