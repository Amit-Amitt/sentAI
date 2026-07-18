import type { Metadata } from "next";
import { FeatureGrid } from "@/components/marketing/feature-grid";
import { AgentWorkflow } from "@/components/marketing/agent-workflow";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = { title: "Features" };

export default function FeaturesPage() {
  return (
    <>
      <section className="relative py-24 sm:py-32">
        <div className="absolute inset-0 bg-gradient-radial" />
        <div className="relative mx-auto max-w-3xl px-6 text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Platform</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Everything you need to <span className="text-gradient">resolve incidents</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            Sentinel AI combines 7 specialized agents, LangGraph orchestration, and frontier LLMs into one autonomous incident commander.
          </p>
        </div>
      </section>
      <FeatureGrid />
      <AgentWorkflow />
      <CTASection />
    </>
  );
}
