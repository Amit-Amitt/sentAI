"use client";

import { motion } from "framer-motion";
import { Bot, ArrowDown, CheckCircle2 } from "lucide-react";

const steps = [
  { label: "Incident Detected", desc: "Alert triggers the Coordinator Agent", status: "complete" },
  { label: "Evidence Gathering", desc: "Log, Metrics, and Deployment agents run in parallel", status: "complete" },
  { label: "Customer Impact", desc: "Review Agent analyzes user reports and tickets", status: "complete" },
  { label: "Root Cause Analysis", desc: "Root Cause Agent synthesizes all evidence", status: "active" },
  { label: "Response Plan", desc: "Recommendation Agent generates playbooks", status: "pending" },
  { label: "Report Generated", desc: "Full incident post-mortem delivered in seconds", status: "pending" },
];

export function AgentWorkflow() {
  return (
    <section className="relative py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-conic opacity-50" />
      <div className="relative mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">How It Works</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            From alert to resolution in seconds
          </h2>
          <p className="mt-4 text-muted-foreground leading-relaxed">
            Watch how Sentinel AI orchestrates a full incident investigation autonomously.
          </p>
        </div>

        <div className="mx-auto max-w-lg space-y-0">
          {steps.map((step, i) => (
            <motion.div
              key={step.label}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-30px" }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              <div className="flex gap-4">
                {/* Timeline Line */}
                <div className="flex flex-col items-center">
                  <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 ${
                    step.status === "complete" ? "border-emerald-500/40 bg-emerald-500/10" :
                    step.status === "active" ? "border-primary/40 bg-primary/10 animate-pulse" :
                    "border-border/40 bg-muted/20"
                  }`}>
                    {step.status === "complete" ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                    ) : (
                      <Bot className={`h-5 w-5 ${step.status === "active" ? "text-primary" : "text-muted-foreground/40"}`} />
                    )}
                  </div>
                  {i < steps.length - 1 && (
                    <div className={`w-0.5 h-12 ${
                      step.status === "complete" ? "bg-emerald-500/30" : "bg-border/30"
                    }`} />
                  )}
                </div>

                {/* Content */}
                <div className="pb-12 pt-1">
                  <h3 className={`text-sm font-bold ${step.status === "pending" ? "text-muted-foreground/40" : "text-foreground"}`}>
                    {step.label}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{step.desc}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
