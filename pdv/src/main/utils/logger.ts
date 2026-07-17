import { getUserDataPath } from './env';
import * as fs from 'fs';
import { join } from 'path';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  meta?: unknown;
}

class Logger {
  private logFile: string;
  private stream: fs.WriteStream | null = null;

  constructor() {
    const logDir = join(getUserDataPath(), 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    this.logFile = join(logDir, `pdv-${new Date().toISOString().split('T')[0]}.log`);
    this.stream = fs.createWriteStream(this.logFile, { flags: 'a' });
  }

  private log(level: LogLevel, message: string, meta?: unknown) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      meta,
    };

    const line = JSON.stringify(entry) + '\n';
    
    if (this.stream) {
      this.stream.write(line);
    }

    // Also log to console in development
    if (process.env.NODE_ENV === 'development') {
      const colors = {
        debug: '\x1b[36m',
        info: '\x1b[32m',
        warn: '\x1b[33m',
        error: '\x1b[31m',
        reset: '\x1b[0m',
      };
      console.log(`${colors[level]}[${level.toUpperCase()}]\x1b[0m ${message}`, meta ?? '');
    }
  }

  debug(message: string, meta?: unknown) { this.log('debug', message, meta); }
  info(message: string, meta?: unknown) { this.log('info', message, meta); }
  warn(message: string, meta?: unknown) { this.log('warn', message, meta); }
  error(message: string, meta?: unknown) { this.log('error', message, meta); }
}

export const logger = new Logger();

export function setupLogger() {
  // Logger is initialized when imported
}