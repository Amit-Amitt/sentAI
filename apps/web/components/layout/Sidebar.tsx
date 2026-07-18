"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Terminal, LogOut, User } from "lucide-react";

import { primaryNavigation, settingsNavigation } from "@/lib/constants/navigation";
import { useStore } from "@/lib/store/use-store";
import { WorkspaceSwitcher } from "./WorkspaceSwitcher";
import { useAuth } from "@/lib/providers/auth-provider";

export function Sidebar() {
  const pathname = usePathname();
  const { isSimulating, activeSimulationAgent } = useStore();
  const { user, logout } = useAuth();

  return (
    <aside className="hidden w-80 shrink-0 border-r border-border/60 bg-zinc-950/85 px-6 py-8 backdrop-blur-xl xl:flex xl:flex-col xl:justify-between h-screen sticky top-0">
      <div className="space-y-6">
        {/* Workspace Switcher */}
        <WorkspaceSwitcher />

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

      {/* Simulator & Session controls */}
      <div className="space-y-3.5">
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

        {/* Commander User Session Profile */}
        {user && (
          <div className="flex items-center justify-between gap-3 p-3 rounded-2xl border border-border/50 bg-background/40">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="h-8.5 w-8.5 rounded-xl border border-border/80 bg-muted/30 shrink-0 overflow-hidden">
                {user.avatarUrl ? (
                  <img src={user.avatarUrl} alt="Avatar" className="h-full w-full object-cover" />
                ) : (
                  <div className="h-full w-full flex items-center justify-center text-muted-foreground">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
              <div className="overflow-hidden">
                <p className="text-[11px] font-bold text-foreground truncate">
                  {user.firstName} {user.lastName}
                </p>
                <p className="text-[9px] text-muted-foreground truncate">
                  {user.companyName}
                </p>
              </div>
            </div>
            
            <button
              onClick={logout}
              className="rounded-lg p-1.5 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/5 transition"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
export default Sidebar;
