import { mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import Database from 'better-sqlite3'
import type { LotStatus } from '#shared/lot'

export interface SaleState {
  lot_id: string
  status: LotStatus
  price_eur: number
}

let database: Database.Database | undefined

function getDatabase(): Database.Database {
  if (database) return database
  const path = resolve(process.env.LOTIMAP_DB_PATH ?? '.data/lotimap.sqlite')
  mkdirSync(dirname(path), { recursive: true })
  database = new Database(path)
  database.pragma('journal_mode = WAL')
  database.exec(`
    CREATE TABLE IF NOT EXISTS lot_sales (
      lot_id TEXT PRIMARY KEY,
      status TEXT NOT NULL CHECK (status IN ('available', 'option', 'reserved', 'sold')),
      price_eur INTEGER NOT NULL CHECK (price_eur > 0)
    )
  `)
  return database
}

export function readSaleStates(lotIds: string[]): Map<string, SaleState> {
  const db = getDatabase()
  const insert = db.prepare('INSERT OR IGNORE INTO lot_sales (lot_id, status, price_eur) VALUES (?, ?, ?)')
  const statuses: LotStatus[] = [
    'available', 'available', 'available', 'available', 'available',
    'available', 'available', 'option', 'reserved', 'sold',
  ]
  db.transaction(() => {
    lotIds.forEach((id, index) => {
      insert.run(id, statuses[index % statuses.length], 65000 + (index % 10) * 2500)
    })
  })()
  const rows = db.prepare('SELECT lot_id, status, price_eur FROM lot_sales').all() as SaleState[]
  return new Map(rows.map(row => [row.lot_id, row]))
}

export function updateSaleState(state: SaleState): SaleState {
  getDatabase().prepare(`
    INSERT INTO lot_sales (lot_id, status, price_eur) VALUES (?, ?, ?)
    ON CONFLICT (lot_id) DO UPDATE SET status = excluded.status, price_eur = excluded.price_eur
  `).run(state.lot_id, state.status, state.price_eur)
  return state
}
