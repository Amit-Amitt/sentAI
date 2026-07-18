"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Key,
  Plus,
  Search,
  Copy,
  Check,
  RefreshCw,
  Trash2,
  Eye,
  AlertTriangle,
  Loader2,
  Calendar,
  X,
  Lock,
  ChevronRight,
  ShieldCheck,
  ExternalLink,
} from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import {
  useApiKeys,
  useCreateApiKey,
  useDeleteApiKey,
  useCopyApiKey,
  useRotateApiKey,
  useRevokeApiKey,
} from "@/lib/api/hooks/useApiKeys";
import type { ApiKey } from "@/lib/api/types/apikey";

const SCOPES_CONFIG = [
  { scope: "incidents:read", label: "Read Incidents", desc: "View incident boards, system anomalies, and investigation reports." },
  { scope: "incidents:write", label: "Write Incidents", desc: "Create, resolve, or trigger incident mitigations." },
  { scope: "reports:read", label: "Read Reports", desc: "View generated incident post-mortems and executive reports." },
  { scope: "reports:write", label: "Write Reports", desc: "Publish post-mortems or edit summaries." },
  { scope: "logs:upload", label: "Upload Logs", desc: "Ingest runtime logs to the AI Incident Commander." },
  { scope: "metrics:upload", label: "Upload Metrics", desc: "Submit metrics data for anomaly detection." },
  { scope: "deployments:upload", label: "Upload Deployments", desc: "Log deployment events for correlation analysis." },
  { scope: "workspace:read", label: "Read Workspace", desc: "Query current workspace settings." },
  { scope: "workspace:write", label: "Write Workspace", desc: "Modify workspace metadata, environments, or retention rates." },
  { scope: "api-keys:manage", label: "Manage API Keys", desc: "Create, edit, rotate, or revoke API keys." },
];

export default function ApiKeysPage() {
  const router = useRouter();
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id || null;

  // React Query hooks
  const { data: apiKeysData, isLoading, refetch } = useApiKeys(workspaceId);
  const createApiKeyMutation = useCreateApiKey();
  const deleteApiKeyMutation = useDeleteApiKey();
  const copyApiKeyMutation = useCopyApiKey();
  const rotateApiKeyMutation = useRotateApiKey();
  const revokeApiKeyMutation = useRevokeApiKey();

  // Component states
  const [searchQuery, setSearchQuery] = useState("");
  const [envFilter, setEnvFilter] = useState<string>("all");
  const [copiedKeyId, setCopiedKeyId] = useState<string | null>(null);

  // Dialog & Form states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newKeyData, setNewKeyData] = useState<{ secret: string; name: string; keyId: string } | null>(null);
  const [keyToRotate, setKeyToRotate] = useState<ApiKey | null>(null);
  const [keyToDelete, setKeyToDelete] = useState<ApiKey | null>(null);
  const [keyToRevoke, setKeyToRevoke] = useState<ApiKey | null>(null);

  // Creation form fields
  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formEnvironment, setFormEnvironment] = useState("development");
  const [formExpiresAt, setFormExpiresAt] = useState("");
  const [formScopes, setFormScopes] = useState<string[]>(["incidents:read", "logs:upload"]);

  // Clipboard copy utility
  const copyToClipboard = (text: string, id: string, keyId?: string) => {
    navigator.clipboard.writeText(text);
    if (keyId) {
      copyApiKeyMutation.mutate(keyId);
    }
    setCopiedKeyId(id);
    setTimeout(() => setCopiedKeyId(null), 2000);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspaceId || !formName.trim()) return;

    try {
      const response = await createApiKeyMutation.mutateAsync({
        workspaceId,
        payload: {
          name: formName,
          description: formDescription.trim() || null,
          environment: formEnvironment,
          scopes: formScopes,
          expires_at: formExpiresAt ? new Date(formExpiresAt).toISOString() : null,
        },
      });

      // Clear form
      setFormName("");
      setFormDescription("");
      setFormEnvironment("development");
      setFormExpiresAt("");
      setFormScopes(["incidents:read", "logs:upload"]);
      setIsCreateModalOpen(false);

      // Open raw reveal dialog
      setNewKeyData({
        keyId: response.id,
        secret: response.secret,
        name: response.name,
      });
      refetch();
    } catch (err) {
      console.error("Failed to create key:", err);
    }
  };

  const handleRotate = async () => {
    if (!keyToRotate) return;
    try {
      const response = await rotateApiKeyMutation.mutateAsync(keyToRotate.id);
      setKeyToRotate(null);
      setNewKeyData({
        keyId: response.id,
        secret: response.secret,
        name: response.name,
      });
      refetch();
    } catch (err) {
      console.error("Failed to rotate key:", err);
    }
  };

  const handleRevoke = async () => {
    if (!keyToRevoke) return;
    try {
      await revokeApiKeyMutation.mutateAsync(keyToRevoke.id);
      setKeyToRevoke(null);
      refetch();
    } catch (err) {
      console.error("Failed to revoke key:", err);
    }
  };

  const handleDelete = async () => {
    if (!keyToDelete || !workspaceId) return;
    try {
      await deleteApiKeyMutation.mutateAsync({ keyId: keyToDelete.id, workspaceId });
      setKeyToDelete(null);
      refetch();
    } catch (err) {
      console.error("Failed to delete key:", err);
    }
  };

  const toggleScope = (scope: string) => {
    setFormScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  if (!activeWorkspace) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
        <Key className="h-12 w-12 text-muted-foreground animate-pulse" />
        <h2 className="text-lg font-semibold">No Workspace Selected</h2>
        <p className="text-sm text-muted-foreground max-w-sm">
          Please select a workspace from the dashboard to manage its API Keys.
        </p>
      </div>
    );
  }

  // Filter keys
  const keys = apiKeysData?.results || [];
  const filteredKeys = keys.filter((key) => {
    const matchesSearch =
      key.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (key.description && key.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      key.prefix.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesEnv = envFilter === "all" || key.environment === envFilter;
    return matchesSearch && matchesEnv;
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-6xl"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">API Key Management</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Issue and manage high-entropy credentials for CI/CD pipelines, log shippers, and monitoring sub-systems.
          </p>
        </div>
        <button
          id="create-key-button"
          onClick={() => setIsCreateModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/20 self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" /> Create API Key
        </button>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground" />
          <input
            id="apikey-search-input"
            type="text"
            placeholder="Search keys..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-border/60 bg-card/40 px-10 py-2.5 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition"
          />
        </div>

        <div className="flex items-center gap-1.5 self-start sm:self-auto ml-auto">
          {["all", "production", "development", "testing"].map((env) => (
            <button
              key={env}
              onClick={() => setEnvFilter(env)}
              className={`rounded-xl px-4 py-2 text-xs font-semibold uppercase tracking-wider transition ${
                envFilter === env
                  ? "bg-muted text-foreground border border-border/80"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {env}
            </button>
          ))}
        </div>
      </div>

      {/* Listing Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="h-8 w-8 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground font-medium">Querying credential registries...</p>
        </div>
      ) : filteredKeys.length === 0 ? (
        <div className="rounded-2xl border border-border/60 bg-card/25 p-12 text-center flex flex-col items-center justify-center space-y-4">
          <div className="rounded-full bg-primary/10 p-4 text-primary">
            <Key className="h-8 w-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold">No API Keys Configured</h3>
            <p className="text-sm text-muted-foreground mt-1 max-w-sm">
              Create an API Key to integrate external pipelines, GitHub Actions, and custom agents with Sentinel AI.
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition"
          >
            <Plus className="h-4 w-4" /> Issue First Key
          </button>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border/60 bg-card/30 backdrop-blur-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border/60 bg-card/50 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  <th className="px-6 py-4">Key details</th>
                  <th className="px-6 py-4">Environment</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 font-mono">Secret Preview</th>
                  <th className="px-6 py-4">Last Active</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40 text-sm">
                {filteredKeys.map((key) => {
                  const isExpired = key.status === "active" && key.expires_at && new Date(key.expires_at) < new Date();
                  const finalStatus = isExpired ? "expired" : key.status;

                  return (
                    <motion.tr
                      key={key.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-muted/15 transition cursor-pointer"
                      onClick={() => router.push(`/settings/apikeys/${key.id}`)}
                    >
                      <td className="px-6 py-4.5 max-w-xs">
                        <div className="font-semibold text-foreground truncate">{key.name}</div>
                        {key.description && (
                          <div className="text-xs text-muted-foreground truncate mt-0.5">{key.description}</div>
                        )}
                      </td>
                      <td className="px-6 py-4.5">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`h-1.5 w-1.5 rounded-full ${
                              key.environment === "production"
                                ? "bg-rose-400"
                                : key.environment === "testing"
                                ? "bg-amber-400"
                                : "bg-emerald-400"
                            }`}
                          />
                          <span className="text-xs font-semibold capitalize">{key.environment}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4.5">
                        <span
                          className={`inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-semibold uppercase tracking-wider ${
                            finalStatus === "active"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : finalStatus === "revoked"
                              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              : "bg-muted text-muted-foreground border border-border/80"
                          }`}
                        >
                          {finalStatus}
                        </span>
                      </td>
                      <td className="px-6 py-4.5 font-mono text-xs text-muted-foreground">
                        <div
                          className="flex items-center gap-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <span>{key.prefix}</span>
                          {finalStatus === "active" && (
                            <button
                              onClick={() => copyToClipboard(key.prefix, key.id, key.id)}
                              className="text-muted-foreground hover:text-foreground transition p-1 hover:bg-muted rounded-lg"
                            >
                              {copiedKeyId === key.id ? (
                                <Check className="h-3.5 w-3.5 text-emerald-400" />
                              ) : (
                                <Copy className="h-3.5 w-3.5" />
                              )}
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4.5 text-xs text-muted-foreground">
                        {key.last_used_at
                          ? new Date(key.last_used_at).toLocaleDateString()
                          : "Never"}
                      </td>
                      <td className="px-6 py-4.5 text-right">
                        <div
                          className="flex items-center justify-end gap-1.5"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={() => router.push(`/settings/apikeys/${key.id}`)}
                            title="Analytics & Logs"
                            className="p-2 text-muted-foreground hover:text-foreground transition hover:bg-muted rounded-xl"
                          >
                            <ChevronRight className="h-4.5 w-4.5" />
                          </button>
                          {finalStatus === "active" && (
                            <>
                              <button
                                onClick={() => setKeyToRotate(key)}
                                title="Rotate secret key"
                                className="p-2 text-muted-foreground hover:text-primary transition hover:bg-muted rounded-xl"
                              >
                                <RefreshCw className="h-4.5 w-4.5" />
                              </button>
                              <button
                                onClick={() => setKeyToRevoke(key)}
                                title="Revoke access"
                                className="p-2 text-muted-foreground hover:text-rose-500 transition hover:bg-muted rounded-xl"
                              >
                                <Lock className="h-4.5 w-4.5" />
                              </button>
                            </>
                          )}
                          <button
                            onClick={() => setKeyToDelete(key)}
                            title="Delete key"
                            className="p-2 text-muted-foreground hover:text-rose-500 transition hover:bg-muted rounded-xl"
                          >
                            <Trash2 className="h-4.5 w-4.5" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* 1. CREATE API KEY MODAL                                  */}
      {/* ======================================================== */}
      <AnimatePresence>
        {isCreateModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-2xl rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Key className="h-5 w-5 text-primary" /> Issue API Key
                </h3>
                <button
                  onClick={() => setIsCreateModalOpen(false)}
                  className="text-muted-foreground hover:text-foreground transition p-1 hover:bg-muted rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1.5 col-span-2 sm:col-span-1">
                    <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      Key Name
                    </label>
                    <input
                      id="create-key-name"
                      type="text"
                      required
                      placeholder="e.g. GitHub Actions CI"
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                      className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                    />
                  </div>

                  <div className="flex flex-col gap-1.5 col-span-2 sm:col-span-1">
                    <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      Environment scope
                    </label>
                    <select
                      value={formEnvironment}
                      onChange={(e) => setFormEnvironment(e.target.value)}
                      className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                    >
                      <option value="development">Development (Development DB)</option>
                      <option value="testing">Testing (Isolated Sandbox)</option>
                      <option value="production">Production (Live Workloads)</option>
                    </select>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Description
                  </label>
                  <input
                    id="create-key-desc"
                    type="text"
                    placeholder="Short description of where this key will be configured"
                    value={formDescription}
                    onChange={(e) => setFormDescription(e.target.value)}
                    className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <Calendar className="h-4 w-4 text-primary" /> Expiration Date
                  </label>
                  <input
                    id="create-key-expires"
                    type="datetime-local"
                    value={formExpiresAt}
                    onChange={(e) => setFormExpiresAt(e.target.value)}
                    className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                  />
                  <p className="text-[10px] text-muted-foreground">
                    Leave blank to create a persistent key. Setting expiration dates is a security best practice.
                  </p>
                </div>

                {/* Scopes checklist */}
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Select Scopes
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-52 overflow-y-auto pr-1 border border-border/40 rounded-xl bg-background/50 p-3">
                    {SCOPES_CONFIG.map((cfg) => {
                      const isChecked = formScopes.includes(cfg.scope);
                      return (
                        <div
                          key={cfg.scope}
                          onClick={() => toggleScope(cfg.scope)}
                          className={`flex items-start gap-3 rounded-xl p-3 border transition cursor-pointer ${
                            isChecked
                              ? "bg-primary/5 border-primary/50"
                              : "bg-card/40 border-border/50 hover:border-border"
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}}
                            className="mt-1 h-4 w-4 rounded accent-primary border-border"
                          />
                          <div>
                            <div className="text-xs font-bold">{cfg.label}</div>
                            <div className="text-[10px] text-muted-foreground mt-0.5 leading-snug">
                              {cfg.desc}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="flex justify-end gap-3 pt-4 border-t border-border/60">
                  <button
                    type="button"
                    onClick={() => setIsCreateModalOpen(false)}
                    className="rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-muted transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    id="create-key-submit"
                    disabled={createApiKeyMutation.isPending}
                    className="flex items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-lg shadow-primary/20"
                  >
                    {createApiKeyMutation.isPending && (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    Generate Key
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* 2. REVEAL NEW SECRET DIALOG                              */}
      {/* ======================================================== */}
      <AnimatePresence>
        {newKeyData && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-lg rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-6"
            >
              <div className="text-center space-y-2">
                <div className="inline-flex rounded-full bg-emerald-500/10 p-3 text-emerald-400 border border-emerald-500/20">
                  <ShieldCheck className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold">API Key Generated Successfully</h3>
                <p className="text-sm text-muted-foreground">
                  Below is the secret credentials for <span className="font-semibold text-foreground">{newKeyData.name}</span>.
                </p>
              </div>

              {/* Danger Warning Banner */}
              <div className="rounded-xl border border-rose-500/25 bg-rose-500/5 p-4 flex gap-3 text-rose-400">
                <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="text-xs leading-normal">
                  <span className="font-bold">Security Alert:</span> Store this secret token immediately in a secure location.
                  Once closed, <span className="font-bold underline">you will not be able to retrieve it</span> from the Sentinel registry.
                </div>
              </div>

              {/* Key Secret Field */}
              <div className="rounded-xl border border-border/80 bg-background/50 p-4 font-mono text-sm break-all relative pr-12 flex items-center">
                <span>{newKeyData.secret}</span>
                <button
                  id="copy-secret-button"
                  onClick={() => copyToClipboard(newKeyData.secret, "newkey", newKeyData.keyId)}
                  className="absolute right-3 top-3.5 text-muted-foreground hover:text-foreground transition p-1.5 hover:bg-muted rounded-lg"
                >
                  {copiedKeyId === "newkey" ? (
                    <Check className="h-4.5 w-4.5 text-emerald-400" />
                  ) : (
                    <Copy className="h-4.5 w-4.5" />
                  )}
                </button>
              </div>

              {/* Confirm & Close */}
              <div className="flex justify-center pt-2">
                <button
                  id="confirm-reveal-close"
                  onClick={() => setNewKeyData(null)}
                  className="w-full rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-lg shadow-primary/20"
                >
                  I have copied the secret key safely
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* 3. ROTATION WARNING DIALOG                               */}
      {/* ======================================================== */}
      <AnimatePresence>
        {keyToRotate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5"
            >
              <div className="flex items-center gap-3 text-amber-500">
                <div className="rounded-full bg-amber-500/10 p-2 border border-amber-500/20">
                  <RefreshCw className="h-5 w-5 animate-spin" />
                </div>
                <h3 className="text-lg font-bold">Rotate API Key?</h3>
              </div>

              <p className="text-sm text-muted-foreground leading-normal">
                You are about to rotate <span className="font-semibold text-foreground">{keyToRotate.name}</span>.
                Rotating will instantly invalidate the current secret, meaning any live integrations using it will
                immediately fail until updated with the new credentials.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setKeyToRotate(null)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-rotate-button"
                  onClick={handleRotate}
                  disabled={rotateApiKeyMutation.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-amber-700 transition"
                >
                  {rotateApiKeyMutation.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  Rotate Immediately
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* 4. REVOCATION WARNING DIALOG                             */}
      {/* ======================================================== */}
      <AnimatePresence>
        {keyToRevoke && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5"
            >
              <div className="flex items-center gap-3 text-rose-500">
                <div className="rounded-full bg-rose-500/10 p-2 border border-rose-500/20">
                  <Lock className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-bold">Revoke API Key?</h3>
              </div>

              <p className="text-sm text-muted-foreground leading-normal">
                You are about to revoke <span className="font-semibold text-foreground">{keyToRevoke.name}</span>.
                This is a permanent security action. All client processes, monitoring nodes, or runners using this key
                will be blocked from making API requests immediately.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setKeyToRevoke(null)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-revoke-button"
                  onClick={handleRevoke}
                  disabled={revokeApiKeyMutation.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 transition"
                >
                  {revokeApiKeyMutation.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  Revoke Key
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* 5. DELETION WARNING DIALOG                               */}
      {/* ======================================================== */}
      <AnimatePresence>
        {keyToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5"
            >
              <div className="flex items-center gap-3 text-rose-500">
                <div className="rounded-full bg-rose-500/10 p-2 border border-rose-500/20">
                  <Trash2 className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-bold">Delete API Key?</h3>
              </div>

              <p className="text-sm text-muted-foreground leading-normal">
                Are you sure you want to permanently delete <span className="font-semibold text-foreground">{keyToDelete.name}</span>?
                This will remove the credential record and all its historical usage analytics logs forever.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setKeyToDelete(null)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-delete-button"
                  onClick={handleDelete}
                  disabled={deleteApiKeyMutation.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 transition"
                >
                  {deleteApiKeyMutation.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  Delete Permanent
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
