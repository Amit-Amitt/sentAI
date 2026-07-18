export interface SentinelConfig {
  apiKey: string;
  endpoint?: string;
  projectId?: string;
  serviceName: string;
  environment?: string;
  release?: string;
  samplingRate?: number;
  ignoredRoutes?: string[];
  ignoredErrors?: string[];
  flushIntervalMs?: number;
  batchSize?: number;
  customTags?: Record<string, string>;
}

export type EventType = "LOG" | "METRIC" | "EVENT" | "EXCEPTION" | "REQUEST" | "HEARTBEAT";

export interface LogPayload {
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "FATAL";
  message: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface MetricPayload {
  name: string;
  value: number;
  tags?: Record<string, string>;
  timestamp: string;
}

export interface EventPayload {
  name: string;
  payload: Record<string, any>;
  timestamp: string;
}

export interface HeartbeatPayload {
  environment: string;
  version: string;
  cpu: number;
  memory: number;
  health: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
}

export interface TelemetryPayload {
  logs: LogPayload[];
  metrics: MetricPayload[];
  events: EventPayload[];
  heartbeats: HeartbeatPayload[];
}
