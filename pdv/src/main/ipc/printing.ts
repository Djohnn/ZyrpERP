import { BrowserWindow, ipcMain } from 'electron';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { logger } from '../utils/logger';

type PrintReceiptPayload = {
  html: string;
  fileName: string;
};

function sanitizeFileName(fileName: string): string {
  return fileName.replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 80) || 'cupom_nao_fiscal';
}

function projectRoot(): string {
  if (process.cwd().endsWith('pdv')) {
    return join(process.cwd(), '..');
  }
  return process.cwd();
}

export function setupPrintingHandlers() {
  ipcMain.handle('printing:receipt', async (_event, payload: PrintReceiptPayload) => {
    const safeFileName = sanitizeFileName(payload.fileName);
    const htmlPath = join(projectRoot(), `${safeFileName}.html`);
    const pdfPath = join(projectRoot(), `${safeFileName}.pdf`);
    let printWindow: BrowserWindow | null = null;

    try {
      await writeFile(htmlPath, payload.html, 'utf-8');

      printWindow = new BrowserWindow({
        show: false,
        webPreferences: {
          sandbox: true,
          nodeIntegration: false,
          contextIsolation: true,
        },
      });

      await printWindow.loadURL(
        `data:text/html;charset=utf-8,${encodeURIComponent(payload.html)}`,
      );

      const pdf = await printWindow.webContents.printToPDF({
        printBackground: true,
        pageSize: {
          width: 80000,
          height: 500000,
        },
        margins: {
          marginType: 'none',
        },
      });
      await writeFile(pdfPath, pdf);

      await new Promise<void>((resolve, reject) => {
        printWindow?.webContents.print(
          {
            silent: false,
            printBackground: true,
          },
          (success, failureReason) => {
            if (success) {
              resolve();
              return;
            }
            reject(new Error(failureReason || 'Falha ao abrir impressão do cupom.'));
          },
        );
      });

      return { success: true, savedPath: pdfPath, htmlPath };
    } catch (error) {
      logger.error('Failed to print receipt:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Falha ao imprimir cupom.',
        savedPath: pdfPath,
        htmlPath,
      };
    } finally {
      printWindow?.close();
    }
  });
}
