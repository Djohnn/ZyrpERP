import React, { useEffect, useState, useCallback } from 'react';
import type { ConnectivityState, SyncState } from '../../shared/types';

declare global {
  interface Window {
    electronAPI: {
      getConnectivityStatus: () => Promise<{ success: boolean; data: ConnectivityState }>;
      checkConnectivity: () => Promise<{ success: boolean; data: { isOnline: boolean } }>;
      getSyncStatus: () => Promise<{ success: boolean; data: SyncState }>;
      startSync: () => Promise<{ success: boolean; data: SyncState }>;
    };
  }
}

const indicatorStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '6px',
  padding: '4px 10px',
  borderRadius: '12px',
  fontSize: '12px',
  fontWeight: 500,
  cursor: 'pointer',
  border: 'none',
  transition: 'all 0.2s ease',
};

export function SyncIndicator() {
  const [isOnline, setIsOnline] = useState(true);
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const [connResult, syncResult] = await Promise.all([
        window.electronAPI.getConnectivityStatus(),
        window.electronAPI.getSyncStatus(),
      ]);
      if (connResult.success) {
        setIsOnline(connResult.data.isOnline);
      }
      if (syncResult.success) {
        setPendingCount(syncResult.data.pendingCount);
        setSyncing(syncResult.data.status === 'syncing');
      }
    } catch {
      setIsOnline(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleClick = async () => {
    if (!isOnline || syncing) return;
    setSyncing(true);
    try {
      await window.electronAPI.startSync();
    } finally {
      await fetchStatus();
    }
  };

  const getStyle = (): React.CSSProperties => {
    if (syncing) {
      return { ...indicatorStyle, background: '#fff8e1', color: '#f57c00', border: '1px solid #ffe082' };
    }
    if (!isOnline) {
      return { ...indicatorStyle, background: '#ffebee', color: '#d32f2f', border: '1px solid #ef9a9a' };
    }
    if (pendingCount > 0) {
      return { ...indicatorStyle, background: '#fff8e1', color: '#f57c00', border: '1px solid #ffe082' };
    }
    return { ...indicatorStyle, background: '#e8f5e9', color: '#388e3c', border: '1px solid #a5d6a7' };
  };

  const getLabel = (): string => {
    if (syncing) return 'Sincronizando...';
    if (!isOnline) return 'Offline';
    if (pendingCount > 0) return `${pendingCount} pendente${pendingCount > 1 ? 's' : ''}`;
    return 'Online';
  };

  const getDot = (): string => {
    if (syncing) return '\u23F3';
    if (!isOnline) return '\u26A0';
    if (pendingCount > 0) return '\u26A0';
    return '\u2714';
  };

  return (
    <button
      onClick={handleClick}
      style={getStyle()}
      title={
        syncing ? 'Sincronizando opera\u00E7\u00F5es...'
        : !isOnline ? 'Sem conex\u00E3o com o servidor'
        : pendingCount > 0 ? `${pendingCount} opera\u00E7\u00F5es aguardando sincroniza\u00E7\u00E3o`
        : 'Conectado ao servidor'
      }
      disabled={syncing || !isOnline}
    >
      <span>{getDot()}</span>
      <span>{getLabel()}</span>
    </button>
  );
}
