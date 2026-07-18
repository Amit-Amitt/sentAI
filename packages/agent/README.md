# @sentinel-ai/agent

The official Node.js Monitoring SDK for Sentinel AI. Connect your applications to the Sentinel AI Observability platform to get autonomous incident detection, root cause analysis, and remediation.

## Installation

```bash
npm install @sentinel-ai/agent
# or
yarn add @sentinel-ai/agent
# or
pnpm add @sentinel-ai/agent
```

## Quick Start (Express)

Initialize the SDK as early as possible in your application lifecycle.

```typescript
import express from 'express';
import { Sentinel } from '@sentinel-ai/agent';

// 1. Initialize Sentinel
Sentinel.init({
  apiKey: process.env.SENTINEL_API_KEY,
  projectId: process.env.SENTINEL_PROJECT_ID,
  serviceName: 'my-express-api',
  environment: 'production',
  release: '1.0.0'
});

const app = express();

// 2. Add the middleware (must be before your routes)
app.use(Sentinel.requestHandler());

app.get('/', (req, res) => {
  res.send('Hello World');
});

app.listen(3000);
```

## Features

- **Automatic Telemetry**: Hooks into Node.js `uncaughtException`, `unhandledRejection`, and process signals automatically.
- **Express Middleware**: Tracks all incoming HTTP requests, latencies, and 500 errors.
- **Heartbeat**: Sends periodic system health and CPU/Memory usage back to the Sentinel AI Command Center.
- **Smart Batching & Retries**: Asynchronously queues data and flushes them efficiently without blocking your main event loop. Includes exponential backoff for offline resilience.
- **Data Sanitization**: Automatically scrubs passwords, JWTs, API keys, and sensitive fields before telemetry leaves your server.

## Custom API

You can capture custom events, metrics, and logs anywhere in your application.

```typescript
// Capture an exception manually
try {
  doSomethingDangerous();
} catch (error) {
  Sentinel.captureException(error, { customContext: 'value' });
}

// Capture a custom business metric
Sentinel.captureMetric('checkout_completed', 1, { currency: 'USD' });

// Send a custom log
Sentinel.captureLog('INFO', 'User completed onboarding', { userId: 123 });

// Tag a user session
Sentinel.setUser('user_98765');
```

## Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `apiKey` | `string` | **Required** | Your project's Sentinel API Key. |
| `serviceName` | `string` | **Required** | The name of this application/service. |
| `endpoint` | `string` | `https://api.sentinel-ai.com/api/v1` | The Sentinel AI ingest endpoint. |
| `environment` | `string` | `production` | Deployment environment (e.g. `staging`, `production`). |
| `release` | `string` | `undefined` | The version or commit hash of your app. |
| `ignoredRoutes` | `string[]` | `[]` | Routes to ignore in the Express middleware. |
| `batchSize` | `number` | `100` | Number of events to batch before flushing. |
| `flushIntervalMs` | `number` | `5000` | How often to flush the queue (in milliseconds). |

## License

MIT
