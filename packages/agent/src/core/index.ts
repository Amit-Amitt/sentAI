import { SentinelConfig } from '../types';
import { TelemetryQueue } from '../queue';
import { Transport } from '../transport';
import { Heartbeat } from '../heartbeat';
import { ProcessCollector } from '../collectors/process';
import { createExpressMiddleware } from '../middleware/express';
import { sanitize } from '../sanitizer';
import { logger } from '../utils/logger';

export class SentinelClient {
  private config: SentinelConfig;
  private transport: Transport;
  private queue: TelemetryQueue;
  private heartbeat: Heartbeat;
  private processCollector: ProcessCollector;

  constructor(config: SentinelConfig) {
    if (!config.apiKey) {
      throw new Error('Sentinel AI: apiKey is required');
    }
    
    this.config = {
      endpoint: 'https://api.sentinel-ai.com/api/v1',
      samplingRate: 1.0,
      flushIntervalMs: 5000,
      batchSize: 100,
      environment: process.env.NODE_ENV || 'production',
      ...config
    };

    this.transport = new Transport(this.config);
    this.queue = new TelemetryQueue(this.config, this.transport);
    
    // Initialize components
    this.heartbeat = new Heartbeat(this.config, this.queue);
    this.processCollector = new ProcessCollector(this.queue);

    this.start();
  }

  private start() {
    this.heartbeat.start();
    this.processCollector.start();
    logger.info(`Sentinel AI initialized for service: ${this.config.serviceName}`);
  }

  captureException(error: Error | unknown, tags?: Record<string, string>) {
    this.queue.addEvent({
      name: 'exception',
      payload: sanitize({
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        tags: { ...this.config.customTags, ...tags }
      }),
      timestamp: new Date().toISOString()
    });
  }

  captureLog(level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL', message: string, metadata?: Record<string, any>) {
    this.queue.addLog({
      level,
      message,
      metadata: sanitize(metadata),
      timestamp: new Date().toISOString()
    });
  }

  captureMetric(name: string, value: number, tags?: Record<string, string>) {
    this.queue.addMetric({
      name,
      value,
      tags: { ...this.config.customTags, ...tags },
      timestamp: new Date().toISOString()
    });
  }

  captureEvent(name: string, payload: Record<string, any>) {
    this.queue.addEvent({
      name,
      payload: sanitize(payload),
      timestamp: new Date().toISOString()
    });
  }

  setUser(id: string) {
    if (!this.config.customTags) {
      this.config.customTags = {};
    }
    this.config.customTags.userId = id;
  }

  setTag(key: string, value: string) {
    if (!this.config.customTags) {
      this.config.customTags = {};
    }
    this.config.customTags[key] = value;
  }

  async flush() {
    await this.queue.flush();
  }

  requestHandler() {
    return createExpressMiddleware(this.queue, this.config.ignoredRoutes || []);
  }
}

// Singleton export
let defaultInstance: SentinelClient | null = null;

export const Sentinel = {
  init(config: SentinelConfig) {
    if (!defaultInstance) {
      defaultInstance = new SentinelClient(config);
    }
    return defaultInstance;
  },
  
  captureException(error: Error | unknown, tags?: Record<string, string>) {
    defaultInstance?.captureException(error, tags);
  },

  captureLog(level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL', message: string, metadata?: Record<string, any>) {
    defaultInstance?.captureLog(level, message, metadata);
  },

  captureMetric(name: string, value: number, tags?: Record<string, string>) {
    defaultInstance?.captureMetric(name, value, tags);
  },

  captureEvent(name: string, payload: Record<string, any>) {
    defaultInstance?.captureEvent(name, payload);
  },

  setUser(id: string) {
    defaultInstance?.setUser(id);
  },

  setTag(key: string, value: string) {
    defaultInstance?.setTag(key, value);
  },

  async flush() {
    await defaultInstance?.flush();
  },

  requestHandler() {
    if (!defaultInstance) {
      throw new Error('Sentinel AI must be initialized before using requestHandler');
    }
    return defaultInstance.requestHandler();
  }
};
