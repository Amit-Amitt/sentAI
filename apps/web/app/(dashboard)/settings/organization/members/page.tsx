"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Crown, Loader2, Mail, Shield, ShieldCheck, Eye, UserPlus, X } from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useMembers, useUpdateMemberRole, useRemoveMember, useInvitations, useCreateInvitation } from "@/lib/api/hooks";
import type { MemberRole } from "@/lib/api/types";

const roleConfig = {
  owner: { icon: Crown, color: "text-amber-400", label: "Owner" },
  admin: { icon: ShieldCheck, color: "text-primary", label: "Admin" },
  engineer: { icon: Shield, color: "text-emerald-400", label: "Engineer" },
  viewer: { icon: Eye, color: "text-muted-foreground", label: "Viewer" },
} as const;

export default function MembersPage() {
  const { activeOrganization } = useOrgStore();
  const orgId = activeOrganization?.id || null;
  const { data: membersData, isLoading } = useMembers(orgId);
  const { data: invitationsData } = useInvitations(orgId);
  const updateRole = useUpdateMemberRole();
  const removeMember = useRemoveMember();
  const createInvitation = useCreateInvitation();
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<MemberRole>("engineer");
  const [editingRole, setEditingRole] = useState<string | null>(null);

  if (!activeOrganization) {
    return <div className="flex items-center justify-center py-20"><p className="text-sm text-muted-foreground">No organization selected.</p></div>;
  }

  const handleInvite = async () => {
    if (!orgId || !inviteEmail.trim()) return;
    await createInvitation.mutateAsync({ orgId, payload: { email: inviteEmail.trim(), role: inviteRole } });
    setInviteEmail(""); setShowInvite(false);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-foreground">Team Members ({membersData?.total || 0})</p>
          <p className="text-xs text-muted-foreground mt-0.5">Manage who has access to this organization.</p>
        </div>
        <button id="invite-member-button" onClick={() => setShowInvite(true)} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition">
          <UserPlus className="h-3.5 w-3.5" /> Invite Member
        </button>
      </div>

      <AnimatePresence>
        {showInvite && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold">Send Invitation</p>
                <button onClick={() => setShowInvite(false)} className="text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></button>
              </div>
              <div className="flex gap-2">
                <input id="invite-email-input" type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="colleague@company.com" className="flex-1 rounded-xl border border-border/60 bg-background/50 px-3 py-2 text-xs outline-none focus:border-primary/50" />
                <select id="invite-role-select" value={inviteRole} onChange={(e) => setInviteRole(e.target.value as MemberRole)} className="rounded-xl border border-border/60 bg-background/50 px-3 py-2 text-xs outline-none appearance-none cursor-pointer">
                  <option value="admin">Admin</option>
                  <option value="engineer">Engineer</option>
                  <option value="viewer">Viewer</option>
                </select>
                <button id="send-invite-button" onClick={handleInvite} disabled={createInvitation.isPending || !inviteEmail.trim()} className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
                  {createInvitation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Mail className="h-3.5 w-3.5" />} Send
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="rounded-2xl border border-border/60 bg-card/50 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
        ) : (
          <div className="divide-y divide-border/30">
            {membersData?.results?.map((member) => {
              const role = roleConfig[member.role as keyof typeof roleConfig] || roleConfig.viewer;
              const RoleIcon = role.icon;
              return (
                <div key={member.id} className="flex items-center gap-4 px-5 py-4 hover:bg-muted/10 transition">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted/40 border border-border/40 text-xs font-bold text-muted-foreground">
                    {member.user?.full_name?.charAt(0)?.toUpperCase() || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-foreground truncate">{member.user?.full_name || "Unknown"}</p>
                    <p className="text-[11px] text-muted-foreground truncate">{member.user?.email || "—"}</p>
                  </div>
                  <div className="relative">
                    <button onClick={() => setEditingRole(editingRole === member.id ? null : member.id)} className={`inline-flex items-center gap-1.5 rounded-lg border border-border/40 px-2.5 py-1 text-[11px] font-semibold hover:bg-muted/30 transition ${role.color}`}>
                      <RoleIcon className="h-3 w-3" /> {role.label}
                    </button>
                    <AnimatePresence>
                      {editingRole === member.id && (
                        <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} className="absolute right-0 top-full z-20 mt-1 w-36 rounded-xl border border-border/80 bg-zinc-950/95 backdrop-blur-xl shadow-lg p-1">
                          {(["owner", "admin", "engineer", "viewer"] as const).map((r) => {
                            const rc = roleConfig[r]; const RcIcon = rc.icon;
                            return (
                              <button key={r} onClick={() => { updateRole.mutateAsync({ orgId: orgId!, memberId: member.id, payload: { role: r } }); setEditingRole(null); }} className="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-[11px] font-medium text-muted-foreground hover:bg-muted/30 hover:text-foreground transition">
                                <RcIcon className={`h-3 w-3 ${rc.color}`} /> {rc.label}
                              </button>
                            );
                          })}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                  {member.role !== "owner" && (
                    <button onClick={() => removeMember.mutateAsync({ orgId: orgId!, memberId: member.id })} className="rounded-lg p-1.5 text-muted-foreground/50 hover:bg-destructive/10 hover:text-destructive transition">
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              );
            })}
            {(!membersData?.results || membersData.results.length === 0) && (
              <div className="flex items-center justify-center py-12"><p className="text-xs text-muted-foreground">No members yet.</p></div>
            )}
          </div>
        )}
      </div>

      {invitationsData && invitationsData.results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm font-semibold">Pending Invitations</p>
          <div className="rounded-2xl border border-border/60 bg-card/50 divide-y divide-border/30">
            {invitationsData.results.map((inv) => (
              <div key={inv.id} className="flex items-center gap-4 px-5 py-3.5">
                <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                <p className="flex-1 text-xs font-medium truncate">{inv.email}</p>
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${inv.status === "pending" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-zinc-800 text-zinc-400"}`}>{inv.status.toUpperCase()}</span>
                <span className="text-[11px] text-muted-foreground">{(roleConfig[inv.role as keyof typeof roleConfig] as any)?.label || inv.role}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
