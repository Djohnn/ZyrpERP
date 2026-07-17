import { app } from 'electron';

export function isDev(): boolean {
  return !app.isPackaged;
}

export function getAppPath(): string {
  return app.getAppPath();
}

export function getUserDataPath(): string {
  return app.getPath('userData');
}