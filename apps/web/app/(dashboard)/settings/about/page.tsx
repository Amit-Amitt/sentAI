"use client";

import { ShieldCheck, HelpCircle, Bot, Code2, Zap } from "lucide-react";
import { Badge } from "@sentinel/ui";

export default function AboutPage() {
  const agentsInfo = [
    { name: "Coordinator", desc: "Decides plan topologies and dispatches parallel sub-agent workers based on incident fields." },
    { name: "Log Agent", desc: "Ingests plain-text or JSON application log volumes to detect anomalously repeating error patterns." },
    { name: "Metrics Agent", desc: "Analyzes system CPU/memory and API latencies to flag deviations from historic baselines." },
    { name: "Deployment Agent", desc: "Tracks commit hashes and release tags to correlate recent code or DB schema updates with outage timestamps." },
    { name: "Review Agent", desc: "Groups customer tickets, support reviews, and descriptive complaints into categorized clusters." },
    { name: "Root Cause Agent", desc: "Performs causal path modeling and evaluates hypotheses to isolate the primary driver of an incident." },
    { name: "Recommendation Agent", desc: "Assembles rollback playbooks, success metrics checklists, and immediate mitigation tasks." },
  ];

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">About Sentinel AI</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Autonomous Agentic SRE Incident Orchestration and Causal Post-Mortems.
        </p>
      </div>

      {/* Main Brand Description */}
      <div className="rounded-2xl border border-border/80 bg-card/45 p-6 backdrop-blur space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-primary" />
          <h2 className="text-lg font-bold">The Autonomous AI Incident Commander</h2>
        </div>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Sentinel AI coordinates groups of highly specialized LLM-backed sub-agents in a LangGraph graph to diagnose production incidents. Instead of simple pattern matching, Sentinel ingest logs, metrics streams, and release history to identify root causes and generate validated rollback playbooks within minutes of an outage.
        </p>
      </div>

      {/* Agents Topology Info */}
      <div className="space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Bot className="h-4.5 w-4.5 text-primary" /> System Architecture Nodes
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {agentsInfo.map((agent) => (
            <div key={agent.name} className="rounded-xl border border-border/60 bg-muted/20 p-5 space-y-2">
              <span className="text-xs font-bold text-foreground">{agent.name}</span>
              <p className="text-xs text-muted-foreground leading-relaxed">{agent.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Spec Stack */}
      <div className="rounded-2xl border border-border/80 bg-card/45 p-6 backdrop-blur space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Code2 className="h-4.5 w-4.5 text-indigo-400" /> Platform Technical Specs
        </h2>
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge className="border-indigo-500/30 bg-indigo-500/10 text-indigo-400">Next.js 15</Badge>
          <Badge className="border-emerald-500/30 bg-emerald-500/10 text-emerald-400">LangGraph Core</Badge>
          <Badge className="border-sky-500/30 bg-sky-500/10 text-sky-400">FastAPI Backend</Badge>
          <Badge className="border-amber-500/30 bg-amber-500/10 text-amber-400">Pydantic V2</Badge>
          <Badge className="border-red-500/30 bg-red-500/10 text-red-400">SQLite + SQLAlchemy</Badge>
        </div>
      </div>
    </div>
  );
}
