"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Puzzle,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  ArrowRight,
  Sparkles,
  Filter,
  ExternalLink,
  Github,
  Gitlab,
  Slack,
  Cloud,
  Container,
  Database,
  Radio,
  Bug,
  Webhook,
  Shield,
  BarChart3,
  MessageSquare,
  X,
  Plus,
  Key,
} from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useIntegrations, useConnectIntegration } from "@/lib/api/hooks/useIntegrations";
import type { IntegrationProvider, IntegrationCategory, ConnectIntegrationPayload } from "@/lib/api/types";

// ─── Logo Mapping ────────────────────────────────────────────────
const LOGO_COLORS: Record<string, string> = {
  Github: "from-zinc-400 to-zinc-600",
  Gitlab: "from-orange-400 to-red-500",
  Bitbucket: "from-blue-400 to-blue-600",
  Slack: "from-purple-400 to-pink-500",
  Microsoft: "from-blue-500 to-cyan-400",
  Discord: "from-indigo-400 to-purple-500",
  PagerDuty: "from-emerald-400 to-green-600",
  Opsgenie: "from-blue-400 to-indigo-500",
  Datadog: "from-violet-400 to-purple-600",
  Grafana: "from-orange-400 to-amber-500",
  Prometheus: "from-red-400 to-orange-500",
  NewRelic: "from-teal-400 to-emerald-500",
  Elasticsearch: "from-yellow-400 to-amber-500",
  Loki: "from-orange-300 to-red-400",
  Splunk: "from-lime-400 to-green-500",
  Aws: "from-amber-400 to-orange-500",
  Azure: "from-blue-400 to-cyan-500",
  Gcp: "from-blue-400 to-red-400",
  Docker: "from-blue-400 to-sky-500",
  Kubernetes: "from-blue-500 to-indigo-500",
  Jira: "from-blue-500 to-indigo-600",
  Linear: "from-violet-400 to-indigo-500",
  Webhook: "from-emerald-400 to-teal-500",
};

const LOGO_INITIALS: Record<string, string> = {
  Github: "GH", Gitlab: "GL", Bitbucket: "BB", Slack: "SL",
  Microsoft: "MS", Discord: "DC", PagerDuty: "PD", Opsgenie: "OG",
  Datadog: "DD", Grafana: "GF", Prometheus: "PM", NewRelic: "NR",
  Elasticsearch: "ES", Loki: "LK", Splunk: "SP", Aws: "AW",
  Azure: "AZ", Gcp: "GC", Docker: "DK", Kubernetes: "K8",
  Jira: "JR", Linear: "LN", Webhook: "WH",
};

const CATEGORY_ICONS: Record<string, any> = {
  "Source Control": Github,
  Communication: MessageSquare,
  "Incident Management": Shield,
  Monitoring: BarChart3,
  Logging: Database,
  Cloud: Cloud,
  Containers: Container,
  "Issue Tracking": Bug,
  General: Webhook,
};

const ALL_CATEGORIES: IntegrationCategory[] = [
  "Source Control",
  "Communication",
  "Incident Management",
  "Monitoring",
  "Logging",
  "Cloud",
  "Containers",
  "Issue Tracking",
  "General",
];

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { bg: string; text: string; dot: string; label: string }> = {
    connected: { bg: "bg-emerald-500/10", text: "text-emerald-400", dot: "bg-emerald-400", label: "Connected" },
    disconnected: { bg: "bg-zinc-500/10", text: "text-zinc-400", dot: "bg-zinc-500", label: "Disconnected" },
    error: { bg: "bg-rose-500/10", text: "text-rose-400", dot: "bg-rose-400", label: "Error" },
    available: { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-400", label: "Available" },
    coming_soon: { bg: "bg-amber-500/10", text: "text-amber-400", dot: "bg-amber-400", label: "Coming Soon" },
    beta: { bg: "bg-violet-500/10", text: "text-violet-400", dot: "bg-violet-400", label: "Beta" },
    disabled: { bg: "bg-zinc-500/10", text: "text-zinc-500", dot: "bg-zinc-500", label: "Disabled" },
    syncing: { bg: "bg-sky-500/10", text: "text-sky-400", dot: "bg-sky-400 animate-pulse", label: "Syncing" },
  };
  const fallback = { bg: "bg-blue-500/10", text: "text-blue-400", dot: "bg-blue-400", label: "Available" };
  const c = cfg[status] || fallback;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-lg px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${c.bg} ${c.text} border border-current/10`}>
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}

function IntegrationLogo({ logo, size = "md" }: { logo: string; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "h-8 w-8 text-[10px]", md: "h-10 w-10 text-xs", lg: "h-14 w-14 text-sm" };
  const gradient = LOGO_COLORS[logo] || "from-primary/60 to-accent/60";
  const initials = LOGO_INITIALS[logo] || logo.slice(0, 2).toUpperCase();

  return (
    <div className={`${sizes[size]} shrink-0 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center font-black text-white shadow-lg shadow-black/20`}>
      {initials}
    </div>
  );
}

export default function IntegrationsPage() {
  const router = useRouter();
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id || null;

  const { data: providers, isLoading } = useIntegrations(workspaceId);
  const connectMutation = useConnectIntegration();

  // UI state
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [activeFilter, setActiveFilter] = useState<"all" | "connected" | "available">("all");
  const [connectDialogProvider, setConnectDialogProvider] = useState<IntegrationProvider | null>(null);

  // Connect form state
  const [formFields, setFormFields] = useState<Record<string, string>>({});

  // Filtered and categorized providers
  const filteredProviders = useMemo(() => {
    if (!providers) return [];
    return providers.filter((p) => {
      const matchesSearch =
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.description.toLowerCase().includes(search.toLowerCase()) ||
        p.category.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = activeCategory === "all" || p.category === activeCategory;
      const matchesFilter =
        activeFilter === "all" ||
        (activeFilter === "connected" && p.connection?.status === "connected") ||
        (activeFilter === "available" && (!p.connection || p.connection.status !== "connected"));
      return matchesSearch && matchesCategory && matchesFilter;
    });
  }, [providers, search, activeCategory, activeFilter]);

  const connectedCount = providers?.filter((p) => p.connection?.status === "connected").length || 0;
  const availableCount = providers?.filter((p) => p.status === "available" && (!p.connection || p.connection.status !== "connected")).length || 0;

  const handleOpenConnectDialog = (provider: IntegrationProvider) => {
    if (provider.status === "coming_soon") return;
    if (provider.connection?.status === "connected") {
      router.push(`/settings/integrations/${provider.id}`);
      return;
    }
    setFormFields({});
    setConnectDialogProvider(provider);
  };

  const handleConnect = async () => {
    if (!connectDialogProvider || !workspaceId) return;
    try {
      await connectMutation.mutateAsync({
        workspaceId,
        payload: {
          provider_id: connectDialogProvider.id,
          config: {},
          credentials: formFields,
        },
      });
      setConnectDialogProvider(null);
      setFormFields({});
    } catch (err) {
      console.error("Connection failed:", err);
    }
  };

  // ─── NO WORKSPACE SELECTED ────────────────────────────────────
  if (!activeWorkspace) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
        <Puzzle className="h-12 w-12 text-muted-foreground animate-pulse" />
        <h2 className="text-lg font-semibold">No Workspace Selected</h2>
        <p className="text-sm text-muted-foreground max-w-sm">
          Please select a workspace from the sidebar to browse and configure integrations.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-7xl"
    >
      {/* ═══════════════════════════════════════════════════════ */}
      {/* HEADER                                                  */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="relative overflow-hidden rounded-2xl border border-border/40 bg-gradient-to-br from-primary/5 via-card/60 to-accent/5 p-8">
        <div className="absolute -top-20 -right-20 h-56 w-56 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-16 -left-16 h-40 w-40 rounded-full bg-accent/5 blur-3xl" />
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="rounded-xl bg-primary/10 p-2.5 border border-primary/20">
                <Puzzle className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-3xl font-bold tracking-tight">Integrations Marketplace</h1>
            </div>
            <p className="text-sm text-muted-foreground max-w-lg mt-1">
              Connect your DevOps stack to Sentinel AI. Synchronize logs, metrics, alerts, and deployments from 20+ enterprise-grade providers.
            </p>
          </div>
          <div className="flex items-center gap-3 self-start">
            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-2.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-sm font-bold text-emerald-400">{connectedCount}</span>
              <span className="text-xs text-emerald-400/70">connected</span>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-blue-500/20 bg-blue-500/5 px-4 py-2.5">
              <Zap className="h-4 w-4 text-blue-400" />
              <span className="text-sm font-bold text-blue-400">{availableCount}</span>
              <span className="text-xs text-blue-400/70">available</span>
            </div>
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* TOOLBAR                                                 */}
      {/* ═══════════════════════════════════════════════════════ */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4">
        {/* Search */}
        <div className="relative w-full lg:max-w-xs">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground" />
          <input
            id="integrations-search"
            type="text"
            placeholder="Search integrations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-border/60 bg-card/40 px-10 py-2.5 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition placeholder:text-muted-foreground/50"
          />
        </div>

        {/* Status Filter Buttons */}
        <div className="flex items-center gap-1.5">
          {(["all", "connected", "available"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`rounded-xl px-4 py-2 text-xs font-semibold uppercase tracking-wider transition ${
                activeFilter === f
                  ? "bg-muted text-foreground border border-border/80"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Category Tabs (scrollable) */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 ml-auto scrollbar-none">
          <button
            onClick={() => setActiveCategory("all")}
            className={`whitespace-nowrap rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
              activeCategory === "all"
                ? "bg-primary/10 text-primary border border-primary/20"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
            }`}
          >
            All
          </button>
          {ALL_CATEGORIES.map((cat) => {
            const Icon = CATEGORY_ICONS[cat] || Puzzle;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`whitespace-nowrap flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                  activeCategory === cat
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/30"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════ */}
      {/* INTEGRATION GRID                                        */}
      {/* ═══════════════════════════════════════════════════════ */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="h-8 w-8 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground font-medium">Querying integration registries...</p>
        </div>
      ) : filteredProviders.length === 0 ? (
        <div className="rounded-2xl border border-border/60 bg-card/25 p-12 text-center flex flex-col items-center justify-center space-y-4">
          <div className="rounded-full bg-primary/10 p-4 text-primary">
            <Search className="h-8 w-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold">No Integrations Found</h3>
            <p className="text-sm text-muted-foreground mt-1 max-w-sm">
              Try a different search keyword or category filter.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredProviders.map((provider, idx) => {
            const isConnected = provider.connection?.status === "connected";
            const isComingSoon = provider.status === "coming_soon";
            const hasError = provider.connection?.status === "error";

            return (
              <motion.div
                key={provider.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.03, duration: 0.3 }}
                onClick={() => handleOpenConnectDialog(provider)}
                className={`group relative rounded-2xl border bg-card/30 backdrop-blur-sm p-5 cursor-pointer transition-all duration-300 hover:shadow-xl hover:shadow-black/10 ${
                  isConnected
                    ? "border-emerald-500/25 hover:border-emerald-500/40 bg-emerald-500/[0.02]"
                    : hasError
                    ? "border-rose-500/25 hover:border-rose-500/40"
                    : isComingSoon
                    ? "border-border/30 opacity-60 cursor-default"
                    : "border-border/50 hover:border-primary/30"
                }`}
              >
                {/* Connected glow */}
                {isConnected && (
                  <div className="absolute -top-px -left-px -right-px h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent" />
                )}

                <div className="flex items-start gap-4">
                  <IntegrationLogo logo={provider.logo} />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-sm font-bold text-foreground truncate">{provider.name}</h3>
                      <StatusBadge status={isConnected ? "connected" : hasError ? "error" : provider.status} />
                    </div>

                    <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2 mb-3">
                      {provider.description}
                    </p>

                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider">
                        {provider.category}
                      </span>
                      {provider.is_oauth_supported && (
                        <span className="text-[10px] font-semibold text-primary/60 uppercase tracking-wider flex items-center gap-1">
                          <Key className="h-2.5 w-2.5" />
                          OAuth
                        </span>
                      )}
                      <span className="text-[10px] font-medium text-muted-foreground/40 ml-auto flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {isConnected ? "Configure" : isComingSoon ? "Notify Me" : "Connect"}
                        <ArrowRight className="h-3 w-3" />
                      </span>
                    </div>
                  </div>
                </div>

                {/* Sync indicator for connected */}
                {isConnected && provider.connection?.last_sync_at && (
                  <div className="mt-3 pt-3 border-t border-border/30 flex items-center gap-2 text-[10px] text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    Last sync: {new Date(provider.connection.last_sync_at).toLocaleDateString()}
                    {provider.connection.is_enabled && (
                      <span className="ml-auto flex items-center gap-1 text-emerald-400">
                        <Radio className="h-2.5 w-2.5 animate-pulse" />
                        Live
                      </span>
                    )}
                  </div>
                )}

                {/* Error indicator */}
                {hasError && provider.connection?.error_message && (
                  <div className="mt-3 pt-3 border-t border-rose-500/20 flex items-center gap-2 text-[10px] text-rose-400">
                    <XCircle className="h-3 w-3" />
                    <span className="truncate">{provider.connection.error_message}</span>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════ */}
      {/* CONNECT DIALOG                                          */}
      {/* ═══════════════════════════════════════════════════════ */}
      <AnimatePresence>
        {connectDialogProvider && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-lg rounded-2xl border border-border/80 bg-card p-6 shadow-2xl space-y-6"
            >
              {/* Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <IntegrationLogo logo={connectDialogProvider.logo} size="lg" />
                  <div>
                    <h3 className="text-lg font-bold">Connect {connectDialogProvider.name}</h3>
                    <p className="text-xs text-muted-foreground">{connectDialogProvider.category}</p>
                  </div>
                </div>
                <button
                  onClick={() => setConnectDialogProvider(null)}
                  className="text-muted-foreground hover:text-foreground transition p-1.5 hover:bg-muted rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Description */}
              <div className="rounded-xl border border-border/40 bg-muted/20 p-4">
                <p className="text-xs text-muted-foreground leading-relaxed">{connectDialogProvider.description}</p>
              </div>

              {/* Credential Fields */}
              <div className="space-y-4">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  Authentication Credentials
                </label>

                {connectDialogProvider.is_oauth_supported ? (
                  <div className="space-y-3">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-semibold text-muted-foreground">Client ID</label>
                      <input
                        type="text"
                        placeholder="Enter OAuth Client ID"
                        value={formFields.client_id || ""}
                        onChange={(e) => setFormFields({ ...formFields, client_id: e.target.value })}
                        className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                      />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-semibold text-muted-foreground">Client Secret</label>
                      <input
                        type="password"
                        placeholder="Enter OAuth Client Secret"
                        value={formFields.client_secret || ""}
                        onChange={(e) => setFormFields({ ...formFields, client_secret: e.target.value })}
                        className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-semibold text-muted-foreground">API Key / Token</label>
                      <input
                        type="password"
                        placeholder={`Enter your ${connectDialogProvider.name} API key`}
                        value={formFields.api_key || ""}
                        onChange={(e) => setFormFields({ ...formFields, api_key: e.target.value })}
                        className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                      />
                    </div>
                    {(connectDialogProvider.key === "datadog" ||
                      connectDialogProvider.key === "aws" ||
                      connectDialogProvider.key === "grafana") && (
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-semibold text-muted-foreground">
                          {connectDialogProvider.key === "aws" ? "Secret Access Key" : "Application Key"}
                        </label>
                        <input
                          type="password"
                          placeholder="Enter secondary credential"
                          value={formFields.app_key || ""}
                          onChange={(e) => setFormFields({ ...formFields, app_key: e.target.value })}
                          className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm outline-none focus:border-primary transition"
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Sync frequency */}
              <div className="flex items-center justify-between rounded-xl border border-border/40 bg-muted/10 p-3">
                <div className="text-xs">
                  <span className="font-semibold text-muted-foreground">Sync Frequency:</span>{" "}
                  <span className="font-bold text-foreground capitalize">{connectDialogProvider.default_sync_frequency}</span>
                </div>
                <Clock className="h-4 w-4 text-muted-foreground/50" />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-2 border-t border-border/60">
                <button
                  type="button"
                  onClick={() => setConnectDialogProvider(null)}
                  className="rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-muted transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConnect}
                  disabled={connectMutation.isPending}
                  className="flex items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/95 transition shadow-lg shadow-primary/20"
                >
                  {connectMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                  Connect Integration
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
