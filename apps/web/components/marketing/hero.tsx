"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Play, Shield, Bot, Zap, Activity } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden py-24 sm:py-32 lg:py-40">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-radial" />
      <div className="absolute inset-0 bg-grid opacity-40" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-primary/8 blur-[120px]" />
      <div className="absolute bottom-0 right-0 h-[300px] w-[400px] rounded-full bg-accent/5 blur-[100px]" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-4xl text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary mb-8">
              <Zap className="h-3 w-3" />
              Now in Public Beta — 14-day free trial
              <ArrowRight className="h-3 w-3" />
            </div>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl"
          >
            Incidents resolved{" "}
            <span className="text-gradient">autonomously</span>
            <br />
            by AI agents
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl"
          >
            7 specialized AI agents detect anomalies, analyze root causes, and recommend fixes — all before your users notice. Cut MTTR by 73%.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/register"
              className="group flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:bg-primary/90 transition-all"
            >
              Start Free
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/contact"
              className="group flex items-center gap-2 rounded-xl border border-border/60 bg-white/[0.03] px-6 py-3 text-sm font-semibold text-foreground hover:bg-white/[0.06] transition-all"
            >
              <Play className="h-4 w-4 text-primary" />
              Book Demo
            </Link>
          </motion.div>
        </div>

        {/* Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="relative mx-auto mt-20 max-w-5xl"
        >
          <div className="absolute -inset-4 rounded-3xl bg-gradient-to-b from-primary/20 via-primary/5 to-transparent blur-2xl" />
          <div className="relative rounded-2xl border border-border/60 bg-card/80 backdrop-blur-xl p-1 shadow-2xl">
            {/* Mock Browser Chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border/50">
              <div className="flex gap-1.5">
                <div className="h-3 w-3 rounded-full bg-red-500/60" />
                <div className="h-3 w-3 rounded-full bg-amber-500/60" />
                <div className="h-3 w-3 rounded-full bg-emerald-500/60" />
              </div>
              <div className="flex-1 mx-8">
                <div className="mx-auto max-w-sm rounded-lg bg-muted/50 px-4 py-1.5 text-center text-xs text-muted-foreground font-mono">
                  app.sentinel-ai.dev/dashboard
                </div>
              </div>
            </div>

            {/* Mock Dashboard Content */}
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: "Active Incidents", value: "3", color: "text-red-400", bg: "bg-red-500/10" },
                  { label: "Resolved Today", value: "12", color: "text-emerald-400", bg: "bg-emerald-500/10" },
                  { label: "Avg MTTR", value: "4.2m", color: "text-primary", bg: "bg-primary/10" },
                  { label: "AI Confidence", value: "94%", color: "text-amber-400", bg: "bg-amber-500/10" },
                ].map((stat) => (
                  <div key={stat.label} className={`rounded-xl ${stat.bg} border border-white/[0.06] p-4`}>
                    <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mt-1">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* Agent Status Row */}
              <div className="flex gap-3">
                {["Coordinator", "Log Agent", "Metrics", "Deploy", "Root Cause", "Recommend"].map((name, i) => (
                  <div key={name} className="flex-1 rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                    <Bot className={`h-4 w-4 mx-auto mb-1 ${i < 4 ? "text-emerald-400" : i === 4 ? "text-primary animate-pulse" : "text-muted-foreground"}`} />
                    <p className="text-[9px] font-semibold text-muted-foreground truncate">{name}</p>
                    <p className={`text-[8px] font-bold uppercase mt-0.5 ${i < 4 ? "text-emerald-400" : i === 4 ? "text-primary" : "text-muted-foreground/60"}`}>
                      {i < 4 ? "DONE" : i === 4 ? "RUNNING" : "QUEUED"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
