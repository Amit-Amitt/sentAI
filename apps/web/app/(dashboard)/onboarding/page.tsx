"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Building2, Check, FolderKanban, Loader2, Rocket, Users } from "lucide-react";
import { useCreateOrganization } from "@/lib/api/hooks";
import { workspacesService } from "@/lib/api/services/workspaces";
import { useOrgStore } from "@/lib/store/org-store";
import { organizationsService } from "@/lib/api/services/organizations";

const steps = [
  { id: 1, label: "Organization", icon: Building2 },
  { id: 2, label: "Workspace", icon: FolderKanban },
  { id: 3, label: "Launch", icon: Rocket },
];

function slugify(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 100) || "my-org";
}

export default function OnboardingPage() {
  const router = useRouter();
  const createOrg = useCreateOrganization();
  const { setActiveOrganization, setWorkspaces, setActiveWorkspace, setOrganizations } = useOrgStore();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [orgForm, setOrgForm] = useState({ name: "", slug: "", industry: "", region: "" });
  const [wsForm, setWsForm] = useState({ name: "Production", slug: "production", environment: "production" });
  const [createdOrgId, setCreatedOrgId] = useState<string | null>(null);

  const handleCreateOrg = async () => {
    setLoading(true);
    try {
      const slug = orgForm.slug || slugify(orgForm.name);
      const org = await createOrg.mutateAsync({ name: orgForm.name, slug, industry: orgForm.industry || undefined, region: orgForm.region || undefined });
      setCreatedOrgId(org.id);
      setStep(2);
    } catch (err) {
      console.error("Failed to create org:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!createdOrgId) return;
    setLoading(true);
    try {
      const slug = wsForm.slug || slugify(wsForm.name);
      await workspacesService.createWorkspace(createdOrgId, { name: wsForm.name, slug, environment: wsForm.environment as any });
      setStep(3);
    } catch (err) {
      console.error("Failed to create workspace:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFinish = async () => {
    try {
      const { results: orgs } = await organizationsService.listOrganizations();
      setOrganizations(orgs);
      const newOrg = orgs.find((o) => o.id === createdOrgId) || orgs[0];
      if (newOrg) {
        setActiveOrganization(newOrg);
        const { results: ws } = await workspacesService.listWorkspaces(newOrg.id);
        setWorkspaces(ws);
        if (ws.length > 0) setActiveWorkspace(ws[0] ?? null);
      }
    } catch {}
    router.push("/dashboard");
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg space-y-8">
        {/* Step Indicator */}
        <div className="flex items-center justify-center gap-2">
          {steps.map((s, i) => {
            const Icon = s.icon;
            const isActive = step === s.id;
            const isDone = step > s.id;
            return (
              <div key={s.id} className="flex items-center gap-2">
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl border transition ${isDone ? "bg-emerald-500/10 border-emerald-500/30" : isActive ? "bg-primary/10 border-primary/30" : "bg-muted/20 border-border/40"}`}>
                  {isDone ? <Check className="h-4 w-4 text-emerald-400" /> : <Icon className={`h-4 w-4 ${isActive ? "text-primary" : "text-muted-foreground"}`} />}
                </div>
                <span className={`text-xs font-semibold hidden sm:inline ${isActive ? "text-foreground" : "text-muted-foreground"}`}>{s.label}</span>
                {i < steps.length - 1 && <div className={`h-px w-8 ${step > s.id ? "bg-emerald-500/30" : "bg-border/30"}`} />}
              </div>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Organization */}
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="rounded-2xl border border-border/60 bg-card/50 p-8 space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-xl font-bold">Create Your Organization</h2>
                <p className="text-sm text-muted-foreground">Set up your company or team to start using Sentinel AI.</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Organization Name *</label>
                  <input id="onboard-org-name" type="text" value={orgForm.name} onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value, slug: slugify(e.target.value) })} className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition" placeholder="Acme Inc." />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Slug</label>
                  <div className="flex items-center rounded-xl border border-border/60 bg-background/50 overflow-hidden">
                    <span className="px-3 text-xs text-muted-foreground bg-muted/20 py-2.5 border-r border-border/40">sentinel.ai/</span>
                    <input id="onboard-org-slug" type="text" value={orgForm.slug} onChange={(e) => setOrgForm({ ...orgForm, slug: e.target.value })} className="flex-1 px-3 py-2.5 text-sm bg-transparent outline-none" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Industry</label>
                    <select id="onboard-industry" value={orgForm.industry} onChange={(e) => setOrgForm({ ...orgForm, industry: e.target.value })} className="w-full rounded-xl border border-border/60 bg-background/50 px-3 py-2.5 text-sm outline-none appearance-none cursor-pointer">
                      <option value="">Select...</option>
                      {["Technology", "Finance", "Healthcare", "E-Commerce", "SaaS", "Other"].map((i) => <option key={i} value={i}>{i}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Region</label>
                    <select id="onboard-region" value={orgForm.region} onChange={(e) => setOrgForm({ ...orgForm, region: e.target.value })} className="w-full rounded-xl border border-border/60 bg-background/50 px-3 py-2.5 text-sm outline-none appearance-none cursor-pointer">
                      <option value="">Select...</option>
                      {["North America", "Europe", "Asia Pacific"].map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                </div>
              </div>
              <button id="onboard-create-org" onClick={handleCreateOrg} disabled={!orgForm.name.trim() || loading} className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />} Continue
              </button>
            </motion.div>
          )}

          {/* Step 2: Workspace */}
          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="rounded-2xl border border-border/60 bg-card/50 p-8 space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-xl font-bold">Create a Workspace</h2>
                <p className="text-sm text-muted-foreground">A default workspace was created. Add another if you need separate environments.</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Workspace Name</label>
                  <input id="onboard-ws-name" type="text" value={wsForm.name} onChange={(e) => setWsForm({ ...wsForm, name: e.target.value, slug: slugify(e.target.value) })} className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-muted-foreground mb-1.5">Environment</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[{ v: "development", l: "Dev", c: "text-emerald-400" }, { v: "staging", l: "Staging", c: "text-amber-400" }, { v: "production", l: "Prod", c: "text-rose-400" }].map((e) => (
                      <button key={e.v} onClick={() => setWsForm({ ...wsForm, environment: e.v })} className={`rounded-xl border p-3 text-center transition ${wsForm.environment === e.v ? "border-primary/50 bg-primary/5" : "border-border/40 hover:border-border/60"}`}>
                        <p className={`text-xs font-semibold ${wsForm.environment === e.v ? e.c : "text-muted-foreground"}`}>{e.l}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setStep(3)} className="flex-1 rounded-xl border border-border/60 px-6 py-3 text-sm font-medium text-muted-foreground hover:bg-muted/20 transition">Skip</button>
                <button id="onboard-create-ws" onClick={handleCreateWorkspace} disabled={!wsForm.name.trim() || loading} className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />} Create & Continue
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Launch */}
          {step === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="rounded-2xl border border-border/60 bg-card/50 p-8 text-center space-y-6">
              <div className="flex justify-center"><div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20"><Rocket className="h-8 w-8 text-emerald-400" /></div></div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold">You&apos;re All Set! 🎉</h2>
                <p className="text-sm text-muted-foreground">Your organization and workspace are ready. Start monitoring incidents with Sentinel AI.</p>
              </div>
              <button id="onboard-finish" onClick={handleFinish} className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition">
                <Rocket className="h-4 w-4" /> Go to Dashboard
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
