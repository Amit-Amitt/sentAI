"use client";

import { useState } from "react";
import { Bot, Cpu, Database, Save, Sliders, Webhook } from "lucide-react";
import { Badge } from "@sentinel/ui";

export default function SettingsPage() {
  const [provider, setProvider] = useState("gemini");
  const [concurrency, setConcurrency] = useState(3);
  const [pagerduty, setPagerduty] = useState("https://events.pagerduty.com/v2/enqueue");

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight font-sans">Settings & Tuning</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Adjust model weights, configure log limits, and register notification endpoints.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Navigation Sidebar */}
        <div className="rounded-2xl border border-border/80 bg-card/40 p-4 backdrop-blur space-y-2 h-fit">
          {[
            { id: "engine", label: "Model Configuration", icon: Bot },
            { id: "thresholds", label: "Agent Thresholds", icon: Sliders },
            { id: "hooks", label: "Integrations & Webhooks", icon: Webhook },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground transition hover:bg-muted/70 hover:text-foreground"
              >
                <Icon className="h-4.5 w-4.5" />
                {item.label}
              </button>
            );
          })}
        </div>

        {/* Configurations Fields */}
        <div className="rounded-2xl border border-border/80 bg-card/60 p-6 backdrop-blur-xl md:col-span-2 space-y-6">
          {/* Section 1 */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" /> Orchestrator Model Engine
            </h2>
            <div className="space-y-3.5">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-muted-foreground">Select AI Provider</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary transition"
                >
                  <option value="gemini">Google Gemini Pro (Recommended)</option>
                  <option value="openai">OpenAI GPT-4o</option>
                  <option value="claude">Anthropic Claude 3.5 Sonnet</option>
                </select>
              </div>
            </div>
          </div>

          <hr className="border-border/60" />

          {/* Section 2 */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Sliders className="h-4 w-4 text-amber-500" /> Pipeline Concurrency Limits
            </h2>
            <div className="space-y-3.5">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-muted-foreground">Max Parallel Sub-Agent Executors</label>
                <input
                  type="number"
                  min={1}
                  max={6}
                  value={concurrency}
                  onChange={(e) => setConcurrency(parseInt(e.target.value))}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2 text-sm text-foreground outline-none focus:border-primary transition max-w-[150px]"
                />
                <p className="text-[10px] text-muted-foreground leading-normal mt-1">
                  Controls how many ingestion agents (Log, Metrics, Deployments) execute in parallel during step 2.
                </p>
              </div>
            </div>
          </div>

          <hr className="border-border/60" />

          {/* Section 3 */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Webhook className="h-4 w-4 text-indigo-400" /> PagerDuty Service Hook
            </h2>
            <div className="space-y-3.5">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-muted-foreground">Notification Event API</label>
                <input
                  type="text"
                  value={pagerduty}
                  onChange={(e) => setPagerduty(e.target.value)}
                  className="rounded-xl border border-border/80 bg-background px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary transition"
                />
              </div>
            </div>
          </div>

          {/* Save Action */}
          <div className="flex justify-end pt-4 border-t border-border/50">
            <button className="flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground transition hover:bg-primary/95">
              <Save className="h-4 w-4" /> Save Configurations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
