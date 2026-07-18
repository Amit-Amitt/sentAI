export interface ApiKeyPermission {
  id: string;
  api_key_id: string;
  scope: string;
  created_at?: string;
  updated_at?: string;
}

export interface ApiKey {
  id: string;
  name: string;
  description: string | null;
  prefix: string;
  environment: 'production' | 'development' | 'testing';
  expires_at: string | null;
  last_used_at: string | null;
  status: 'active' | 'expired' | 'revoked' | 'disabled';
  workspace_id: string;
  created_by_id: string | null;
  created_at: string;
  updated_at: string;
  scopes: string[];
}

export interface ApiKeyCreatePayload {
  name: string;
  environment: string;
  scopes: string[];
  description?: string | null;
  expires_at?: string | null;
}

export interface ApiKeyUpdatePayload {
  name?: string | null;
  description?: string | null;
  expires_at?: string | null;
  scopes?: string[] | null;
}

export interface ApiKeyCreatedResponse extends ApiKey {
  secret: string; // The raw secret key only returned once during creation/rotation
}

export interface ApiKeyActionResponse {
  success: boolean;
  message: string;
}

export interface ApiKeyUsage {
  id: string;
  api_key_id: string;
  endpoint: string;
  method: string;
  status_code: number;
  response_time_ms: number;
  ip_address: string | null;
  user_agent: string | null;
  timestamp: string;
}

export interface ApiKeyAudit {
  id: string;
  api_key_id: string;
  action: string;
  performed_by_id: string | null;
  ip_address: string | null;
  user_agent: string | null;
  details: Record<string, any> | null;
  timestamp: string;
  performed_by?: {
    id: string;
    email: string;
    first_name?: string;
    last_name?: string;
  } | null;
}

export interface ApiKeyUsageStats {
  requests_today: number;
  requests_this_month: number;
  successful_requests: number;
  failed_requests: number;
  top_endpoint: string | null;
  last_used_at: string | null;
  recent_usages: ApiKeyUsage[];
  audit_history: ApiKeyAudit[];
}

export interface ApiKeyAuditListResponse {
  results: ApiKeyAudit[];
  total: number;
}

export interface ApiKeysListResponse {
  results: ApiKey[];
  total: number;
  skip: number;
  limit: number;
}
