# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS build
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npx --yes npm@12.2.0 ci
COPY web/nuxt.config.ts web/tsconfig.json web/eslint.config.mjs ./
COPY web/app/ ./app/
COPY web/server/ ./server/
COPY web/shared/ ./shared/
COPY web/public/ ./public/
ENV NITRO_PRESET=node-server
RUN npm run build

FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000 \
    LOTIMAP_GEOJSON_PATH=/app/data/clos_du_verger.geojson \
    LOTIMAP_ENRICHMENT_PATH=/app/data/enrichment.json \
    LOTIMAP_DB_PATH=/app/state/lotimap.sqlite
WORKDIR /app/web
COPY --from=build --chown=node:node /app/web/.output/ ./.output/
COPY data/demo/geojson/clos_du_verger.geojson /app/data/clos_du_verger.geojson
COPY data/demo/enrichment.json /app/data/enrichment.json
RUN mkdir /app/state && chown node:node /app/state
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
