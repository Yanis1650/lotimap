import type { Feature, Polygon } from 'geojson'

export type LotStatus = 'available' | 'option' | 'reserved' | 'sold'

export interface LotProperties {
  kind: 'lot'
  lot_id: string
  layer: string
  number: string | null
  area_m2: number
  price_eur: number
  status: LotStatus
  plu_zone: string | null
  plu_description: string | null
}

export interface OpenDataContext {
  generated_on: string
  commune_name: string
  plu_document_dates: string[]
  risk_families: string[]
  dvf: { median_eur_m2: number | null; sample_size: number; years: number[] }
}

export interface AreaProperties {
  kind: 'road' | 'operation_boundary'
  layer: string
}

export type IdentifiedFeature<Properties> = Feature<Polygon, Properties> & { id: string }
export type LotFeature = IdentifiedFeature<LotProperties>
export type AreaFeature = IdentifiedFeature<AreaProperties>
export type PlanFeature = LotFeature | AreaFeature

export interface PlanCollection {
  type: 'FeatureCollection'
  features: PlanFeature[]
  context?: OpenDataContext | null
}

export function isLotFeature(feature: PlanFeature): feature is LotFeature {
  return feature.properties.kind === 'lot'
}

export function isLotStatus(value: unknown): value is LotStatus {
  return value === 'available' || value === 'option' || value === 'reserved' || value === 'sold'
}
