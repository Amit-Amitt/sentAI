"use client";

import Link from "next/link";
import { useAuth } from "@/lib/providers/auth-provider";
import { Shield, Sparkles, Terminal, Activity, ArrowRight, UserCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function WelcomePage() {
  const { user } = useAuth();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8 max-w-md mx-auto"
    >
      {/* Decorative shield */}
      <div className="flex justify-center">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 blur-[30px] rounded-full" />
          <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 border border-primary/25">
            <Shield className="h-8 w-8 text-primary" />
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-[10px] font-semibold text-primary uppercase tracking-wider">
          <Sparkles className="h-3 w-3 animate-pulse" />
          <span>Access Granted</span>
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight">
          Welcome, {user?.firstName || "Commander"}!
        </h1>
        <p className="text-sm text-muted-foreground leading-relaxed max-w-sm mx-auto">
          You are about to deploy Sentinel AI — the autonomous AI Incident Commander designed to detect, diagnose, and resolve SRE incidents.
        </p>
      </div>

      {/* Capabilities list */}
      <div className="space-y-3.5 border-y border-border/40 py-5">
        {[
          {
            icon: Terminal,
            title: "7 Autonomous Agents",
            desc: "Log scanners, anomaly detectors, and deployment monitors work in sync.",
          },
          {
            icon: Activity,
            title: "Real-time Telemetry",
            desc: "Ingests log dumps, metrics grids, and alerts to resolve anomalies.",
          },
          {
            icon: UserCheck,
            title: "Smart Recommendations",
            desc: "Provides step-by-step mitigation plans and executable checkbooks.",
          },
        ].map((item, idx) => (
          <div key={idx} className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-zinc-900 border border-border/50 text-muted-foreground">
              <item.icon className="h-4 w-4" />
            </div>
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-foreground">{item.title}</h4>
              <p className="text-[11px] text-muted-foreground leading-normal">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* CTA Button */}
      <Link
        id="welcome-start-btn"
        href="/onboarding"
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/15"
      >
        <span>Begin Setup Wizard</span>
        <ArrowRight className="h-4 w-4" />
      </Link>
    </motion.div>
  );
}
