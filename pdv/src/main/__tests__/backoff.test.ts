// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { getBackoffDelay, shouldRetry } from '../utils/backoff';

describe('backoff', () => {
  it('returns 5s for first retry', () => {
    expect(getBackoffDelay(0)).toBe(5000);
  });

  it('returns 15s for second retry', () => {
    expect(getBackoffDelay(1)).toBe(15000);
  });

  it('returns 45s for third retry', () => {
    expect(getBackoffDelay(2)).toBe(45000);
  });

  it('returns 120s for fourth retry', () => {
    expect(getBackoffDelay(3)).toBe(120000);
  });

  it('caps at 120s for subsequent retries', () => {
    expect(getBackoffDelay(10)).toBe(120000);
    expect(getBackoffDelay(100)).toBe(120000);
  });

  it('shouldRetry returns true below max', () => {
    expect(shouldRetry(0)).toBe(true);
    expect(shouldRetry(5)).toBe(true);
    expect(shouldRetry(9)).toBe(true);
  });

  it('shouldRetry returns false at max', () => {
    expect(shouldRetry(10)).toBe(false);
    expect(shouldRetry(20)).toBe(false);
  });
});
