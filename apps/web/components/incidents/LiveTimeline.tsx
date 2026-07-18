"use client";

import { motion } from "framer-motion";
import { Activity, AlertCircle, Bot, GitMerge, CheckCircle2 } from "lucide-react";

type TimelineStep = {
  id: string;
  title: string;
  timestamp: string;
  icon: React.ReactNode;
  color: string;
  status: "pending" | "active" | "completed";
};

// Mock data representing a typical AI investigation flow
const steps: TimelineStep[] = [
  {
    id: "step-1",
    title: "Anomaly Detected in Telemetry Stream",
    timestamp: "10:42:05 AM",
    icon: <Activity className="w-5 h-5" />,
    color: "bg-blue-500",
    status: "completed"
  },
  {
    id: "step-2",
    title: "Incident #492 Created",
    timestamp: "10:42:06 AM",
    icon: <AlertCircle className="w-5 h-5" />,
    color: "bg-red-500",
    status: "completed"
  },
  {
    id: "step-3",
    title: "LangGraph AI Agent Dispatched",
    timestamp: "10:42:08 AM",
    icon: <Bot className="w-5 h-5" />,
    color: "bg-purple-500",
    status: "completed"
  },
  {
    id: "step-4",
    title: "Correlating GitHub Deployments",
    timestamp: "10:42:15 AM",
    icon: <GitMerge className="w-5 h-5" />,
    color: "bg-gray-500",
    status: "completed"
  },
  {
    id: "step-5",
    title: "Root Cause Identified",
    timestamp: "10:42:24 AM",
    icon: <CheckCircle2 className="w-5 h-5" />,
    color: "bg-green-500",
    status: "active"
  }
];

export function LiveTimeline() {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <h3 className="font-bold text-lg mb-6">Investigation Timeline</h3>
      
      <div className="relative pl-4 border-l border-white/10 space-y-8">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.5, duration: 0.5 }}
            className="relative"
          >
            {/* Timeline Dot */}
            <div className={`absolute -left-[25px] w-[18px] h-[18px] rounded-full border-4 border-black ${step.color} ${
              step.status === "active" ? "animate-pulse shadow-[0_0_15px_currentColor]" : ""
            }`} />
            
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg bg-white/5 border border-white/10 ${step.status === 'active' ? step.color.replace('bg-', 'text-') : 'text-gray-400'}`}>
                  {step.icon}
                </div>
                <div>
                  <h4 className={`font-semibold ${step.status === 'active' ? 'text-white' : 'text-gray-300'}`}>
                    {step.title}
                  </h4>
                  <p className="text-xs text-gray-500">{step.timestamp}</p>
                </div>
              </div>
              
              {step.status === "active" && (
                <span className="text-xs font-mono text-purple-400 bg-purple-400/10 px-2 py-1 rounded border border-purple-400/20">
                  Running...
                </span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
