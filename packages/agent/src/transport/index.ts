import { SentinelConfig, TelemetryPayload } from '../types';
import { RetryManager } from '../retry';
import { logger } from '../utils/logger';

export class Transport {
  private config: SentinelConfig;
  private retryManager: RetryManager;
  private offlineQueue: { endpoint: string, payload: any }[] = [];

  constructor(config: SentinelConfig) {
    this.config = config;
    this.retryManager = new RetryManager();
  }

  private async fetchWrapper(endpoint: string, payload: any): Promise<void> {
    const url = `${this.config.endpoint || 'http://localhost:8000/api/v1'}${endpoint}`;
    
    // Use dynamic import for Node 18+ native fetch or fallback
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.config.apiKey
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Sentinel API Error: ${res.status} ${res.statusText}`);
    }
  }

  async send(endpoint: string, payload: any) {
    try {
      await this.retryManager.execute(() => this.fetchWrapper(endpoint, payload));
    } catch (e) {
      logger.error(`Failed to send to ${endpoint}. Queueing for offline sync.`);
      // Limit offline queue to 100 items to prevent memory leak
      if (this.offlineQueue.length < 100) {
        this.offlineQueue.push({ endpoint, payload });
      }
    }
  }

  async flushOfflineQueue() {
    if (this.offlineQueue.length === 0) return;
    logger.info(`Attempting to flush ${this.offlineQueue.length} queued requests`);
    
    const queueToProcess = [...this.offlineQueue];
    this.offlineQueue = [];
    
    for (const item of queueToProcess) {
      await this.send(item.endpoint, item.payload);
    }
  }
}
