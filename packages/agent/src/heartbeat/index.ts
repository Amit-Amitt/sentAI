import { TelemetryQueue } from '../queue';
import { SentinelConfig } from '../types';
import { getSystemStats } from '../utils/system';

export class Heartbeat {
  private queue: TelemetryQueue;
  private config: SentinelConfig;
  private timer: NodeJS.Timeout | null = null;

  constructor(config: SentinelConfig, queue: TelemetryQueue) {
    this.config = config;
    this.queue = queue;
  }

  start() {
    if (this.timer) return;
    
    this.timer = setInterval(() => {
      const stats = getSystemStats();
      this.queue.addHeartbeat({
        environment: this.config.environment || 'production',
        version: this.config.release || 'unknown',
        cpu: stats.cpuPercent,
        memory: stats.memoryPercent,
        health: 'healthy',
        timestamp: new Date().toISOString()
      });
    }, 30000); // 30 seconds
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}
