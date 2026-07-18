import type { Metadata } from "next";
import { PricingPreview } from "@/components/marketing/pricing-preview";
import { FAQ } from "@/components/marketing/faq";
import { CTASection } from "@/components/marketing/cta-section";

export const metadata: Metadata = { title: "Pricing" };

export default function PricingPage() {
  return (
    <>
      <PricingPreview />
      <section className="mx-auto max-w-5xl px-6 py-16">
        <h2 className="text-2xl font-bold text-center mb-10">Feature Comparison</h2>
        <div className="overflow-x-auto rounded-2xl border border-border/50">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 bg-muted/10">
                <th className="text-left p-4 font-semibold text-muted-foreground">Feature</th>
                {["Free", "Starter", "Pro", "Enterprise"].map(p => (
                  <th key={p} className="p-4 text-center font-semibold">{p}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/30">
              {[
                ["Users", "1", "5", "Unlimited", "Unlimited"],
                ["Incidents", "10/mo", "Unlimited", "Unlimited", "Unlimited"],
                ["AI Agents", "Basic", "Advanced", "All 7", "All 7 + Custom"],
                ["Data Retention", "7 days", "30 days", "90 days", "Unlimited"],
                ["SSO & RBAC", "—", "—", "✓", "✓"],
                ["API Access", "—", "—", "✓", "✓"],
                ["Private Cloud", "—", "—", "—", "✓"],
                ["Custom SLA", "—", "—", "—", "99.99%"],
                ["Support", "Community", "Email", "Priority", "Dedicated"],
              ].map(([feature, ...vals]) => (
                <tr key={feature} className="hover:bg-muted/5 transition">
                  <td className="p-4 text-muted-foreground font-medium">{feature}</td>
                  {vals.map((v, i) => (
                    <td key={i} className={`p-4 text-center ${v === "✓" ? "text-emerald-400 font-bold" : v === "—" ? "text-muted-foreground/30" : ""}`}>{v}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <FAQ />
      <CTASection />
    </>
  );
}
