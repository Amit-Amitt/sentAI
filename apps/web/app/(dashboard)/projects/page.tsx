"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Copy, Plus, TerminalSquare, Server, Key, Activity, CheckCircle2 } from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";

export default function ProjectsPage() {
  const { activeWorkspace } = useOrgStore();
  const [projects, setProjects] = useState<any[]>([]); // In a real app this would use a fetch hook
  
  const [isCreating, setIsCreating] = useState(false);
  const [newProject, setNewProject] = useState({ name: "", language: "typescript" });
  const [generatedKey, setGeneratedKey] = useState("");

  const handleCreate = () => {
    // Mocking project creation
    const apiKey = `sent_${Math.random().toString(36).substring(2, 15)}_${Math.random().toString(36).substring(2, 15)}`;
    setGeneratedKey(apiKey);
    
    setProjects(prev => [...prev, {
      id: `proj_${Date.now()}`,
      name: newProject.name,
      language: newProject.language,
      status: "ACTIVE",
      created_at: new Date().toISOString(),
      api_key: apiKey
    }]);
    
    setIsCreating(false);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold flex items-center gap-3">
            <Server className="h-8 w-8 text-primary" />
            Connected Applications
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage projects emitting live telemetry to Sentinel AI.
          </p>
        </div>
        <button 
          onClick={() => setIsCreating(true)}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-xl font-bold flex items-center gap-2 hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" /> New Project
        </button>
      </div>

      {isCreating && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-2xl p-6"
        >
          <h3 className="font-bold mb-4">Create New Project</h3>
          <div className="flex gap-4 mb-4">
            <input 
              type="text" 
              placeholder="Project Name (e.g., api-gateway)" 
              value={newProject.name}
              onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              className="bg-background border border-border rounded-lg px-4 py-2 w-full"
            />
            <select 
              value={newProject.language}
              onChange={(e) => setNewProject({ ...newProject, language: e.target.value })}
              className="bg-background border border-border rounded-lg px-4 py-2"
            >
              <option value="typescript">Node.js (TypeScript)</option>
              <option value="python">Python (FastAPI)</option>
              <option value="go">Go</option>
            </select>
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setIsCreating(false)} className="px-4 py-2 text-muted-foreground font-semibold hover:text-foreground">Cancel</button>
            <button onClick={handleCreate} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-bold">Create & Generate Key</button>
          </div>
        </motion.div>
      )}

      {generatedKey && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 p-6 rounded-2xl">
          <div className="flex items-start gap-4">
            <CheckCircle2 className="h-6 w-6 text-emerald-500 shrink-0" />
            <div className="flex-1 space-y-4">
              <h3 className="font-bold text-emerald-500">Project Created Successfully</h3>
              <p className="text-sm text-foreground">Copy this API Key immediately. It will not be shown again.</p>
              
              <div className="flex items-center gap-2 bg-zinc-950 border border-zinc-800 p-3 rounded-lg">
                <code className="text-emerald-400 font-mono text-sm flex-1">{generatedKey}</code>
                <button className="text-zinc-400 hover:text-white" onClick={() => navigator.clipboard.writeText(generatedKey)}>
                  <Copy className="h-4 w-4" />
                </button>
              </div>

              <div>
                <p className="text-sm font-bold mt-4 mb-2">Installation Instructions</p>
                <pre className="bg-zinc-950 border border-zinc-800 p-4 rounded-lg text-xs font-mono text-zinc-300 overflow-x-auto">
{`npm install @sentinel-ai/agent

import { Sentinel } from '@sentinel-ai/agent';

Sentinel.init({
  apiKey: "${generatedKey}",
  serviceName: "${projects[projects.length - 1]?.name}"
});

// For Express apps
app.use(Sentinel.requestHandler());`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {projects.length === 0 ? (
          <div className="text-center p-12 border border-dashed border-border/50 rounded-2xl text-muted-foreground">
            <TerminalSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No projects created yet. Create a project to start streaming telemetry.</p>
          </div>
        ) : (
          projects.map(proj => (
            <div key={proj.id} className="bg-card border border-border p-6 rounded-2xl flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                  <Activity className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">{proj.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs font-mono bg-muted px-2 py-0.5 rounded text-muted-foreground">{proj.language}</span>
                    <span className="flex items-center gap-1 text-[10px] uppercase font-bold text-emerald-500">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      Receiving Data
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider">Events (24h)</p>
                <p className="font-mono font-bold text-xl mt-1">45,291</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
