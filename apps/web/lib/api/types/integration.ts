/** TypeScript types for Sentinel AI Integrations Marketplace. */

export type IntegrationStatus =
  | "available"
  | "connected"
  | "disconnected"
  | "error"
  | "syncing"
  | "disabled"
  | "coming_soon"
  | "beta";

export type SyncFrequency = "realtime" | "hourly" | "daily" | "weekly";

export type IntegrationCategory =
  | "Source Control"
  | "Communication"
  | "Incident Management"
  | "Monitoring"
  | "Logging"
  | "Cloud"
  | "Containers"
  | "Issue Tracking"
  | "General";

export interface IntegrationCredential {
  id: string;
  credential_type: string;
  key: string;
  value: string;
  expires_at: string | null;
}

export interface IntegrationWebhook {
  id: string;
  name: string;
  url: string;
  direction: "incoming" | "outgoing";
  secret: string | null;
  retry_strategy: Record<string, any>;
  status: "active" | "inactive" | "error";
  delivery_status: string | null;
  delivery_history: Array<{
    id: string;
    timestamp: string;
    response_code: number;
    status: string;
    payload_size_bytes: number;
  }>;
}

export interface IntegrationSync {
  id: string;
  status: "success" | "failed" | "running";
  started_at: string;
  completed_at: string | null;
  duration_ms: number;
  imported_resources: number;
  errors: Array<{ code: string; message: string }>;
  warnings: Array<{ code: string; message: string }>;
}

export interface IntegrationAudit {
  id: string;
  action: string;
  performed_by_name: string | null;
  details: Record<string, any>;
  ip_address: string | null;
  user_agent: string | null;
  timestamp: string;
}

export interface WorkspaceConnection {
  id: string;
  workspace_id: string;
  provider_id: string;
  status: IntegrationStatus;
  config: Record<string, any>;
  last_sync_at: string | null;
  error_message: string | null;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
  credentials: IntegrationCredential[];
  webhooks: IntegrationWebhook[];
}

export interface IntegrationProvider {
  id: string;
  name: string;
  key: string;
  category: IntegrationCategory;
  logo: string;
  description: string;
  overview: string;
  status: IntegrationStatus;
  is_oauth_supported: boolean;
  default_sync_frequency: SyncFrequency;
  created_at: string;
  updated_at: string;
  connection: WorkspaceConnection | null;
}

export interface IntegrationProviderListResponse {
  results: IntegrationProvider[];
  total: number;
}

export interface ConnectIntegrationPayload {
  provider_id: string;
  config: Record<string, any>;
  credentials: Record<string, string>;
}

export interface UpdateIntegrationPayload {
  config?: Record<string, any>;
  credentials?: Record<string, string>;
  is_enabled?: boolean;
}

export interface ConnectionTestResponse {
  success: boolean;
  status: string;
  message: string;
  latency_ms: number;
  details: Record<string, any>;
}

export interface SyncTriggerResponse {
  success: boolean;
  sync_id: string;
  status: string;
  message: string;
}

export interface IntegrationHistoryResponse {
  syncs: IntegrationSync[];
  audits: IntegrationAudit[];
}
