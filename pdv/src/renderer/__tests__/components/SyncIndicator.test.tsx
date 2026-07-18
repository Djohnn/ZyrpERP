import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import { SyncIndicator } from '../../components/SyncIndicator';

beforeEach(() => {
  window.electronAPI = {
    getConnectivityStatus: vi.fn(),
    checkConnectivity: vi.fn(),
    getSyncStatus: vi.fn(),
    startSync: vi.fn(),
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('SyncIndicator', () => {
  it('shows online state with enabled button when connected and no pending', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 0, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('Online')).toBeInTheDocument();
    });
    expect(screen.getByRole('button')).not.toBeDisabled();
  });

  it('shows offline state with disabled button when disconnected', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: false, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 0, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    });
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows pending count when there are pending items', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 3, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('3 pendentes')).toBeInTheDocument();
    });
  });

  it('shows singular pending label for single item', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 1, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('1 pendente')).toBeInTheDocument();
    });
  });

  it('shows syncing state with disabled button during sync', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'syncing', pendingCount: 5, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('Sincronizando...')).toBeInTheDocument();
    });
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('triggers sync on click when online with pending items', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 2, lastSyncAt: null, error: null },
    });
    window.electronAPI.startSync.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 0, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('2 pendentes')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button'));
    expect(window.electronAPI.startSync).toHaveBeenCalledTimes(1);
  });

  it('does not trigger sync when offline', async () => {
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: false, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 2, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button'));
    expect(window.electronAPI.startSync).not.toHaveBeenCalled();
  });

  it('updates state on polling interval', async () => {
    vi.useFakeTimers();
    window.electronAPI.getConnectivityStatus.mockResolvedValue({
      success: true, data: { isOnline: true, lastOnlineAt: null, lastOfflineAt: null, lastSyncAt: null },
    });
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 0, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);

    await vi.waitFor(() => {
      expect(screen.queryByText('Online')).toBeInTheDocument();
    }, { interval: 50, timeout: 3000 });

    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 7, lastSyncAt: null, error: null },
    });

    act(() => {
      vi.advanceTimersByTime(15000);
    });

    await vi.waitFor(() => {
      expect(screen.queryByText('7 pendentes')).toBeInTheDocument();
    }, { interval: 50, timeout: 3000 });
    vi.useRealTimers();
  });

  it('falls back to offline when connectivity fetch fails', async () => {
    window.electronAPI.getConnectivityStatus.mockRejectedValue(new Error('fail'));
    window.electronAPI.getSyncStatus.mockResolvedValue({
      success: true, data: { status: 'idle', pendingCount: 0, lastSyncAt: null, error: null },
    });
    render(<SyncIndicator />);
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    });
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
