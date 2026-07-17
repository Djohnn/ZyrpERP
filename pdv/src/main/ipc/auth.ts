import { ipcMain, IpcMainInvokeEvent } from 'electron';
import { api } from '../services/api';
import { auth } from '../services/auth';
import { logger } from '../utils/logger';

export function setupAuthHandlers() {
  ipcMain.handle('auth:login', async (event: IpcMainInvokeEvent, apiKey: string) => {
    logger.info('Attempting login with API key');
    try {
      const result = await auth.validateApiKey(apiKey);
      return { success: true, data: result };
    } catch (error) {
      logger.error('Login failed:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Invalid API key' };
    }
  });

  ipcMain.handle('auth:logout', async () => {
    auth.clearAuth();
    return { success: true };
  });

  ipcMain.handle('auth:check', async () => {
    return { success: true, authenticated: auth.isAuthenticated(), deviceId: auth.getDeviceId(), branchId: auth.getBranchId() };
  });

  ipcMain.handle('auth:refresh', async () => {
    try {
      const result = await auth.refreshToken();
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Failed to refresh token' };
    }
  });
}