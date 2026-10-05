import assert from 'node:assert/strict'
import test from 'node:test'
import { validateStyleMin } from '@maplibre/maplibre-gl-style-spec'
import { landscapeLayers } from '../app/utils/landscape-layers.ts'

test('2D, 3D and orthophoto landscape layers satisfy the native MapLibre specification', () => {
  for (const mode of ['landscape', 'volume', 'orthophoto']) {
    const style = {
      version: 8,
      sources: {
        landscape: { type: 'geojson', data: { type: 'FeatureCollection', features: [] } },
      },
      layers: landscapeLayers(mode),
    }
    const errors = validateStyleMin(style)
    assert.deepEqual(errors.map(error => error.message), [], mode)
  }
})
