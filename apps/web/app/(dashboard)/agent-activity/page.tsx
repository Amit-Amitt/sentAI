"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, Bot, Cpu, GitBranch, Play, RefreshCw, Zap } from "lucide-react";
import Link from "next/link";

import { useStore } from "@/lib/store/use-store";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import { useIncidents } from "@/lib/api/hooks/useIncidents";
import { useIncident } from "@/lib/api/hooks/useIncident";
import { ListSkeleton } from "@/components/ui/skeletons";

const getCompletedAgentsForSimulation = (activeAgent: string | null, targetAgent: string) => {
  if (!activeAgent) return false;
  const order = ["Coordinator", "Ingestion", "Analysis", "Recommendation Agent"];
  
  const getGroup = (agent: string) => {
    if (agent === "Coordinator") return "Coordinator";
    if (["Deployment Agent", "Log Agent", "Metrics Agent"].includes(agent)) return "Ingestion";
    if (["Review Agent", "Root Cause Agent"].includes(agent)) return "Analysis";
    return "Recommendation Agent";
  };
  
  const activeGroup = getGroup(activeAgent);
  const targetGroup = getGroup(targetAgent);
  
  const activeIdx = order.indexOf(activeGroup);
  const targetIdx = order.indexOf(targetGroup);
  
  return targetIdx < activeIdx;
};

export default function AgentActivityPage() {
  const { selectedIncidentId, isSimulating, activeSimulationAgent } = useStore();
  const { data: incidentsData } = useIncidents();
  const incidents = incidentsData?.results || [];

  const targetIncidentId = selectedIncidentId || incidents[0]?.incident_id;
  const { data: selectedIncident, isLoading } = useIncident(targetIncidentId);

  // Recharts Chart Data: Latency of each agent run
  const chartData = selectedIncident
    ? Object.entries(selectedIncident.agents).map(([name, data]) => ({
        name: name.replace(" Agent", ""),
        latency: data.duration_ms,
        confidence: Math.round(data.confidence * 100)
      }))
    : [];

  // Graph levels for visual representation
  const levels = [
    { name: "Level 1: Orchestration", agents: ["Coordinator"] },
    { name: "Level 2: Telemetry Ingestion", agents: ["Log Agent", "Metrics Agent", "Deployment Agent"] },
    { name: "Level 3: Causation & Reasoning", agents: ["Review Agent", "Root Cause Agent"] },
    { name: "Level 4: Playbook Formulation", agents: ["Recommendation Agent"] },
  ];

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Control Center</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time execution stats for parallel LangGraph sub-agent nodes.
          </p>
        </div>
        <ListSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Control Center</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time execution stats for parallel LangGraph sub-agent nodes.
          </p>
        </div>
        <Link
          href="/simulation"
          className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition hover:bg-primary/95"
        >
          <Play className="h-4 w-4 fill-current" />
          Dispatch Graph Run
        </Link>
      </div>

      {/* Visual Workflow Graph */}
      <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-xl space-y-6">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <GitBranch className="h-4.5 w-4.5 text-primary" /> Active Workflow Execution Graph
        </h2>
        
        <div className="grid gap-6 md:grid-cols-4 relative">
          {levels.map((level, levelIdx) => (
            <div key={level.name} className="space-y-4">
              <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60 text-center md:text-left border-b border-border/50 pb-2">
                {level.name}
              </p>
              <div className="flex flex-row md:flex-col gap-3 justify-center">
                {level.agents.map((agentName) => {
                  const agentState = selectedIncident?.agents[agentName];
                  const isRunning = isSimulating && activeSimulationAgent === agentName;
                  const isCompleted = isSimulating
                    ? getCompletedAgentsForSimulation(activeSimulationAgent, agentName)
                    : agentState?.status === "COMPLETED";

                  return (
                    <div
                      key={agentName}
                      className={`flex items-center gap-3 rounded-xl border p-3 transition-all duration-300 w-full ${
                        isRunning
                          ? "border-primary/50 bg-primary/10 shadow-[0_0_12px_rgba(59,130,246,0.2)]"
                          : isCompleted
                          ? "border-emerald-500/20 bg-emerald-500/5"
                          : "border-border/60 bg-muted/10 opacity-60"
                      }`}
                    >
                      <Bot className={`h-5 w-5 ${isRunning ? "text-primary animate-bounce" : isCompleted ? "text-emerald-400" : "text-muted-foreground"}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-foreground truncate">{agentName}</p>
                        <p className="text-[9px] text-muted-foreground uppercase font-mono mt-0.5">
                          {isRunning ? "RUNNING" : isCompleted ? "COMPLETED" : "STANDBY"}
                        </p>
                      </div>
                      {isCompleted && (
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Latency & Quality Charts */}
      {selectedIncident && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Latency Chart */}
          <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-xl space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Zap className="h-4.5 w-4.5 text-amber-400" /> Execution Latency (ms)
            </h2>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical">
                  <XAxis type="number" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#71717a" fontSize={11} tickLine={false} width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                    labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                  />
                  <Bar dataKey="latency" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Latency" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Confidence Chart */}
          <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-xl space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Activity className="h-4.5 w-4.5 text-emerald-400" /> Quality Confidence (%)
            </h2>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis stroke="#71717a" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "rgba(24, 24, 27, 0.9)", borderColor: "rgba(63, 63, 70, 0.8)", borderRadius: "8px" }}
                    labelStyle={{ color: "#a1a1aa", fontSize: "11px", fontWeight: "bold" }}
                  />
                  <Bar dataKey="confidence" fill="#10b981" radius={[4, 4, 0, 0]} name="Confidence" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Detail Agent Logs List */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Cpu className="h-4.5 w-4.5 text-indigo-400" /> Detailed Agent Outputs for {selectedIncident?.id || targetIncidentId}
        </h2>
        {selectedIncident ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(selectedIncident.agents).map(([agentName, agentData]) => (
              <div key={agentName} className="rounded-2xl border border-border/80 bg-card/50 p-6 backdrop-blur space-y-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-foreground">{agentName}</h3>
                    <p className="text-[10px] text-muted-foreground">Execution Latency: {agentData.duration_ms}ms</p>
                  </div>
                  <ConfidenceIndicator confidence={agentData.confidence} size={40} strokeWidth={4} />
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed min-h-[40px]">
                  {agentData.summary}
                </p>
                {agentData.findings && agentData.findings.length > 0 && (
                  <div className="rounded-xl bg-background/50 border border-border/50 p-3">
                    <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider mb-2">Findings Telemetry</p>
                    <pre className="overflow-x-auto font-mono text-[9px] text-emerald-400 max-h-[80px] whitespace-pre-wrap">
                      {typeof agentData.findings[0] === "string" ? agentData.findings[0] : JSON.stringify(agentData.findings[0], null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border/50 rounded-xl bg-muted/10">
            <p className="text-xs text-muted-foreground">No active execution logs loaded.</p>
          </div>
        )}
      </div>
    </div>
  );
}
