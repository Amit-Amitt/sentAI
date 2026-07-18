"use client";

import Link from "next/link";
import { AlertCircle, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-center bg-zinc-950 px-6 text-foreground">
      {/* Glow Backdrop */}
      <div className="absolute h-96 w-96 rounded-full bg-red-500/10 blur-[120px]" />

      {/* 404 Card */}
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-border bg-card/60 p-8 text-center shadow-2xl backdrop-blur-xl space-y-6">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
          <AlertCircle className="h-6 w-6" />
        </div>
        
        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight">404 - Outpost Unreachable</h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            The telemetry address or settings route you are attempting to query does not exist in the Sentinel registry.
          </p>
        </div>

        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground transition hover:bg-primary/90"
        >
          <ArrowLeft className="h-4 w-4" /> Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
