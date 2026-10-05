import type { FillExtrusionLayerSpecification } from 'maplibre-gl'

export const volumeDefinitions = [
  { kind: 'house', color: '#efe7d3', base: 0, height: 4.2 },
  { kind: 'roof', color: '#3c565d', base: 4.2, height: 4.7 },
  { kind: 'hedge-volume', color: '#79917a', base: 0, height: 1.3 },
  { kind: 'trunk', color: '#957352', base: 0, height: 2.3 },
  { kind: 'canopy', color: '#718b69', base: 2.3, height: 4.8 },
] as const

export function volumeLayers(visible: boolean): FillExtrusionLayerSpecification[] {
  return volumeDefinitions.map(({ kind, color, base, height }) => ({
    id: `volume-${kind}`,
    type: 'fill-extrusion',
    source: 'landscape',
    layout: { visibility: visible ? 'visible' : 'none' },
    filter: ['==', ['get', 'kind'], kind],
    paint: {
      'fill-extrusion-color': color,
      'fill-extrusion-base': base,
      'fill-extrusion-height': height,
      'fill-extrusion-opacity': 1,
      'fill-extrusion-vertical-gradient': true,
    },
  }))
}
