<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'
import type { FeatureCollection } from 'geojson'
import * as maplibregl from 'maplibre-gl'
import type { GeoJSONSource } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import type { PlanCollection } from '#shared/lot'
import { buildLandscape } from '~/utils/landscape'
import { landscapeLayers, setMapMode } from '~/utils/landscape-layers'
import type { MapMode } from '~/utils/landscape-layers'

const props = defineProps<{ collection: PlanCollection; selectedId: string | null; mode: MapMode }>()
const emit = defineEmits<{ select: [id: string] }>()
const container = ref<HTMLElement | null>(null)
const mapError = ref(false)
let map: maplibregl.Map | undefined

const ignTiles = 'https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&FORMAT=image/jpeg&TILEMATRIXSET=PM_0_19&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}'

function fitPlan() {
  if (!map) return
  const bounds = new maplibregl.LngLatBounds()
  for (const feature of props.collection.features) {
    for (const ring of feature.geometry.coordinates) {
      for (const position of ring) bounds.extend([position[0]!, position[1]!])
    }
  }
  if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 48, maxZoom: 17, duration: 0 })
}

watch(container, (element) => {
  if (!element || map) return
  try {
    maplibregl.setWorkerUrl(workerUrl)
    map = new maplibregl.Map({
      container: element,
      center: [-1.357, 48.684],
      zoom: 15,
      attributionControl: false,
      style: {
        version: 8,
        sources: {
          ign: {
            type: 'raster',
            tiles: [ignTiles],
            tileSize: 256,
            minzoom: 0,
            maxzoom: 19,
            attribution: '<a href="https://cartes.gouv.fr/" target="_blank" rel="noopener noreferrer">© IGN</a>',
          },
          plan: { type: 'geojson', data: props.collection as FeatureCollection },
          landscape: { type: 'geojson', data: buildLandscape(props.collection) },
        },
        layers: [
          { id: 'ground', type: 'background', paint: { 'background-color': '#e7eddf' } },
          { id: 'orthophoto', type: 'raster', source: 'ign', layout: { visibility: props.mode === 'orthophoto' ? 'visible' : 'none' } },
          {
            id: 'road', type: 'fill', source: 'plan',
            filter: ['==', ['get', 'kind'], 'road'],
            paint: { 'fill-color': '#f3f0e7', 'fill-opacity': 0.68 },
          },
          {
            id: 'boundary', type: 'line', source: 'plan',
            filter: ['==', ['get', 'kind'], 'operation_boundary'],
            paint: { 'line-color': '#fffaf0', 'line-width': 3, 'line-dasharray': [3, 2] },
          },
          {
            id: 'lots-fill', type: 'fill', source: 'plan',
            filter: ['==', ['get', 'kind'], 'lot'],
            paint: {
              'fill-color': [
                'match', ['get', 'status'],
                'available', '#79bfa0', 'option', '#e8c265',
                'reserved', '#e99166', 'sold', '#a0aab0', '#a0aab0',
              ],
              'fill-opacity': 0.62,
            },
          },
          {
            id: 'lots-outline', type: 'line', source: 'plan',
            filter: ['==', ['get', 'kind'], 'lot'],
            paint: { 'line-color': '#ffffff', 'line-width': 2 },
          },
          {
            id: 'selected-outline', type: 'line', source: 'plan',
            filter: ['==', ['get', 'lot_id'], props.selectedId ?? ''],
            paint: { 'line-color': '#163d33', 'line-width': 5 },
          },
          ...landscapeLayers(props.mode),
          {
            id: 'lot-numbers', type: 'symbol', source: 'plan',
            filter: ['==', ['get', 'kind'], 'lot'],
            layout: { 'text-field': ['get', 'number'], 'text-size': 14, 'text-font': ['Open Sans Bold'] },
            paint: { 'text-color': '#163d33', 'text-halo-color': '#ffffff', 'text-halo-width': 1.5 },
          },
        ],
      },
    })
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
    map.on('error', (event) => {
      if (event.error?.message?.includes('Worker failed')) mapError.value = true
    })
    map.once('style.load', () => {
      fitPlan()
      setMapMode(map!, props.mode)
    })
    map.on('click', (event) => {
      const feature = map?.queryRenderedFeatures(event.point, { layers: ['lots-fill'] })[0]
      const id = feature?.properties?.lot_id
      if (typeof id === 'string') emit('select', id)
    })
    map.on('mouseenter', 'lots-fill', () => { map!.getCanvas().style.cursor = 'pointer' })
    map.on('mouseleave', 'lots-fill', () => { map!.getCanvas().style.cursor = '' })
  } catch {
    mapError.value = true
  }
}, { flush: 'post' })

watch(() => props.collection, (collection) => {
  map?.getSource<GeoJSONSource>('plan')?.setData(collection as FeatureCollection)
  map?.getSource<GeoJSONSource>('landscape')?.setData(buildLandscape(collection))
})
watch(() => props.mode, mode => { if (map) setMapMode(map, mode) })
watch(() => props.selectedId, (id) => {
  if (map?.getLayer('selected-outline')) map.setFilter('selected-outline', ['==', ['get', 'lot_id'], id ?? ''])
})
onUnmounted(() => map?.remove())
</script>

<template>
  <div class="map-wrap">
    <div ref="container" class="map-canvas" :aria-label="mode === 'landscape' ? 'Plan paysager illustratif des lots' : 'Plan des lots sur orthophoto IGN'" />
    <p v-if="mapError" class="map-error" role="alert">La carte ne peut pas s'afficher sur cet appareil. La liste des lots reste disponible.</p>
  </div>
</template>
