"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft, CheckCircle2, XCircle, Loader2, RefreshCw, Zap, Clock,
  Trash2, Power, PowerOff, Activity, Settings, FileText, Webhook,
  Shield, Radio, X, AlertTriangle, BarChart3, ExternalLink, Key,
} from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import {
  useIntegration, useDisconnectIntegration, useDeleteIntegration,
  useTestConnection, useTriggerSync, useIntegrationHistory,
} from "@/lib/api/hooks/useIntegrations";

const LOGO_COLORS: Record<string, string> = {
  Github: "from-zinc-400 to-zinc-600", Gitlab: "from-orange-400 to-red-500",
  Slack: "from-purple-400 to-pink-500", Microsoft: "from-blue-500 to-cyan-400",
  Discord: "from-indigo-400 to-purple-500", PagerDuty: "from-emerald-400 to-green-600",
  Datadog: "from-violet-400 to-purple-600", Grafana: "from-orange-400 to-amber-500",
  Prometheus: "from-red-400 to-orange-500", Elasticsearch: "from-yellow-400 to-amber-500",
  Loki: "from-orange-300 to-red-400", Aws: "from-amber-400 to-orange-500",
  Azure: "from-blue-400 to-cyan-500", Gcp: "from-blue-400 to-red-400",
  Kubernetes: "from-blue-500 to-indigo-500", Jira: "from-blue-500 to-indigo-600",
  Linear: "from-violet-400 to-indigo-500", Webhook: "from-emerald-400 to-teal-500",
  Docker: "from-blue-400 to-sky-500", Bitbucket: "from-blue-400 to-blue-600",
  Opsgenie: "from-blue-400 to-indigo-500", NewRelic: "from-teal-400 to-emerald-500",
  Splunk: "from-lime-400 to-green-500",
};
const LOGO_INITIALS: Record<string, string> = {
  Github: "GH", Gitlab: "GL", Bitbucket: "BB", Slack: "SL", Microsoft: "MS",
  Discord: "DC", PagerDuty: "PD", Opsgenie: "OG", Datadog: "DD", Grafana: "GF",
  Prometheus: "PM", NewRelic: "NR", Elasticsearch: "ES", Loki: "LK", Splunk: "SP",
  Aws: "AW", Azure: "AZ", Gcp: "GC", Docker: "DK", Kubernetes: "K8",
  Jira: "JR", Linear: "LN", Webhook: "WH",
};

type TabKey = "overview" | "health" | "sync" | "webhooks" | "audit";
const TABS: { key: TabKey; label: string; icon: any }[] = [
  { key: "overview", label: "Overview", icon: FileText },
  { key: "health", label: "Health", icon: Activity },
  { key: "sync", label: "Sync History", icon: RefreshCw },
  { key: "webhooks", label: "Webhooks", icon: Webhook },
  { key: "audit", label: "Audit Logs", icon: Shield },
];

export default function IntegrationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { activeWorkspace } = useOrgStore();
  const wsId = activeWorkspace?.id || null;

  const { data: provider, isLoading, refetch } = useIntegration(id, wsId);
  const { data: history } = useIntegrationHistory(provider?.connection?.id, wsId);
  const disconnectMut = useDisconnectIntegration();
  const deleteMut = useDeleteIntegration();
  const testMut = useTestConnection();
  const syncMut = useTriggerSync();

  const [tab, setTab] = useState<TabKey>("overview");
  const [showDelete, setShowDelete] = useState(false);
  const [showDisconnect, setShowDisconnect] = useState(false);

  const conn = provider?.connection;
  const isConnected = conn?.status === "connected";
  const gradient = LOGO_COLORS[provider?.logo || ""] || "from-primary/60 to-accent/60";
  const initials = LOGO_INITIALS[provider?.logo || ""] || "??";

  const handleTest = async () => {
    if (!conn || !wsId) return;
    await testMut.mutateAsync({ connectionId: conn.id, workspaceId: wsId });
    refetch();
  };

  const handleSync = async () => {
    if (!conn || !wsId) return;
    await syncMut.mutateAsync({ connectionId: conn.id, workspaceId: wsId });
    refetch();
  };

  const handleDisconnect = async () => {
    if (!conn || !wsId) return;
    await disconnectMut.mutateAsync({ connectionId: conn.id, workspaceId: wsId });
    setShowDisconnect(false);
    refetch();
  };

  const handleDelete = async () => {
    if (!conn || !wsId) return;
    await deleteMut.mutateAsync({ connectionId: conn.id, workspaceId: wsId });
    setShowDelete(false);
    router.push("/settings/integrations");
  };

  if (isLoading || !provider) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-medium">Loading integration details...</p>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-5xl">
      {/* Back */}
      <button onClick={() => router.push("/settings/integrations")} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition">
        <ArrowLeft className="h-4 w-4" /> Back to Marketplace
      </button>

      {/* Header Card */}
      <div className="relative overflow-hidden rounded-2xl border border-border/40 bg-gradient-to-br from-card/80 to-card/40 p-6">
        <div className="absolute -top-16 -right-16 h-40 w-40 rounded-full bg-primary/5 blur-3xl" />
        <div className="relative z-10 flex flex-col sm:flex-row items-start gap-5">
          <div className={`h-16 w-16 shrink-0 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center font-black text-white text-lg shadow-xl shadow-black/20`}>
            {initials}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold tracking-tight">{provider.name}</h1>
              <span className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider border ${
                isConnected ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                conn?.status === "error" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" :
                conn?.status === "disconnected" ? "bg-zinc-500/10 text-zinc-400 border-zinc-500/20" :
                "bg-blue-500/10 text-blue-400 border-blue-500/20"
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? "bg-emerald-400" : conn?.status === "error" ? "bg-rose-400" : "bg-blue-400"}`} />
                {conn?.status || provider.status}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">{provider.description}</p>
            <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground/60">
              <span className="font-semibold uppercase tracking-wider">{provider.category}</span>
              <span>Sync: <span className="text-foreground/80 capitalize">{provider.default_sync_frequency}</span></span>
              {provider.is_oauth_supported && <span className="flex items-center gap-1"><Key className="h-3 w-3" /> OAuth</span>}
            </div>
          </div>

          {/* Actions */}
          {conn && (
            <div className="flex items-center gap-2 shrink-0">
              <button onClick={handleTest} disabled={testMut.isPending}
                className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card/50 px-4 py-2 text-xs font-semibold hover:bg-muted/40 transition">
                {testMut.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5 text-amber-400" />} Test
              </button>
              <button onClick={handleSync} disabled={syncMut.isPending}
                className="flex items-center gap-1.5 rounded-xl border border-border/60 bg-card/50 px-4 py-2 text-xs font-semibold hover:bg-muted/40 transition">
                {syncMut.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5 text-blue-400" />} Sync
              </button>
              {isConnected ? (
                <button onClick={() => setShowDisconnect(true)}
                  className="flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/5 px-4 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition">
                  <PowerOff className="h-3.5 w-3.5" /> Disconnect
                </button>
              ) : (
                <button onClick={() => setShowDelete(true)}
                  className="flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/5 px-4 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition">
                  <Trash2 className="h-3.5 w-3.5" /> Delete
                </button>
              )}
            </div>
          )}
        </div>

        {/* Test result banner */}
        <AnimatePresence>
          {testMut.data && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mt-4">
              <div className={`rounded-xl border p-4 flex items-center gap-3 ${testMut.data.success ? "border-emerald-500/25 bg-emerald-500/5 text-emerald-400" : "border-rose-500/25 bg-rose-500/5 text-rose-400"}`}>
                {testMut.data.success ? <CheckCircle2 className="h-5 w-5 shrink-0" /> : <XCircle className="h-5 w-5 shrink-0" />}
                <div className="flex-1"><p className="text-xs font-semibold">{testMut.data.message}</p></div>
                <span className="text-[10px] font-mono">{testMut.data.latency_ms}ms</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Sync result banner */}
        <AnimatePresence>
          {syncMut.data && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mt-4">
              <div className={`rounded-xl border p-4 flex items-center gap-3 ${syncMut.data.success ? "border-blue-500/25 bg-blue-500/5 text-blue-400" : "border-rose-500/25 bg-rose-500/5 text-rose-400"}`}>
                {syncMut.data.success ? <CheckCircle2 className="h-5 w-5 shrink-0" /> : <XCircle className="h-5 w-5 shrink-0" />}
                <p className="text-xs font-semibold flex-1">{syncMut.data.message}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-border/40 pb-px">
        {TABS.map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold transition border-b-2 -mb-px ${
                tab === t.key ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}>
              <Icon className="h-3.5 w-3.5" /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="min-h-[300px]">
        {/* Overview */}
        {tab === "overview" && (
          <div className="space-y-6">
            <div className="rounded-2xl border border-border/40 bg-card/30 p-6">
              <h3 className="text-sm font-bold mb-3">About this Integration</h3>
              <div className="prose prose-invert prose-sm max-w-none text-muted-foreground text-xs leading-relaxed whitespace-pre-line">
                {provider.overview}
              </div>
            </div>
            {conn && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Status", value: conn.status, color: isConnected ? "text-emerald-400" : "text-rose-400" },
                  { label: "Last Sync", value: conn.last_sync_at ? new Date(conn.last_sync_at).toLocaleString() : "Never", color: "text-foreground" },
                  { label: "Connected Since", value: new Date(conn.created_at).toLocaleDateString(), color: "text-foreground" },
                  { label: "Credentials", value: `${conn.credentials.length} stored`, color: "text-foreground" },
                ].map((s) => (
                  <div key={s.label} className="rounded-xl border border-border/40 bg-card/20 p-4">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/50 mb-1">{s.label}</p>
                    <p className={`text-sm font-bold capitalize ${s.color}`}>{s.value}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Health */}
        {tab === "health" && conn && (
          <div className="space-y-4">
            <div className="rounded-2xl border border-border/40 bg-card/30 p-6 text-center space-y-4">
              <div className={`inline-flex rounded-full p-4 ${isConnected ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
                {isConnected ? <CheckCircle2 className="h-10 w-10" /> : <XCircle className="h-10 w-10" />}
              </div>
              <h3 className="text-lg font-bold">{isConnected ? "Connection Healthy" : "Connection Issues Detected"}</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                {isConnected ? "All systems operational. Last health check passed successfully." : conn.error_message || "Connection test required."}
              </p>
              <button onClick={handleTest} disabled={testMut.isPending}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition">
                {testMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />} Run Health Check
              </button>
            </div>
          </div>
        )}

        {/* Sync History */}
        {tab === "sync" && (
          <div className="rounded-2xl border border-border/40 bg-card/30 overflow-hidden">
            {!history?.syncs?.length ? (
              <div className="p-12 text-center text-sm text-muted-foreground">No sync history available.</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border/40 bg-card/50 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    <th className="px-5 py-3">Status</th><th className="px-5 py-3">Started</th>
                    <th className="px-5 py-3">Duration</th><th className="px-5 py-3">Resources</th><th className="px-5 py-3">Errors</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30 text-xs">
                  {history.syncs.map((s) => (
                    <tr key={s.id} className="hover:bg-muted/10 transition">
                      <td className="px-5 py-3">
                        <span className={`inline-flex items-center gap-1.5 rounded-lg px-2 py-0.5 text-[10px] font-bold uppercase ${
                          s.status === "success" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                        }`}>
                          {s.status === "success" ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                          {s.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-muted-foreground">{new Date(s.started_at).toLocaleString()}</td>
                      <td className="px-5 py-3 font-mono">{s.duration_ms}ms</td>
                      <td className="px-5 py-3 font-bold">{s.imported_resources}</td>
                      <td className="px-5 py-3">{s.errors.length > 0 ? <span className="text-rose-400">{s.errors.length} error(s)</span> : <span className="text-muted-foreground/50">—</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Webhooks */}
        {tab === "webhooks" && (
          <div className="space-y-4">
            {!conn?.webhooks?.length ? (
              <div className="rounded-2xl border border-border/40 bg-card/30 p-12 text-center text-sm text-muted-foreground">No webhooks configured.</div>
            ) : conn.webhooks.map((wh) => (
              <div key={wh.id} className="rounded-2xl border border-border/40 bg-card/30 p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Webhook className="h-5 w-5 text-primary" />
                    <div><h4 className="text-sm font-bold">{wh.name}</h4><p className="text-[10px] text-muted-foreground uppercase">{wh.direction}</p></div>
                  </div>
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-lg ${wh.status === "active" ? "bg-emerald-500/10 text-emerald-400" : "bg-zinc-500/10 text-zinc-400"}`}>{wh.status}</span>
                </div>
                <div className="rounded-xl bg-background/50 border border-border/30 p-3 font-mono text-xs text-muted-foreground break-all">{wh.url}</div>
                {wh.secret && <div className="text-[10px] text-muted-foreground">Secret: <code className="bg-muted/30 px-1.5 py-0.5 rounded">{wh.secret.slice(0, 12)}••••••</code></div>}
                {wh.delivery_history.length > 0 && (
                  <div className="border-t border-border/30 pt-3">
                    <p className="text-[10px] font-bold uppercase text-muted-foreground/50 mb-2">Recent Deliveries</p>
                    <div className="space-y-1">
                      {wh.delivery_history.slice(0, 5).map((d) => (
                        <div key={d.id} className="flex items-center gap-3 text-[10px] text-muted-foreground">
                          {d.status === "success" ? <CheckCircle2 className="h-3 w-3 text-emerald-400" /> : <XCircle className="h-3 w-3 text-rose-400" />}
                          <span className="font-mono">{d.response_code}</span>
                          <span>{new Date(d.timestamp).toLocaleString()}</span>
                          <span className="ml-auto font-mono">{d.payload_size_bytes}B</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Audit Logs */}
        {tab === "audit" && (
          <div className="rounded-2xl border border-border/40 bg-card/30 overflow-hidden">
            {!history?.audits?.length ? (
              <div className="p-12 text-center text-sm text-muted-foreground">No audit history available.</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border/40 bg-card/50 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    <th className="px-5 py-3">Action</th><th className="px-5 py-3">Performed By</th>
                    <th className="px-5 py-3">Details</th><th className="px-5 py-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30 text-xs">
                  {history.audits.map((a) => (
                    <tr key={a.id} className="hover:bg-muted/10 transition">
                      <td className="px-5 py-3"><span className="inline-flex items-center gap-1.5 rounded-lg bg-primary/10 text-primary px-2 py-0.5 text-[10px] font-bold uppercase">{a.action}</span></td>
                      <td className="px-5 py-3 text-muted-foreground">{a.performed_by_name || "System"}</td>
                      <td className="px-5 py-3 text-muted-foreground font-mono text-[10px]">{JSON.stringify(a.details).slice(0, 60)}</td>
                      <td className="px-5 py-3 text-muted-foreground">{new Date(a.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      {/* Disconnect Dialog */}
      <AnimatePresence>
        {showDisconnect && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5">
              <div className="flex items-center gap-3 text-amber-500">
                <div className="rounded-full bg-amber-500/10 p-2 border border-amber-500/20"><PowerOff className="h-5 w-5" /></div>
                <h3 className="text-lg font-bold">Disconnect {provider.name}?</h3>
              </div>
              <p className="text-sm text-muted-foreground">This will deactivate the connection. Credentials will be preserved for reconnection.</p>
              <div className="flex justify-end gap-3 pt-2">
                <button onClick={() => setShowDisconnect(false)} className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition">Cancel</button>
                <button onClick={handleDisconnect} disabled={disconnectMut.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-amber-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-amber-700 transition">
                  {disconnectMut.isPending && <Loader2 className="h-4 w-4 animate-spin" />} Disconnect
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Delete Dialog */}
      <AnimatePresence>
        {showDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-5">
              <div className="flex items-center gap-3 text-rose-500">
                <div className="rounded-full bg-rose-500/10 p-2 border border-rose-500/20"><Trash2 className="h-5 w-5" /></div>
                <h3 className="text-lg font-bold">Delete {provider.name}?</h3>
              </div>
              <p className="text-sm text-muted-foreground">This permanently removes the connection, credentials, webhooks, and all sync history.</p>
              <div className="flex justify-end gap-3 pt-2">
                <button onClick={() => setShowDelete(false)} className="rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-muted transition">Cancel</button>
                <button onClick={handleDelete} disabled={deleteMut.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-700 transition">
                  {deleteMut.isPending && <Loader2 className="h-4 w-4 animate-spin" />} Delete Permanently
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
