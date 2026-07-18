"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FolderKanban, Save, Loader2, Server, FileText, Brain, Clock } from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useUpdateWorkspace } from "@/lib/api/hooks";

const environments = [
  { value: "development", label: "Development", color: "text-emerald-400" },
  { value: "staging", label: "Staging", color: "text-amber-400" },
  { value: "production", label: "Production", color: "text-rose-400" },
];

export default function WorkspaceSettingsPage() {
  const { activeWorkspace, setActiveWorkspace, setWorkspaces, workspaces } = useOrgStore();
  const updateWs = useUpdateWorkspace();
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({ name: "", environment: "development", description: "", incident_retention_days: 90 });

  useEffect(() => {
    if (activeWorkspace) {
      setForm({
        name: activeWorkspace.name || "",
        environment: activeWorkspace.environment || "development",
        description: activeWorkspace.description || "",
        incident_retention_days: activeWorkspace.incident_retention_days || 90,
      });
    }
  }, [activeWorkspace]);

  const handleSave = async () => {
    if (!activeWorkspace) return;
    try {
      const updated = await updateWs.mutateAsync({
        wsId: activeWorkspace.id,
        payload: { name: form.name || undefined, environment: form.environment as any || undefined, description: form.description || undefined, incident_retention_days: form.incident_retention_days },
      });
      setActiveWorkspace(updated);
      setWorkspaces(workspaces.map((w) => (w.id === updated.id ? updated : w)));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error("Failed to update workspace:", err);
    }
  };

  if (!activeWorkspace) {
    return <div className="flex items-center justify-center py-20"><p className="text-sm text-muted-foreground">No workspace selected.</p></div>;
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Workspace Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Configure your workspace environment and preferences.</p>
      </div>

      {/* Workspace Name */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold"><FolderKanban className="h-4 w-4 text-primary" /> Workspace Name</div>
        <input id="ws-name-input" type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition" placeholder="Workspace name" />
      </div>

      {/* Environment */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold"><Server className="h-4 w-4 text-primary" /> Environment</div>
        <div className="grid grid-cols-3 gap-3">
          {environments.map((env) => (
            <button key={env.value} onClick={() => setForm({ ...form, environment: env.value })}
              className={`rounded-xl border p-3 text-center transition ${form.environment === env.value ? "border-primary/50 bg-primary/5" : "border-border/40 bg-background/30 hover:border-border/60"}`}>
              <p className={`text-xs font-semibold ${form.environment === env.value ? env.color : "text-muted-foreground"}`}>{env.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Description */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold"><FileText className="h-4 w-4 text-primary" /> Description</div>
        <textarea id="ws-description-input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition resize-none" placeholder="Describe this workspace..." />
      </div>

      {/* AI Config Placeholder */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold"><Brain className="h-4 w-4 text-primary" /> Default AI Configuration</div>
        <div className="rounded-xl border border-border/30 bg-muted/10 p-4">
          <p className="text-xs text-muted-foreground">AI configuration editor will be available in a future update. Current settings: default model configuration.</p>
        </div>
      </div>

      {/* Incident Retention */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold"><Clock className="h-4 w-4 text-primary" /> Incident Retention</div>
          <span className="text-xs font-mono text-primary">{form.incident_retention_days} days</span>
        </div>
        <input id="ws-retention-slider" type="range" min="7" max="365" value={form.incident_retention_days} onChange={(e) => setForm({ ...form, incident_retention_days: Number(e.target.value) })} className="w-full accent-primary h-1.5 rounded-full cursor-pointer" />
        <div className="flex justify-between text-[10px] text-muted-foreground"><span>7 days</span><span>365 days</span></div>
      </div>

      {/* Save */}
      <div className="flex items-center gap-3 pt-2">
        <button id="ws-save-button" onClick={handleSave} disabled={updateWs.isPending} className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition">
          {updateWs.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />} Save Changes
        </button>
        {saved && <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="text-xs font-medium text-emerald-400">✓ Saved</motion.span>}
      </div>
    </motion.div>
  );
}
