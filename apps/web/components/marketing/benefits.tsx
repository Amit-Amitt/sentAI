"use client";

import { motion } from "framer-motion";
import { Clock, Bot, Layers, ShieldCheck } from "lucide-react";

const benefits = [
  { icon: Clock, title: "Reduce MTTR by 73%", desc: "Automated root cause analysis cuts mean time to resolution from hours to minutes.", stat: "4.2 min", statLabel: "avg resolution" },
  { icon: Bot, title: "Autonomous AI", desc: "7 specialized agents work in parallel — no human intervention required for analysis.", stat: "24/7", statLabel: "always on" },
  { icon: Layers, title: "Multi-Agent Analysis", desc: "Logs, metrics, deployments, and customer feedback analyzed simultaneously.", stat: "7", statLabel: "parallel agents" },
  { icon: ShieldCheck, title: "Enterprise Ready", desc: "SOC2 compliant, SSO, private cloud deployment, and custom SLAs available.", stat: "99.99%", statLabel: "uptime SLA" },
];

export function Benefits() {
  return (
    <section className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Why Sentinel AI</p>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Built for teams that ship fast
          </h2>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          {benefits.map((b, i) => (
            <motion.div
              key={b.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="group relative rounded-2xl border border-border/50 bg-card/40 p-8 hover:border-primary/20 transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 border border-primary/10">
                    <b.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="text-lg font-bold">{b.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">{b.desc}</p>
                </div>
                <div className="text-right shrink-0 ml-4">
                  <p className="text-3xl font-bold text-gradient">{b.stat}</p>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mt-1">{b.statLabel}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
