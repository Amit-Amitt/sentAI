"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, Database, Server, Cpu, GitMerge, AlertCircle, Bot, Activity } from "lucide-react";

type ComponentData = {
  id: string;
  title: string;
  icon: React.ReactNode;
  purpose: string;
  inputs: string;
  outputs: string;
};

const components: ComponentData[] = [
  {
    id: "telemetry",
    title: "Telemetry Ingestion Pipeline",
    icon: <Activity className="w-8 h-8 text-blue-400" />,
    purpose: "Ingests millions of logs, metrics, and traces per minute from Kubernetes clusters and OpenTelemetry collectors via a non-blocking Redis queue.",
    inputs: "OTLP Payloads, Prometheus Scrapes",
    outputs: "Standardized Sentinel Telemetry Events"
  },
  {
    id: "detection",
    title: "Incident Detection Engine",
    icon: <AlertCircle className="w-8 h-8 text-red-400" />,
    purpose: "Evaluates incoming telemetry streams against deterministic thresholds and dynamic machine learning baselines to trigger an Incident.",
    inputs: "Telemetry Events",
    outputs: "High-Severity Incident Ticket"
  },
  {
    id: "ai",
    title: "LangGraph AI Agents",
    icon: <Bot className="w-8 h-8 text-purple-400" />,
    purpose: "Acts as the SRE investigator. Queries the Vector DB for historical context, fetches logs around the anomaly time, and analyzes the stack trace.",
    inputs: "Incident Ticket, Raw Logs, Traces",
    outputs: "Root Cause Narrative, Confidence Score"
  },
  {
    id: "github",
    title: "Deployment Intelligence",
    icon: <GitMerge className="w-8 h-8 text-gray-300" />,
    purpose: "Correlates the exact timestamp of the anomaly against recent GitHub deployments and code changes to pinpoint if a recent release broke production.",
    inputs: "GitHub Webhooks, Commits",
    outputs: "Deployment Context for AI"
  },
  {
    id: "remediation",
    title: "Auto-Remediation Engine",
    icon: <Cpu className="w-8 h-8 text-green-400" />,
    purpose: "If the root cause is a bad configuration or code change, the AI automatically generates a patch and opens a GitHub Pull Request.",
    inputs: "Root Cause Narrative",
    outputs: "Draft GitHub PR"
  },
  {
    id: "data",
    title: "State & Storage",
    icon: <Database className="w-8 h-8 text-yellow-400" />,
    purpose: "Highly available PostgreSQL for relational state (Organizations, RBAC, Subscriptions) and Qdrant for semantic AI memory storage.",
    inputs: "Backend API",
    outputs: "Persistent Storage"
  }
];

export default function ArchitecturePage() {
  const [activeComponent, setActiveComponent] = useState<ComponentData | null>(components[0] ?? null);

  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500/30">
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
            <ChevronLeft className="w-5 h-5" />
            Back to Home
          </Link>
          <div className="font-semibold tracking-tight text-indigo-400">System Architecture</div>
        </div>
      </header>

      <main className="container mx-auto px-6 pt-12 pb-24">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-6">How Sentinel AI Works</h1>
          <p className="text-xl text-gray-400">
            Click on any component in the architecture diagram to understand its role in the autonomous incident response workflow.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Interactive Diagram (Simplified as a grid for the hackathon UI) */}
          <div className="grid sm:grid-cols-2 gap-4">
            {components.map((comp) => (
              <motion.button
                key={comp.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveComponent(comp)}
                className={`p-6 text-left rounded-2xl border transition-all ${
                  activeComponent?.id === comp.id 
                    ? "bg-indigo-500/10 border-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.2)]" 
                    : "bg-white/5 border-white/10 hover:border-white/20"
                }`}
              >
                <div className="mb-4 bg-black/50 p-3 rounded-xl inline-block">
                  {comp.icon}
                </div>
                <h3 className="font-bold text-lg">{comp.title}</h3>
              </motion.button>
            ))}
          </div>

          {/* Details Panel */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-8 relative overflow-hidden h-fit sticky top-24">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[80px] rounded-full pointer-events-none" />
            
            <AnimatePresence mode="wait">
              {activeComponent && (
                <motion.div
                  key={activeComponent.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="relative z-10"
                >
                  <div className="mb-6 bg-black/50 p-4 rounded-2xl inline-block">
                    {activeComponent.icon}
                  </div>
                  <h2 className="text-3xl font-bold mb-6">{activeComponent.title}</h2>
                  
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Purpose</h4>
                      <p className="text-gray-300 leading-relaxed text-lg">{activeComponent.purpose}</p>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-6 pt-6 border-t border-white/10">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Inputs</h4>
                        <p className="text-gray-300 font-medium">{activeComponent.inputs}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Outputs</h4>
                        <p className="text-gray-300 font-medium">{activeComponent.outputs}</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}
