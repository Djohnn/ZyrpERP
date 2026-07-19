// @vitest-environment node
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

type RequestHandler = (...args: unknown[]) => void;

function makeRequestMock(simulateOnline: boolean) {
  const handlers = new Map<string, RequestHandler>();
  return {
    on: vi.fn((event: string, handler: RequestHandler) => {
      handlers.set(event, handler);
    }),
    abort: vi.fn(),
    end: vi.fn(() => {
      const h = handlers.get(simulateOnline ? 'response' : 'error');
      if (h) h(simulateOnline ? { statusCode: 200 } : new Error('connect ECONNREFUSED'));
    }),
  };
}

async function flushMicrotasks(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0));
}

vi.mock('electron', () => ({
  net: {
    request: vi.fn(),
  },
  app: {
    getPath: vi.fn(() => '/tmp'),
    isPackaged: false,
    getAppPath: vi.fn(() => '/tmp'),
  },
}));

vi.mock('../utils/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn() },
}));

import { net } from 'electron';
import { connectivityMonitor } from '../services/connectivityMonitor';

describe('connectivityMonitor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    connectivityMonitor.destroy();
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
  });

  afterEach(() => {
    connectivityMonitor.destroy();
  });

  it('starts online after init with successful ping', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    connectivityMonitor.init();
    await flushMicrotasks();
    expect(connectivityMonitor.isOnline()).toBe(true);
  });

  it('starts offline after init with failed ping', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(false) as never);
    connectivityMonitor.init();
    await flushMicrotasks();
    expect(connectivityMonitor.isOnline()).toBe(false);
  });

  it('notifies listeners when connectivity changes from offline to online', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(false) as never);
    connectivityMonitor.init();
    await flushMicrotasks();
    expect(connectivityMonitor.isOnline()).toBe(false);
    const listener = vi.fn();
    connectivityMonitor.onConnectivityChange(listener);
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    await connectivityMonitor.forceCheck();
    expect(listener).toHaveBeenCalledWith(true);
  });

  it('forceCheck returns online status', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    connectivityMonitor.init();
    await flushMicrotasks();
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    const result = await connectivityMonitor.forceCheck();
    expect(result).toBe(true);
  });

  it('forceCheck returns false when offline', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    connectivityMonitor.init();
    await flushMicrotasks();
    vi.mocked(net.request).mockReturnValue(makeRequestMock(false) as never);
    const result = await connectivityMonitor.forceCheck();
    expect(result).toBe(false);
  });

  it('getState returns current state', async () => {
    vi.mocked(net.request).mockReturnValue(makeRequestMock(true) as never);
    connectivityMonitor.init();
    await vi.waitFor(() => expect(connectivityMonitor.isOnline()).toBe(true));
    const state = connectivityMonitor.getState();
    expect(state.isOnline).toBe(true);
    expect(state.lastOnlineAt).toBeInstanceOf(Date);
  });

  it('setLastSyncAt updates lastSyncAt', () => {
    const date = new Date();
    connectivityMonitor.setLastSyncAt(date);
    expect(connectivityMonitor.getState().lastSyncAt).toBe(date);
  });

  it('destroy clears listeners and stops pinging', () => {
    const listener = vi.fn();
    connectivityMonitor.onConnectivityChange(listener);
    connectivityMonitor.destroy();
    connectivityMonitor.init();
    expect(connectivityMonitor.getState().isOnline).toBe(true);
  });
});
