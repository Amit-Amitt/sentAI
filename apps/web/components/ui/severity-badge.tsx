"use client";

import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: "SEV1" | "SEV2" | "SEV3";
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const styles = {
    SEV1: "border-red-500/30 bg-red-500/10 text-red-400 shadow-[0_0_12px_rgba(239,68,68,0.15)]",
    SEV2: "border-amber-500/30 bg-amber-500/10 text-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.15)]",
    SEV3: "border-sky-500/30 bg-sky-500/10 text-sky-400 shadow-[0_0_12px_rgba(14,165,233,0.15)]",
  };

  const labels = {
    SEV1: "CRITICAL",
    SEV2: "WARNING",
    SEV3: "LOW",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider",
        styles[severity],
        className
      )}
    >
      <span className={cn(
        "mr-1.5 h-1.5 w-1.5 rounded-full",
        severity === "SEV1" ? "bg-red-400 animate-pulse" :
        severity === "SEV2" ? "bg-amber-400" : "bg-sky-400"
      )} />
      {severity} ({labels[severity]})
    </span>
  );
}
