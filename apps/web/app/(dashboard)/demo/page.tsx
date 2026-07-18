"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaultInjectionPanel } from "@/components/demo/FaultInjectionPanel";
import { LiveTimeline } from "@/components/incidents/LiveTimeline";
import { RootCauseStory } from "@/components/incidents/RootCauseStory";

export default function DemoLabPage() {
  // Mock Project ID for the demo environment
  const demoProjectId = "demo-proj-1234-5678";
  
  // State to simulate the demo script flow
  const [demoStage, setDemoStage] = useState<"idle" | "injected" | "investigating" | "resolved">("idle");

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold">Hackathon Demo Lab</h1>
        <p className="text-muted-foreground mt-2">
          Experience Sentinel AI in action without connecting your own infrastructure.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          {/* Left Column: Controls */}
          <div onClick={() => {
            // Very hacky simulation timer for the Hackathon Demo Script
            if (demoStage === "idle") {
              setDemoStage("injected");
              setTimeout(() => setDemoStage("investigating"), 3000);
              setTimeout(() => setDemoStage("resolved"), 10000);
            }
          }}>
            <FaultInjectionPanel projectId={demoProjectId} />
          </div>
          
          <div className="bg-card border border-border rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-4">Sample Production Environment</h3>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between border-b border-border pb-2">
                <span className="text-muted-foreground">Workspace</span>
                <span className="font-medium">Acme Corp</span>
              </div>
              <div className="flex justify-between border-b border-border pb-2">
                <span className="text-muted-foreground">Project</span>
                <span className="font-medium">Payments API (Prod)</span>
              </div>
              <div className="flex justify-between border-b border-border pb-2">
                <span className="text-muted-foreground">Infrastructure</span>
                <span className="font-medium">Kubernetes (EKS)</span>
              </div>
              <div className="flex justify-between pb-2">
                <span className="text-muted-foreground">Active Telemetry</span>
                <span className="font-medium text-green-500">2,450 eps</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Right Column: AI Output */}
          <AnimatePresence mode="popLayout">
            {demoStage !== "idle" && (
              <motion.div
                key="timeline"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-8"
              >
                <LiveTimeline />
                
                {demoStage === "resolved" && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <RootCauseStory />
                  </motion.div>
                )}
              </motion.div>
            )}
            
            {demoStage === "idle" && (
              <motion.div 
                key="empty"
                className="h-full flex flex-col items-center justify-center text-center p-12 border border-dashed border-border rounded-2xl bg-card/50"
              >
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="font-bold text-lg mb-2">Waiting for Telemetry...</h3>
                <p className="text-muted-foreground text-sm max-w-sm">
                  Trigger a scenario in the Fault Injection Lab to watch Sentinel AI autonomously investigate the root cause.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
