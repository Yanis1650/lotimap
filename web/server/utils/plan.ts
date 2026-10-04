import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import type { Feature, Polygon } from 'geojson'

interface RawProperties {
  kind: 'lot' | 'road' | 'operation_boundary'
  layer: string
  number?: string | null
  area_m2?: number
}

export type RawFeature = Feature<Polygon, RawProperties> & { id: string }

export async function readPlanSnapshot(): Promise<{ features: RawFeature[]; sha256: string }> {
  const path = resolve(
    process.env.LOTIMAP_GEOJSON_PATH ?? '../data/demo/geojson/clos_du_verger.geojson',
  )
  const content = await readFile(path, 'utf8')
  const plan: unknown = JSON.parse(content)
  if (!plan || typeof plan !== 'object' || !('features' in plan) || !Array.isArray(plan.features)) {
    throw new Error('Le GeoJSON de démonstration est invalide.')
  }
  return { features: plan.features as RawFeature[], sha256: createHash('sha256').update(content).digest('hex') }
}

export async function readPlan(): Promise<RawFeature[]> {
  return (await readPlanSnapshot()).features
}
