"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { History, Loader2, ChevronLeft, ChevronRight, User, AlertCircle } from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useActivities } from "@/lib/api/hooks";

export default function ActivityLogPage() {
  const { activeOrganization } = useOrgStore();
  const orgId = activeOrganization?.id || null;

  const [page, setPage] = useState(1);
  const limit = 10;
  const offset = (page - 1) * limit;

  const { data, isLoading } = useActivities(orgId, limit, offset);

  if (!activeOrganization) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-muted-foreground">No organization selected.</p>
      </div>
    );
  }

  const formatActivityText = (act: any) => {
    const actor = act.user?.full_name || "System";
    const details = act.details || {};

    switch (act.action) {
      case "member_added":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> added{" "}
            <span className="font-semibold text-foreground">{details.target_email || "user"}</span> as{" "}
            <span className="capitalize">{details.role || "member"}</span>.
          </>
        );
      case "member_invited":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> invited{" "}
            <span className="font-semibold text-foreground">{details.email}</span> to join the team.
          </>
        );
      case "role_changed":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> updated member role to{" "}
            <span className="capitalize font-semibold text-primary">{details.new_role}</span>.
          </>
        );
      case "member_removed":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> removed{" "}
            <span className="font-semibold text-foreground">{details.target_email || "member"}</span>.
          </>
        );
      case "ownership_transferred":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> transferred organization ownership to{" "}
            <span className="font-semibold text-amber-400">{details.new_owner_email}</span>.
          </>
        );
      case "invitation_accepted":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> accepted the invitation to join.
          </>
        );
      case "invitation_rejected":
        return (
          <>
            <span className="font-semibold text-foreground">{details.email || "Invited user"}</span> rejected the invitation.
          </>
        );
      case "invitation_cancelled":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> cancelled the invitation for{" "}
            <span className="font-semibold text-foreground">{details.email}</span>.
          </>
        );
      case "invitation_resent":
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> resent/renewed the invitation for{" "}
            <span className="font-semibold text-foreground">{details.email}</span>.
          </>
        );
      default:
        return (
          <>
            <span className="font-semibold text-foreground">{actor}</span> performed action:{" "}
            <span className="font-mono">{act.action}</span>.
          </>
        );
    }
  };

  const totalPages = Math.ceil((data?.total || 0) / limit);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-4xl text-foreground"
    >
      <div>
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <History className="h-4 w-4 text-primary" /> Security & Audit Log
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Real-time record of all team membership changes, role promotions, and configuration accesses.
        </p>
      </div>

      <div className="rounded-2xl border border-border/60 bg-card/50 overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : data && data.results.length > 0 ? (
          <div className="divide-y divide-border/30">
            {data.results.map((act) => (
              <div key={act.id} className="flex items-start gap-4 px-5 py-4 hover:bg-muted/5 transition">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-muted/40 border border-border/40 text-muted-foreground">
                  <User className="h-3.5 w-3.5" />
                </div>
                <div className="flex-1 space-y-1 min-w-0">
                  <p className="text-xs text-muted-foreground leading-normal">
                    {formatActivityText(act)}
                  </p>
                  <p className="text-[10px] text-muted-foreground/60">
                    {act.created_at ? new Date(act.created_at).toLocaleString() : "—"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-2">
            <AlertCircle className="h-8 w-8 text-muted-foreground/45" />
            <p className="text-xs text-muted-foreground">No audit activities recorded yet.</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-muted-foreground pt-2">
          <span>
            Showing {offset + 1} to {Math.min(offset + limit, data?.total || 0)} of {data?.total || 0} logs
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-border hover:bg-muted/20 disabled:opacity-50"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-border hover:bg-muted/20 disabled:opacity-50"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
