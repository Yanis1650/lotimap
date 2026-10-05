import type { LayerSpecification, Map } from 'maplibre-gl'

export type MapMode = 'landscape' | 'orthophoto'

export function landscapeLayers(mode: MapMode): LayerSpecification[] {
  const layout = { visibility: mode === 'landscape' ? 'visible' as const : 'none' as const }
  return [
    {
      id: 'driveway', type: 'fill', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'driveway'],
      paint: { 'fill-color': '#e4decd' },
    },
    {
      id: 'terrace', type: 'fill', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'terrace'],
      paint: { 'fill-color': '#c8a681' },
    },
    {
      id: 'house', type: 'fill', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'house'],
      paint: { 'fill-color': '#3c565d', 'fill-outline-color': '#f7f2e6' },
    },
    {
      id: 'roof-ridge', type: 'line', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'ridge'],
      paint: { 'line-color': '#c6d5d7', 'line-width': 1 },
    },
    {
      id: 'hedge', type: 'line', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'hedge'],
      paint: { 'line-color': '#79917a', 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 1, 19, 6] },
    },
    {
      id: 'trees', type: 'circle', source: 'landscape', layout,
      filter: ['==', ['get', 'kind'], 'tree'],
      paint: {
        'circle-color': '#718b69', 'circle-opacity': 0.9,
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 14, 2, 17, 6, 19, 14],
        'circle-stroke-color': '#e7eddf', 'circle-stroke-width': 1,
      },
    },
  ]
}

export function setMapMode(map: Map, mode: MapMode) {
  const landscape = mode === 'landscape'
  if (!map.getLayer('orthophoto')) return
  map.setLayoutProperty('orthophoto', 'visibility', landscape ? 'none' : 'visible')
  for (const layer of landscapeLayers(mode)) map.setLayoutProperty(layer.id, 'visibility', landscape ? 'visible' : 'none')
  map.setPaintProperty('lots-fill', 'fill-opacity', landscape ? 0.3 : 0.62)
  map.setPaintProperty('boundary', 'line-color', landscape ? '#3c565d' : '#fffaf0')
  map.setPaintProperty('road', 'fill-color', landscape ? '#d5d1c7' : '#f3f0e7')
  map.setPaintProperty('road', 'fill-opacity', landscape ? 1 : 0.68)
}
