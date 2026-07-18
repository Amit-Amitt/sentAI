"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Database, Server, Zap, CheckCircle2 } from "lucide-react";

type FaultScenario = {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
};

const scenarios: FaultScenario[] = [
  {
    id: "db_latency",
    name: "Database Latency Spike",
    description: "Simulates a bad connection pool configuration causing queries to stall for 1.4s.",
    icon: <Database className="w-5 h-5" />,
    color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20"
  },
  {
    id: "redis_oom",
    name: "Redis OOM Kill",
    description: "Simulates a memory leak pushing Redis over its maxmemory limit, causing pod evictions.",
    icon: <Server className="w-5 h-5" />,
    color: "text-red-400 bg-red-400/10 border-red-400/20"
  },
  {
    id: "github_bad_deploy",
    name: "Bad GitHub Deploy",
    description: "Simulates a recent merge to main that breaks downstream microservices.",
    icon: <Zap className="w-5 h-5" />,
    color: "text-purple-400 bg-purple-400/10 border-purple-400/20"
  }
];

export function FaultInjectionPanel({ projectId }: { projectId: string }) {
  const [isInjecting, setIsInjecting] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const injectFault = async (scenarioId: string) => {
    setIsInjecting(scenarioId);
    setSuccess(null);
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      const response = await fetch(`${apiUrl}/api/v1/demo/inject-fault`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // In a real app we'd pass the auth token here, 
          // assuming Demo Mode bypasses auth or uses a static demo token.
          "Authorization": `Bearer ${localStorage.getItem("sentinel_token")}`
        },
        body: JSON.stringify({
          project_id: projectId,
          scenario: scenarioId
        })
      });

      if (!response.ok) {
        throw new Error("Failed to inject fault");
      }

      setSuccess(scenarioId);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      setError("Failed to communicate with Demo Backend.");
    } finally {
      setIsInjecting(null);
    }
  };

  return (
    <div className="bg-black/40 border border-red-500/30 rounded-2xl p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <AlertTriangle className="w-32 h-32 text-red-500" />
      </div>

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-2 text-red-400">
          <AlertTriangle className="w-5 h-5" />
          <h3 className="font-bold text-lg">Fault Injection Lab</h3>
        </div>
        <p className="text-gray-400 text-sm mb-6 max-w-lg">
          Select a scenario below to safely inject simulated telemetry into the ingestion pipeline. Watch how Sentinel AI detects the anomaly and automatically remediates the issue.
        </p>

        {error && (
          <div className="bg-red-500/10 text-red-400 text-sm p-3 rounded-lg border border-red-500/20 mb-4">
            {error}
          </div>
        )}

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map((scenario) => (
            <div 
              key={scenario.id}
              className="bg-white/5 border border-white/10 p-4 rounded-xl flex flex-col h-full"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className={`p-2 rounded-lg ${scenario.color}`}>
                  {scenario.icon}
                </div>
                <h4 className="font-semibold">{scenario.name}</h4>
              </div>
              <p className="text-xs text-gray-400 mb-6 flex-grow">{scenario.description}</p>
              
              <button
                onClick={() => injectFault(scenario.id)}
                disabled={isInjecting !== null}
                className={`w-full py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 ${
                  success === scenario.id
                    ? "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30"
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isInjecting === scenario.id ? (
                  <span className="flex items-center gap-2">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-4 h-4 border-2 border-red-400 border-t-transparent rounded-full"
                    />
                    Injecting...
                  </span>
                ) : success === scenario.id ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" /> Injected
                  </>
                ) : (
                  "Trigger Scenario"
                )}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
