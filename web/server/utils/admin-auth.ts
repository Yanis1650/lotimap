import { createHash, timingSafeEqual } from 'node:crypto'
import {
  createError, getHeader, getRequestProtocol, getRequestURL, useSession,
  type H3Event,
} from 'h3'

interface AdminSession {
  authorized?: boolean
  passwordVersion?: string
}

const SESSION_AGE_SECONDS = 8 * 60 * 60

function credentials() {
  const password = process.env.LOTIMAP_ADMIN_PASSWORD
  const secret = process.env.LOTIMAP_SESSION_SECRET
  if (!password || !secret || secret.length < 32) {
    throw createError({ statusCode: 503, statusMessage: 'Administration non configurée.' })
  }
  return { password, secret }
}

function version(password: string): string {
  return createHash('sha256').update(password).digest('hex')
}

export function adminConfigured(): boolean {
  return Boolean(
    process.env.LOTIMAP_ADMIN_PASSWORD
    && process.env.LOTIMAP_SESSION_SECRET
    && process.env.LOTIMAP_SESSION_SECRET.length >= 32,
  )
}

export function validPassword(candidate: string): boolean {
  const expected = createHash('sha256').update(credentials().password).digest()
  const actual = createHash('sha256').update(candidate).digest()
  return timingSafeEqual(actual, expected)
}

export function assertAdminRequest(event: H3Event, jsonBody = false): void {
  const expectedOrigin = process.env.LOTIMAP_PUBLIC_ORIGIN ?? getRequestURL(event).origin
  if (getHeader(event, 'origin') !== expectedOrigin) {
    throw createError({ statusCode: 403, statusMessage: 'Origine de la requête refusée.' })
  }
  if (jsonBody && getHeader(event, 'content-type')?.split(';')[0]?.trim() !== 'application/json') {
    throw createError({ statusCode: 415, statusMessage: 'JSON requis.' })
  }
}

export async function adminSession(event: H3Event) {
  const { secret } = credentials()
  return useSession<AdminSession>(event, {
    name: 'lotimap_admin',
    password: secret,
    maxAge: SESSION_AGE_SECONDS,
    sessionHeader: false,
    cookie: {
      path: '/api/admin',
      httpOnly: true,
      sameSite: 'strict',
      secure: getRequestProtocol(event) === 'https',
    },
  })
}

export async function requireAdmin(event: H3Event): Promise<void> {
  if (!await adminAuthenticated(event)) {
    throw createError({ statusCode: 401, statusMessage: 'Connexion requise.' })
  }
}

export async function adminAuthenticated(event: H3Event): Promise<boolean> {
  const session = await adminSession(event)
  return session.data.authorized === true
    && session.data.passwordVersion === version(credentials().password)
}

export function passwordVersion(): string {
  return version(credentials().password)
}
