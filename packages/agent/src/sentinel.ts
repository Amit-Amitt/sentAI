export interface SentinelConfig {
    apiKey: string;
    projectId?: string;
    environment?: string;
    serviceName?: string;
    apiBase?: string;
}

export class Sentinel {
    private static config: SentinelConfig;
    private static queue: any[] = [];
    private static flushTimer: any = null;

    static init(config: SentinelConfig) {
        this.config = {
            apiBase: 'http://localhost:8000',
            ...config
        };
        this.setupHooks();
        console.log(`[Sentinel AI] Initialized for service: ${config.serviceName || 'unknown'}`);
    }

    private static setupHooks() {
        if (typeof process !== 'undefined') {
            process.on('uncaughtException', (error: Error) => {
                this.captureException(error, true);
            });
            process.on('unhandledRejection', (reason: any) => {
                this.captureException(reason instanceof Error ? reason : new Error(String(reason)), true);
            });
        }
    }

    static captureException(error: Error, fatal: boolean = false) {
        this.queue.push({
            event_type: 'EXCEPTION',
            timestamp: new Date().toISOString(),
            data: {
                message: error.message,
                stack: error.stack,
                fatal
            }
        });
        this.scheduleFlush();
    }

    static captureMetric(name: string, value: number, tags: Record<string, string> = {}) {
        this.queue.push({
            event_type: 'METRIC',
            timestamp: new Date().toISOString(),
            data: {
                name,
                value,
                tags
            }
        });
        this.scheduleFlush();
    }

    static requestHandler() {
        return (req: any, res: any, next: Function) => {
            const start = Date.now();
            res.on('finish', () => {
                const duration = Date.now() - start;
                const status = res.statusCode;
                
                this.queue.push({
                    event_type: 'REQUEST',
                    timestamp: new Date().toISOString(),
                    data: {
                        method: req.method,
                        url: req.url,
                        status,
                        duration
                    }
                });

                if (status >= 500) {
                    this.queue.push({
                        event_type: 'ERROR',
                        timestamp: new Date().toISOString(),
                        data: {
                            message: `HTTP ${status} on ${req.method} ${req.url}`,
                            status
                        }
                    });
                }
                
                this.scheduleFlush();
            });
            next();
        };
    }

    private static scheduleFlush() {
        if (!this.flushTimer) {
            this.flushTimer = setTimeout(() => this.flush(), 2000); // batch flush every 2s
        }
    }

    private static async flush() {
        if (this.queue.length === 0 || !this.config) return;

        const events = [...this.queue];
        this.queue = [];
        this.flushTimer = null;

        try {
            await fetch(`${this.config.apiBase}/api/v1/telemetry/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.config.apiKey
                },
                body: JSON.stringify({ events })
            });
        } catch (e) {
            console.error('[Sentinel AI] Failed to flush telemetry batch', e);
            // In a real app we'd retry or persist locally.
        }
    }
}
