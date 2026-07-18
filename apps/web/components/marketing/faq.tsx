"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

const faqs = [
  { q: "How does the 14-day free trial work?", a: "Sign up with your work email — no credit card required. You get full access to the Pro plan for 14 days. After the trial, you can choose to downgrade to Free or pick a paid plan." },
  { q: "What data does Sentinel AI analyze?", a: "Sentinel AI processes logs, infrastructure metrics, deployment history, and customer feedback. All data is encrypted in transit and at rest. We never store raw credentials or PII." },
  { q: "Can I self-host Sentinel AI?", a: "Yes. Our Enterprise plan includes private cloud deployment options. We support AWS, GCP, Azure, and on-premise Kubernetes clusters." },
  { q: "How is this different from PagerDuty or Datadog?", a: "PagerDuty alerts you. Datadog shows dashboards. Sentinel AI goes further: it autonomously investigates incidents, determines root causes, and recommends fixes — like having a senior SRE team on autopilot." },
  { q: "What LLMs does Sentinel AI use?", a: "We use a combination of frontier models (GPT-4, Claude) orchestrated through LangGraph. Our multi-agent architecture ensures each agent uses the optimal model for its task." },
  { q: "Is Sentinel AI SOC2 compliant?", a: "Yes. We maintain SOC2 Type II compliance. Enterprise customers also get HIPAA BAA and custom compliance documentation." },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-3xl px-6">
        <div className="text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">FAQ</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Frequently asked questions
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={faq.q}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="rounded-2xl border border-border/50 bg-card/40 overflow-hidden"
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="flex w-full items-center justify-between p-5 text-left"
              >
                <span className="text-sm font-semibold text-foreground pr-4">{faq.q}</span>
                <ChevronDown className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform ${openIndex === i ? "rotate-180" : ""}`} />
              </button>
              <AnimatePresence>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="px-5 pb-5">
                      <p className="text-sm text-muted-foreground leading-relaxed">{faq.a}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
