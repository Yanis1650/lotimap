import type { FeatureCollection, LineString, Point, Polygon, Position } from 'geojson'
import type { PlanCollection } from '#shared/lot'

type Kind = 'house' | 'ridge' | 'terrace' | 'driveway' | 'hedge' | 'tree'
type Shape = Polygon | LineString | Point
export type LandscapeCollection = FeatureCollection<Shape, { kind: Kind }>

function mix(a: Position, b: Position, ratio: number): Position {
  return [a[0]! + (b[0]! - a[0]!) * ratio, a[1]! + (b[1]! - a[1]!) * ratio]
}

function distanceToRoad(point: Position, ring: Position[]): number {
  const scale = Math.cos(point[1]! * Math.PI / 180)
  return Math.min(...ring.map((a, index) => {
    const b = ring[(index + 1) % ring.length]!
    const dx = (b[0]! - a[0]!) * scale
    const dy = b[1]! - a[1]!
    const px = (point[0]! - a[0]!) * scale
    const py = point[1]! - a[1]!
    const squaredLength = dx * dx + dy * dy
    const ratio = squaredLength ? Math.max(0, Math.min(1, (px * dx + py * dy) / squaredLength)) : 0
    return Math.hypot(px - ratio * dx, py - ratio * dy)
  }))
}

export function buildLandscape(plan: PlanCollection): LandscapeCollection {
  const features: LandscapeCollection['features'] = []
  const road = plan.features.find(feature => feature.properties.kind === 'road')
  const roadRing = road?.geometry.coordinates[0]?.slice(0, -1)
  if (!roadRing?.length) return { type: 'FeatureCollection', features }

  function add(kind: Kind, geometry: Shape) {
    features.push({ type: 'Feature', properties: { kind }, geometry })
  }

  for (const lot of plan.features.filter(feature => feature.properties.kind === 'lot')) {
    const ring = lot.geometry.coordinates[0]
    // Illustration limitée aux quadrilatères convexes, sans trous, du plan fictif.
    if (!ring || ring.length !== 5 || lot.geometry.coordinates.length !== 1) continue
    const corners = ring.slice(0, 4)
    const crosses = corners.map((point, index) => {
      const next = corners[(index + 1) % 4]!
      const after = corners[(index + 2) % 4]!
      return (next[0]! - point[0]!) * (after[1]! - next[1]!) - (next[1]! - point[1]!) * (after[0]! - next[0]!)
    })
    if (!crosses.every(value => value > 0) && !crosses.every(value => value < 0)) continue
    const frontage = corners.reduce((best, point, index) => {
      const midpoint = mix(point, corners[(index + 1) % 4]!, 0.5)
      const previous = mix(corners[best]!, corners[(best + 1) % 4]!, 0.5)
      return distanceToRoad(midpoint, roadRing) < distanceToRoad(previous, roadRing) ? index : best
    }, 0)
    const [a, b, c, d] = [0, 1, 2, 3].map(offset => corners[(frontage + offset) % 4]!)
    const point = (u: number, v: number) => mix(mix(a!, b!, u), mix(d!, c!, u), v)
    const rectangle = (kind: Kind, left: number, near: number, right: number, far: number) => {
      const coordinates = [point(left, near), point(right, near), point(right, far), point(left, far), point(left, near)]
      add(kind, { type: 'Polygon', coordinates: [coordinates] })
    }
    rectangle('driveway', 0.68, 0.02, 0.84, 0.44)
    rectangle('terrace', 0.24, 0.48, 0.65, 0.62)
    rectangle('house', 0.22, 0.22, 0.65, 0.5)
    add('ridge', { type: 'LineString', coordinates: [point(0.24, 0.36), point(0.63, 0.36)] })
    add('hedge', { type: 'LineString', coordinates: [point(0.06, 0.1), point(0.06, 0.94), point(0.94, 0.94), point(0.94, 0.1)] })
    for (const [u, v] of [[0.28, 0.8], [0.75, 0.76], [0.16, 0.12]]) {
      add('tree', { type: 'Point', coordinates: point(u!, v!) })
    }
  }
  return { type: 'FeatureCollection', features }
}
