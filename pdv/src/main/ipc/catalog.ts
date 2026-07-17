import { ipcMain, IpcMainInvokeEvent } from 'electron';
import { api } from '../services/api';
import { logger } from '../utils/logger';

export function setupCatalogHandlers() {
  ipcMain.handle('catalog:search-products', async (event: IpcMainInvokeEvent, query: string) => {
    logger.info('Searching products', { query });
    try {
      const result = await api.get('/products/', { params: { search: query } });
      return { success: true, data: result };
    } catch (error) {
      logger.error('Failed to search products:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Failed to search products' };
    }
  });

  ipcMain.handle('catalog:get-product', async (event: IpcMainInvokeEvent, productId: string) => {
    try {
      const result = await api.get(`/products/${productId}/`);
      return { success: true, data: result };
    } catch (error) {
      logger.error('Failed to get product:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Failed to get product' };
    }
  });

  ipcMain.handle('catalog:get-price', async (event: IpcMainInvokeEvent, data: { productId: string; branchId?: string }) => {
    try {
      const result = await api.get(`/products/${data.productId}/prices/`, {
        params: { branch: data.branchId },
      });
      return { success: true, data: result };
    } catch (error) {
      logger.error('Failed to get price:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Failed to get price' };
    }
  });

  ipcMain.handle('catalog:list-units', async () => {
    try {
      const result = await api.get('/units/');
      return { success: true, data: result };
    } catch (error) {
      logger.error('Failed to list units:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Failed to list units' };
    }
  });
}