import { TelemetryQueue } from '../queue';
import { sanitize } from '../sanitizer';

export class ProcessCollector {
  private queue: TelemetryQueue;

  constructor(queue: TelemetryQueue) {
    this.queue = queue;
  }

  start() {
    if (typeof process === 'undefined') return;

    process.on('uncaughtException', (error: Error) => {
      this.queue.addEvent({
        name: 'uncaughtException',
        payload: sanitize({
          message: error.message,
          stack: error.stack,
          fatal: true
        }),
        timestamp: new Date().toISOString()
      });
      // Force flush on fatal error
      this.queue.flush().finally(() => {
        process.exit(1);
      });
    });

    process.on('unhandledRejection', (reason: any) => {
      this.queue.addEvent({
        name: 'unhandledRejection',
        payload: sanitize({
          reason: reason instanceof Error ? reason.message : String(reason),
          stack: reason instanceof Error ? reason.stack : undefined,
          fatal: true
        }),
        timestamp: new Date().toISOString()
      });
    });

    const handleSignal = (signal: string) => {
      this.queue.addEvent({
        name: 'process_signal',
        payload: { signal },
        timestamp: new Date().toISOString()
      });
      this.queue.flush().finally(() => {
        process.exit(0);
      });
    };

    process.on('SIGTERM', () => handleSignal('SIGTERM'));
    process.on('SIGINT', () => handleSignal('SIGINT'));
  }
}
