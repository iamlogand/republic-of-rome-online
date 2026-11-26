# Infrastructure

Republic of Rome Online is hosted on AWS. The domain roronline.com is registered through AWS Route 53.

## Frontend

The frontend is a Next.js React application in the `frontend` folder. It is continuously deployed to AWS Amplify whenever changes are made to the `frontend` folder in the `main` branch. The specific infrastructure used by the frontend server is heavily abstracted by Amplify, but it runs on a Node.js server.

## Backend

The backend is a Django application in the `backend` folder. It is deployed to AWS Elastic Beanstalk via GitHub Actions whenever changes are made to the `backend` folder in the `main` branch.

The backend runs in Docker containers with the following components:

- **NGINX** — terminates SSL/TLS connections and forwards requests to Django/Daphne
- **Daphne** — manages HTTP and WebSocket connections using the ASGI protocol
- **Django** — powers the REST API and application logic
- **Channels** — Django extension that enables asynchronous functionality for WebSocket support
- **Redis** — runs in a separate container and acts as a message broker to allow communication between the coroutines that manage open WebSocket connections
- **PostgreSQL** — hosted on Amazon RDS

Redis and SSL/TLS termination are handled at the application level rather than using dedicated AWS services (ElastiCache, load balancers) in order to reduce costs.

### Administrative interfaces

- Django admin: api.roronline.com/admin
- Browsable API: api.roronline.com/rorapp/api

The frontend uses the `www` subdomain and the backend uses the `api` subdomain.

## Map tiles

Map tiles are stored on S3 and served via CloudFront. The Terraform configuration for this infrastructure lives in `infra/map-tiles/` — see `infra/map-tiles/README.md` for setup instructions.

Tiles are generated from the source image using `gdal2tiles` and deployed automatically by the deploy-map-tiles GitHub Actions workflow when a release is published with map image assets attached (e.g. `map-base-v3.png`, `map-overlay-v2.png`). After deployment, manually update the relevant tile version in `frontend/app/map/tile-config.ts` and merge to make production point at the new tiles.

To generate tiles locally for development, slice a map PNG with `gdal2tiles` and copy the output into the frontend. Replace `<layer>` with `map-base` or `map-overlay`.

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "/path/to/map/directory:/data" \
  ghcr.io/osgeo/gdal:ubuntu-small-latest \
  gdal2tiles --profile raster --xyz --zoom=0-6 --processes=4 \
  /data/<layer>.png /data/<layer>-tiles

cp -r /path/to/map/directory/<layer>-tiles/{0,1,2,3,4,5,6} frontend/public/tiles/<layer>/
```

To use local tiles in dev, set `NEXT_PUBLIC_TILES_CDN=` in `frontend/.env`.
