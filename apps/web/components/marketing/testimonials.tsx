"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Star, Quote } from "lucide-react";

const testimonials = [
  { quote: "Sentinel AI cut our MTTR from 45 minutes to under 5. The multi-agent approach finds root causes our team would miss.", name: "Sarah Chen", role: "VP Engineering", company: "DataFlow", avatar: "SC" },
  { quote: "We went from 3am wake-up calls to automated incident reports waiting in Slack by morning. Game changer.", name: "Marcus Rodriguez", role: "SRE Lead", company: "ScaleGrid", avatar: "MR" },
  { quote: "The deployment correlation engine alone saved us hundreds of hours of post-mortem investigation.", name: "Priya Patel", role: "CTO", company: "CloudNative", avatar: "PP" },
  { quote: "Finally, an AI tool that actually understands infrastructure. Not just pattern matching — real reasoning.", name: "James Park", role: "Director of DevOps", company: "FinServe", avatar: "JP" },
];

export function Testimonials() {
  return (
    <section className="relative py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-radial opacity-30" />
      <div className="relative mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Testimonials</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Loved by engineering teams
          </h2>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="relative rounded-2xl border border-border/50 bg-card/40 p-8 space-y-6"
            >
              <Quote className="h-8 w-8 text-primary/20" />
              <p className="text-sm text-foreground leading-relaxed">&ldquo;{t.quote}&rdquo;</p>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-xs font-bold text-primary">
                  {t.avatar}
                </div>
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role} · {t.company}</p>
                </div>
                <div className="ml-auto flex gap-0.5">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="h-3 w-3 fill-amber-400 text-amber-400" />
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
