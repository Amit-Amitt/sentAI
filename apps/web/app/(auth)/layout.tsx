import Link from "next/link";
import { Shield } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Left Panel — Branding Illustration */}
      <div className="relative hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-primary/10 via-background to-accent/5 border-r border-border/50 p-12">
        {/* Background grid */}
        <div className="absolute inset-0 bg-grid opacity-50" />
        {/* Gradient orbs */}
        <div className="absolute top-20 left-20 h-72 w-72 rounded-full bg-primary/10 blur-[100px]" />
        <div className="absolute bottom-20 right-20 h-72 w-72 rounded-full bg-accent/10 blur-[100px]" />

        {/* Logo */}
        <Link href="/" className="relative flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
            <Shield className="h-4 w-4 text-primary" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            Sentinel<span className="text-primary">AI</span>
          </span>
        </Link>

        {/* Center Content */}
        <div className="relative space-y-6 max-w-md">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">
              Autonomous incident resolution, <span className="text-gradient">powered by AI</span>
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              7 specialized AI agents work together to detect, analyze, and recommend fixes — before your users even notice.
            </p>
          </div>

          {/* Floating Stat Cards */}
          <div className="flex gap-4">
            {[
              { label: "MTTR Reduction", value: "73%", color: "text-emerald-400" },
              { label: "Incidents Resolved", value: "12.4k", color: "text-primary" },
              { label: "Uptime", value: "99.99%", color: "text-amber-400" },
            ].map((stat) => (
              <div key={stat.label} className="glass rounded-xl p-4 space-y-1 flex-1">
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Quote */}
        <div className="relative">
          <blockquote className="text-sm text-muted-foreground italic leading-relaxed">
            &ldquo;Sentinel AI cut our incident resolution time by 73%. It&rsquo;s like having a senior SRE team that never sleeps.&rdquo;
          </blockquote>
          <p className="mt-2 text-xs font-semibold text-foreground">Sarah Chen, VP Engineering — DataFlow</p>
        </div>
      </div>

      {/* Right Panel — Auth Form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}
