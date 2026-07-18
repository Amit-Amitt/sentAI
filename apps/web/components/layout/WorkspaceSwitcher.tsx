"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Building2,
  Check,
  ChevronDown,
  FolderKanban,
  Plus,
  Search,
} from "lucide-react";

import { useOrgStore } from "@/lib/store/org-store";
import { workspacesService } from "@/lib/api/services/workspaces";
import type { Organization, Workspace } from "@/lib/api/types";

export function WorkspaceSwitcher() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const {
    activeOrganization,
    activeWorkspace,
    organizations,
    workspaces,
    setActiveOrganization,
    setActiveWorkspace,
    setWorkspaces,
  } = useOrgStore();

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setSearch("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Focus search on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => searchRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleSelectOrg = async (org: Organization) => {
    setActiveOrganization(org);
    // Load workspaces for selected org
    try {
      const { results } = await workspacesService.listWorkspaces(org.id);
      setWorkspaces(results);
      if (results.length > 0) {
        setActiveWorkspace(results[0] ?? null);
      }
    } catch (err) {
      console.error("Failed to load workspaces:", err);
    }
    setIsOpen(false);
    setSearch("");
  };

  const handleSelectWorkspace = (ws: Workspace) => {
    setActiveWorkspace(ws);
    setIsOpen(false);
    setSearch("");
  };

  // Filter organizations and workspaces by search
  const filteredOrgs = organizations.filter((o) =>
    o.name.toLowerCase().includes(search.toLowerCase())
  );
  const filteredWorkspaces = workspaces.filter((w) =>
    w.name.toLowerCase().includes(search.toLowerCase())
  );

  // Generate initials for avatar
  const orgInitial = activeOrganization?.name?.charAt(0)?.toUpperCase() || "S";

  return (
    <div ref={dropdownRef} className="relative">
      {/* Trigger Button */}
      <button
        id="workspace-switcher-trigger"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-3 rounded-xl border border-border/60 bg-muted/20 px-3 py-2.5 text-left transition hover:bg-muted/40 hover:border-border/80 group"
      >
        {/* Org Avatar */}
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 border border-primary/20 text-sm font-bold text-primary">
          {orgInitial}
        </div>
        {/* Text */}
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-foreground truncate">
            {activeOrganization?.name || "Select Organization"}
          </p>
          <p className="text-[10px] text-muted-foreground truncate">
            {activeWorkspace?.name || "No workspace"}
            {activeWorkspace?.environment && (
              <span className="ml-1 opacity-60">
                · {activeWorkspace.environment}
              </span>
            )}
          </p>
        </div>
        {/* Chevron */}
        <ChevronDown
          className={`h-3.5 w-3.5 text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="absolute left-0 right-0 top-full z-50 mt-2 rounded-xl border border-border/80 bg-zinc-950/95 backdrop-blur-xl shadow-2xl overflow-hidden"
          >
            {/* Search */}
            <div className="border-b border-border/50 p-2">
              <div className="flex items-center gap-2 rounded-lg bg-muted/30 px-2.5 py-1.5">
                <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <input
                  ref={searchRef}
                  id="workspace-switcher-search"
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search..."
                  className="flex-1 bg-transparent text-xs text-foreground outline-none placeholder:text-muted-foreground/50"
                />
              </div>
            </div>

            {/* Scrollable Content */}
            <div className="max-h-72 overflow-y-auto p-1.5">
              {/* Organizations Section */}
              <div className="mb-1">
                <p className="px-2 py-1.5 text-[9px] font-bold uppercase tracking-wider text-muted-foreground/60">
                  Organizations
                </p>
                {filteredOrgs.length === 0 ? (
                  <p className="px-2 py-3 text-center text-[11px] text-muted-foreground/50">
                    No organizations found
                  </p>
                ) : (
                  filteredOrgs.map((org) => (
                    <button
                      key={org.id}
                      onClick={() => handleSelectOrg(org)}
                      className={`flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition ${
                        activeOrganization?.id === org.id
                          ? "bg-primary/10 text-foreground"
                          : "text-muted-foreground hover:bg-muted/30 hover:text-foreground"
                      }`}
                    >
                      <Building2 className="h-3.5 w-3.5 shrink-0" />
                      <span className="flex-1 text-xs font-medium truncate">
                        {org.name}
                      </span>
                      {activeOrganization?.id === org.id && (
                        <Check className="h-3.5 w-3.5 text-primary shrink-0" />
                      )}
                    </button>
                  ))
                )}
              </div>

              {/* Workspaces Section (for active org) */}
              {activeOrganization && (
                <div className="mb-1 border-t border-border/30 pt-1">
                  <p className="px-2 py-1.5 text-[9px] font-bold uppercase tracking-wider text-muted-foreground/60">
                    Workspaces
                  </p>
                  {filteredWorkspaces.length === 0 ? (
                    <p className="px-2 py-3 text-center text-[11px] text-muted-foreground/50">
                      No workspaces found
                    </p>
                  ) : (
                    filteredWorkspaces.map((ws) => (
                      <button
                        key={ws.id}
                        onClick={() => handleSelectWorkspace(ws)}
                        className={`flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition ${
                          activeWorkspace?.id === ws.id
                            ? "bg-primary/10 text-foreground"
                            : "text-muted-foreground hover:bg-muted/30 hover:text-foreground"
                        }`}
                      >
                        <FolderKanban className="h-3.5 w-3.5 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="text-xs font-medium truncate block">
                            {ws.name}
                          </span>
                          <span className="text-[10px] text-muted-foreground/60">
                            {ws.environment}
                          </span>
                        </div>
                        {activeWorkspace?.id === ws.id && (
                          <Check className="h-3.5 w-3.5 text-primary shrink-0" />
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Actions Footer */}
            <div className="border-t border-border/50 p-1.5 space-y-0.5">
              <button
                onClick={() => {
                  setIsOpen(false);
                  router.push("/onboarding");
                }}
                className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left text-xs font-medium text-muted-foreground transition hover:bg-muted/30 hover:text-foreground"
              >
                <Plus className="h-3.5 w-3.5" />
                Create Organization
              </button>
              {activeOrganization && (
                <button
                  onClick={() => {
                    setIsOpen(false);
                    router.push("/settings/organization");
                  }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left text-xs font-medium text-muted-foreground transition hover:bg-muted/30 hover:text-foreground"
                >
                  <Building2 className="h-3.5 w-3.5" />
                  Organization Settings
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
