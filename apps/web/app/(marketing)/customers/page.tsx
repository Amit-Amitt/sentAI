import type { Metadata } from "next";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = { title: "Customers" };

const customers = [
  { name: "DataFlow", industry: "Data Infrastructure", quote: "73% MTTR reduction in the first month.", logo: "DF" },
  { name: "ScaleGrid", industry: "Cloud Hosting", quote: "Eliminated 3am on-call wake-ups entirely.", logo: "SG" },
  { name: "CloudNative", industry: "Platform Engineering", quote: "Deployment correlation saved us 200+ hours.", logo: "CN" },
  { name: "FinServe", industry: "Financial Services", quote: "SOC2-compliant AI that actually understands our stack.", logo: "FS" },
  { name: "MediaStream", industry: "Video Streaming", quote: "Latency incidents detected before users noticed.", logo: "MS" },
  { name: "HealthBridge", industry: "Healthcare", quote: "HIPAA-compliant incident investigation at scale.", logo: "HB" },
];

export default function CustomersPage() {
  return (
    <>
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Customers</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Trusted by teams <span className="text-gradient">who ship fast</span>
          </h1>
        </div>
        <div className="mx-auto max-w-5xl px-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {customers.map((c) => (
            <div key={c.name} className="rounded-2xl border border-border/50 bg-card/40 p-6 space-y-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 text-sm font-bold text-primary">{c.logo}</div>
              <div>
                <h3 className="text-lg font-bold">{c.name}</h3>
                <p className="text-xs text-muted-foreground">{c.industry}</p>
              </div>
              <p className="text-sm text-muted-foreground italic">&ldquo;{c.quote}&rdquo;</p>
            </div>
          ))}
        </div>
      </section>
      <CTASection />
    </>
  );
}
