import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Clock } from "lucide-react";

export const metadata: Metadata = { title: "Blog" };

const posts = [
  { title: "How We Built a Multi-Agent Incident Response System", desc: "A deep dive into our LangGraph architecture and why we chose parallel agent execution.", date: "Jul 15, 2026", tag: "Engineering", read: "8 min" },
  { title: "Reducing MTTR by 73%: A Case Study with DataFlow", desc: "How DataFlow used Sentinel AI to transform their incident response from reactive to proactive.", date: "Jul 10, 2026", tag: "Case Study", read: "6 min" },
  { title: "The Future of AIOps: Beyond Dashboards and Alerts", desc: "Why the next generation of incident response tools will think, not just display.", date: "Jul 5, 2026", tag: "Thought Leadership", read: "5 min" },
  { title: "Announcing Sentinel AI Public Beta", desc: "Today we're opening Sentinel AI to all engineering teams. Start your 14-day free trial.", date: "Jul 1, 2026", tag: "Product", read: "3 min" },
  { title: "Building Trustworthy AI for Critical Infrastructure", desc: "How we ensure our AI agents make reliable, explainable decisions under pressure.", date: "Jun 25, 2026", tag: "Engineering", read: "10 min" },
  { title: "Series A: $12M to Build the AI Incident Commander", desc: "We're thrilled to announce our Series A funding to accelerate autonomous incident response.", date: "Jun 15, 2026", tag: "Company", read: "4 min" },
];

export default function BlogPage() {
  return (
    <section className="py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <div className="text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Blog</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">Latest Updates</h1>
          <p className="mt-4 text-muted-foreground">Engineering insights, product updates, and industry perspectives.</p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map(post => (
            <article key={post.title} className="group rounded-2xl border border-border/50 bg-card/40 p-6 space-y-4 hover:border-primary/20 transition cursor-pointer">
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold text-primary">{post.tag}</span>
                <span className="text-[10px] text-muted-foreground flex items-center gap-1"><Clock className="h-3 w-3" /> {post.read}</span>
              </div>
              <h3 className="text-sm font-bold group-hover:text-primary transition leading-snug">{post.title}</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">{post.desc}</p>
              <p className="text-[10px] text-muted-foreground/60">{post.date}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
