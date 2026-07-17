const RETRY_DELAYS = [5000, 15000, 45000, 120000];

export function getBackoffDelay(retryCount: number): number {
  const index = Math.min(retryCount, RETRY_DELAYS.length - 1);
  return RETRY_DELAYS[index];
}

export function shouldRetry(retryCount: number, maxRetries: number = 10): boolean {
  return retryCount < maxRetries;
}

export function resetBackoff(): void {
}
