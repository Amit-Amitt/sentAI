"use client";

import { useState } from "react";
import { useScenarios, useStartSimulation, useSimulationHistory } from "@/lib/api/hooks/useSimulation";
import { useOrgStore } from "@/lib/store/org-store";
import { Play, Activity, Server, AlertTriangle, CheckCircle2, TerminalSquare, Database, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { ListSkeleton } from "@/components/ui/skeletons";

export default function SimulationCenterPage() {
  const router = useRouter();
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id;

  const { data: scenarios, isLoading: scenariosLoading } = useScenarios();
  const { data: history, isLoading: historyLoading } = useSimulationHistory(workspaceId);
  const startSimulation = useStartSimulation();

  const [selectedSeverity, setSelectedSeverity] = useState<string>("SEV1");
  const [runningScenario, setRunningScenario] = useState<string | null>(null);

  const handleRunSimulation = async (scenarioId: string) => {
    if (!workspaceId) return;
    setRunningScenario(scenarioId);
    try {
      const run = await startSimulation.mutateAsync({
        workspaceId,
        payload: { scenario_id: scenarioId, severity: selectedSeverity }
      });
      // Redirect to incident details page to watch live execution
      router.push(`/incidents/${run.incident_id}`);
    } catch (error) {
      console.error("Failed to start simulation", error);
      setRunningScenario(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Simulation Center</h1>
        <p className="text-muted-foreground mt-2">
          Trigger realistic production incidents to test LangGraph orchestration and AI agents.
        </p>
      </div>

      <div className="flex items-center gap-4 border-b border-border/60 pb-6">
        <span className="text-sm font-semibold text-muted-foreground">Simulation Severity:</span>
        <div className="flex rounded-xl border border-border/80 bg-background/50 p-1 text-xs">
          {["SEV1", "SEV2", "SEV3"].map((val) => (
            <button
              key={val}
              onClick={() => setSelectedSeverity(val)}
              className={`rounded-lg px-3 py-1 font-semibold transition ${
                selectedSeverity === val
                  ? "bg-primary text-primary-foreground shadow"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {val}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {scenariosLoading ? (
          <ListSkeleton />
        ) : (
          scenarios?.map((scenario) => (
            <div
              key={scenario.id}
              className="group relative flex flex-col justify-between rounded-2xl border border-border/60 bg-card/40 p-6 backdrop-blur transition-all duration-200 hover:border-primary/40 hover:bg-card/60"
            >
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
                    <Activity className="h-5 w-5" />
                  </div>
                  <SeverityBadge severity={selectedSeverity as any} />
                </div>
                
                <div>
                  <h3 className="text-lg font-bold text-foreground">{scenario.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {scenario.description}
                  </p>
                </div>

                <div className="space-y-3 pt-2">
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground mb-1.5 uppercase tracking-wider">Affected Services</p>
                    <div className="flex flex-wrap gap-1.5">
                      {scenario.affected_services.map(svc => (
                        <span key={svc} className="inline-flex items-center rounded bg-muted/60 px-2 py-0.5 text-[10px] font-medium text-foreground border border-border/50">
                          <Server className="mr-1 h-3 w-3 text-muted-foreground" /> {svc}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wider">Expected Root Cause</p>
                    <p className="text-sm font-medium text-amber-500/90">{scenario.expected_root_cause}</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-border/50">
                <button
                  disabled={runningScenario === scenario.id}
                  onClick={() => handleRunSimulation(scenario.id)}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow transition hover:bg-primary/90 disabled:opacity-50"
                >
                  {runningScenario === scenario.id ? (
                    <>
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                      Initializing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 fill-current" />
                      Run Simulation
                    </>
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="pt-8">
        <h2 className="text-xl font-bold tracking-tight mb-4">Simulation History</h2>
        {historyLoading ? (
          <ListSkeleton />
        ) : history && history.length > 0 ? (
          <div className="rounded-xl border border-border/60 bg-card/20 overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/50 text-muted-foreground text-xs uppercase">
                <tr>
                  <th className="px-6 py-3 font-semibold">Incident ID</th>
                  <th className="px-6 py-3 font-semibold">Scenario</th>
                  <th className="px-6 py-3 font-semibold">Severity</th>
                  <th className="px-6 py-3 font-semibold">Status</th>
                  <th className="px-6 py-3 font-semibold">Date</th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {history.map((run) => (
                  <tr key={run.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-primary font-medium">{run.incident_id}</td>
                    <td className="px-6 py-4 text-foreground font-medium">{scenarios?.find(s => s.id === run.scenario_id)?.title || run.scenario_id}</td>
                    <td className="px-6 py-4"><SeverityBadge severity={run.severity as any} /></td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold border ${
                        run.status === "RUNNING"
                          ? "bg-amber-500/10 text-amber-500 border-amber-500/20 animate-pulse"
                          : run.status === "FAILED"
                          ? "bg-red-500/10 text-red-500 border-red-500/20"
                          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      }`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {run.created_at ? new Date(run.created_at).toLocaleString() : "N/A"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => router.push(`/incidents/${run.incident_id}`)} className="text-muted-foreground hover:text-primary transition-colors">
                        <ArrowRight className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-border/60 bg-card/10 p-8 text-center text-muted-foreground">
            No simulations run yet in this workspace.
          </div>
        )}
      </div>
    </div>
  );
}
