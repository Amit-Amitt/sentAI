import type { Metadata } from "next";
import { Shield, Users, Rocket, Globe2, Heart } from "lucide-react";

export const metadata: Metadata = { title: "About" };

const values = [
  { icon: Shield, title: "Reliability First", desc: "We build systems that engineering teams can trust with their most critical workflows." },
  { icon: Users, title: "Customer Obsessed", desc: "Every feature starts with a real customer pain point. No vanity features." },
  { icon: Rocket, title: "Ship Fast", desc: "We practice what we preach — continuous delivery with autonomous quality gates." },
  { icon: Globe2, title: "Open Ecosystem", desc: "We believe in interoperability. APIs, webhooks, and integrations are first-class citizens." },
  { icon: Heart, title: "Builder Culture", desc: "We're engineers building for engineers. Craftsmanship and technical depth matter." },
];

const team = [
  { name: "Alex Rivera", role: "CEO & Co-Founder", bg: "AR" },
  { name: "Priya Sharma", role: "CTO & Co-Founder", bg: "PS" },
  { name: "Marcus Chen", role: "VP Engineering", bg: "MC" },
  { name: "Sarah Kim", role: "Head of Product", bg: "SK" },
];

export default function AboutPage() {
  return (
    <>
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-3xl px-6 text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">About</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            We&apos;re building the future of <span className="text-gradient">incident response</span>
          </h1>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            Sentinel AI was founded by SREs who were tired of 3am pages and 4-hour post-mortems. We believe AI should handle the toil so engineers can focus on building.
          </p>
        </div>

        {/* Stats */}
        <div className="mx-auto max-w-4xl px-6 grid grid-cols-2 sm:grid-cols-4 gap-6 mb-24">
          {[
            { stat: "$12M", label: "Series A Raised" },
            { stat: "32", label: "Team Members" },
            { stat: "500+", label: "Companies" },
            { stat: "2024", label: "Founded" },
          ].map(s => (
            <div key={s.label} className="text-center rounded-2xl border border-border/50 bg-card/40 p-6">
              <p className="text-3xl font-bold text-gradient">{s.stat}</p>
              <p className="text-xs text-muted-foreground font-semibold mt-1 uppercase tracking-wider">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Values */}
        <div className="mx-auto max-w-5xl px-6 mb-24">
          <h2 className="text-2xl font-bold text-center mb-10">Our Values</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {values.map(v => (
              <div key={v.title} className="rounded-2xl border border-border/50 bg-card/40 p-6 space-y-3">
                <v.icon className="h-6 w-6 text-primary" />
                <h3 className="text-sm font-bold">{v.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Team */}
        <div className="mx-auto max-w-3xl px-6">
          <h2 className="text-2xl font-bold text-center mb-10">Leadership</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            {team.map(t => (
              <div key={t.name} className="text-center space-y-3">
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20 text-xl font-bold text-primary">{t.bg}</div>
                <div>
                  <p className="text-sm font-bold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
