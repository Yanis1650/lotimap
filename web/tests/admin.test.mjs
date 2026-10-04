import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { createServer } from 'node:net'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { setTimeout as delay } from 'node:timers/promises'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

const webRoot = dirname(dirname(fileURLToPath(import.meta.url)))
const fixture = resolve(webRoot, '../data/demo/geojson/clos_du_verger.geojson')
const password = 'lotimap-integration-test-password'
const secret = 'lotimap-integration-test-secret-very-long-and-random-in-real-use'

async function freePort() {
  const probe = createServer()
  await new Promise(resolve => probe.listen(0, '127.0.0.1', resolve))
  const port = probe.address().port
  await new Promise(resolve => probe.close(resolve))
  return port
}

async function waitForServer(base, child) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (child.exitCode !== null) throw new Error(`Serveur arrêté : ${child.exitCode}`)
    try {
      const response = await fetch(`${base}/api/admin/session`)
      if (response.ok) return
    } catch { /* Server not listening yet. */ }
    await delay(100)
  }
  throw new Error('Le serveur ne démarre pas.')
}

test('admin login, validation, update and logout', async (t) => {
  const directory = mkdtempSync(join(tmpdir(), 'lotimap-admin-'))
  const planPath = join(directory, 'plan.geojson')
  const enrichmentPath = join(directory, 'enrichment.json')
  const planContent = readFileSync(fixture, 'utf8')
  const enrichmentContent = readFileSync(resolve(webRoot, '../data/demo/enrichment.json'), 'utf8')
  writeFileSync(planPath, planContent)
  writeFileSync(enrichmentPath, enrichmentContent)
  const port = await freePort()
  const base = `http://127.0.0.1:${port}`
  const child = spawn(process.execPath, ['.output/server/index.mjs'], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(port),
      HOST: '127.0.0.1',
      LOTIMAP_ADMIN_PASSWORD: password,
      LOTIMAP_SESSION_SECRET: secret,
      LOTIMAP_DB_PATH: join(directory, 'sales.sqlite'),
      LOTIMAP_GEOJSON_PATH: planPath,
      LOTIMAP_ENRICHMENT_PATH: enrichmentPath,
    },
    stdio: 'ignore',
  })
  t.after(async () => {
    child.kill()
    if (child.exitCode === null) await Promise.race([once(child, 'exit'), delay(3000)])
    rmSync(directory, { recursive: true, force: true })
  })
  await waitForServer(base, child)

  const sessionBefore = await fetch(`${base}/api/admin/session`)
  assert.deepEqual(await sessionBefore.json(), { configured: true, authenticated: false })
  const publicBefore = await (await fetch(`${base}/api/lots`)).json()
  const lot = publicBefore.features.find(feature => feature.properties.kind === 'lot')
  assert.equal(typeof lot.properties.plu_zone, 'string')
  assert.equal(typeof publicBefore.context.dvf.median_eur_m2, 'number')
  assert.ok(publicBefore.context.risk_families.length > 0)
  const url = `${base}/api/admin/lots/${encodeURIComponent(lot.id)}`

  const unauthorized = await fetch(url, {
    method: 'PATCH',
    headers: { Origin: base, 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'sold', price_eur: 99999 }),
  })
  assert.equal(unauthorized.status, 401)

  const wrongLogin = await fetch(`${base}/api/admin/login`, {
    method: 'POST',
    headers: { Origin: base, 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: 'wrong' }),
  })
  assert.equal(wrongLogin.status, 401)

  const login = await fetch(`${base}/api/admin/login`, {
    method: 'POST',
    headers: { Origin: base, 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  assert.equal(login.status, 200)
  const setCookie = login.headers.getSetCookie().at(-1)
  assert.match(setCookie, /lotimap_admin=/)
  assert.match(setCookie, /HttpOnly/i)
  assert.match(setCookie, /SameSite=Strict/i)
  const cookie = setCookie.split(';')[0]
  const authenticated = await (await fetch(`${base}/api/admin/session`, {
    headers: { Cookie: cookie },
  })).json()
  assert.equal(authenticated.authenticated, true)

  const forbidden = await fetch(url, {
    method: 'PATCH',
    headers: { Origin: 'https://example.invalid', Cookie: cookie, 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'sold', price_eur: 99999 }),
  })
  assert.equal(forbidden.status, 403)
  const invalid = await fetch(url, {
    method: 'PATCH',
    headers: { Origin: base, Cookie: cookie, 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'sold', price_eur: -1 }),
  })
  assert.equal(invalid.status, 400)

  const updated = await fetch(url, {
    method: 'PATCH',
    headers: { Origin: base, Cookie: cookie, 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'sold', price_eur: 99999 }),
  })
  assert.equal(updated.status, 200)
  const publicAfter = await (await fetch(`${base}/api/lots`)).json()
  const changed = publicAfter.features.find(feature => feature.id === lot.id)
  assert.equal(changed.properties.status, 'sold')
  assert.equal(changed.properties.price_eur, 99999)

  const logout = await fetch(`${base}/api/admin/logout`, {
    method: 'POST', headers: { Origin: base, Cookie: cookie },
  })
  assert.equal(logout.status, 200)
  const sessionAfter = await (await fetch(`${base}/api/admin/session`)).json()
  assert.equal(sessionAfter.authenticated, false)

  const invalidEnrichment = JSON.parse(enrichmentContent)
  invalidEnrichment.generated_on = '2026-02-30'
  writeFileSync(enrichmentPath, JSON.stringify(invalidEnrichment))
  assert.equal((await (await fetch(`${base}/api/lots`)).json()).context, null)
  writeFileSync(enrichmentPath, enrichmentContent)
  writeFileSync(planPath, `${planContent}\n`)
  const changedPlan = await (await fetch(`${base}/api/lots`)).json()
  assert.equal(changedPlan.context, null)
  assert.equal(changedPlan.features.find(feature => feature.id === lot.id).properties.plu_zone, null)
})
