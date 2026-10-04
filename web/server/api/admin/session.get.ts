import { adminAuthenticated, adminConfigured } from '../../utils/admin-auth'

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'no-store')
  if (!adminConfigured()) return { configured: false, authenticated: false }
  return { configured: true, authenticated: await adminAuthenticated(event) }
})
