"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  FileCheck,
  GitPullRequest,
  Globe,
  HardDrive,
  History,
  Info,
  Network,
  Play,
  PlayCircle,
  Search,
  Server,
  Settings,
  ShieldAlert,
  Sparkles,
  Terminal,
  TerminalSquare,
  Wrench,
  Zap,
} from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useIncidents } from "@/lib/api/hooks/useIncidents";
import { useIncident } from "@/lib/api/hooks/useIncident";
import { useRemediation } from "@/lib/api/hooks/useRemediation";
import { useSimilarMemories } from "@/lib/api/hooks/useMemory";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// --- Subcomponents --- //

function AnimatedCard({ children, className = "", delay = 0 }: { children: React.ReactNode, className?: string, delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={`rounded-2xl border border-border/60 bg-card/40 backdrop-blur-xl p-6 shadow-xl relative overflow-hidden group ${className}`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}

// 1. Hero Section
function HeroSection({ incident }: { incident: any }) {
  return (
    <AnimatedCard delay={0.1} className="col-span-full xl:col-span-8 flex flex-col justify-between border-primary/20">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border/50 pb-6 mb-6">
        <div>
          <div className="flex items-center gap-3 mb-3">
            <span className="font-mono text-sm font-bold text-primary px-2 py-0.5 rounded bg-primary/10 border border-primary/20">{incident?.id || "INC-0000"}</span>
            <SeverityBadge severity={incident?.severity || "SEV1"} />
            <span className="animate-pulse flex h-2 w-2 rounded-full bg-red-500"></span>
            <span className="text-xs font-bold text-red-500 uppercase tracking-wider">Live Incident</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground">{incident?.summary || "Global API Gateway Latency Spike & Connection Drops"}</h1>
        </div>
        <div className="flex items-center gap-4 bg-background/50 rounded-2xl p-3 border border-border/50 shadow-inner">
          <div className="text-right">
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">System Confidence</p>
            <p className="text-lg font-bold text-emerald-400">{incident?.confidence || 94}%</p>
          </div>
          <ConfidenceIndicator confidence={incident?.confidence || 94} size={60} />
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Affected Services</p>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {(incident?.affected_services || ["api-gateway", "auth-service", "redis-cluster"]).map((svc: string) => (
              <span key={svc} className="bg-muted/80 px-2 py-1 rounded text-[10px] font-mono border border-border/50">{svc}</span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Environment</p>
          <p className="font-semibold flex items-center gap-2 mt-2"><Globe className="h-4 w-4 text-blue-400" /> Production</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Time Elapsed</p>
          <p className="font-semibold flex items-center gap-2 mt-2 text-amber-500"><Clock className="h-4 w-4" /> 14m 32s</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">AI Verdict</p>
          <p className="font-semibold flex items-center gap-2 mt-2 text-emerald-400"><CheckCircle2 className="h-4 w-4" /> Root Cause Found</p>
        </div>
      </div>
    </AnimatedCard>
  );
}

// 2. Quick Actions
function QuickActions() {
  return (
    <AnimatedCard delay={0.2} className="col-span-full xl:col-span-4 flex flex-col">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
        <Zap className="h-4 w-4" /> Command Center Actions
      </h3>
      <div className="grid grid-cols-2 gap-3 h-full">
        <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-primary/30 bg-primary/10 hover:bg-primary/20 text-primary transition">
          <PlayCircle className="h-6 w-6 mb-2" />
          <span className="text-xs font-bold">Auto-Remediate</span>
        </button>
        <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 transition">
          <GitPullRequest className="h-6 w-6 mb-2" />
          <span className="text-xs font-bold">Create PR</span>
        </button>
        <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-border/60 bg-card hover:bg-muted/50 transition">
          <FileCheck className="h-6 w-6 mb-2 text-muted-foreground" />
          <span className="text-xs font-bold">Export Report</span>
        </button>
        <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-border/60 bg-card hover:bg-muted/50 transition">
          <History className="h-6 w-6 mb-2 text-muted-foreground" />
          <span className="text-xs font-bold">Replay Investigation</span>
        </button>
      </div>
    </AnimatedCard>
  );
}

// 3. Agent Workflow
function AgentWorkflow({ agents }: { agents: any }) {
  const defaultAgents = [
    { name: "Orchestrator", status: "COMPLETED", duration: "120ms" },
    { name: "Log Analysis", status: "COMPLETED", duration: "850ms" },
    { name: "Metrics Analysis", status: "COMPLETED", duration: "420ms" },
    { name: "Root Cause", status: "COMPLETED", duration: "1.2s" },
    { name: "Memory Engine", status: "COMPLETED", duration: "300ms" },
    { name: "Remediation", status: "RUNNING", duration: "Active" },
    { name: "GitHub PR", status: "WAITING", duration: "-" },
  ];

  return (
    <AnimatedCard delay={0.3} className="col-span-full">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-6 flex items-center gap-2">
        <BrainCircuit className="h-4 w-4" /> Live LangGraph Orchestration
      </h3>
      <div className="flex flex-wrap items-center gap-2">
        {defaultAgents.map((agent, i) => (
          <div key={agent.name} className="flex items-center gap-2">
            <motion.div 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 + (i * 0.1) }}
              className={`flex flex-col items-center justify-center w-32 h-20 rounded-xl border p-2 text-center relative ${
              agent.status === 'COMPLETED' ? 'bg-emerald-500/10 border-emerald-500/30' :
              agent.status === 'RUNNING' ? 'bg-blue-500/10 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.3)]' :
              'bg-muted/30 border-border/40 opacity-50'
            }`}>
              {agent.status === 'RUNNING' && (
                <span className="absolute top-2 right-2 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
              )}
              <span className="text-[10px] font-bold text-foreground leading-tight">{agent.name}</span>
              <span className={`text-[9px] mt-1 font-mono ${
                agent.status === 'COMPLETED' ? 'text-emerald-500' :
                agent.status === 'RUNNING' ? 'text-blue-400 animate-pulse' : 'text-muted-foreground'
              }`}>{agent.status}</span>
              <span className="text-[8px] text-muted-foreground mt-0.5">{agent.duration}</span>
            </motion.div>
            {i < defaultAgents.length - 1 && (
              <div className="w-8 h-[2px] bg-border/50 relative">
                {agent.status === 'COMPLETED' && (
                  <motion.div 
                    initial={{ width: 0 }} 
                    animate={{ width: "100%" }} 
                    transition={{ duration: 0.5, delay: 0.4 + (i * 0.1) }}
                    className="absolute top-0 left-0 h-full bg-emerald-500/50" 
                  />
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </AnimatedCard>
  );
}

// 4. Live Log Stream (Simulated)
function LiveLogStream() {
  const [logs, setLogs] = useState<string[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/stream/dashboard`);
    
    eventSource.addEventListener('telemetry', (e) => {
      try {
        const data = JSON.parse(e.data);
        const logLine = `[${data.type}] ${data.timestamp} - ${JSON.stringify(data.payload)}`;
        setLogs(prev => [...prev, logLine].slice(-50));
      } catch (err) {}
    });
    
    eventSource.addEventListener('incident', (e) => {
      try {
        const data = JSON.parse(e.data);
        const logLine = `[INCIDENT] ${data.severity} ${data.incident_id} created - Status: ${data.status}`;
        setLogs(prev => [...prev, logLine].slice(-50));
      } catch (err) {}
    });

    return () => eventSource.close();
  }, []);

  return (
    <AnimatedCard delay={0.4} className="col-span-full lg:col-span-6 flex flex-col h-[400px]">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
          <TerminalSquare className="h-4 w-4" /> Live Telemetry Stream
        </h3>
        <span className="animate-pulse flex h-2 w-2 rounded-full bg-green-500"></span>
      </div>
      <div className="flex-1 bg-zinc-950 rounded-xl p-4 overflow-y-auto font-mono text-[10px] md:text-xs leading-relaxed border border-zinc-800 flex flex-col justify-end">
        <AnimatePresence initial={false}>
          {logs.map((log, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`py-0.5 ${log.includes("ERROR") ? "text-red-400" : log.includes("WARN") ? "text-amber-400" : log.includes("agent:") ? "text-purple-400 font-bold" : "text-zinc-400"}`}
            >
              {log}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </AnimatedCard>
  );
}

// 5. Metrics Panel (Simulated Live Recharts)
function LiveMetricsPanel() {
  const [data, setData] = useState(Array.from({length: 20}, (_, i) => ({ time: i, cpu: 30 + Math.random()*20, mem: 40 + Math.random()*10, err: 0 })));

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => {
        const last = prev[prev.length - 1];
        if (!last) return prev;
        const newCpu = last.cpu > 80 ? 95 + Math.random()*5 : last.cpu + Math.random()*10;
        const newErr = newCpu > 85 ? Math.random() * 50 : 0;
        const next = [...prev.slice(1), { time: last.time + 1, cpu: newCpu, mem: 60 + Math.random()*10, err: newErr }];
        return next;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <AnimatedCard delay={0.5} className="col-span-full lg:col-span-6 h-[400px]">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
        <Activity className="h-4 w-4" /> Real-time System Metrics
      </h3>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorErr" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
            <XAxis dataKey="time" hide />
            <YAxis stroke="#666" fontSize={10} tickFormatter={(val) => `${val}%`} />
            <Tooltip contentStyle={{ backgroundColor: '#09090b', borderColor: '#333', fontSize: '12px' }} />
            <Area type="monotone" dataKey="cpu" name="CPU Usage" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorCpu)" isAnimationActive={false} />
            <Area type="monotone" dataKey="err" name="Error Rate" stroke="#f59e0b" strokeWidth={2} fillOpacity={1} fill="url(#colorErr)" isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </AnimatedCard>
  );
}

// 6. Root Cause & Memory Panel
function InsightsPanel({ incident }: { incident: any }) {
  return (
    <AnimatedCard delay={0.6} className="col-span-full lg:col-span-4 space-y-6 bg-gradient-to-br from-card/40 to-primary/5">
      <div>
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" /> Root Cause Diagnosis
        </h3>
        <div className="bg-background/80 rounded-xl p-4 border border-primary/20 shadow-inner">
          <p className="text-sm font-bold leading-relaxed">{incident?.root_cause?.primary || "Database connection pool exhausted due to sudden spike in checkout requests."}</p>
        </div>
      </div>
      
      <div>
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
          <Database className="h-4 w-4 text-blue-500" /> Historical Memory Context
        </h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/40 border border-border/50 text-xs">
            <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
            <div>
              <p className="font-bold">Similar incident occurred on May 12th</p>
              <p className="text-muted-foreground mt-1">Resolution involved expanding the Redis maxmemory-policy and scaling connection pool.</p>
            </div>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-primary/10 border border-primary/20 text-xs font-bold text-primary">
            <span>Historical Fix Success Rate</span>
            <span>98.4%</span>
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
}

// 7. Remediation & GitHub Panel
function RemediationPanel({ remediation }: { remediation: any }) {
  return (
    <AnimatedCard delay={0.7} className="col-span-full lg:col-span-8 flex flex-col md:flex-row gap-6 bg-gradient-to-br from-card/40 to-emerald-500/5">
      <div className="flex-1 space-y-4">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
          <Wrench className="h-4 w-4 text-emerald-500" /> Autonomous Remediation
        </h3>
        <div className="bg-background/80 rounded-xl p-4 border border-border/50 shadow-inner">
          <p className="text-xs font-bold text-foreground mb-3">Proposed Infrastructure Commands</p>
          <div className="bg-zinc-950 rounded-lg p-3 overflow-x-auto border border-zinc-800">
            <pre className="text-[10px] text-zinc-300 font-mono">
              <code>{`kubectl scale deployment redis-cluster --replicas=5
helm upgrade pg-pool -f new-limits.yaml
systemctl restart api-gateway`}</code>
            </pre>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-amber-500/10 border border-amber-500/20 p-3 rounded-lg">
            <p className="text-[10px] font-bold text-amber-500 uppercase">Risk Level</p>
            <p className="font-bold mt-1">Low (Non-Breaking)</p>
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 p-3 rounded-lg">
            <p className="text-[10px] font-bold text-blue-500 uppercase">Est. Downtime</p>
            <p className="font-bold mt-1">0 Minutes</p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 space-y-4 border-l border-border/50 pl-0 md:pl-6 pt-6 md:pt-0">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
          <GitPullRequest className="h-4 w-4 text-purple-500" /> GitHub PR Draft
        </h3>
        <div className="bg-background/80 rounded-xl p-4 border border-border/50 shadow-inner h-full flex flex-col">
          <div className="mb-3">
            <p className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Branch</p>
            <code className="text-[10px] font-mono text-purple-400 bg-purple-400/10 px-2 py-1 rounded">fix/redis-conn-pool-exhaustion</code>
          </div>
          <div className="mb-4">
            <p className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Title</p>
            <p className="text-xs font-bold">fix(infra): increase database connection limits and redis memory policy</p>
          </div>
          <div className="flex-1 bg-zinc-950 rounded-lg p-3 overflow-x-auto border border-zinc-800 flex flex-col justify-end">
            <pre className="text-[10px] text-emerald-400 font-mono">
              <code>{`+ max_connections: 5000
+ maxmemory-policy: allkeys-lru
- max_connections: 1000
- maxmemory-policy: noeviction`}</code>
            </pre>
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
}

// --- Main Page --- //

export default function CommandCenterPage() {
  const { activeWorkspace } = useOrgStore();
  const { data: incidentsList, isLoading } = useIncidents();
  
  // Try to use the most recent active incident, fallback to latest overall, or null
  const recentIncidentId = incidentsList?.results?.[0]?.id;
  const { data: fullIncident } = useIncident(recentIncidentId || "");
  const { data: remediation } = useRemediation(activeWorkspace?.id, recentIncidentId);

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-8 space-y-8 bg-background relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute top-0 right-0 -mr-48 -mt-48 w-96 h-96 bg-primary/20 rounded-full blur-[120px] opacity-50 pointer-events-none" />
      <div className="absolute bottom-0 left-0 -ml-48 -mb-48 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] opacity-50 pointer-events-none" />
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight flex items-center gap-3">
            <TerminalSquare className="h-8 w-8 text-primary" />
            Executive AI Command Center
          </h1>
          <p className="text-sm text-muted-foreground mt-2">
            Sentinel AI Unified Operations & Remediation Dashboard
          </p>
        </div>
        <div className="flex items-center gap-3 bg-muted/40 p-2 rounded-xl border border-border/50">
          <div className="text-right mr-2 hidden md:block">
            <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Global Status</p>
            <p className="text-sm font-bold text-emerald-400">All Systems Nominal</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="text-sm font-semibold tracking-wider uppercase">Initializing AI Core...</p>
          </div>
        </div>
      ) : (
        /* Grid Layout */
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 relative z-10">
          <HeroSection incident={fullIncident || incidentsList?.results?.[0]} />
          <QuickActions />
          <AgentWorkflow agents={fullIncident?.agents} />
          
          <LiveLogStream />
          <LiveMetricsPanel />
          
          <InsightsPanel incident={fullIncident} />
          <RemediationPanel remediation={remediation} />
        </div>
      )}
    </div>
  );
}
