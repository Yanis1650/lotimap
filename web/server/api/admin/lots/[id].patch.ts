import { createError, getRouterParam } from 'h3'
import { isLotStatus } from '#shared/lot'
import { assertAdminRequest, requireAdmin } from '../../../utils/admin-auth'
import { updateSaleState } from '../../../utils/database'
import { readPlan } from '../../../utils/plan'

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'no-store')
  assertAdminRequest(event, true)
  await requireAdmin(event)

  const id = getRouterParam(event, 'id')
  const features = await readPlan()
  if (!id || !features.some(feature => feature.id === id && feature.properties.kind === 'lot')) {
    throw createError({ statusCode: 404, statusMessage: 'Lot introuvable.' })
  }

  const body: unknown = await readBody(event)
  const input = body && typeof body === 'object' ? body as Record<string, unknown> : {}
  const price = input.price_eur
  if (!isLotStatus(input.status) || typeof price !== 'number' || !Number.isSafeInteger(price) || price <= 0) {
    throw createError({ statusCode: 400, statusMessage: 'Statut ou prix invalide.' })
  }

  return updateSaleState({ lot_id: id, status: input.status, price_eur: price })
})
