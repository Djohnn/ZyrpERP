// @vitest-environment node
import { describe, it, expect, vi } from 'vitest';

vi.mock('../utils/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn() },
}));

import { resolveConflict, getConflictStrategy } from '../services/conflictResolver';

describe('conflictResolver', () => {
  describe('getConflictStrategy', () => {
    it('returns last-write-wins for sale:create', () => {
      expect(getConflictStrategy('sale:create')).toBe('last-write-wins');
    });

    it('returns server-wins for cash-session:open', () => {
      expect(getConflictStrategy('cash-session:open')).toBe('server-wins');
    });

    it('returns last-write-wins for cash-session:close', () => {
      expect(getConflictStrategy('cash-session:close')).toBe('last-write-wins');
    });

    it('returns server-wins for unknown type', () => {
      expect(getConflictStrategy('unknown')).toBe('server-wins');
    });
  });

  describe('resolveConflict', () => {
    it('resolves sale:create as local wins', () => {
      const resolution = resolveConflict('sale:create', { id: 'local' }, { id: 'server' });
      expect(resolution.strategy).toBe('last-write-wins');
      expect(resolution.resolution).toBe('local');
    });

    it('resolves cash-session:open as server wins', () => {
      const resolution = resolveConflict('cash-session:open', { amount: '100' }, { amount: '200' });
      expect(resolution.strategy).toBe('server-wins');
      expect(resolution.resolution).toBe('server');
    });

    it('resolves cash-session:close as local wins', () => {
      const resolution = resolveConflict('cash-session:close', { amount: '150' }, { amount: '200' });
      expect(resolution.strategy).toBe('last-write-wins');
      expect(resolution.resolution).toBe('local');
    });

    it('handles unknown type with server-wins fallback', () => {
      const resolution = resolveConflict('unknown:type', {}, {});
      expect(resolution.strategy).toBe('server-wins');
      expect(resolution.resolution).toBe('server');
    });
  });
});
