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

## Generate map tiles

Slices the source map PNG into tiles at zoom levels 0-6 and copies them into the frontend.

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "/path/to/map/directory:/data" \
  ghcr.io/osgeo/gdal:ubuntu-small-latest \
  gdal2tiles --profile raster --xyz --zoom=0-6 --processes=4 \
  /data/map.png /data/tiles

cp -r /path/to/map/directory/tiles/{0,1,2,3,4,5,6} ../frontend/public/tiles/
```

To use local tiles in dev, set `NEXT_PUBLIC_TILES_CDN=` in `frontend/.env`.
