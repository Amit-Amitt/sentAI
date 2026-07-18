"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Bot, Terminal } from "lucide-react";

import { APP_METADATA } from "@sentinel/config";
import { Badge } from "@sentinel/ui";

import { primaryNavigation, settingsNavigation } from "@/lib/constants/navigation";
import { useStore } from "@/lib/store/use-store";

export function Sidebar() {
  const pathname = usePathname();
  const { isSimulating, activeSimulationAgent } = useStore();

  return (
    <aside className="hidden w-80 shrink-0 border-r border-border/60 bg-zinc-950/85 px-6 py-8 backdrop-blur-xl xl:flex xl:flex-col xl:justify-between h-screen sticky top-0">
      <div className="space-y-8">
        {/* Brand Header */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge variant="warning" className="border-amber-500/30 bg-amber-500/10 text-amber-400">
              Agentic SRE
            </Badge>
            {isSimulating && (
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping" />
            )}
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              {APP_METADATA.name}
            </h1>
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              {APP_METADATA.tagline}
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-6">
          <div className="space-y-2">
            <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60 px-3">
              Operations Center
            </p>
            <ul className="space-y-1">
              {primaryNavigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`relative flex items-center gap-3 rounded-xl px-3.5 py-3 transition group ${
                        isActive
                          ? "bg-primary/10 border border-primary/20 text-foreground"
                          : "border border-transparent text-muted-foreground hover:bg-muted/40 hover:text-foreground"
                      }`}
                    >
                      <Icon className={`h-4.5 w-4.5 transition ${isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"}`} />
                      <div className="flex-1">
                        <p className="text-xs font-semibold">{item.label}</p>
                        <p className="text-[10px] text-muted-foreground/80 mt-0.5 line-clamp-1 group-hover:text-muted-foreground transition">
                          {item.description}
                        </p>
                      </div>
                      
                      {isActive && (
                        <motion.div
                          layoutId="activeIndicator"
                          className="absolute left-0 w-[3px] h-[60%] rounded-r bg-primary"
                          transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="space-y-2">
            <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60 px-3">
              Configuration
            </p>
            <ul className="space-y-1">
              {settingsNavigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-xs font-medium transition ${
                        isActive
                          ? "bg-primary/10 border border-primary/20 text-foreground"
                          : "border border-transparent text-muted-foreground hover:bg-muted/40 hover:text-foreground"
                      }`}
                    >
                      <Icon className="h-4.5 w-4.5" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </nav>
      </div>

      {/* Simulator / Telemetry Running State */}
      <div className="rounded-2xl border border-border/50 bg-muted/20 p-4 space-y-3">
        <div className="flex justify-between items-center text-xs">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <Terminal className="h-4 w-4" /> LangGraph Status
          </span>
          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold ${
            isSimulating ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-zinc-800 text-zinc-400"
          }`}>
            {isSimulating ? "DIAGNOSING" : "STANDBY"}
          </span>
        </div>
        {isSimulating && (
          <div className="space-y-2">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Active Agent:</span>
              <span className="font-semibold text-foreground animate-pulse">{activeSimulationAgent}</span>
            </div>
            <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-emerald-500"
                initial={{ width: "10%" }}
                animate={{ width: "90%" }}
                transition={{ duration: 10, ease: "easeInOut" }}
              />
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
export default Sidebar;
