export const logger = {
  debug: (...args: any[]) => {
    if (process.env.SENTINEL_DEBUG === 'true') {
      console.log('[Sentinel AI Debug]', ...args);
    }
  },
  info: (...args: any[]) => {
    console.log('[Sentinel AI]', ...args);
  },
  warn: (...args: any[]) => {
    console.warn('[Sentinel AI Warning]', ...args);
  },
  error: (...args: any[]) => {
    console.error('[Sentinel AI Error]', ...args);
  }
};
