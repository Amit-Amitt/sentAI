import { Transport } from '../transport';
import { SentinelConfig, TelemetryPayload } from '../types';

export class TelemetryQueue {
  private config: SentinelConfig;
  private transport: Transport;
  private payload: TelemetryPayload;
  private timer: NodeJS.Timeout | null = null;
  private recordCount: number = 0;

  constructor(config: SentinelConfig, transport: Transport) {
    this.config = config;
    this.transport = transport;
    this.payload = {
      logs: [],
      metrics: [],
      events: [],
      heartbeats: []
    };
  }

  addLog(log: any) {
    this.payload.logs.push(log);
    this.incrementAndCheck();
  }

  addMetric(metric: any) {
    this.payload.metrics.push(metric);
    this.incrementAndCheck();
  }

  addEvent(event: any) {
    this.payload.events.push(event);
    this.incrementAndCheck();
  }

  addHeartbeat(heartbeat: any) {
    this.payload.heartbeats.push(heartbeat);
    this.incrementAndCheck();
  }

  private incrementAndCheck() {
    this.recordCount++;
    if (this.recordCount >= (this.config.batchSize || 100)) {
      this.flush();
    } else {
      this.scheduleFlush();
    }
  }

  private scheduleFlush() {
    if (!this.timer) {
      this.timer = setTimeout(() => {
        this.flush();
      }, this.config.flushIntervalMs || 5000);
    }
  }

  async flush() {
    if (this.recordCount === 0) return;

    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    const payloadToSend = { ...this.payload };
    this.payload = {
      logs: [],
      metrics: [],
      events: [],
      heartbeats: []
    };
    this.recordCount = 0;

    // Send to specific endpoints
    if (payloadToSend.logs.length > 0) {
      await this.transport.send('/telemetry/logs', { logs: payloadToSend.logs });
    }
    if (payloadToSend.metrics.length > 0) {
      await this.transport.send('/telemetry/metrics', { metrics: payloadToSend.metrics });
    }
    if (payloadToSend.events.length > 0) {
      await this.transport.send('/telemetry/events', { events: payloadToSend.events });
    }
    if (payloadToSend.heartbeats.length > 0) {
      await this.transport.send('/telemetry/heartbeat', payloadToSend.heartbeats[payloadToSend.heartbeats.length - 1]);
    }
    
    // Also try flushing offline queue
    await this.transport.flushOfflineQueue();
  }
}
