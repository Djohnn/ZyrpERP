import Database from 'better-sqlite3';
import { app } from 'electron';
import { join } from 'path';
import { logger } from '../utils/logger';

export interface JournalEntry {
  id: number;
  uuid: string;
  type: 'sale:create' | 'cash-session:open' | 'cash-session:close';
  payload: string;
  idempotency_key: string;
  status: 'pending' | 'syncing' | 'synced' | 'conflict' | 'failed';
  created_at: string;
  synced_at: string | null;
  retry_count: number;
  last_error: string | null;
  conflict_resolution: string | null;
}

class OperationJournal {
  private db: Database.Database | null = null;

  init(): void {
    const dbPath = join(app.getPath('userData'), 'operation-journal.db');
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.createTables();
    logger.info('Operation journal initialized');
  }

  private createTables(): void {
    if (!this.db) return;
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS operation_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL CHECK(type IN ('sale:create', 'cash-session:open', 'cash-session:close')),
        payload TEXT NOT NULL,
        idempotency_key TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'syncing', 'synced', 'conflict', 'failed')),
        created_at TEXT NOT NULL,
        synced_at TEXT,
        retry_count INTEGER DEFAULT 0,
        last_error TEXT,
        conflict_resolution TEXT
      );
      CREATE INDEX IF NOT EXISTS idx_journal_status ON operation_journal(status);
      CREATE INDEX IF NOT EXISTS idx_journal_created ON operation_journal(created_at);
      CREATE TABLE IF NOT EXISTS sync_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
    `);

    const stmt = this.db.prepare('INSERT OR IGNORE INTO sync_metadata (key, value, updated_at) VALUES (?, ?, ?)');
    stmt.run('last_catalog_sync', '0', '1970-01-01T00:00:00Z');
    stmt.run('last_operations_sync', '0', '1970-01-01T00:00:00Z');
    stmt.run('schema_version', '2', '2026-07-17T00:00:00Z');
  }

  addOperation(op: {
    uuid: string;
    type: 'sale:create' | 'cash-session:open' | 'cash-session:close';
    payload: Record<string, unknown>;
    idempotencyKey: string;
  }): JournalEntry {
    if (!this.db) throw new Error('Journal not initialized');
    const now = new Date().toISOString();
    const stmt = this.db.prepare(`
      INSERT INTO operation_journal (uuid, type, payload, idempotency_key, status, created_at)
      VALUES (?, ?, ?, ?, 'pending', ?)
    `);
    stmt.run(op.uuid, op.type, JSON.stringify(op.payload), op.idempotencyKey, now);
    return this.getByUuid(op.uuid)!;
  }

  getPending(): JournalEntry[] {
    if (!this.db) return [];
    const stmt = this.db.prepare(
      'SELECT * FROM operation_journal WHERE status = ? ORDER BY created_at ASC'
    );
    return stmt.all('pending') as JournalEntry[];
  }

  getPendingCount(): number {
    if (!this.db) return 0;
    const stmt = this.db.prepare('SELECT COUNT(*) as count FROM operation_journal WHERE status = ?');
    const row = stmt.get('pending') as { count: number };
    return row.count;
  }

  getByUuid(uuid: string): JournalEntry | null {
    if (!this.db) return null;
    const stmt = this.db.prepare('SELECT * FROM operation_journal WHERE uuid = ?');
    return stmt.get(uuid) as JournalEntry | null;
  }

  markSyncing(uuid: string): void {
    if (!this.db) return;
    const stmt = this.db.prepare("UPDATE operation_journal SET status = 'syncing' WHERE uuid = ?");
    stmt.run(uuid);
  }

  markSynced(uuid: string): void {
    if (!this.db) return;
    const now = new Date().toISOString();
    const stmt = this.db.prepare(
      "UPDATE operation_journal SET status = 'synced', synced_at = ? WHERE uuid = ?"
    );
    stmt.run(now, uuid);
  }

  markConflict(uuid: string, resolution: Record<string, unknown>): void {
    if (!this.db) return;
    const stmt = this.db.prepare(
      "UPDATE operation_journal SET status = 'conflict', conflict_resolution = ? WHERE uuid = ?"
    );
    stmt.run(JSON.stringify(resolution), uuid);
  }

  markFailed(uuid: string, error: string): void {
    if (!this.db) return;
    const stmt = this.db.prepare(
      'UPDATE operation_journal SET status = ?, last_error = ?, retry_count = retry_count + 1 WHERE uuid = ?'
    );
    stmt.run('failed', error, uuid);
  }

  markRetry(uuid: string, error: string): void {
    if (!this.db) return;
    const stmt = this.db.prepare(
      "UPDATE operation_journal SET status = 'pending', last_error = ?, retry_count = retry_count + 1 WHERE uuid = ?"
    );
    stmt.run(error, uuid);
  }

  cleanup(daysOld: number = 7): number {
    if (!this.db) return 0;
    const cutoff = new Date(Date.now() - daysOld * 24 * 60 * 60 * 1000).toISOString();
    const stmt = this.db.prepare(
      "DELETE FROM operation_journal WHERE status = 'synced' AND created_at < ?"
    );
    const result = stmt.run(cutoff);
    return result.changes;
  }

  getAll(): JournalEntry[] {
    if (!this.db) return [];
    const stmt = this.db.prepare('SELECT * FROM operation_journal ORDER BY created_at DESC');
    return stmt.all() as JournalEntry[];
  }

  getSyncMetadata(key: string): string | null {
    if (!this.db) return null;
    const stmt = this.db.prepare('SELECT value FROM sync_metadata WHERE key = ?');
    const row = stmt.get(key) as { value: string } | undefined;
    return row?.value ?? null;
  }

  setSyncMetadata(key: string, value: string): void {
    if (!this.db) return;
    const now = new Date().toISOString();
    const stmt = this.db.prepare(
      'INSERT OR REPLACE INTO sync_metadata (key, value, updated_at) VALUES (?, ?, ?)'
    );
    stmt.run(key, value, now);
  }

  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

export const operationJournal = new OperationJournal();
