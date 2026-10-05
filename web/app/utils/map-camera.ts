import type { Map } from 'maplibre-gl'
import type { PlanCollection } from '#shared/lot'
import type { MapMode } from './landscape-layers.ts'

export function framePlan(map: Map, plan: PlanCollection, mode: MapMode, duration = 0) {
  let west = Infinity
  let south = Infinity
  let east = -Infinity
  let north = -Infinity
  for (const feature of plan.features) {
    for (const ring of feature.geometry.coordinates) {
      for (const [longitude, latitude] of ring) {
        west = Math.min(west, longitude!)
        south = Math.min(south, latitude!)
        east = Math.max(east, longitude!)
        north = Math.max(north, latitude!)
      }
    }
  }
  if (!Number.isFinite(west)) return
  const volume = mode === 'volume'
  map.fitBounds([[west, south], [east, north]], {
    padding: 44,
    maxZoom: volume ? 18 : 17,
    pitch: volume ? 50 : 0,
    bearing: volume ? -25 : 0,
    duration,
    linear: true,
  })
}

export function rotateView(map: Map, direction: -1 | 1) {
  map.easeTo({ bearing: map.getBearing() + direction * 30, duration: 350 })
}
