// ── Multi-Tenant Organization & Workspace Types ──────────────

export type MemberRole = "owner" | "admin" | "engineer" | "viewer";
export type InvitationStatus = "pending" | "accepted" | "expired" | "revoked" | "cancelled" | "rejected";
export type WorkspaceEnvironment = "development" | "staging" | "production";

export interface UserInfo {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  is_active: boolean;
}

// ── Organization ─────────────────────────────────────────────

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
  industry?: string | null;
  region?: string | null;
  timezone?: string | null;
  owner_id: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface OrganizationListResponse {
  results: Organization[];
  total: number;
}

export interface CreateOrganizationRequest {
  name: string;
  slug: string;
  industry?: string;
  region?: string;
  timezone?: string;
}

export interface UpdateOrganizationRequest {
  name?: string;
  logo_url?: string;
  industry?: string;
  region?: string;
  timezone?: string;
}

// ── Workspace ────────────────────────────────────────────────

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  environment: WorkspaceEnvironment;
  description?: string | null;
  ai_config: Record<string, any>;
  incident_retention_days: number;
  organization_id: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface WorkspaceListResponse {
  results: Workspace[];
  total: number;
}

export interface CreateWorkspaceRequest {
  name: string;
  slug: string;
  environment?: WorkspaceEnvironment;
  description?: string;
}

export interface UpdateWorkspaceRequest {
  name?: string;
  description?: string;
  environment?: WorkspaceEnvironment;
  ai_config?: Record<string, any>;
  incident_retention_days?: number;
}

// ── Membership ───────────────────────────────────────────────

export interface Membership {
  id: string;
  user_id: string;
  organization_id: string;
  workspace_id?: string | null;
  role: MemberRole;
  user?: UserInfo | null;
  created_at?: string | null;
  workspaces?: Workspace[];
}

export interface MembershipListResponse {
  results: Membership[];
  total: number;
}

export interface AddMemberRequest {
  email: string;
  role?: MemberRole;
}

export interface UpdateMemberRoleRequest {
  role: MemberRole;
}

// ── Invitation ───────────────────────────────────────────────

export interface Invitation {
  id: string;
  email: string;
  role: MemberRole;
  status: InvitationStatus;
  organization_id: string;
  invited_by: string;
  token: string;
  expires_at?: string | null;
  created_at?: string | null;
  workspaces?: string[];
}

export interface InvitationListResponse {
  results: Invitation[];
  total: number;
}

export interface CreateInvitationRequest {
  email: string;
  role?: MemberRole;
  workspaces?: string[];
}

// ── Activity Log ─────────────────────────────────────────────

export interface MemberActivity {
  id: string;
  organization_id: string;
  user_id?: string | null;
  action: string;
  details: Record<string, any>;
  created_at?: string | null;
  user?: UserInfo | null;
}

export interface MemberActivityListResponse {
  results: MemberActivity[];
  total: number;
}
