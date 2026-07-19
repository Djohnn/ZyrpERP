// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  printMock: vi.fn((_options, callback) => callback(true)),
  printToPDFMock: vi.fn().mockResolvedValue(Buffer.from('pdf')),
  loadURLMock: vi.fn().mockResolvedValue(undefined),
  closeMock: vi.fn(),
  writeFileMock: vi.fn().mockResolvedValue(undefined),
  handleMock: vi.fn(),
}));

vi.mock('electron', () => ({
  BrowserWindow: vi.fn().mockImplementation(function () {
    return {
    loadURL: mocks.loadURLMock,
    close: mocks.closeMock,
    webContents: {
      print: mocks.printMock,
      printToPDF: mocks.printToPDFMock,
    },
    };
  }),
  ipcMain: {
    handle: mocks.handleMock,
  },
}));

vi.mock('fs/promises', () => ({
  writeFile: mocks.writeFileMock,
}));

vi.mock('../utils/logger', () => ({
  logger: { error: vi.fn() },
}));

import { setupPrintingHandlers } from '../ipc/printing';

describe('printing IPC', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.printMock.mockImplementation((_options, callback) => callback(true));
    mocks.printToPDFMock.mockResolvedValue(Buffer.from('pdf'));
    mocks.loadURLMock.mockResolvedValue(undefined);
    mocks.writeFileMock.mockResolvedValue(undefined);
    vi.spyOn(process, 'cwd').mockReturnValue('C:\\ERP\\pdv');
  });

  it('saves receipt files and opens native print dialog', async () => {
    setupPrintingHandlers();
    const handler = mocks.handleMock.mock.calls.find(([channel]) => channel === 'printing:receipt')?.[1];

    const result = await handler({}, {
      fileName: 'cupom_nao_fiscal_sale-1',
      html: '<html><body>Produto PDV</body></html>',
    });

    expect(mocks.writeFileMock).toHaveBeenCalledWith(
      'C:\\ERP\\cupom_nao_fiscal_sale-1.html',
      '<html><body>Produto PDV</body></html>',
      'utf-8',
    );
    expect(mocks.printToPDFMock).toHaveBeenCalledOnce();
    expect(mocks.writeFileMock).toHaveBeenCalledWith(
      'C:\\ERP\\cupom_nao_fiscal_sale-1.pdf',
      Buffer.from('pdf'),
    );
    expect(mocks.printMock).toHaveBeenCalledWith(
      expect.objectContaining({ silent: false, printBackground: true }),
      expect.any(Function),
    );
    expect(mocks.closeMock).toHaveBeenCalledOnce();
    expect(result).toEqual(expect.objectContaining({
      success: true,
      savedPath: 'C:\\ERP\\cupom_nao_fiscal_sale-1.pdf',
    }));
  });
});
