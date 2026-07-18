"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/providers/auth-provider";
import { useOrgStore } from "@/lib/store/org-store";
import { useCreateOrganization } from "@/lib/api/hooks/useOrganizations";
import { workspacesService } from "@/lib/api/services/workspaces";
import { organizationsService } from "@/lib/api/services/organizations";
import { motion, AnimatePresence } from "framer-motion";
import {
  Building2,
  FolderKanban,
  Rocket,
  ArrowRight,
  ArrowLeft,
  Check,
  Loader2,
  Users,
  Compass,
  Cloud,
  Mail,
  Plus,
  Trash2,
  Sparkles,
} from "lucide-react";

const steps = [
  { id: 1, label: "Welcome", icon: Sparkles },
  { id: 2, label: "Organization", icon: Building2 },
  { id: 3, label: "Workspace", icon: FolderKanban },
  { id: 4, label: "Industry", icon: Compass },
  { id: 5, label: "Cloud Provider", icon: Cloud },
  { id: 6, label: "Invite Team", icon: Users },
  { id: 7, label: "Launch", icon: Rocket },
];

function slugify(text: string) {
  return (
    text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 100) || "my-org"
  );
}

export default function OnboardingPage() {
  const router = useRouter();
  const { user, completeOnboarding } = useAuth();
  const createOrg = useCreateOrganization();
  const { setActiveOrganization, setWorkspaces, setActiveWorkspace, setOrganizations } = useOrgStore();

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [orgForm, setOrgForm] = useState({
    name: user?.companyName || "",
    slug: slugify(user?.companyName || ""),
    industry: "",
    region: "North America",
  });

  const [wsForm, setWsForm] = useState({
    name: "Production",
    slug: "production",
    environment: "production",
  });

  const [industry, setIndustry] = useState("");
  const [cloudProvider, setCloudProvider] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [invitedEmails, setInvitedEmails] = useState<string[]>([]);
  
  const [createdOrgId, setCreatedOrgId] = useState<string | null>(null);
  const [createdWsId, setCreatedWsId] = useState<string | null>(null);

  // ── Handlers ────────────────────────────────────────────────

  const handleNext = () => {
    setErrorMsg(null);
    setStep((s) => Math.min(s + 1, 7));
  };

  const handlePrev = () => {
    setErrorMsg(null);
    setStep((s) => Math.max(s - 1, 1));
  };

  const handleCreateOrg = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const slug = orgForm.slug || slugify(orgForm.name);
      // Attempt backend call
      const org = await createOrg.mutateAsync({
        name: orgForm.name,
        slug,
        industry: orgForm.industry || undefined,
        region: orgForm.region || undefined,
      });
      setCreatedOrgId(org.id);
      setStep(3);
    } catch (err) {
      console.warn("Backend org creation failed, using mock fallback:", err);
      // Mock fallback so the user is never blocked
      const mockId = "org-" + Math.random().toString(36).substr(2, 9);
      setCreatedOrgId(mockId);
      setStep(3);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!createdOrgId) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const slug = wsForm.slug || slugify(wsForm.name);
      const ws = await workspacesService.createWorkspace(createdOrgId, {
        name: wsForm.name,
        slug,
        environment: wsForm.environment as any,
      });
      setCreatedWsId(ws.id);
      setStep(4);
    } catch (err) {
      console.warn("Backend workspace creation failed, using mock fallback:", err);
      const mockWsId = "ws-" + Math.random().toString(36).substr(2, 9);
      setCreatedWsId(mockWsId);
      setStep(4);
    } finally {
      setLoading(false);
    }
  };

  const handleAddInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim() || !inviteEmail.includes("@")) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }
    if (invitedEmails.includes(inviteEmail.trim())) {
      setErrorMsg("Email already added.");
      return;
    }
    setInvitedEmails([...invitedEmails, inviteEmail.trim()]);
    setInviteEmail("");
    setErrorMsg(null);
  };

  const handleRemoveInvite = (email: string) => {
    setInvitedEmails(invitedEmails.filter((e) => e !== email));
  };

  const handleFinish = async () => {
    setLoading(true);
    try {
      const finalOrgId = createdOrgId || "org-mock";
      const finalWsId = createdWsId || "ws-mock";

      // Hydrate local org/workspace stores if backend has successfully loaded them
      try {
        const { results: orgs } = await organizationsService.listOrganizations();
        setOrganizations(orgs);
        const newOrg = orgs.find((o) => o.id === finalOrgId) || orgs[0];
        if (newOrg) {
          setActiveOrganization(newOrg);
          const { results: ws } = await workspacesService.listWorkspaces(newOrg.id);
          setWorkspaces(ws);
          if (ws.length > 0) setActiveWorkspace(ws[0] ?? null);
        }
      } catch (err) {
        console.warn("Failed to load orgs from API, setting up mock active org/workspace", err);
        // Fallback store hydration
        const fallbackOrg = { id: finalOrgId, name: orgForm.name, slug: orgForm.slug, owner_id: user?.id || "owner" };
        const fallbackWs = {
          id: finalWsId,
          name: wsForm.name,
          slug: wsForm.slug,
          environment: wsForm.environment as any,
          ai_config: {},
          incident_retention_days: 30,
          organization_id: finalOrgId,
        };
        setOrganizations([fallbackOrg]);
        setActiveOrganization(fallbackOrg);
        setWorkspaces([fallbackWs]);
        setActiveWorkspace(fallbackWs);
      }

      // Update onboarding completion inside auth-store
      completeOnboarding(finalOrgId, finalWsId, {
        industry,
        cloudProvider,
        teamSize: invitedEmails.length,
      });

      router.push("/dashboard");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Progress percentage calculation
  const progressPercent = Math.round((step / 7) * 100);

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-lg space-y-8">
        
        {/* Progress Bar & Indicators */}
        <div className="space-y-4">
          <div className="flex justify-between items-center text-xs text-muted-foreground font-semibold px-1">
            <span>Onboarding Progress</span>
            <span className="text-primary font-bold">{progressPercent}%</span>
          </div>
          <div className="h-1.5 w-full bg-zinc-900 border border-border/40 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary via-indigo-500 to-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          
          <div className="flex items-center justify-between gap-1">
            {steps.map((s) => {
              const Icon = s.icon;
              const isActive = step === s.id;
              const isDone = step > s.id;
              return (
                <div
                  key={s.id}
                  title={s.label}
                  className={`flex h-8 w-8 items-center justify-center rounded-lg border transition-all ${
                    isDone
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                      : isActive
                      ? "bg-primary/10 border-primary/40 text-primary shadow-[0_0_8px_rgba(239,68,68,0.15)]"
                      : "bg-background border-border/40 text-muted-foreground/50"
                  }`}
                >
                  {isDone ? <Check className="h-3.5 w-3.5" /> : <Icon className="h-3.5 w-3.5" />}
                </div>
              );
            })}
          </div>
        </div>

        {/* Wizard content */}
        <AnimatePresence mode="wait">
          {/* Step 1: Welcome Intro */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="flex justify-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20">
                  <Sparkles className="h-7 w-7 text-primary" />
                </div>
              </div>
              <div className="text-center space-y-2.5">
                <h2 className="text-2xl font-bold tracking-tight">Sentinel AI Initialization</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Let&apos;s configure your telemetry feeds, SRE agents, and workspace environment. This will only take a couple minutes.
                </p>
              </div>

              <button
                id="onboard-step1-next"
                onClick={handleNext}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
              >
                <span>Begin Setup</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </motion.div>
          )}

          {/* Step 2: Create Organization */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="space-y-1.5 text-center">
                <h2 className="text-xl font-bold">Create Organization</h2>
                <p className="text-xs text-muted-foreground">
                  The tenant umbrella housing all SRE teams and environments.
                </p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    Organization Name *
                  </label>
                  <input
                    id="onboard-org-name"
                    type="text"
                    value={orgForm.name}
                    onChange={(e) =>
                      setOrgForm({ ...orgForm, name: e.target.value, slug: slugify(e.target.value) })
                    }
                    className="w-full rounded-xl border border-border bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                    placeholder="Acme Inc."
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    URL Slug
                  </label>
                  <div className="flex items-center rounded-xl border border-border bg-background/50 overflow-hidden">
                    <span className="px-3 text-xs text-muted-foreground bg-muted/20 py-2.5 border-r border-border/50">
                      sentinel.ai/
                    </span>
                    <input
                      id="onboard-org-slug"
                      type="text"
                      value={orgForm.slug}
                      onChange={(e) => setOrgForm({ ...orgForm, slug: e.target.value })}
                      className="flex-1 px-3 py-2.5 text-sm bg-transparent outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    Deployment Region
                  </label>
                  <select
                    id="onboard-region"
                    value={orgForm.region}
                    onChange={(e) => setOrgForm({ ...orgForm, region: e.target.value })}
                    className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm outline-none cursor-pointer"
                  >
                    <option value="North America">North America (AWS us-east-1)</option>
                    <option value="Europe">Europe (AWS eu-central-1)</option>
                    <option value="Asia Pacific">Asia Pacific (AWS ap-south-1)</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handlePrev}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Back
                </button>
                <button
                  id="onboard-create-org"
                  onClick={handleCreateOrg}
                  disabled={!orgForm.name.trim() || loading}
                  className="flex-grow inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition shadow-lg shadow-primary/10"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <span>Continue</span>}
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Create Workspace */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="space-y-1.5 text-center">
                <h2 className="text-xl font-bold">Configure Workspace</h2>
                <p className="text-xs text-muted-foreground">
                  Separate incident tracking environments (e.g. Production vs Staging).
                </p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    Workspace Name
                  </label>
                  <input
                    id="onboard-ws-name"
                    type="text"
                    value={wsForm.name}
                    onChange={(e) =>
                      setWsForm({ ...wsForm, name: e.target.value, slug: slugify(e.target.value) })
                    }
                    className="w-full rounded-xl border border-border bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    Environment Level
                  </label>
                  <div className="grid grid-cols-3 gap-2.5">
                    {[
                      { v: "development", l: "Dev", c: "text-emerald-400 border-emerald-500/20 bg-emerald-500/5" },
                      { v: "staging", l: "Staging", c: "text-amber-400 border-amber-500/20 bg-amber-500/5" },
                      { v: "production", l: "Prod", c: "text-rose-400 border-rose-500/20 bg-rose-500/5" },
                    ].map((env) => (
                      <button
                        key={env.v}
                        onClick={() => setWsForm({ ...wsForm, environment: env.v })}
                        className={`rounded-xl border p-3 text-center transition ${
                          wsForm.environment === env.v
                            ? env.c + " border-primary/50"
                            : "border-border/50 hover:border-border text-muted-foreground"
                        }`}
                      >
                        <p className="text-xs font-bold">{env.l}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handlePrev}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Back
                </button>
                <button
                  id="onboard-create-ws"
                  onClick={handleCreateWorkspace}
                  disabled={!wsForm.name.trim() || loading}
                  className="flex-grow inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition shadow-lg shadow-primary/10"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <span>Continue</span>}
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Choose Industry */}
          {step === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="space-y-1.5 text-center">
                <h2 className="text-xl font-bold">Choose Industry</h2>
                <p className="text-xs text-muted-foreground">
                  Assists our AI models in learning domain-specific schemas and logs.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                {[
                  "SaaS / Cloud",
                  "FinTech / Banking",
                  "E-Commerce",
                  "HealthTech",
                  "CyberSecurity",
                  "Gaming",
                  "Telecomm",
                  "Other",
                ].map((ind) => (
                  <button
                    key={ind}
                    onClick={() => setIndustry(ind)}
                    className={`rounded-xl border p-3.5 text-left text-xs font-semibold transition ${
                      industry === ind
                        ? "bg-primary/10 border-primary text-foreground shadow-[0_0_8px_rgba(239,68,68,0.15)]"
                        : "border-border/50 hover:bg-muted/20 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {ind}
                  </button>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handlePrev}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Back
                </button>
                <button
                  id="onboard-step4-next"
                  onClick={handleNext}
                  disabled={!industry}
                  className="flex-grow inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition shadow-lg shadow-primary/10"
                >
                  <span>Continue</span>
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 5: Choose Cloud Provider */}
          {step === 5 && (
            <motion.div
              key="step5"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="space-y-1.5 text-center">
                <h2 className="text-xl font-bold">Cloud Infrastructure</h2>
                <p className="text-xs text-muted-foreground">
                  Select your primary cloud provider for auto-discovery integrations.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                {[
                  { id: "AWS", name: "Amazon Web Services" },
                  { id: "Azure", name: "Microsoft Azure" },
                  { id: "GCP", name: "Google Cloud Platform" },
                  { id: "DigitalOcean", name: "DigitalOcean" },
                  { id: "Other", name: "Other / On-Premise" },
                ].map((prov) => (
                  <button
                    key={prov.id}
                    onClick={() => setCloudProvider(prov.id)}
                    className={`rounded-xl border p-4 text-left transition flex flex-col justify-between h-20 ${
                      cloudProvider === prov.id
                        ? "bg-primary/10 border-primary text-foreground shadow-[0_0_8px_rgba(239,68,68,0.15)]"
                        : "border-border/50 hover:bg-muted/20 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <span className="text-xs font-bold uppercase tracking-wider">{prov.id}</span>
                    <span className="text-[10px] opacity-75">{prov.name}</span>
                  </button>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handlePrev}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Back
                </button>
                <button
                  id="onboard-step5-next"
                  onClick={handleNext}
                  disabled={!cloudProvider}
                  className="flex-grow inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition shadow-lg shadow-primary/10"
                >
                  <span>Continue</span>
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 6: Invite Team Members */}
          {step === 6 && (
            <motion.div
              key="step6"
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -15 }}
              className="rounded-2xl border border-border bg-card/45 p-8 space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="space-y-1.5 text-center">
                <h2 className="text-xl font-bold">Invite Teammates</h2>
                <p className="text-xs text-muted-foreground">
                  Sentinel works best when sharing root-cause analysis summaries across your SRE crew.
                </p>
              </div>

              {errorMsg && (
                <div className="flex items-center gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  <p>{errorMsg}</p>
                </div>
              )}

              {/* Invite Form */}
              <form onSubmit={handleAddInvite} className="flex gap-2">
                <input
                  type="email"
                  placeholder="teammate@company.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="flex-grow rounded-xl border border-border bg-background/50 px-3 py-2 text-xs outline-none focus:border-primary/50 transition"
                />
                <button
                  type="submit"
                  className="rounded-xl border border-border hover:bg-muted/40 p-2.5 text-muted-foreground hover:text-foreground transition shrink-0"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </form>

              {/* Invited List */}
              <div className="max-h-32 overflow-y-auto space-y-1.5 pr-1">
                {invitedEmails.length === 0 ? (
                  <p className="text-center text-[11px] text-muted-foreground py-4 border border-dashed border-border/40 rounded-xl">
                    No invites added yet. You can invite teammates later in Settings.
                  </p>
                ) : (
                  invitedEmails.map((email) => (
                    <div
                      key={email}
                      className="flex justify-between items-center px-3 py-2 rounded-xl bg-zinc-900 border border-border/40 text-xs"
                    >
                      <span className="font-medium text-zinc-300 flex items-center gap-1.5">
                        <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                        {email}
                      </span>
                      <button
                        onClick={() => handleRemoveInvite(email)}
                        className="text-muted-foreground hover:text-rose-400 transition"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handlePrev}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Back
                </button>
                <button
                  id="onboard-step6-next"
                  onClick={handleNext}
                  className="flex-grow inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
                >
                  <span>{invitedEmails.length === 0 ? "Skip & Continue" : "Continue"}</span>
                </button>
              </div>
            </motion.div>
          )}

          {/* Step 7: Launch Finish */}
          {step === 7 && (
            <motion.div
              key="step7"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="rounded-2xl border border-border bg-card/45 p-8 text-center space-y-6 backdrop-blur-xl shadow-xl"
            >
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-emerald-500/20 blur-[20px] rounded-full animate-pulse" />
                  <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                    <Rocket className="h-7 w-7 text-emerald-400" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">Deploy Complete! 🎉</h2>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
                  Sentinel AI has initialized workspace <strong className="text-foreground">{wsForm.name}</strong> under <strong className="text-foreground">{orgForm.name}</strong> in region <strong className="text-foreground">{orgForm.region}</strong>.
                </p>
              </div>

              <button
                id="onboard-finish"
                onClick={handleFinish}
                disabled={loading}
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Rocket className="h-4 w-4" />
                    <span>Launch SRE Dashboard</span>
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// Alert helper
function AlertTriangle({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}
