import Database from 'better-sqlite3';
import { app } from 'electron';
import { join } from 'path';
import { logger } from '../utils/logger';

export interface CachedProduct {
  id: string;
  sku: string;
  name: string;
  base_unit_id: string;
  requires_lot: boolean;
  requires_expiry: boolean;
  is_active: boolean;
  updated_at: string;
}

export interface CachedPrice {
  id: string;
  product_id: string;
  amount: string;
  valid_from: string;
  valid_to: string | null;
  updated_at: string;
}

export interface SearchResult {
  products: CachedProduct[];
  fromCache: boolean;
}

class CatalogCache {
  private db: Database.Database | null = null;
  private lastSync: Date | null = null;

  init(): void {
    const dbPath = join(app.getPath('userData'), 'catalog.db');
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.createTables();
  }

  private createTables(): void {
    if (!this.db) return;

    this.db.exec(`
      CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        sku TEXT NOT NULL,
        name TEXT NOT NULL,
        base_unit_id TEXT NOT NULL,
        requires_lot INTEGER NOT NULL DEFAULT 0,
        requires_expiry INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS prices (
        id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        amount TEXT NOT NULL,
        valid_from TEXT NOT NULL,
        valid_to TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
      );

      CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
      CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
      CREATE INDEX IF NOT EXISTS idx_prices_product ON prices(product_id);
    `);
  }

  async syncFromBackend(): Promise<{ products: number; prices: number }> {
    this.lastSync = new Date();
    return { products: 0, prices: 0 };
  }

  searchProducts(query: string): CachedProduct[] {
    if (!this.db) return [];

    const stmt = this.db.prepare(`
      SELECT * FROM products 
      WHERE (sku LIKE ? OR name LIKE ?) AND is_active = 1
      ORDER BY sku
      LIMIT 20
    `);

    const searchTerm = `%${query}%`;
    return stmt.all(searchTerm, searchTerm) as CachedProduct[];
  }

  getProductById(id: string): CachedProduct | null {
    if (!this.db) return null;
    const stmt = this.db.prepare('SELECT * FROM products WHERE id = ?');
    return stmt.get(id) as CachedProduct | null;
  }

  getProductBySku(sku: string): CachedProduct | null {
    if (!this.db) return null;
    const stmt = this.db.prepare('SELECT * FROM products WHERE sku = ? AND is_active = 1');
    return stmt.get(sku) as CachedProduct | null;
  }

  getPrice(productId: string, at: Date = new Date()): CachedPrice | null {
    if (!this.db) return null;
    const stmt = this.db.prepare(`
      SELECT * FROM prices 
      WHERE product_id = ? AND valid_from <= ?
      AND (valid_to IS NULL OR valid_to > ?)
      ORDER BY valid_from DESC
      LIMIT 1
    `);
    const atStr = at.toISOString();
    return stmt.get(productId, atStr, atStr) as CachedPrice | null;
  }

  updateProduct(product: CachedProduct): void {
    if (!this.db) return;
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO products 
      (id, sku, name, base_unit_id, requires_lot, requires_expiry, is_active, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      product.id, product.sku, product.name, product.base_unit_id,
      product.requires_lot ? 1 : 0, product.requires_expiry ? 1 : 0,
      product.is_active ? 1 : 0, product.updated_at
    );
  }

  updatePrice(price: CachedPrice): void {
    if (!this.db) return;
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO prices 
      (id, product_id, amount, valid_from, valid_to, updated_at)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      price.id, price.product_id, price.amount,
      price.valid_from, price.valid_to, price.updated_at
    );
  }

  getLastSync(): Date | null {
    return this.lastSync;
  }

  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

export const catalogCache = new CatalogCache();
