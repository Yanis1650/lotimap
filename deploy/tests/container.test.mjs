import assert from 'node:assert/strict'
import { execFile } from 'node:child_process'
import { setTimeout as delay } from 'node:timers/promises'
import { promisify } from 'node:util'
import test from 'node:test'

const run = promisify(execFile)
const base = `http://127.0.0.1:${process.env.LOTIMAP_LOCAL_PORT ?? '3333'}`

async function readPlan() {
  const response = await fetch(`${base}/api/lots`)
  assert.equal(response.status, 200)
  return response.json()
}

test('container data, HTTPS cookie, persistence and indexing directives', async () => {
  for (const path of ['/', '/admin']) {
    const page = await fetch(`${base}${path}`)
    assert.equal(page.status, 200)
    assert.match(page.headers.get('x-robots-tag'), /noindex/)
    assert.match(await page.text(), /name="robots"[^>]+content="noindex/)
  }
  const robots = await fetch(`${base}/robots.txt`)
  assert.equal(robots.status, 200)
  assert.match(await robots.text(), /Disallow: \/\s*$/m)
  const before = await readPlan()
  const lots = before.features.filter(feature => feature.properties.kind === 'lot')
  assert.equal(lots.length, 20)
  assert.ok(before.context)

  const login = await fetch(`${base}/api/admin/login`, {
    method: 'POST',
    headers: { Origin: base, 'Content-Type': 'application/json', 'X-Forwarded-Proto': 'https' },
    body: JSON.stringify({ password: process.env.LOTIMAP_ADMIN_PASSWORD }),
  })
  assert.equal(login.status, 200)
  const setCookie = login.headers.getSetCookie().at(-1)
  assert.match(setCookie, /; Secure/i)
  const price = lots[0].properties.price_eur + 123
  const updated = await fetch(`${base}/api/admin/lots/${encodeURIComponent(lots[0].id)}`, {
    method: 'PATCH',
    headers: { Origin: base, 'Content-Type': 'application/json', Cookie: setCookie.split(';')[0] },
    body: JSON.stringify({ status: 'option', price_eur: price }),
  })
  assert.equal(updated.status, 200)

  await run('docker', [
    'compose', '-p', 'lotimap-check', '-f', 'deploy/compose.yaml',
    '-f', 'deploy/compose.local.yaml', 'restart', 'web',
  ], { timeout: 30000 })
  let after
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try { after = await readPlan(); break } catch { await delay(100) }
  }
  assert.ok(after, 'Le conteneur doit redémarrer.')
  const persisted = after.features.find(feature => feature.id === lots[0].id)
  assert.equal(persisted.properties.price_eur, price)
  assert.equal(persisted.properties.status, 'option')
})
