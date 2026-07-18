"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Calendar, Activity, Shield, ShieldCheck, Crown, Eye, Layers } from "lucide-react";
import type { Membership } from "@/lib/api/types";

interface MemberDetailsDrawerProps {
  member: Membership | null;
  onClose: () => void;
}

const roleConfig = {
  owner: { icon: Crown, color: "bg-amber-500/10 text-amber-400 border-amber-500/20", label: "Owner" },
  admin: { icon: ShieldCheck, color: "bg-blue-500/10 text-blue-400 border-blue-500/20", label: "Admin" },
  engineer: { icon: Shield, color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20", label: "Engineer" },
  viewer: { icon: Eye, color: "bg-zinc-800 text-zinc-400 border-zinc-700", label: "Viewer" },
} as const;

export function MemberDetailsDrawer({ member, onClose }: MemberDetailsDrawerProps) {
  if (!member) return null;

  const role = roleConfig[member.role] || roleConfig.viewer;
  const RoleIcon = role.icon;
  const joinedDate = member.created_at
    ? new Date(member.created_at).toLocaleDateString("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
      })
    : "—";

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-hidden">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.4 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        />

        {/* Sliding Panel */}
        <div className="absolute inset-y-0 right-0 flex max-w-full pl-10">
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="w-screen max-w-md border-l border-border/80 bg-zinc-950/95 backdrop-blur-xl p-6 shadow-2xl flex flex-col h-full text-foreground"
          >
            {/* Header */}
            <div className="flex items-center justify-between pb-5 border-b border-border/40">
              <h2 className="text-sm font-semibold">Member Profile</h2>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted/30 hover:text-foreground transition"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Profile Info */}
            <div className="flex flex-col items-center text-center py-6 border-b border-border/30">
              <div className="h-16 w-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-lg font-bold text-primary mb-3">
                {member.user?.full_name?.charAt(0).toUpperCase() || "?"}
              </div>
              <h3 className="text-sm font-bold">{member.user?.full_name || "Unknown"}</h3>
              <p className="text-xs text-muted-foreground mt-0.5">{member.user?.email || "—"}</p>

              <div className={`mt-3 inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-semibold ${role.color}`}>
                <RoleIcon className="h-3.5 w-3.5" />
                {role.label}
              </div>
            </div>

            {/* Content Details */}
            <div className="flex-1 overflow-y-auto py-6 space-y-6">
              {/* Meta information */}
              <div className="space-y-4">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Details</h4>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="rounded-xl bg-zinc-900/40 border border-border/20 p-3">
                    <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>Joined On</span>
                    </div>
                    <span className="font-medium">{joinedDate}</span>
                  </div>
                  <div className="rounded-xl bg-zinc-900/40 border border-border/20 p-3">
                    <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                      <Activity className="h-3.5 w-3.5" />
                      <span>Status</span>
                    </div>
                    <span className="inline-flex items-center gap-1.5 font-medium">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      Active
                    </span>
                  </div>
                </div>
              </div>

              {/* Workspaces Scopes */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="h-3.5 w-3.5" /> Workspaces ({member.workspaces?.length || 0})
                </h4>
                <div className="space-y-2">
                  {member.workspaces && member.workspaces.length > 0 ? (
                    member.workspaces.map((ws) => (
                      <div
                        key={ws.id}
                        className="flex items-center justify-between rounded-xl border border-border/40 bg-zinc-900/20 px-3.5 py-2.5"
                      >
                        <div className="min-w-0">
                          <p className="text-xs font-semibold truncate">{ws.name}</p>
                          <p className="text-[10px] text-muted-foreground truncate">/{ws.slug}</p>
                        </div>
                        <span className={`rounded-md border px-1.5 py-0.5 text-[9px] font-semibold capitalize ${
                          ws.environment === "production"
                            ? "bg-red-500/10 text-red-400 border-red-500/20"
                            : ws.environment === "staging"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                        }`}>
                          {ws.environment}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-4 border border-dashed border-border/40 rounded-xl">
                      <p className="text-[11px] text-muted-foreground">No explicit workspaces assigned.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </AnimatePresence>
  );
}
