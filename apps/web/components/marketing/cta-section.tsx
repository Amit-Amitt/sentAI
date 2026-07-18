"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="relative py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-radial" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[800px] rounded-full bg-primary/8 blur-[150px]" />
      <div className="relative mx-auto max-w-3xl px-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary mb-6">
          <Sparkles className="h-3 w-3" />
          14-day free trial · No credit card
        </div>
        <h2 className="text-3xl font-bold tracking-tight sm:text-5xl">
          Ready to resolve incidents <span className="text-gradient">autonomously</span>?
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Join thousands of engineering teams using Sentinel AI to cut MTTR and ship with confidence.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            href="/register"
            className="group flex items-center gap-2 rounded-xl bg-primary px-8 py-3.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:bg-primary/90 transition-all"
          >
            Start Free Trial
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
          <Link
            href="/contact"
            className="rounded-xl border border-border/60 bg-white/[0.03] px-8 py-3.5 text-sm font-semibold text-foreground hover:bg-white/[0.06] transition-all"
          >
            Talk to Sales
          </Link>
        </div>
      </div>
    </section>
  );
}
