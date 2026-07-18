import { TelemetryQueue } from '../queue';
import { sanitize } from '../sanitizer';

export function createExpressMiddleware(queue: TelemetryQueue, ignoredRoutes: string[] = []) {
  return (req: any, res: any, next: Function) => {
    // Skip ignored routes
    if (ignoredRoutes.some(route => req.path.includes(route) || req.originalUrl.includes(route))) {
      return next();
    }

    const start = process.hrtime();

    // Hook into response finish
    res.on('finish', () => {
      const diff = process.hrtime(start);
      const durationMs = (diff[0] * 1e9 + diff[1]) / 1e6;
      const status = res.statusCode;

      // Extract sanitized headers, query, body
      const sanitizedHeaders = sanitize(req.headers || {});
      const sanitizedQuery = sanitize(req.query || {});
      const sanitizedBody = sanitize(req.body || {});

      queue.addEvent({
        name: 'http_request',
        payload: {
          method: req.method,
          url: req.originalUrl || req.url,
          status,
          durationMs,
          userAgent: req.get ? req.get('user-agent') : '',
          ip: req.ip || req.connection?.remoteAddress,
          headers: sanitizedHeaders,
          query: sanitizedQuery
        },
        timestamp: new Date().toISOString()
      });

      if (status >= 500) {
        queue.addEvent({
          name: 'http_error',
          payload: {
            method: req.method,
            url: req.originalUrl || req.url,
            status,
            body: sanitizedBody
          },
          timestamp: new Date().toISOString()
        });
      }
    });

    next();
  };
}
