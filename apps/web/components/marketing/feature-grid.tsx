"use client";

import { motion } from "framer-motion";
import { Bot, FileSearch, BarChart3, GitBranch, MessageSquare, Search, Lightbulb } from "lucide-react";

const agents = [
  { name: "Coordinator Agent", desc: "Orchestrates the full investigation workflow across all sub-agents using LangGraph.", icon: Bot, color: "from-blue-500/20 to-blue-600/5", border: "border-blue-500/20" },
  { name: "Log Agent", desc: "Parses and analyzes log entries to detect error patterns, stack traces, and anomalies.", icon: FileSearch, color: "from-emerald-500/20 to-emerald-600/5", border: "border-emerald-500/20" },
  { name: "Metrics Agent", desc: "Monitors infrastructure metrics to identify threshold violations and unusual trends.", icon: BarChart3, color: "from-amber-500/20 to-amber-600/5", border: "border-amber-500/20" },
  { name: "Deployment Agent", desc: "Correlates deployment history and config changes with incident timelines.", icon: GitBranch, color: "from-purple-500/20 to-purple-600/5", border: "border-purple-500/20" },
  { name: "Review Agent", desc: "Analyzes customer feedback, support tickets, and user reports for operational evidence.", icon: MessageSquare, color: "from-pink-500/20 to-pink-600/5", border: "border-pink-500/20" },
  { name: "Root Cause Agent", desc: "Synthesizes evidence from all agents to determine the most probable root cause.", icon: Search, color: "from-red-500/20 to-red-600/5", border: "border-red-500/20" },
  { name: "Recommendation Agent", desc: "Generates prioritized, actionable incident response recommendations and playbooks.", icon: Lightbulb, color: "from-cyan-500/20 to-cyan-600/5", border: "border-cyan-500/20" },
];

export function FeatureGrid() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Multi-Agent Architecture</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            7 agents. One mission.
          </h2>
          <p className="mt-4 text-muted-foreground leading-relaxed">
            Each agent is a specialist. Together, they form an autonomous incident response team that works 24/7.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent, i) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className={`group relative rounded-2xl border ${agent.border} bg-gradient-to-b ${agent.color} p-6 hover:border-border transition-all duration-300 hover:-translate-y-1`}
            >
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/[0.06] border border-white/[0.06]">
                  <agent.icon className="h-5 w-5 text-foreground" />
                </div>
                <div className="space-y-1.5">
                  <h3 className="text-sm font-bold text-foreground">{agent.name}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{agent.desc}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
