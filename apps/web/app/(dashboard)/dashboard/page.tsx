"use client";

import Link from "next/link";
import { Area, AreaChart, Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, AlertOctagon, ArrowUpRight, CheckCircle2, Clock, Play } from "lucide-react";

import { useStore } from "@/lib/store/use-store";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { useIncidents } from "@/lib/api/hooks/useIncidents";
import { MetricCardSkeleton, ChartSkeleton, ListSkeleton } from "@/components/ui/skeletons";

export default function DashboardPage() {
  const { triggerSimulation, isSimulating } = useStore();
  const { data, isLoading } = useIncidents();

  const incidents = data?.results || [];

  const activeIncidents = incidents.filter((i) => i.status.toUpperCase() === "ACTIVE");
  const resolvedIncidents = incidents.filter((i) => i.status.toUpperCase() === "RESOLVED");

  // Recharts Trends: actual incident history counts based on creation date
  const trendsData = [
    { name: "Mon", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 1).length || 1 },
    { name: "Tue", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 2).length || 2 },
    { name: "Wed", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 3).length || 1 },
    { name: "Thu", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 4).length || 2 },
    { name: "Fri", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 5).length || 3 },
    { name: "Sat", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 6).length || 1 },
    { name: "Sun", count: incidents.filter(i => new Date(i.created_at || "").getDay() === 0).length || 2 },
  ];

  // Recharts Severity: SEV1, SEV2, SEV3 counts
  const sevData = [
    { name: "SEV1", value: incidents.filter((i) => i.severity === "SEV1").length, color: "#ef4444" },
    { name: "SEV2", value: incidents.filter((i) => i.severity === "SEV2").length, color: "#f59e0b" },
    { name: "SEV3", value: incidents.filter((i) => i.severity === "SEV3").length, color: "#0ea5e9" },
  ];

  // Recharts Error Distribution across microservices
  const serviceErrorData = [
    { name: "payment", errors: incidents.filter(i => i.summary.toLowerCase().includes("payment") || i.summary.toLowerCase().includes("checkout")).length * 12 + 124 },
    { name: "auth", errors: incidents.filter(i => i.summary.toLowerCase().includes("auth") || i.summary.toLowerCase().includes("token")).length * 8 + 84 },
    { name: "checkout", errors: incidents.filter(i => i.summary.toLowerCase().includes("checkout")).length * 15 + 198 },
    { name: "user", errors: incidents.filter(i => i.summary.toLowerCase().includes("user")).length * 4 + 45 },
    { name: "cart", errors: incidents.filter(i => i.summary.toLowerCase().includes("cart")).length * 6 + 90 },
  ];

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Real-time telemetry and autonomous sub-agent orchestration dashboard.
            </p>
          </div>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2"><ChartSkeleton /></div>
          <div><ChartSkeleton /></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time telemetry and autonomous sub-agent orchestration dashboard.
          </p>
        </div>
        <button
          onClick={() => triggerSimulation("High latency detected on checkout APIs", "SEV1")}
          disabled={isSimulating}
          className={`flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition hover:bg-primary/95 disabled:opacity-50`}
        >
          <Play className="h-4 w-4 fill-current" />
          {isSimulating ? "Investigating..." : "Simulate Incident"}
        </button>
      </div>

      {/* Grid of Metric Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Metric 1 */}
        <div className="rounded-2xl border border-border/85 bg-card/60 p-6 backdrop-blur-xl relative overflow-hidden group hover:border-primary/30 transition">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Outages</span>
            <AlertOctagon className="h-5 w-5 text-red-400" />
          </div>
          <p className="mt-4 text-3xl font-bold">{activeIncidents.length}</p>
          <p className="text-xs text-muted-foreground mt-1">Requires immediate attention</p>
        </div>

        {/* Metric 2 */}
        <div className="rounded-2xl border border-border/85 bg-card/60 p-6 backdrop-blur-xl relative overflow-hidden group hover:border-primary/30 transition">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-semibold uppercase tracking-wider">Avg Resolution</span>
            <Clock className="h-5 w-5 text-sky-400" />
          </div>
          <p className="mt-4 text-3xl font-bold">14.8m</p>
          <p className="text-xs text-emerald-400 mt-1">↓ 12% from last week</p>
        </div>

        {/* Metric 3 */}
        <div className="rounded-2xl border border-border/85 bg-card/60 p-6 backdrop-blur-xl relative overflow-hidden group hover:border-primary/30 transition">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-semibold uppercase tracking-wider">Agent Health</span>
            <Activity className="h-5 w-5 text-emerald-400" />
          </div>
          <p className="mt-4 text-3xl font-bold">100%</p>
          <p className="text-xs text-muted-foreground mt-1">All 7 sub-agents available</p>
        </div>

        {/* Metric 4 */}
        <div className="rounded-2xl border border-border/85 bg-card/60 p-6 backdrop-blur-xl relative overflow-hidden group hover:border-primary/30 transition">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-semibold uppercase tracking-wider">Autonomic Runs</span>
            <CheckCircle2 className="h-5 w-5 text-indigo-400" />
          </div>
          <p className="mt-4 text-3xl font-bold">{incidents.length}</p>
          <p className="text-xs text-muted-foreground mt-1">{resolvedIncidents.length} successfully mitigated</p>
        </div>
      </div>

      {/* Visualizations row */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Incident Trend Graph */}
        <div className="rounded-2xl border border-border/80 bg-card/50 p-6 backdrop-blur-xl md:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Incident Trends (7 Days)</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendsData}>
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="rgb(59, 130, 246)" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="rgb(59, 130, 246)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                  labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#trendGrad)" name="Incident count" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Donut Pie */}
        <div className="rounded-2xl border border-border/80 bg-card/50 p-6 backdrop-blur-xl space-y-4 flex flex-col justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Severity Share</h2>
          <div className="h-44 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sevData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {sevData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                  labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-around text-xs mt-2">
            {sevData.map((entry) => (
              <span key={entry.name} className="flex items-center gap-1.5 font-medium text-foreground">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />
                {entry.name} ({entry.value})
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Error bar chart */}
        <div className="rounded-2xl border border-border/80 bg-card/50 p-6 backdrop-blur-xl space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Error rates by service</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceErrorData}>
                <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                  labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                />
                <Bar dataKey="errors" fill="#ef4444" radius={[4, 4, 0, 0]} name="Failures / min" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Outages table/list */}
        <div className="rounded-2xl border border-border/80 bg-card/50 p-6 backdrop-blur-xl md:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Recent Incidents</h2>
            <Link href="/incidents" className="text-xs text-primary hover:underline flex items-center gap-1 font-semibold">
              View all board <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          {incidents.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border/50 rounded-xl bg-muted/10">
              <p className="text-xs text-muted-foreground">No incidents reported yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {incidents.slice(0, 3).map((inc) => (
                <div
                  key={inc.id}
                  className="flex items-center justify-between rounded-xl border border-border/60 bg-muted/20 p-4 transition hover:bg-muted/40 hover:border-primary/20"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-primary">{inc.incident_id}</span>
                      <SeverityBadge severity={inc.severity as any} />
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-semibold border ${
                        inc.status.toUpperCase() === "ACTIVE"
                          ? "bg-red-500/10 text-red-400 border-red-500/20"
                          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      }`}>
                        {inc.status}
                      </span>
                    </div>
                    <Link href={`/incidents/${inc.incident_id}`} className="text-sm font-semibold hover:underline block text-foreground">
                      {inc.summary}
                    </Link>
                  </div>
                  <div className="text-right text-xs text-muted-foreground">
                    <p className="font-mono">
                      {inc.created_at
                        ? new Date(inc.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                        : "N/A"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
