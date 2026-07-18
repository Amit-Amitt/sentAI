"use client";

import { create } from "zustand";
import type { Organization, Workspace } from "../api/types";

interface OrgState {
  // Active selections
  activeOrganization: Organization | null;
  activeWorkspace: Workspace | null;

  // Cached lists
  organizations: Organization[];
  workspaces: Workspace[];

  // Loading state
  isHydrated: boolean;

  // Actions
  setActiveOrganization: (org: Organization | null) => void;
  setActiveWorkspace: (ws: Workspace | null) => void;
  setOrganizations: (orgs: Organization[]) => void;
  setWorkspaces: (workspaces: Workspace[]) => void;
  setHydrated: (hydrated: boolean) => void;
  reset: () => void;
}

const STORAGE_KEY_ORG = "sentinel_active_org_id";
const STORAGE_KEY_WS = "sentinel_active_ws_id";

export const useOrgStore = create<OrgState>((set) => ({
  activeOrganization: null,
  activeWorkspace: null,
  organizations: [],
  workspaces: [],
  isHydrated: false,

  setActiveOrganization: (org) => {
    if (org) {
      try {
        localStorage.setItem(STORAGE_KEY_ORG, org.id);
      } catch {}
    } else {
      try {
        localStorage.removeItem(STORAGE_KEY_ORG);
      } catch {}
    }
    set({ activeOrganization: org, activeWorkspace: null, workspaces: [] });
  },

  setActiveWorkspace: (ws) => {
    if (ws) {
      try {
        localStorage.setItem(STORAGE_KEY_WS, ws.id);
      } catch {}
    } else {
      try {
        localStorage.removeItem(STORAGE_KEY_WS);
      } catch {}
    }
    set({ activeWorkspace: ws });
  },

  setOrganizations: (orgs) => set({ organizations: orgs }),
  setWorkspaces: (workspaces) => set({ workspaces }),
  setHydrated: (hydrated) => set({ isHydrated: hydrated }),

  reset: () => {
    try {
      localStorage.removeItem(STORAGE_KEY_ORG);
      localStorage.removeItem(STORAGE_KEY_WS);
    } catch {}
    set({
      activeOrganization: null,
      activeWorkspace: null,
      organizations: [],
      workspaces: [],
      isHydrated: false,
    });
  },
}));

/**
 * Helper to read persisted IDs from localStorage (called during hydration).
 */
export function getPersistedOrgId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY_ORG);
  } catch {
    return null;
  }
}

export function getPersistedWorkspaceId(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY_WS);
  } catch {
    return null;
  }
}
