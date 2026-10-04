import { adminSession, assertAdminRequest } from '../../utils/admin-auth'

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'no-store')
  assertAdminRequest(event)
  const session = await adminSession(event)
  await session.clear()
  return { authenticated: false }
})
