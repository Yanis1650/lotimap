import type { PlanCollection, PlanFeature } from '#shared/lot'
import { readSaleStates } from '../utils/database'
import { readPlanSnapshot } from '../utils/plan'
import { readEnrichment } from '../utils/enrichment'

export default defineEventHandler(async (event): Promise<PlanCollection> => {
  setHeader(event, 'Cache-Control', 'no-store')
  const { features, sha256 } = await readPlanSnapshot()
  const enrichment = await readEnrichment(sha256)
  const lotIds = features.filter(feature => feature.properties.kind === 'lot').map(feature => feature.id)
  const states = readSaleStates(lotIds)
  const publicFeatures = features.map((feature): PlanFeature => {
    if (feature.properties.kind !== 'lot') return feature as PlanFeature
    const state = states.get(feature.id)
    if (!state || typeof feature.properties.area_m2 !== 'number') {
      throw createError({ statusCode: 500, statusMessage: 'Données de lot incomplètes.' })
    }
    return {
      ...feature,
      properties: {
        kind: 'lot',
        lot_id: feature.id,
        layer: feature.properties.layer,
        number: feature.properties.number ?? null,
        area_m2: feature.properties.area_m2,
        price_eur: state.price_eur,
        status: state.status,
        plu_zone: enrichment?.plu[feature.id]?.code ?? null,
        plu_description: enrichment?.plu[feature.id]?.description ?? null,
      },
    }
  })
  return { type: 'FeatureCollection', features: publicFeatures, context: enrichment?.context ?? null }
})
