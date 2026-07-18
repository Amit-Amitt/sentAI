"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mail, Check, X, Loader2, Building, Layers } from "lucide-react";
import { useInvitation, useAcceptInvitation, useRejectInvitation } from "@/lib/api/hooks";

interface PageProps {
  params: Promise<{ token: string }>;
}

export default function InvitationAcceptancePage({ params }: PageProps) {
  const router = useRouter();
  const { token } = use(params);

  const { data: invitation, isLoading, error } = useInvitation(token);
  const acceptInvitation = useAcceptInvitation();
  const rejectInvitation = useRejectInvitation();

  const [status, setStatus] = useState<"idle" | "accepting" | "rejecting" | "success" | "rejected">("idle");

  const handleAccept = async () => {
    setStatus("accepting");
    try {
      await acceptInvitation.mutateAsync(token);
      setStatus("success");
      setTimeout(() => {
        router.push("/settings/organization/members");
      }, 1500);
    } catch (e) {
      setStatus("idle");
    }
  };

  const handleReject = async () => {
    setStatus("rejecting");
    try {
      await rejectInvitation.mutateAsync(token);
      setStatus("rejected");
      setTimeout(() => {
        router.push("/");
      }, 1500);
    } catch (e) {
      setStatus("idle");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center text-foreground">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
        <p className="text-xs text-muted-foreground">Retrieving invitation details...</p>
      </div>
    );
  }

  if (error || !invitation) {
    return (
      <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center p-4 text-foreground">
        <div className="w-full max-w-sm border border-red-500/20 bg-red-500/5 rounded-2xl p-6 text-center space-y-3">
          <X className="h-8 w-8 text-red-500 mx-auto" />
          <h3 className="text-sm font-semibold">Invalid or Expired Invitation</h3>
          <p className="text-xs text-muted-foreground">
            This invitation link is invalid, expired, or has already been used. Please contact the administrator.
          </p>
          <button
            onClick={() => router.push("/")}
            className="w-full rounded-xl bg-zinc-900 border border-border/80 py-2 text-xs font-semibold hover:bg-zinc-800"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4 text-foreground">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md border border-border/80 bg-zinc-900/40 backdrop-blur-xl p-6 rounded-2xl shadow-2xl space-y-6 text-center"
      >
        <div className="h-12 w-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto text-primary">
          <Building className="h-6 w-6" />
        </div>

        <div className="space-y-2">
          <h2 className="text-base font-bold">You've been invited!</h2>
          <p className="text-xs text-muted-foreground px-4">
            You've been invited to join the organization as an{" "}
            <strong className="text-primary capitalize">{invitation.role}</strong>.
          </p>
        </div>

        {/* Workspaces included */}
        {invitation.workspaces && invitation.workspaces.length > 0 && (
          <div className="rounded-xl border border-border bg-zinc-900/30 p-3.5 text-left space-y-2.5">
            <h4 className="text-[11px] font-bold text-muted-foreground uppercase flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5" /> Scoped Workspaces ({invitation.workspaces.length})
            </h4>
            <div className="text-xs font-medium space-y-1">
              {invitation.workspaces.map((wsId) => (
                <div key={wsId} className="flex items-center gap-2 text-[11px]">
                  <span className="h-1 w-1 rounded-full bg-primary" />
                  <span className="font-mono text-muted-foreground">{wsId}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {status === "success" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-emerald-400 font-semibold flex items-center justify-center gap-1.5 py-2">
            <Check className="h-4 w-4" /> Welcome to the team! Redirecting...
          </motion.div>
        )}

        {status === "rejected" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-amber-500 font-semibold flex items-center justify-center gap-1.5 py-2">
            <X className="h-4 w-4" /> Invitation declined. Redirecting...
          </motion.div>
        )}

        {status === "idle" && (
          <div className="flex gap-3">
            <button
              onClick={handleReject}
              disabled={status !== "idle"}
              className="flex-1 rounded-xl border border-border py-2.5 text-xs font-semibold hover:bg-muted/10 transition"
            >
              Decline
            </button>
            <button
              onClick={handleAccept}
              disabled={status !== "idle"}
              className="flex-1 rounded-xl bg-primary py-2.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
            >
              Accept & Join
            </button>
          </div>
        )}

        {(status === "accepting" || status === "rejecting") && (
          <div className="flex justify-center py-2">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        )}
      </motion.div>
    </div>
  );
}
