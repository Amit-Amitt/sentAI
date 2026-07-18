"use client";

import { useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AlertTriangle, Clock, Database, FileText, GitCommit, LineChart, MessageSquare, Terminal } from "lucide-react";

interface EvidenceViewerProps {
  logs: string;
  metrics: string;
  deployment_history: string;
  customer_reports: string;
}

export function EvidenceViewer({
  logs,
  metrics,
  deployment_history,
  customer_reports
}: EvidenceViewerProps) {
  const [activeTab, setActiveTab] = useState<"logs" | "metrics" | "deploys" | "tickets">("logs");

  // Simulated metrics time-series data for recharts
  const metricData = [
    { time: "00:00", value: 32, baseline: 30 },
    { time: "00:10", value: 35, baseline: 30 },
    { time: "00:20", value: 34, baseline: 30 },
    { time: "00:30", value: 38, baseline: 30 },
    { time: "00:40", value: 45, baseline: 31 },
    { time: "00:50", value: 89, baseline: 30 }, // Spikes here
    { time: "01:00", value: 100, baseline: 30 },
    { time: "01:10", value: 98, baseline: 29 },
  ];

  return (
    <div className="rounded-2xl border border-border/80 bg-card/60 backdrop-blur-xl overflow-hidden">
      {/* Tab Headers */}
      <div className="flex border-b border-border/70 bg-muted/20 px-4">
        {[
          { id: "logs", label: "Log Analyzer", icon: Terminal },
          { id: "metrics", label: "Metrics Stream", icon: LineChart },
          { id: "deploys", label: "Change Logs", icon: GitCommit },
          { id: "tickets", label: "Customer Reports", icon: MessageSquare },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 border-b-2 px-4 py-4 text-xs font-semibold uppercase tracking-wider transition ${
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Body */}
      <div className="p-6 min-h-[300px]">
        {activeTab === "logs" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5 font-mono"><Clock className="h-3.5 w-3.5" /> Aggregated log trace (UTC)</span>
              <span className="rounded bg-muted/60 px-1.5 py-0.5">Found 84 matches</span>
            </div>
            <pre className="overflow-x-auto rounded-xl bg-background/90 p-4 font-mono text-xs leading-relaxed text-slate-300 border border-border/50 max-h-[300px]">
              {logs || "No log traces aggregated for this incident."}
            </pre>
          </div>
        )}

        {activeTab === "metrics" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5 font-mono"><Database className="h-3.5 w-3.5" /> db_connections_active vs baseline</span>
              <span className="text-red-400 font-semibold flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5" /> Saturation threshold exceeded</span>
            </div>
            <div className="h-60 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricData}>
                  <defs>
                    <linearGradient id="metricGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="rgb(239, 68, 68)" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="rgb(239, 68, 68)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#52525b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#52525b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                    labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#metricGrad)" name="Active connections" />
                  <Area type="monotone" dataKey="baseline" stroke="#52525b" strokeWidth={1} strokeDasharray="4 4" fill="none" name="Baseline" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === "deploys" && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-foreground font-semibold">
              <GitCommit className="h-5 w-5 text-primary" />
              Recent Infrastructure / Application Releases
            </div>
            <div className="relative border-l border-border/80 pl-6 space-y-6">
              {deployment_history ? (
                deployment_history.split("\n").map((line, idx) => (
                  <div key={idx} className="relative">
                    <span className="absolute -left-[31px] mt-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-background border-2 border-primary" />
                    <p className="text-xs font-mono text-muted-foreground">{line.substring(0, 20)}</p>
                    <p className="text-sm font-medium text-foreground mt-1">{line.substring(21)}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No recent deployments registered in timeline cache.</p>
              )}
            </div>
          </div>
        )}

        {activeTab === "tickets" && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-foreground font-semibold">
              <MessageSquare className="h-5 w-5 text-amber-500" />
              Clustered Customer Support & Issue Reports
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-border/70 bg-background/50 p-4 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-mono text-muted-foreground">Ticket #38294</span>
                  <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-medium text-red-400">Critical</span>
                </div>
                <p className="text-sm font-semibold">"Checkout stuck spinner"</p>
                <p className="text-xs text-muted-foreground">User reports the payment spinner spins indefinitely without updating or completing the order.</p>
              </div>
              <div className="rounded-xl border border-border/70 bg-background/50 p-4 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-mono text-muted-foreground">Ticket #38291</span>
                  <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-medium text-red-400">Critical</span>
                </div>
                <p className="text-sm font-semibold">"Payment checkout hangs"</p>
                <p className="text-xs text-muted-foreground">Customer support reports checkout operations are crashing with 500 server errors.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
export default EvidenceViewer;
