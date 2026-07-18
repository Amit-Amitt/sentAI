import type { Metadata } from "next";
import { Hero } from "@/components/marketing/hero";
import { TrustedBy } from "@/components/marketing/trusted-by";
import { FeatureGrid } from "@/components/marketing/feature-grid";
import { AgentWorkflow } from "@/components/marketing/agent-workflow";
import { Benefits } from "@/components/marketing/benefits";
import { Testimonials } from "@/components/marketing/testimonials";
import { PricingPreview } from "@/components/marketing/pricing-preview";
import { FAQ } from "@/components/marketing/faq";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = {
  title: "Sentinel AI — The Autonomous AI Incident Commander",
  description: "7 AI agents detect, investigate, and resolve incidents autonomously. Cut MTTR by 73%. Start your free trial today.",
};

export default function LandingPage() {
  return (
    <>
      <Hero />
      <TrustedBy />
      <FeatureGrid />
      <AgentWorkflow />
      <Benefits />
      <Testimonials />
      <PricingPreview />
      <FAQ />
      <CTASection />
    </>
  );
}
