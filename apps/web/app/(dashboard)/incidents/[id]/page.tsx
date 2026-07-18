"use client";

import { use, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { AlertCircle, ArrowLeft, Bot, CheckSquare, Clock, Cpu, FileCheck, ShieldAlert, Sparkles, BrainCircuit } from "lucide-react";

import { useStore } from "@/lib/store/use-store";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import { EvidenceViewer } from "@/components/ui/evidence-viewer";
import { useIncident } from "@/lib/api/hooks/useIncident";
import { useSimilarMemories } from "@/lib/api/hooks/useMemory";
import { useOrgStore } from "@/lib/store/org-store";

export default function IncidentDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id || null;
  const { toggleChecklistItem, checkedPlaybookItems } = useStore();
  const { data: incident, isLoading, error } = useIncident(id);
  
  // Retrieve similar incidents from memory for the context panel
  const { data: similarMemories, isLoading: isLoadingMemories } = useSimilarMemories(
    workspaceId,
    incident?.summary || "",
    3
  );

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-32 text-center">
        <Bot className="h-12 w-12 text-primary mb-4 animate-bounce" />
        <h2 className="text-xl font-bold">Assembling incident post-mortem...</h2>
        <p className="text-sm text-muted-foreground mt-2">
          Sub-agents are currently aggregating evidence logs, metrics and playbooks.
        </p>
      </div>
    );
  }

  if (!incident || error) {
    return (
      <div className="flex flex-col items-center justify-center p-16 text-center">
        <ShieldAlert className="h-12 w-12 text-red-400 mb-4" />
        <h2 className="text-xl font-bold">Incident Not Found</h2>
        <p className="text-sm text-muted-foreground mt-2">
          The requested incident ID does not exist or has been deleted.
        </p>
        <Link href="/incidents" className="mt-6 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground">
          Return to Outpost
        </Link>
      </div>
    );
  }

  // Count checklist completion using Zustand store state reactively
  const recoveryChecklist = incident.recovery_checklist.map((step) => ({
    ...step,
    completed: !!checkedPlaybookItems[`${incident.id}-${step.title}`],
  }));

  const totalSteps = recoveryChecklist.length;
  const completedSteps = recoveryChecklist.filter(s => s.completed).length;
  const progressPercent = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div className="space-y-8">
      {/* Back button */}
      <Link href="/incidents" className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground font-semibold">
        <ArrowLeft className="h-4 w-4" /> Back to board
      </Link>

      {/* Top Banner Header */}
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between border-b border-border/60 pb-6">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="font-mono text-sm font-bold text-primary">{incident.id}</span>
            <SeverityBadge severity={incident.severity} />
            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border ${
              incident.status === "ACTIVE"
                ? "bg-red-500/10 text-red-400 border-red-500/20 animate-pulse"
                : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
            }`}>
              {incident.status}
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">{incident.summary}</h1>
          <p className="text-xs text-muted-foreground flex items-center gap-2">
            <Clock className="h-4 w-4" /> Aggregated {new Date(incident.created_at).toLocaleString()} by {incident.owner}
          </p>
        </div>

        {/* Confidence Dial widget */}
        <div className="flex items-center gap-4 rounded-2xl border border-border/80 bg-card/40 p-4 backdrop-blur">
          <div>
            <p className="text-xs font-semibold text-muted-foreground">Orchestrator</p>
            <p className="text-sm font-bold text-foreground">Confidence Score</p>
          </div>
          <ConfidenceIndicator confidence={incident.confidence} size={70} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left 2 Columns: Overview, Evidence, Agents */}
        <div className="lg:col-span-2 space-y-8">
          {/* Overview */}
          <div className="rounded-2xl border border-border/85 bg-card/60 p-6 backdrop-blur-xl space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <AlertCircle className="h-4 w-4" /> Incident Overview
            </h2>
            <p className="text-sm leading-relaxed text-foreground/95">{incident.description}</p>
            
            <div className="grid gap-4 sm:grid-cols-2 pt-2 border-t border-border/50 text-xs">
              <div>
                <p className="font-semibold text-muted-foreground">Affected Microservices</p>
                <div className="flex gap-1.5 mt-1.5 flex-wrap">
                  {incident.affected_services.map(s => (
                    <span key={s} className="rounded bg-muted px-2 py-1 font-mono">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="font-semibold text-muted-foreground">Causal Reasoning</p>
                <p className="mt-1.5 font-bold text-emerald-400 flex items-center gap-1">
                  <Sparkles className="h-4 w-4" /> {incident.root_cause.primary || "Awaiting investigation"}
                </p>
              </div>
            </div>
          </div>

          {/* Evidence tabbed viewer component */}
          <EvidenceViewer
            logs={incident.logs}
            metrics={incident.metrics}
            deployment_history={incident.deployment_history}
            customer_reports={incident.customer_reports}
          />

          {/* Sub-agent logs */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" /> Parallel Agent Executions
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {Object.entries(incident.agents).map(([name, state]) => (
                <div key={name} className="rounded-xl border border-border/70 bg-card/20 p-4 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold flex items-center gap-1.5"><Cpu className="h-3.5 w-3.5 text-muted-foreground" /> {name}</span>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-semibold border ${
                      state.status === "COMPLETED" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
                      state.status === "RUNNING" ? "bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse" :
                      "bg-zinc-800 text-zinc-400"
                    }`}>
                      {state.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-normal">{state.summary}</p>
                  <div className="flex justify-between items-center text-[10px] text-muted-foreground pt-1 border-t border-border/30">
                    <span>{state.duration_ms}ms latency</span>
                    <span className="font-bold text-foreground">{Math.round(state.confidence * 100)}% conf</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Root Cause hypotheses, Recovery Checklist, Context Panel, and Recs */}
        <div className="space-y-6">
          {/* AI Context Panel (Historical Matches) */}
          <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 backdrop-blur-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-primary flex items-center gap-2">
              <BrainCircuit className="h-4 w-4" /> AI Context Engine
            </h2>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Based on the memory bank, the following similar incidents were successfully resolved in the past.
            </p>
            
            {isLoadingMemories ? (
              <div className="animate-pulse space-y-3">
                <div className="h-12 bg-primary/10 rounded-xl" />
                <div className="h-12 bg-primary/10 rounded-xl" />
              </div>
            ) : similarMemories && similarMemories.length > 0 ? (
              <div className="space-y-3">
                {similarMemories.map(memory => (
                  <Link href={`/incidents/${memory.incident_id}`} key={memory.id}>
                    <div className="group rounded-xl bg-card/60 border border-border/50 p-3 hover:border-primary/50 transition-colors space-y-2 mt-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="font-mono font-bold text-primary">{memory.incident_id}</span>
                        <span className="text-muted-foreground">{Math.round((memory.time_taken_ms || 0)/1000)}s MTTR</span>
                      </div>
                      <p className="text-xs font-medium line-clamp-1">{memory.summary}</p>
                      <div className="flex items-center gap-2 pt-2 border-t border-border/30">
                        <span className="text-[10px] text-muted-foreground font-semibold uppercase">Past Root Cause:</span>
                        <span className="text-[10px] text-emerald-400 font-bold truncate">
                          {memory.root_cause?.primary || "Unknown"}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-border/60 p-4 text-center">
                <p className="text-xs text-muted-foreground">No historical matches found for this signature.</p>
              </div>
            )}
          </div>

          {/* Root cause analysis */}
          <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" /> Root Cause Diagnosis
            </h2>
            <div className="space-y-3">
              <div className="rounded-xl bg-primary/10 border border-primary/20 p-4 space-y-1">
                <p className="text-[10px] font-bold text-primary uppercase tracking-wider">Primary Driver</p>
                <p className="text-sm font-bold text-foreground">{incident.root_cause.primary}</p>
              </div>
              
              <div className="text-xs space-y-2">
                <p className="font-semibold text-muted-foreground">Supporting Arguments</p>
                <ul className="list-disc list-inside space-y-1 text-muted-foreground leading-relaxed">
                  {incident.root_cause.supporting_evidence.map((ev, i) => (
                    <li key={i}>{ev}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Recovery playbook checklist */}
          <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-md space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <CheckSquare className="h-4 w-4" /> Recovery Playbook
              </h2>
              {totalSteps > 0 && (
                <span className="text-xs font-semibold text-primary">{progressPercent}% complete</span>
              )}
            </div>
            
            {totalSteps === 0 ? (
              <p className="text-xs text-muted-foreground">No playbook steps generated by Recommendation Agent.</p>
            ) : (
              <div className="space-y-4">
                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary transition-all duration-300" style={{ width: `${progressPercent}%` }} />
                </div>
                
                <ul className="space-y-3.5">
                  {recoveryChecklist.map((step) => (
                    <li key={step.title} className="flex gap-3">
                      <input
                        type="checkbox"
                        checked={step.completed}
                        onChange={() => toggleChecklistItem(incident.id, step.title)}
                        className="mt-0.5 h-4 w-4 rounded border-border bg-background text-primary accent-primary cursor-pointer"
                      />
                      <div className="space-y-1.5 flex-1">
                        <p className={`text-xs font-semibold ${step.completed ? "line-through text-muted-foreground/80" : "text-foreground"}`}>
                          {step.title}
                        </p>
                        {step.command && (
                          <pre className="rounded bg-background/80 p-2 font-mono text-[9px] text-zinc-400 border border-border/30 overflow-x-auto max-w-[250px]">
                            {step.command}
                          </pre>
                        )}
                        <p className="text-[10px] text-muted-foreground">
                          <span className="font-semibold">Success:</span> {step.success_criteria}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action Recommendations list */}
          <div className="rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <FileCheck className="h-4 w-4" /> Remediation Plan
            </h2>
            {incident.recommendations.length === 0 ? (
              <p className="text-xs text-muted-foreground">No recommendations formulated yet.</p>
            ) : (
              <div className="space-y-3">
                {incident.recommendations.map((rec) => (
                  <div key={rec.id} className="rounded-xl border border-border/60 bg-muted/20 p-4 space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-foreground">Action {rec.execution_order}</span>
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-semibold ${
                        rec.priority === "Critical" ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                        rec.priority === "High" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                        "bg-zinc-800 text-zinc-400"
                      }`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-xs font-semibold mt-1">{rec.title}</p>
                    <p className="text-[10px] text-muted-foreground leading-normal mt-0.5">{rec.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
