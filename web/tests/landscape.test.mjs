import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { buildLandscape } from '../app/utils/landscape.ts'

const plan = JSON.parse(readFileSync(new URL('../../data/demo/geojson/clos_du_verger.geojson', import.meta.url), 'utf8'))
const lots = plan.features.filter(feature => feature.properties.kind === 'lot')
const road = plan.features.find(feature => feature.properties.kind === 'road')

function inside([x, y], ring) {
  let contained = false
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const [ax, ay] = ring[index]
    const [bx, by] = ring[previous]
    if ((ay > y) !== (by > y) && x < (bx - ax) * (y - ay) / (by - ay) + ax) contained = !contained
  }
  return contained
}

test('illustrative buildings and plants stay inside the synthetic lots', () => {
  const before = JSON.stringify(plan)
  const landscape = buildLandscape(plan)
  assert.equal(landscape.features.filter(feature => feature.properties.kind === 'house').length, 20)
  assert.equal(landscape.features.filter(feature => feature.properties.kind === 'tree').length, 60)
  for (const feature of landscape.features) {
    const geometry = feature.geometry
    const points = geometry.type === 'Point' ? [geometry.coordinates]
      : geometry.type === 'Polygon' ? geometry.coordinates.flat() : geometry.coordinates
    const lot = lots.find(lot => lot.id === feature.properties.lot_id)
    assert.ok(lot, 'Each illustrated element belongs to an existing lot ID')
    assert.ok(points.every(point => inside(point, lot.geometry.coordinates[0])))
  }
  assert.equal(JSON.stringify(plan), before)
})

test('filtering keeps only the visible lots in the landscape', () => {
  const subset = { type: 'FeatureCollection', features: [road, lots[11], lots[12]] }
  assert.equal(buildLandscape(subset).features.filter(feature => feature.properties.kind === 'house').length, 2)
})

test('missing road, concave polygons and polygons with holes get no invented implantation', () => {
  assert.equal(buildLandscape({ type: 'FeatureCollection', features: lots }).features.length, 0)
  const concave = { ...lots[0], geometry: { type: 'Polygon', coordinates: [[[0, 0], [4, 0], [1, 1], [0, 4], [0, 0]]] } }
  const hole = { ...lots[0], geometry: { ...lots[0].geometry, coordinates: [...lots[0].geometry.coordinates, lots[0].geometry.coordinates[0]] } }
  assert.equal(buildLandscape({ type: 'FeatureCollection', features: [road, concave, hole] }).features.length, 0)
})
