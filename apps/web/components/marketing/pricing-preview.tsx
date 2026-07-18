"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Check, ArrowRight, Sparkles } from "lucide-react";

const plans = [
  { name: "Free", price: { monthly: 0, yearly: 0 }, desc: "Get started with basic AI", cta: "Start Free", popular: false, features: ["1 User", "10 Incidents / month", "Basic AI Analysis", "Community Support", "7-day data retention"] },
  { name: "Starter", price: { monthly: 29, yearly: 24 }, desc: "For growing engineering teams", cta: "Start Trial", popular: false, features: ["5 Users", "Unlimited Incidents", "Advanced AI Agents", "Priority Support", "30-day data retention", "Slack Integration"] },
  { name: "Pro", price: { monthly: 99, yearly: 79 }, desc: "Full power for scaling teams", cta: "Start Trial", popular: true, features: ["Unlimited Users", "Unlimited AI Analysis", "Advanced Analytics", "SSO & RBAC", "API Access", "90-day data retention", "Custom Integrations"] },
  { name: "Enterprise", price: { monthly: -1, yearly: -1 }, desc: "For organizations with custom needs", cta: "Contact Sales", popular: false, features: ["Everything in Pro", "Dedicated Support", "Private Cloud Deploy", "Custom SLA (99.99%)", "Custom Integrations", "Compliance (SOC2, HIPAA)", "Unlimited Retention"] },
];

export function PricingPreview() {
  const [annual, setAnnual] = useState(true);

  return (
    <section className="relative py-24 sm:py-32" id="pricing">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Pricing</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-muted-foreground">Start free. Scale as you grow. No hidden fees.</p>

          {/* Toggle */}
          <div className="mt-8 inline-flex items-center gap-3 rounded-full border border-border/50 bg-muted/20 p-1">
            <button onClick={() => setAnnual(false)} className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${!annual ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:text-foreground"}`}>Monthly</button>
            <button onClick={() => setAnnual(true)} className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${annual ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground hover:text-foreground"}`}>
              Yearly <span className="ml-1 text-xs opacity-80">Save 20%</span>
            </button>
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className={`relative rounded-2xl border p-6 space-y-6 ${
                plan.popular ? "border-primary/40 bg-primary/5 shadow-glow-sm" : "border-border/50 bg-card/40"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 inline-flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-[10px] font-bold text-primary-foreground uppercase tracking-wider">
                  <Sparkles className="h-3 w-3" /> Most Popular
                </div>
              )}
              <div>
                <h3 className="text-lg font-bold">{plan.name}</h3>
                <p className="text-xs text-muted-foreground mt-1">{plan.desc}</p>
              </div>
              <div>
                {plan.price.monthly === -1 ? (
                  <p className="text-3xl font-bold">Custom</p>
                ) : (
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold">${annual ? plan.price.yearly : plan.price.monthly}</span>
                    {plan.price.monthly > 0 && <span className="text-sm text-muted-foreground">/mo</span>}
                  </div>
                )}
              </div>
              <Link
                href={plan.price.monthly === -1 ? "/contact" : "/register"}
                className={`flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
                  plan.popular
                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40"
                    : "border border-border/60 text-foreground hover:bg-white/[0.04]"
                }`}
              >
                {plan.cta}
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
              <ul className="space-y-2.5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-xs text-muted-foreground">
                    <Check className="h-3.5 w-3.5 text-emerald-400 mt-0.5 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
