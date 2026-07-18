"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  Key,
  Calendar,
  Lock,
  RefreshCw,
  Trash2,
  Activity,
  History,
  CheckCircle2,
  XCircle,
  Clock,
  Globe,
  Loader2,
  Copy,
  Check,
  Edit,
  Save,
  AlertTriangle,
  User,
  ShieldCheck,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useOrgStore } from "@/lib/store/org-store";
import {
  useApiKey,
  useApiKeyUsage,
  useApiKeyAudits,
  useCopyApiKey,
  useUpdateApiKey,
  useRotateApiKey,
  useRevokeApiKey,
  useDeleteApiKey,
} from "@/lib/api/hooks/useApiKeys";

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

export default function ApiKeyDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const keyId = params.id as string;
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id || null;

  // React Query hooks
  const { data: apiKey, isLoading: isLoadingKey, refetch: refetchKey } = useApiKey(keyId);
  const { data: usageStats, isLoading: isLoadingUsage, refetch: refetchUsage } = useApiKeyUsage(keyId);
  const { data: auditHistory, isLoading: isLoadingAudits, refetch: refetchAudits } = useApiKeyAudits(keyId);
  const updateApiKeyMutation = useUpdateApiKey();
  const copyApiKeyMutation = useCopyApiKey();
  const rotateApiKeyMutation = useRotateApiKey();
  const revokeApiKeyMutation = useRevokeApiKey();
  const deleteApiKeyMutation = useDeleteApiKey();

  // Local states
  const [copiedText, setCopiedText] = useState(false);
  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editExpiresAt, setEditExpiresAt] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
  const [showNewSecret, setShowNewSecret] = useState<{ secret: string; keyId: string } | null>(null);

  // Dialog actions
  const [showRotateConfirm, setShowRotateConfirm] = useState(false);
  const [showRevokeConfirm, setShowRevokeConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Sync state with loaded data
  useEffect(() => {
    if (apiKey) {
      setEditName(apiKey.name);
      setEditDescription(apiKey.description || "");
      setSelectedScopes(apiKey.scopes || []);
      setEditExpiresAt(
        apiKey.expires_at ? new Date(apiKey.expires_at).toISOString().slice(0, 16) : ""
      );
    }
  }, [apiKey]);

  const copyToClipboard = (text: string, keyId?: string) => {
    navigator.clipboard.writeText(text);
    if (keyId) {
      copyApiKeyMutation.mutate(keyId);
    }
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleUpdateInfo = async () => {
    try {
      await updateApiKeyMutation.mutateAsync({
        keyId,
        payload: {
          name: editName,
          description: editDescription || null,
          expires_at: editExpiresAt ? new Date(editExpiresAt).toISOString() : null,
        },
      });
      setIsEditingInfo(false);
      refetchKey();
    } catch (err) {
      console.error("Failed to update key info:", err);
    }
  };

  const handleUpdateScopes = async () => {
    try {
      await updateApiKeyMutation.mutateAsync({
        keyId,
        payload: {
          scopes: selectedScopes,
        },
      });
      refetchKey();
    } catch (err) {
      console.error("Failed to update key scopes:", err);
    }
  };

  const handleRotate = async () => {
    try {
      const resp = await rotateApiKeyMutation.mutateAsync(keyId);
      setShowRotateConfirm(false);
      setShowNewSecret({ secret: resp.secret, keyId });
      refetchKey();
      refetchUsage();
      refetchAudits();
    } catch (err) {
      console.error("Failed to rotate key:", err);
    }
  };

  const handleRevoke = async () => {
    try {
      await revokeApiKeyMutation.mutateAsync(keyId);
      setShowRevokeConfirm(false);
      refetchKey();
      refetchUsage();
      refetchAudits();
    } catch (err) {
      console.error("Failed to revoke key:", err);
    }
  };

  const handleDelete = async () => {
    if (!workspaceId) return;
    try {
      await deleteApiKeyMutation.mutateAsync({ keyId, workspaceId });
      setShowDeleteConfirm(false);
      router.push("/settings/apikeys");
    } catch (err) {
      console.error("Failed to delete key:", err);
    }
  };

  const toggleScope = (scope: string) => {
    setSelectedScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  if (isLoadingKey || !apiKey) {
    return (
      <div className="flex flex-col items-center justify-center py-40 gap-3">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-medium">Resolving key metadata...</p>
      </div>
    );
  }

  const isExpired = apiKey.status === "active" && apiKey.expires_at && new Date(apiKey.expires_at) < new Date();
  const finalStatus = isExpired ? "expired" : apiKey.status;

  // Process data for Recharts (e.g. usage statistics over time)
  // Let's build a mock timeline for the chart based on actual logs or daily partitions
  const chartData = usageStats?.recent_usages
    ? [...usageStats.recent_usages]
        .reverse()
        .reduce((acc: any[], usage) => {
          const day = new Date(usage.timestamp).toLocaleDateString([], { month: "short", day: "numeric" });
          const existing = acc.find((d) => d.name === day);
          if (existing) {
            existing.Requests += 1;
            if (usage.status_code >= 400) {
              existing.Errors += 1;
            }
          } else {
            acc.push({
              name: day,
              Requests: 1,
              Errors: usage.status_code >= 400 ? 1 : 0,
            });
          }
          return acc;
        }, [])
    : [];

  // Fallback chart data if empty
  const displayChartData = chartData.length > 0 ? chartData : [
    { name: "Mon", Requests: 0, Errors: 0 },
    { name: "Tue", Requests: 0, Errors: 0 },
    { name: "Wed", Requests: 0, Errors: 0 },
    { name: "Thu", Requests: 0, Errors: 0 },
    { name: "Fri", Requests: 0, Errors: 0 },
  ];

  const totalRequests = (usageStats?.successful_requests || 0) + (usageStats?.failed_requests || 0);
  const successRate = totalRequests > 0 ? Math.round((usageStats!.successful_requests / totalRequests) * 100) : 100;

  const scopesChanged = JSON.stringify(selectedScopes.sort()) !== JSON.stringify((apiKey.scopes || []).sort());

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-6xl"
    >
      {/* Back Button */}
      <button
        onClick={() => router.push("/settings/apikeys")}
        className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-muted-foreground hover:text-foreground transition"
      >
        <ArrowLeft className="h-4 w-4" /> Back to API Keys
      </button>

      {/* Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-border/60 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{apiKey.name}</h1>
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
          </div>
          {apiKey.description && (
            <p className="text-sm text-muted-foreground max-w-xl">{apiKey.description}</p>
          )}
          <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  apiKey.environment === "production"
                    ? "bg-rose-400"
                    : apiKey.environment === "testing"
                    ? "bg-amber-400"
                    : "bg-emerald-400"
                }`}
              />
              <span className="capitalize font-semibold">{apiKey.environment} scope</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" /> Created {new Date(apiKey.created_at).toLocaleDateString()}
            </div>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" /> Expiration:{" "}
              {apiKey.expires_at ? new Date(apiKey.expires_at).toLocaleString() : "Never"}
            </div>
          </div>
        </div>

        {/* Action Panel */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setIsEditingInfo(!isEditingInfo)}
            className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-border/80 bg-card px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
          >
            <Edit className="h-4 w-4" /> Edit Details
          </button>
        </div>
      </div>

      {/* Editing Info Form Dropdown */}
      <AnimatePresence>
        {isEditingInfo && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden rounded-2xl border border-border/60 bg-card/40 p-6 space-y-4"
          >
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
              Modify Key Properties
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-muted-foreground">Name</label>
                <input
                  id="edit-key-name"
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2 text-sm outline-none focus:border-primary transition"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-muted-foreground">Description</label>
                <input
                  id="edit-key-desc"
                  type="text"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2 text-sm outline-none focus:border-primary transition"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold text-muted-foreground">Expiration Date</label>
                <input
                  id="edit-key-expires"
                  type="datetime-local"
                  value={editExpiresAt}
                  onChange={(e) => setEditExpiresAt(e.target.value)}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2 text-sm outline-none focus:border-primary transition"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsEditingInfo(false)}
                className="rounded-xl px-4 py-2 text-xs font-semibold hover:bg-muted transition"
              >
                Discard
              </button>
              <button
                id="save-key-details"
                onClick={handleUpdateInfo}
                disabled={updateApiKeyMutation.isPending}
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary/95 transition"
              >
                {updateApiKeyMutation.isPending ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Save className="h-3.5 w-3.5" />
                )}
                Save Metadata
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Grid Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Side: Analytics */}
        <div className="lg:col-span-2 space-y-6">
          {/* Key Analytics Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="rounded-2xl border border-border/60 bg-card/45 p-4 space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Requests today</div>
              <div className="text-2xl font-bold font-mono text-foreground">
                {usageStats?.requests_today ?? 0}
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card/45 p-4 space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Requests this month</div>
              <div className="text-2xl font-bold font-mono text-foreground">
                {usageStats?.requests_this_month ?? 0}
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card/45 p-4 space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Success Rate</div>
              <div className="text-2xl font-bold font-mono text-emerald-400">
                {successRate}%
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card/45 p-4 space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Top Endpoint</div>
              <div className="text-xs font-bold text-foreground truncate mt-1">
                {usageStats?.top_endpoint ?? "None"}
              </div>
            </div>
          </div>

          {/* Usage Chart */}
          <div className="rounded-2xl border border-border/60 bg-card/30 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Activity className="h-4.5 w-4.5 text-primary" /> Traffic rate over time
              </h3>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={displayChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorErrors" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                  <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} tickLine={false} />
                  <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1f2937",
                      borderColor: "#4b5563",
                      borderRadius: "12px",
                      color: "#f3f4f6",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="Requests"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorRequests)"
                  />
                  <Area
                    type="monotone"
                    dataKey="Errors"
                    stroke="#ef4444"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorErrors)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Usage Logs */}
          <div className="rounded-2xl border border-border/60 bg-card/30 p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Globe className="h-4.5 w-4.5 text-emerald-400" /> Recent transactions log (50 requests)
            </h3>
            {isLoadingUsage ? (
              <div className="py-10 text-center text-xs text-muted-foreground">Loading records...</div>
            ) : !usageStats?.recent_usages || usageStats.recent_usages.length === 0 ? (
              <div className="py-10 text-center text-xs text-muted-foreground">
                No active traffic has been processed by this key yet.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-border/40 text-muted-foreground font-bold uppercase">
                      <th className="pb-3 pr-4">Endpoint</th>
                      <th className="pb-3 pr-4">Method</th>
                      <th className="pb-3 pr-4">Status</th>
                      <th className="pb-3 pr-4">Response Time</th>
                      <th className="pb-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/20">
                    {usageStats.recent_usages.map((u) => (
                      <tr key={u.id} className="hover:bg-muted/10">
                        <td className="py-3 pr-4 font-mono truncate max-w-xs">{u.endpoint}</td>
                        <td className="py-3 pr-4 font-bold">{u.method}</td>
                        <td className="py-3 pr-4">
                          <span
                            className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 font-bold ${
                              u.status_code < 400
                                ? "text-emerald-400 bg-emerald-500/10"
                                : "text-rose-400 bg-rose-500/10"
                            }`}
                          >
                            {u.status_code < 400 ? (
                              <CheckCircle2 className="h-3 w-3" />
                            ) : (
                              <XCircle className="h-3 w-3" />
                            )}
                            {u.status_code}
                          </span>
                        </td>
                        <td className="py-3 pr-4 font-mono">{u.response_time_ms} ms</td>
                        <td className="py-3 text-muted-foreground">
                          {new Date(u.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Audit History Logs */}
          <div className="rounded-2xl border border-border/60 bg-card/30 p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <History className="h-4.5 w-4.5 text-indigo-400" /> Administrative Audit Log
            </h3>
            {isLoadingAudits ? (
              <div className="py-10 text-center text-xs text-muted-foreground">Loading audit log...</div>
            ) : !auditHistory?.results || auditHistory.results.length === 0 ? (
              <div className="py-10 text-center text-xs text-muted-foreground">
                No administrative logs generated yet.
              </div>
            ) : (
              <div className="space-y-3.5">
                {auditHistory.results.map((audit) => (
                  <div
                    key={audit.id}
                    className="flex items-start justify-between border-b border-border/20 pb-3 last:border-0 last:pb-0 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold capitalize bg-muted px-1.5 py-0.5 rounded text-foreground">
                          {audit.action.replace("_", " ")}
                        </span>
                        <span className="text-muted-foreground flex items-center gap-1">
                          <User className="h-3 w-3" />{" "}
                          {audit.performed_by?.email ?? "System Task"}
                        </span>
                      </div>
                      {audit.details && (
                        <pre className="rounded bg-background/50 p-2 font-mono text-[10px] text-muted-foreground max-w-lg overflow-x-auto mt-1">
                          {JSON.stringify(audit.details, null, 2)}
                        </pre>
                      )}
                    </div>
                    <div className="text-right text-muted-foreground text-[10px] space-y-0.5">
                      <div>{new Date(audit.timestamp).toLocaleString()}</div>
                      {audit.ip_address && <div>IP: {audit.ip_address}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Key config & actions */}
        <div className="space-y-6">
          {/* Key Secret Field */}
          <div className="rounded-2xl border border-border/60 bg-card/30 p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
              Key Preview
            </h3>
            <div className="rounded-xl border border-border/80 bg-background/50 p-4 font-mono text-xs relative pr-12 select-all break-all">
              <span>{apiKey.prefix}</span>
              <button
                onClick={() => copyToClipboard(apiKey.prefix, apiKey.id)}
                className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground transition p-1.5 hover:bg-muted rounded-lg"
              >
                {copiedText ? (
                  <Check className="h-4 w-4 text-emerald-400" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
            <p className="text-[10px] leading-normal text-muted-foreground">
              Use this key value to authorize headers with `X-API-Key: {apiKey.prefix}` or `Authorization: Bearer [secret_key]`.
            </p>
          </div>

          {/* Scope Editor */}
          <div className="rounded-2xl border border-border/60 bg-card/30 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Key Permissions
              </h3>
              {apiKey.status === "active" && scopesChanged && (
                <button
                  id="save-key-scopes"
                  onClick={handleUpdateScopes}
                  disabled={updateApiKeyMutation.isPending}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3 py-1.5 text-xs font-bold text-primary-foreground hover:bg-primary/95 transition"
                >
                  {updateApiKeyMutation.isPending ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Save className="h-3 w-3" />
                  )}
                  Save Changes
                </button>
              )}
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {SCOPES_CONFIG.map((cfg) => {
                const isChecked = selectedScopes.includes(cfg.scope);
                const isKeyActive = apiKey.status === "active";
                return (
                  <div
                    key={cfg.scope}
                    onClick={() => isKeyActive && toggleScope(cfg.scope)}
                    className={`flex items-start gap-3 rounded-xl p-3 border transition ${
                      isKeyActive ? "cursor-pointer" : "opacity-60 cursor-not-allowed"
                    } ${
                      isChecked
                        ? "bg-primary/5 border-primary/50"
                        : "bg-background/40 border-border/50 hover:border-border"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      disabled={!isKeyActive}
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

          {/* Danger Zone */}
          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4" /> Danger Zone
            </h3>
            <p className="text-xs text-muted-foreground leading-normal">
              Rotating, revoking, or deleting keys are immediate, non-reversible actions. Make sure no automated pipelines depend on this credentials before proceeding.
            </p>

            <div className="flex flex-col gap-2 pt-2">
              {apiKey.status === "active" && (
                <>
                  <button
                    id="rotate-key-detail"
                    onClick={() => setShowRotateConfirm(true)}
                    className="w-full flex items-center justify-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/5 py-2.5 text-xs font-semibold text-amber-400 hover:bg-amber-500/10 transition"
                  >
                    <RefreshCw className="h-4 w-4" /> Rotate API Key
                  </button>
                  <button
                    id="revoke-key-detail"
                    onClick={() => setShowRevokeConfirm(true)}
                    className="w-full flex items-center justify-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/5 py-2.5 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition"
                  >
                    <Lock className="h-4 w-4" /> Revoke Key Access
                  </button>
                </>
              )}
              <button
                id="delete-key-detail"
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full flex items-center justify-center gap-2 rounded-xl border border-rose-600 bg-rose-600 py-2.5 text-xs font-semibold text-white hover:bg-rose-700 transition"
              >
                <Trash2 className="h-4 w-4" /> Delete Key Permanently
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ======================================================== */}
      {/* REVEAL NEW SECRET DIALOG                                  */}
      {/* ======================================================== */}
      <AnimatePresence>
        {showNewSecret && (
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
                <h3 className="text-xl font-bold">New Secret Key Generated</h3>
                <p className="text-sm text-muted-foreground">
                  The old secret is now deprecated. Update your configurations using the new credentials:
                </p>
              </div>

              <div className="rounded-xl border border-rose-500/25 bg-rose-500/5 p-4 flex gap-3 text-rose-400">
                <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                <div className="text-xs leading-normal">
                  <span className="font-bold">Security Alert:</span> Store this token safely. Once you close this modal,
                  it will not be shown again.
                </div>
              </div>

              <div className="rounded-xl border border-border/80 bg-background/50 p-4 font-mono text-sm break-all relative pr-12 flex items-center">
                <span>{showNewSecret.secret}</span>
                <button
                  onClick={() => copyToClipboard(showNewSecret.secret, showNewSecret.keyId)}
                  className="absolute right-3 top-3.5 text-muted-foreground hover:text-foreground transition p-1.5 hover:bg-muted rounded-lg"
                >
                  {copiedText ? (
                    <Check className="h-4.5 w-4.5 text-emerald-400" />
                  ) : (
                    <Copy className="h-4.5 w-4.5" />
                  )}
                </button>
              </div>

              <div className="flex justify-center pt-2">
                <button
                  onClick={() => setShowNewSecret(null)}
                  className="w-full rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-lg shadow-primary/20"
                >
                  I have copied the new secret safely
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* ROTATION WARNING DIALOG                                  */}
      {/* ======================================================== */}
      <AnimatePresence>
        {showRotateConfirm && (
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
                You are about to rotate <span className="font-semibold text-foreground">{apiKey.name}</span>.
                Rotating will instantly invalidate the current secret key. Any runners, scripts, or apps using it
                will break immediately.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowRotateConfirm(false)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-rotate-detail"
                  onClick={handleRotate}
                  disabled={rotateApiKeyMutation.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-amber-700 transition"
                >
                  {rotateApiKeyMutation.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  Rotate Key
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* REVOCATION WARNING DIALOG                                 */}
      {/* ======================================================== */}
      <AnimatePresence>
        {showRevokeConfirm && (
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
                You are about to revoke <span className="font-semibold text-foreground">{apiKey.name}</span>.
                This is a permanent security action. All client processes using this key will be blocked immediately.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowRevokeConfirm(false)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-revoke-detail"
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
      {/* DELETION WARNING DIALOG                                  */}
      {/* ======================================================== */}
      <AnimatePresence>
        {showDeleteConfirm && (
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
                Are you sure you want to permanently delete <span className="font-semibold text-foreground">{apiKey.name}</span>?
                This will remove the credential record and all its historical usage analytics logs forever.
              </p>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  id="confirm-delete-detail"
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
