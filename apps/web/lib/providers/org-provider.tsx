"use client";

import { useEffect } from "react";
import { organizationsService } from "../api/services/organizations";
import { workspacesService } from "../api/services/workspaces";
import {
  useOrgStore,
  getPersistedOrgId,
  getPersistedWorkspaceId,
} from "../store/org-store";

/**
 * OrgProvider hydrates the organization/workspace context on mount.
 * Reads persisted selections from localStorage and fetches fresh data from the API.
 */
export function OrgProvider({ children }: { children: React.ReactNode }) {
  const {
    setOrganizations,
    setActiveOrganization,
    setWorkspaces,
    setActiveWorkspace,
    setHydrated,
    isHydrated,
  } = useOrgStore();

  useEffect(() => {
    if (isHydrated) return;

    async function hydrate() {
      try {
        const { results: orgs } =
          await organizationsService.listOrganizations();
        setOrganizations(orgs);

        if (orgs.length === 0) {
          setHydrated(true);
          return;
        }

        // Restore persisted org or default to first
        const persistedOrgId = getPersistedOrgId();
        const activeOrg =
          orgs.find((o) => o.id === persistedOrgId) || orgs[0];
        setActiveOrganization(activeOrg ?? null);

        if (activeOrg) {
          // Load workspaces for active org
          const { results: workspaces } =
            await workspacesService.listWorkspaces(activeOrg.id);
          setWorkspaces(workspaces);

          // Restore persisted workspace or default to first
          const persistedWsId = getPersistedWorkspaceId();
          const activeWs =
            workspaces.find((w) => w.id === persistedWsId) || workspaces[0];
          setActiveWorkspace(activeWs ?? null);
        }
      } catch (err) {
        console.error("Failed to hydrate org context:", err);
      } finally {
        setHydrated(true);
      }
    }

    hydrate();
  }, [
    isHydrated,
    setOrganizations,
    setActiveOrganization,
    setWorkspaces,
    setActiveWorkspace,
    setHydrated,
  ]);

  return <>{children}</>;
}
