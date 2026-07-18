"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Crown,
  Loader2,
  Mail,
  Shield,
  ShieldCheck,
  Eye,
  UserPlus,
  X,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
  Trash2,
  Share2,
  Check,
  Copy,
} from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import {
  useMembers,
  useUpdateMemberRole,
  useRemoveMember,
  useTransferOwnership,
  useInvitations,
  useCreateInvitation,
  useCancelInvitation,
  useResendInvitation,
  useWorkspaces,
} from "@/lib/api/hooks";
import { MemberDetailsDrawer } from "@/components/layout/MemberDetailsDrawer";
import type { MemberRole, Membership } from "@/lib/api/types";

const roleConfig = {
  owner: { icon: Crown, color: "text-amber-400 border-amber-500/20 bg-amber-500/5", label: "Owner" },
  admin: { icon: ShieldCheck, color: "text-blue-400 border-blue-500/20 bg-blue-500/5", label: "Admin" },
  engineer: { icon: Shield, color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5", label: "Engineer" },
  viewer: { icon: Eye, color: "text-zinc-400 border-zinc-500/20 bg-zinc-500/5", label: "Viewer" },
} as const;

export default function MembersPage() {
  const { activeOrganization } = useOrgStore();
  const orgId = activeOrganization?.id || null;

  // Search, Filters & Pagination
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [page, setPage] = useState(1);
  const limit = 5;
  const offset = (page - 1) * limit;

  // Data fetching
  const { data: membersData, isLoading: isLoadingMembers } = useMembers(
    orgId,
    search,
    roleFilter,
    limit,
    offset
  );
  const { data: invitationsData, isLoading: isLoadingInvites } = useInvitations(orgId);
  const { data: workspacesData } = useWorkspaces(orgId);

  // Mutations
  const updateRole = useUpdateMemberRole();
  const removeMember = useRemoveMember();
  const transferOwnership = useTransferOwnership();
  const createInvitation = useCreateInvitation();
  const cancelInvitation = useCancelInvitation();
  const resendInvitation = useResendInvitation();

  // Component UI state
  const [activeTab, setActiveTab] = useState<"members" | "invitations">("members");
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<MemberRole>("engineer");
  const [invitedWorkspaces, setInvitedWorkspaces] = useState<string[]>([]);
  const [copiedToken, setCopiedToken] = useState<string | null>(null);

  // Selection/Drawers/Dialogs
  const [selectedMember, setSelectedMember] = useState<Membership | null>(null);
  const [editingRole, setEditingRole] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Membership | null>(null);
  const [confirmTransfer, setConfirmTransfer] = useState<Membership | null>(null);

  if (!activeOrganization) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-muted-foreground">No organization selected.</p>
      </div>
    );
  }

  const handleInvite = async () => {
    if (!orgId || !inviteEmail.trim()) return;
    await createInvitation.mutateAsync({
      orgId,
      payload: {
        email: inviteEmail.trim(),
        role: inviteRole,
        workspaces: invitedWorkspaces,
      },
    });
    setInviteEmail("");
    setInvitedWorkspaces([]);
    setShowInvite(false);
  };

  const handleCopyLink = (token: string) => {
    const link = `${window.location.origin}/invitations/${token}`;
    navigator.clipboard.writeText(link);
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  };

  const handleRemove = async (m: Membership) => {
    if (!orgId) return;
    await removeMember.mutateAsync({ orgId, memberId: m.id });
    setConfirmDelete(null);
  };

  const handleTransfer = async (m: Membership) => {
    if (!orgId) return;
    await transferOwnership.mutateAsync({ orgId, memberId: m.id });
    setConfirmTransfer(null);
  };

  const totalPages = Math.ceil((membersData?.total || 0) / limit);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-4xl pb-10 text-foreground"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Team Settings</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Manage your organization membership, workspace assignments, and invitations.
          </p>
        </div>
        <button
          id="invite-member-button"
          onClick={() => setShowInvite(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
        >
          <UserPlus className="h-3.5 w-3.5" /> Invite Member
        </button>
      </div>

      {/* Navigation tabs */}
      <div className="flex border-b border-border/40 gap-4 text-xs font-medium">
        <button
          onClick={() => setActiveTab("members")}
          className={`pb-2 transition ${
            activeTab === "members"
              ? "text-foreground border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Members ({membersData?.total || 0})
        </button>
        <button
          onClick={() => setActiveTab("invitations")}
          className={`pb-2 transition ${
            activeTab === "invitations"
              ? "text-foreground border-b-2 border-primary"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Pending Invitations ({invitationsData?.results?.length || 0})
        </button>
      </div>

      {/* Invite Modal Dialog */}
      <AnimatePresence>
        {showInvite && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowInvite(false)}
              className="absolute inset-0 bg-black"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative w-full max-w-md rounded-2xl border border-border bg-zinc-950 p-6 shadow-2xl space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Invite teammate</h3>
                <button
                  onClick={() => setShowInvite(false)}
                  className="rounded-lg p-1 text-muted-foreground hover:bg-muted/30 hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-muted-foreground uppercase">Email Address</label>
                  <input
                    id="invite-email-input"
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="teammate@company.com"
                    className="w-full rounded-xl border border-border bg-zinc-900/50 px-3.5 py-2.5 text-xs outline-none focus:border-primary/50"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-muted-foreground uppercase">Assign Role</label>
                  <select
                    id="invite-role-select"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as MemberRole)}
                    className="w-full rounded-xl border border-border bg-zinc-900/50 px-3.5 py-2.5 text-xs outline-none cursor-pointer"
                  >
                    <option value="admin">Admin (Manage members, workspaces)</option>
                    <option value="engineer">Engineer (Run incidents, view logs)</option>
                    <option value="viewer">Viewer (Read-only access)</option>
                  </select>
                </div>

                {/* Workspace list */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-muted-foreground uppercase">Scope Workspaces</label>
                  <div className="max-h-28 overflow-y-auto border border-border rounded-xl p-2 space-y-1.5 bg-zinc-900/30">
                    {workspacesData?.results?.map((ws) => (
                      <label key={ws.id} className="flex items-center gap-2 text-xs font-medium cursor-pointer py-1 px-1.5 rounded-lg hover:bg-muted/20">
                        <input
                          type="checkbox"
                          checked={invitedWorkspaces.includes(ws.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setInvitedWorkspaces([...invitedWorkspaces, ws.id]);
                            } else {
                              setInvitedWorkspaces(invitedWorkspaces.filter((id) => id !== ws.id));
                            }
                          }}
                          className="rounded border-border text-primary focus:ring-primary"
                        />
                        <span>{ws.name}</span>
                      </label>
                    ))}
                    {(!workspacesData?.results || workspacesData.results.length === 0) && (
                      <p className="text-[11px] text-muted-foreground py-2 text-center">No workspaces found.</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-2.5 pt-2">
                <button
                  onClick={() => setShowInvite(false)}
                  className="flex-1 rounded-xl border border-border py-2 text-xs font-semibold hover:bg-muted/20"
                >
                  Cancel
                </button>
                <button
                  id="send-invite-button"
                  onClick={handleInvite}
                  disabled={createInvitation.isPending || !inviteEmail.trim()}
                  className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-primary py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {createInvitation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  Send Invitation
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Confirmation Dialog: Delete member */}
      <AnimatePresence>
        {confirmDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 0.6 }} exit={{ opacity: 0 }} onClick={() => setConfirmDelete(null)} className="absolute inset-0 bg-black" />
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-sm rounded-2xl border border-border bg-zinc-950 p-5 shadow-2xl space-y-4">
              <h3 className="text-sm font-semibold">Remove team member?</h3>
              <p className="text-xs text-muted-foreground">
                Are you sure you want to remove <strong>{confirmDelete.user?.full_name}</strong> ({confirmDelete.user?.email}) from the organization? They will lose access to all resources.
              </p>
              <div className="flex gap-2">
                <button onClick={() => setConfirmDelete(null)} className="flex-1 rounded-xl border border-border py-2 text-xs font-semibold hover:bg-muted/20">Cancel</button>
                <button onClick={() => handleRemove(confirmDelete)} className="flex-1 rounded-xl bg-red-600 py-2 text-xs font-semibold hover:bg-red-700">Remove</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Confirmation Dialog: Transfer ownership */}
      <AnimatePresence>
        {confirmTransfer && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 0.6 }} exit={{ opacity: 0 }} onClick={() => setConfirmTransfer(null)} className="absolute inset-0 bg-black" />
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-sm rounded-2xl border border-border bg-zinc-950 p-5 shadow-2xl space-y-4">
              <h3 className="text-sm font-semibold text-amber-400">Transfer Organization Ownership?</h3>
              <p className="text-xs text-muted-foreground">
                This will transfer the Owner role to <strong>{confirmTransfer.user?.full_name}</strong>. Your role will be changed to Admin. This action cannot be undone.
              </p>
              <div className="flex gap-2">
                <button onClick={() => setConfirmTransfer(null)} className="flex-1 rounded-xl border border-border py-2 text-xs font-semibold hover:bg-muted/20">Cancel</button>
                <button onClick={() => handleTransfer(confirmTransfer)} className="flex-1 rounded-xl bg-amber-500 text-black py-2 text-xs font-semibold hover:bg-amber-600">Transfer</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Active Tab Views */}
      {activeTab === "members" ? (
        <div className="space-y-4">
          {/* Controls: Search & Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-xl border border-border/80 bg-zinc-900/10 pl-9.5 pr-4 py-2 text-xs outline-none focus:border-primary/50"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={roleFilter}
                onChange={(e) => {
                  setRoleFilter(e.target.value);
                  setPage(1);
                }}
                className="rounded-xl border border-border/80 bg-zinc-900/10 px-3 py-2 text-xs outline-none cursor-pointer"
              >
                <option value="all">All Roles</option>
                <option value="owner">Owner</option>
                <option value="admin">Admin</option>
                <option value="engineer">Engineer</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
          </div>

          {/* Members Table */}
          <div className="rounded-2xl border border-border/60 bg-card/50 overflow-hidden shadow-sm">
            {isLoadingMembers ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <div className="divide-y divide-border/30">
                {membersData?.results?.map((member) => {
                  const role = roleConfig[member.role as keyof typeof roleConfig] || roleConfig.viewer;
                  const RoleIcon = role.icon;
                  return (
                    <div
                      key={member.id}
                      className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-muted/10 transition cursor-pointer"
                      onClick={() => setSelectedMember(member)}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted/40 border border-border/40 text-xs font-bold text-muted-foreground">
                          {member.user?.full_name?.charAt(0)?.toUpperCase() || "?"}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-foreground truncate">
                            {member.user?.full_name || "Unknown"}
                          </p>
                          <p className="text-[11px] text-muted-foreground truncate">
                            {member.user?.email || "—"}
                          </p>
                        </div>
                      </div>

                      {/* Role selection & Actions */}
                      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        <div className="relative">
                          <button
                            onClick={() => setEditingRole(editingRole === member.id ? null : member.id)}
                            className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-[11px] font-semibold hover:bg-muted/30 transition ${role.color}`}
                          >
                            <RoleIcon className="h-3 w-3" /> {role.label}
                          </button>
                          <AnimatePresence>
                            {editingRole === member.id && (
                              <motion.div
                                initial={{ opacity: 0, y: -4 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -4 }}
                                className="absolute right-0 top-full z-20 mt-1 w-44 rounded-xl border border-border bg-zinc-950/95 backdrop-blur-xl shadow-lg p-1"
                              >
                                {(["admin", "engineer", "viewer"] as const).map((r) => {
                                  const rc = roleConfig[r];
                                  const RcIcon = rc.icon;
                                  return (
                                    <button
                                      key={r}
                                      onClick={() => {
                                        updateRole.mutateAsync({
                                          orgId: orgId!,
                                          memberId: member.id,
                                          payload: { role: r },
                                        });
                                        setEditingRole(null);
                                      }}
                                      className="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-[11px] font-medium text-muted-foreground hover:bg-muted/30 hover:text-foreground transition text-left"
                                    >
                                      <RcIcon className={`h-3 w-3 ${rc.color}`} />
                                      {rc.label}
                                    </button>
                                  );
                                })}

                                {member.role !== "owner" && (
                                  <>
                                    <div className="h-px bg-border/40 my-1" />
                                    <button
                                      onClick={() => {
                                        setConfirmTransfer(member);
                                        setEditingRole(null);
                                      }}
                                      className="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-[11px] font-medium text-amber-400 hover:bg-amber-500/10 transition text-left"
                                    >
                                      <Crown className="h-3 w-3 text-amber-400" />
                                      Make Owner
                                    </button>
                                  </>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>

                        {member.role !== "owner" && (
                          <button
                            onClick={() => setConfirmDelete(member)}
                            className="rounded-lg p-1.5 text-muted-foreground/50 hover:bg-destructive/10 hover:text-destructive transition"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
                {(!membersData?.results || membersData.results.length === 0) && (
                  <div className="flex items-center justify-center py-12">
                    <p className="text-xs text-muted-foreground">No members matched the criteria.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between text-xs text-muted-foreground pt-2">
              <span>
                Showing {offset + 1} to {Math.min(offset + limit, membersData?.total || 0)} of{" "}
                {membersData?.total || 0} members
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
        </div>
      ) : (
        /* Pending Invitations list */
        <div className="rounded-2xl border border-border/60 bg-card/50 overflow-hidden shadow-sm">
          {isLoadingInvites ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="divide-y divide-border/30">
              {invitationsData?.results?.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between gap-4 px-5 py-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-foreground truncate">{inv.email}</p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-semibold tracking-wide ${
                          inv.status === "pending"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-zinc-800 text-zinc-400 border border-zinc-700"
                        }`}>
                          {inv.status.toUpperCase()}
                        </span>
                        <span className="text-[10px] text-muted-foreground">
                          As {(roleConfig[inv.role as keyof typeof roleConfig] as any)?.label || inv.role}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Actions: Resend / Cancel / Copy invite link */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleCopyLink(inv.token)}
                      className="inline-flex items-center gap-1 rounded-lg border border-border/60 px-2 py-1 text-[10px] font-semibold hover:bg-muted/20"
                    >
                      {copiedToken === inv.token ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-400" /> Copied
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" /> Link
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => resendInvitation.mutateAsync({ orgId: orgId!, invitationId: inv.id })}
                      disabled={resendInvitation.isPending}
                      className="rounded-lg border border-border/60 px-2 py-1 text-[10px] font-semibold hover:bg-muted/20"
                    >
                      Resend
                    </button>
                    <button
                      onClick={() => cancelInvitation.mutateAsync({ orgId: orgId!, invitationId: inv.id })}
                      disabled={cancelInvitation.isPending}
                      className="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
              {(!invitationsData?.results || invitationsData.results.length === 0) && (
                <div className="flex items-center justify-center py-12">
                  <p className="text-xs text-muted-foreground">No pending invitations.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Member details drawer */}
      <MemberDetailsDrawer
        member={selectedMember}
        onClose={() => setSelectedMember(null)}
      />
    </motion.div>
  );
}
