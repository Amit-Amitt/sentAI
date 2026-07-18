import type { Metadata } from "next";
import { CTASection } from "@/components/marketing/cta-section";
import { Shield, Server, CreditCard, Globe, Cpu, HeartPulse } from "lucide-react";

export const metadata: Metadata = { title: "Use Cases" };

const useCases = [
  { icon: Server, title: "Infrastructure Outages", desc: "Automatically detect cascading failures across microservices and identify the root service.", industry: "DevOps / SRE" },
  { icon: CreditCard, title: "Payment Failures", desc: "Correlate checkout errors with recent deployments, third-party API degradation, and database issues.", industry: "FinTech" },
  { icon: Globe, title: "CDN & Edge Incidents", desc: "Analyze latency spikes across regions and pinpoint misconfigured edge rules or origin failures.", industry: "Media / Streaming" },
  { icon: Cpu, title: "ML Pipeline Failures", desc: "Track model serving errors, data pipeline breaks, and GPU utilization anomalies end-to-end.", industry: "AI / ML" },
  { icon: HeartPulse, title: "Healthcare Systems", desc: "HIPAA-compliant incident investigation for EHR, telehealth, and medical device platforms.", industry: "Healthcare" },
  { icon: Shield, title: "Security Incidents", desc: "Correlate IDS alerts, access logs, and deployment changes to identify breach vectors.", industry: "Security" },
];

export default function UseCasesPage() {
  return (
    <>
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Use Cases</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Built for every <span className="text-gradient">engineering team</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground">
            From startups to Fortune 500, Sentinel AI adapts to your stack and workflows.
          </p>
        </div>
        <div className="mx-auto max-w-5xl px-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {useCases.map((uc) => (
            <div key={uc.title} className="rounded-2xl border border-border/50 bg-card/40 p-6 space-y-4 hover:border-primary/20 transition">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 border border-primary/10">
                <uc.icon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-primary">{uc.industry}</p>
                <h3 className="text-lg font-bold mt-1">{uc.title}</h3>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{uc.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <CTASection />
    </>
  );
}
