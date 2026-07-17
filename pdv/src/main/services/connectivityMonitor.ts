import { net } from 'electron';
import { logger } from '../utils/logger';

export type ConnectivityListener = (isOnline: boolean) => void;

export interface ConnectivityState {
  isOnline: boolean;
  lastOnlineAt: Date | null;
  lastOfflineAt: Date | null;
  lastSyncAt: Date | null;
}

const ONLINE_CHECK_URL = process.env.VITE_API_BASE_URL
  ? `${process.env.VITE_API_BASE_URL.replace('/api/v1/', '/')}health/`
  : 'http://localhost:8000/health/';

const PING_INTERVAL_MS = 30000;
const PING_TIMEOUT_MS = 5000;

class ConnectivityMonitor {
  private state: ConnectivityState = {
    isOnline: true,
    lastOnlineAt: null,
    lastOfflineAt: null,
    lastSyncAt: null,
  };

  private listeners: ConnectivityListener[] = [];
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private checking = false;
  private initialized = false;

  init(): void {
    if (this.initialized) return;
    this.initialized = true;

    this.checkConnectivity().then((online) => {
      this.setState(online);
      this.startPinging();
    });

    logger.info('Connectivity monitor initialized');
  }

  private startPinging(): void {
    this.pingTimer = setInterval(() => {
      this.checkConnectivity().then((online) => {
        if (online !== this.state.isOnline) {
          logger.info('Connectivity changed', { from: this.state.isOnline, to: online });
        }
        this.setState(online);
      });
    }, PING_INTERVAL_MS);
  }

  private async checkConnectivity(): Promise<boolean> {
    if (this.checking) return this.state.isOnline;
    this.checking = true;

    try {
      const result = await new Promise<boolean>((resolve) => {
        const request = net.request({
          method: 'GET',
          url: ONLINE_CHECK_URL,
        });

        const timer = setTimeout(() => {
          request.abort();
          resolve(false);
        }, PING_TIMEOUT_MS);

        request.on('response', (response) => {
          clearTimeout(timer);
          resolve(response.statusCode === 200);
        });

        request.on('error', () => {
          clearTimeout(timer);
          resolve(false);
        });

        request.end();
      });

      return result;
    } finally {
      this.checking = false;
    }
  }

  private setState(online: boolean): void {
    const changed = online !== this.state.isOnline;
    this.state.isOnline = online;

    if (online) {
      if (!this.state.lastOnlineAt) {
        this.state.lastOnlineAt = new Date();
      }
    } else {
      if (!this.state.lastOfflineAt) {
        this.state.lastOfflineAt = new Date();
      }
    }

    if (changed) {
      this.notifyListeners(online);
    }
  }

  onConnectivityChange(listener: ConnectivityListener): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private notifyListeners(online: boolean): void {
    for (const listener of this.listeners) {
      try {
        listener(online);
      } catch (err) {
        logger.error('Connectivity listener error:', err);
      }
    }
  }

  isOnline(): boolean {
    return this.state.isOnline;
  }

  getState(): ConnectivityState {
    return { ...this.state };
  }

  setLastSyncAt(date: Date): void {
    this.state.lastSyncAt = date;
  }

  async forceCheck(): Promise<boolean> {
    const online = await this.checkConnectivity();
    this.setState(online);
    return online;
  }

  destroy(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    this.listeners = [];
    this.initialized = false;
    logger.info('Connectivity monitor destroyed');
  }
}

export const connectivityMonitor = new ConnectivityMonitor();
