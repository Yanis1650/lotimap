import { createError, getRequestIP } from 'h3'
import {
  adminSession, assertAdminRequest, passwordVersion, validPassword,
} from '../../utils/admin-auth'

const failures = new Map<string, { count: number; expiresAt: number }>()
const WINDOW_MS = 15 * 60 * 1000
const MAX_ATTEMPTS = 5

export default defineEventHandler(async (event) => {
  setHeader(event, 'Cache-Control', 'no-store')
  assertAdminRequest(event, true)
  const body: unknown = await readBody(event)
  const password = body && typeof body === 'object' && 'password' in body
    ? body.password : undefined
  if (typeof password !== 'string' || password.length > 4096) {
    throw createError({ statusCode: 400, statusMessage: 'Mot de passe invalide.' })
  }

  const ip = getRequestIP(event, { xForwardedFor: true }) ?? 'unknown'
  const now = Date.now()
  const previous = failures.get(ip)
  if (previous && previous.expiresAt > now && previous.count >= MAX_ATTEMPTS) {
    setHeader(event, 'Retry-After', Math.ceil((previous.expiresAt - now) / 1000))
    throw createError({ statusCode: 429, statusMessage: 'Trop de tentatives. Réessayez plus tard.' })
  }
  if (!validPassword(password)) {
    if (failures.size >= 1000 && !failures.has(ip)) failures.delete(failures.keys().next().value!)
    failures.set(ip, {
      count: previous && previous.expiresAt > now ? previous.count + 1 : 1,
      expiresAt: previous && previous.expiresAt > now ? previous.expiresAt : now + WINDOW_MS,
    })
    throw createError({ statusCode: 401, statusMessage: 'Mot de passe incorrect.' })
  }

  failures.delete(ip)
  const session = await adminSession(event)
  await session.update({ authorized: true, passwordVersion: passwordVersion() })
  return { authenticated: true }
})
