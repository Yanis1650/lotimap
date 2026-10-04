import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import type { OpenDataContext } from '#shared/lot'

interface PluMatch { code: string | null; description: string | null; coverage_pct: number }
interface Enrichment {
  plu: Record<string, PluMatch>
  context: OpenDataContext
}

function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function strings(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string')
}

function isoDate(value: unknown): value is string {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const date = new Date(`${value}T00:00:00Z`)
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
}

export function parseEnrichment(data: unknown, planHash: string): Enrichment | null {
  if (!object(data) || data.schema_version !== 1 || data.plan_sha256 !== planHash) return null
  if (!isoDate(data.generated_on) || !object(data.commune) || typeof data.commune.name !== 'string') return null
  if (!object(data.plu) || !object(data.risks) || !strings(data.risks.families) || data.risks.scope !== 'commune') return null
  if (!object(data.dvf) || !Number.isSafeInteger(data.dvf.sample_size) || Number(data.dvf.sample_size) < 0) return null
  const median = data.dvf.median_eur_m2
  if (median !== null && (typeof median !== 'number' || !Number.isFinite(median) || median <= 0)) return null
  const years = data.dvf.years
  if (!Array.isArray(years) || years.length === 0 || !years.every(Number.isSafeInteger)) return null
  if (!object(data.sources) || !object(data.sources.gpu) || !strings(data.sources.gpu.document_dates)) return null
  if (!data.sources.gpu.document_dates.every(value => /^\d{8}$/.test(value)
    && isoDate(`${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`))) return null
  const plu: Record<string, PluMatch> = {}
  for (const [id, match] of Object.entries(data.plu)) {
    if (!object(match) || typeof match.coverage_pct !== 'number' || !Number.isFinite(match.coverage_pct)
      || match.coverage_pct < 0 || match.coverage_pct > 100) return null
    if (match.code !== null && typeof match.code !== 'string') return null
    if (match.description !== null && typeof match.description !== 'string') return null
    plu[id] = { code: match.code, description: match.description, coverage_pct: match.coverage_pct }
  }
  return {
    plu,
    context: {
      generated_on: data.generated_on,
      commune_name: data.commune.name,
      plu_document_dates: data.sources.gpu.document_dates,
      risk_families: data.risks.families,
      dvf: { median_eur_m2: median, sample_size: Number(data.dvf.sample_size), years: years as number[] },
    },
  }
}

export async function readEnrichment(planHash: string): Promise<Enrichment | null> {
  const path = resolve(process.env.LOTIMAP_ENRICHMENT_PATH ?? '../data/demo/enrichment.json')
  try {
    return parseEnrichment(JSON.parse(await readFile(path, 'utf8')), planHash)
  } catch {
    return null
  }
}
