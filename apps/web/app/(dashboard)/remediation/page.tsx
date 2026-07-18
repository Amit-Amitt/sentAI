"use client";

import { useState } from "react";
import { useOrgStore } from "@/lib/store/org-store";
import { useRemediations } from "@/lib/api/hooks/useRemediation";
import { RemediationRun } from "@/lib/api/services/remediation";
import { Wrench, GitPullRequest, Code2, ShieldAlert, History, BookOpen, PlayCircle, ExternalLink } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";

function formatDistanceToNowFallback(dateString: string) {
  const diff = Date.now() - new Date(dateString).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function RemediationCenterPage() {
  const { activeWorkspace } = useOrgStore();
  const searchParams = useSearchParams();
  const initialIncidentId = searchParams.get("incident_id");
  
  const { data: remediations, isLoading } = useRemediations(activeWorkspace?.id);
  const [selectedRun, setSelectedRun] = useState<RemediationRun | null>(null);

  useEffect(() => {
    if (initialIncidentId && remediations) {
      const match = remediations.find(r => r.incident_id === initialIncidentId);
      if (match) setSelectedRun(match);
    }
  }, [initialIncidentId, remediations]);
  
  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        <div className="h-10 w-48 bg-muted rounded animate-pulse" />
        <div className="h-[400px] w-full bg-muted rounded animate-pulse" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] border rounded-xl overflow-hidden bg-background">
      {/* Sidebar List */}
      <div className="w-1/3 border-r border-border bg-muted/10 overflow-y-auto">
        <div className="p-6 sticky top-0 bg-background/95 backdrop-blur z-10 border-b border-border">
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Wrench className="h-5 w-5 text-primary" />
            Remediation Center
          </h1>
          <p className="text-muted-foreground mt-2 text-xs leading-relaxed">
            AI-generated recovery strategies, automated PR drafts, and incident runbooks.
          </p>
        </div>
        
        <div className="p-4 space-y-3">
          {remediations?.length === 0 && (
            <div className="text-center p-8 text-xs text-muted-foreground border border-dashed rounded-lg">
              No remediations generated yet. Trigger one from an active incident.
            </div>
          )}
          
          {remediations?.map((run) => (
            <div 
              key={run.id}
              className={`cursor-pointer transition-all duration-200 rounded-xl border p-4 ${
                selectedRun?.id === run.id 
                  ? "border-primary bg-primary/5 shadow-sm" 
                  : "border-border/60 bg-card hover:border-primary/50"
              }`}
              onClick={() => setSelectedRun(run)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold text-primary px-2 py-0.5 rounded-full bg-primary/10">{run.incident_id}</span>
                {run.status === "COMPLETED" ? (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Ready</span>
                ) : run.status === "GENERATING" ? (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse">Generating</span>
                ) : (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border bg-red-500/10 text-red-500 border-red-500/20">Failed</span>
                )}
              </div>
              <div className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <History className="h-3 w-3" />
                {run.created_at ? formatDistanceToNowFallback(run.created_at) : "Just now"}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="w-2/3 overflow-y-auto p-8">
        {selectedRun ? (
          <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between pb-4 border-b border-border/50">
              <div>
                <h2 className="text-2xl font-extrabold tracking-tight">Remediation Plan</h2>
                <p className="text-xs text-muted-foreground mt-1">Generated for <span className="font-mono font-semibold">{selectedRun.incident_id}</span></p>
              </div>
              <div className="flex gap-2">
                <button className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-semibold hover:bg-muted transition-colors">
                  <PlayCircle className="h-4 w-4" /> Run Playbook
                </button>
                <button className="flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors">
                  <GitPullRequest className="h-4 w-4" /> Create PR
                </button>
              </div>
            </div>

            {selectedRun.status === "GENERATING" && (
              <div className="p-12 text-center border border-dashed rounded-xl bg-muted/10">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                <h3 className="text-base font-bold">Synthesizing Fix</h3>
                <p className="text-xs text-muted-foreground mt-2">The AI engine is writing code patches, rollback plans, and incident runbooks...</p>
              </div>
            )}

            {selectedRun.status === "COMPLETED" && (
              <div className="space-y-6">
                
                {/* Fix Strategy */}
                <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
                  <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
                    <Wrench className="h-4 w-4 text-blue-500" /> Recommended Strategy
                  </h3>
                  <ul className="space-y-3">
                    {selectedRun.fix_strategy?.map((step: string, idx: number) => (
                      <li key={idx} className="text-sm leading-relaxed text-foreground/90 flex gap-3">
                        <span className="text-primary font-bold">{idx + 1}.</span> {step}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Risk Analysis */}
                <div className={`rounded-xl border p-6 shadow-sm ${selectedRun.risk_analysis?.risk_level === "High" ? "border-red-500/30 bg-red-500/5" : "border-border/80 bg-card"}`}>
                  <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
                    <ShieldAlert className={`h-4 w-4 ${selectedRun.risk_analysis?.risk_level === "High" ? "text-red-500" : "text-amber-500"}`} /> 
                    Risk Analysis
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 rounded-lg bg-background/50 border border-border/40 text-sm">
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Risk Level</p>
                      <p className={`font-bold ${selectedRun.risk_analysis?.risk_level === "High" ? "text-red-500" : "text-amber-500"}`}>{selectedRun.risk_analysis?.risk_level || "Unknown"}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Confidence</p>
                      <p className="font-bold text-foreground">{selectedRun.risk_analysis?.confidence_score}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-muted-foreground font-semibold mb-1">Breaking</p>
                      <p className="font-bold text-foreground">{selectedRun.risk_analysis?.breaking_changes ? "Yes" : "No"}</p>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-xs font-bold text-muted-foreground uppercase mb-2">Side Effects</h4>
                      <ul className="list-disc pl-4 text-xs text-foreground/80 space-y-1.5 leading-relaxed">
                        {selectedRun.risk_analysis?.potential_side_effects?.map((effect: string, i: number) => (
                          <li key={i}>{effect}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-muted-foreground uppercase mb-2">Verification Steps</h4>
                      <ul className="space-y-2">
                        {selectedRun.risk_analysis?.verification_steps?.map((step: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-foreground/80 leading-relaxed">
                            <input type="checkbox" className="mt-0.5 rounded border-border" />
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Code Patch */}
                <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm overflow-hidden">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground">
                      <Code2 className="h-4 w-4 text-purple-500" /> Generated Patch
                    </h3>
                  </div>
                  <p className="text-sm mb-4 leading-relaxed">{selectedRun.code_patch?.explanation}</p>
                  
                  <div className="mb-4 flex flex-wrap gap-2">
                    {selectedRun.code_patch?.changed_files?.map((f: string) => (
                      <span key={f} className="text-[10px] font-mono bg-muted/60 px-2 py-1 rounded border border-border/50 text-foreground">{f}</span>
                    ))}
                  </div>

                  <div className="rounded-lg bg-zinc-950 p-4 overflow-x-auto border border-zinc-800">
                    <pre className="text-[11px] text-zinc-300 font-mono leading-relaxed">
                      <code>{selectedRun.code_patch?.diff}</code>
                    </pre>
                  </div>
                  
                  <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs">
                    <span className="font-bold text-amber-500 uppercase mr-2 text-[10px]">Testing Notes:</span>
                    <span className="text-foreground/80">{selectedRun.code_patch?.testing_notes}</span>
                  </div>
                </div>

                {/* GitHub PR Draft */}
                <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
                  <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
                    <GitPullRequest className="h-4 w-4 text-emerald-500" /> Pull Request Draft
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-muted/30 border border-border/50 space-y-3">
                      <div>
                        <span className="text-[10px] uppercase text-muted-foreground font-bold mr-2">Branch:</span>
                        <code className="text-xs font-mono text-primary bg-primary/10 px-1.5 py-0.5 rounded">{selectedRun.github_pr_draft?.branch_name}</code>
                      </div>
                      <div>
                        <span className="text-[10px] uppercase text-muted-foreground font-bold block mb-1">Title:</span>
                        <p className="text-sm font-semibold">{selectedRun.github_pr_draft?.title}</p>
                      </div>
                      <div>
                        <span className="text-[10px] uppercase text-muted-foreground font-bold block mb-1">Description:</span>
                        <div className="text-xs leading-relaxed whitespace-pre-wrap text-foreground/80 font-mono bg-background p-3 rounded border border-border/40">
                          {selectedRun.github_pr_draft?.description}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Runbook & Rollback */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Runbook */}
                  <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
                    <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
                      <BookOpen className="h-4 w-4 text-indigo-500" /> Incident Runbook
                    </h3>
                    <div className="space-y-4 text-xs">
                      <div>
                        <p className="font-bold mb-1 text-foreground">Executive Summary</p>
                        <p className="text-muted-foreground leading-relaxed">{selectedRun.runbook?.executive_summary}</p>
                      </div>
                      <div>
                        <p className="font-bold mb-1 text-foreground">Recovery Steps</p>
                        <ol className="list-decimal pl-4 text-muted-foreground space-y-1">
                          {selectedRun.runbook?.recovery_steps?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ol>
                      </div>
                      <div>
                        <p className="font-bold mb-1 text-foreground">Future Prevention</p>
                        <ul className="list-disc pl-4 text-muted-foreground space-y-1">
                          {selectedRun.runbook?.future_prevention?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Rollback */}
                  <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
                    <h3 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4">
                      <History className="h-4 w-4 text-orange-500" /> Rollback Plan
                    </h3>
                    <div className="space-y-4 text-xs">
                      <div className="flex gap-3">
                        <div className="bg-muted/50 px-3 py-2 rounded-lg border border-border/50">
                          <p className="text-[9px] uppercase text-muted-foreground font-bold">Est. Downtime</p>
                          <p className="font-semibold">{selectedRun.rollback_plan?.estimated_downtime_minutes} mins</p>
                        </div>
                        <div className="bg-muted/50 px-3 py-2 rounded-lg border border-border/50">
                          <p className="text-[9px] uppercase text-muted-foreground font-bold">RTO</p>
                          <p className="font-semibold">{selectedRun.rollback_plan?.recovery_time_objective_minutes} mins</p>
                        </div>
                      </div>
                      
                      <div>
                        <p className="font-bold mb-1.5 text-foreground">Rollback Commands</p>
                        <div className="rounded-lg bg-zinc-950 p-3 overflow-x-auto border border-zinc-800">
                          <pre className="text-[10px] text-zinc-300 font-mono">
                            <code>{selectedRun.rollback_plan?.commands?.join('\n')}</code>
                          </pre>
                        </div>
                      </div>

                      <div>
                        <p className="font-bold mb-1.5 text-foreground">Rollback Checklist</p>
                        <ul className="space-y-1.5">
                          {selectedRun.rollback_plan?.checklist?.map((step: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-muted-foreground">
                              <input type="checkbox" className="mt-0.5 rounded border-border" />
                              <span className="leading-relaxed">{step}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Wrench className="h-12 w-12 mx-auto mb-4 opacity-20" />
              <p className="text-sm font-medium">Select a remediation run to view the AI strategy.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
