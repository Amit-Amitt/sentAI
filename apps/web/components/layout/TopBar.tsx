"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { Bell, Command, Menu, Search, User } from "lucide-react";

import { useStore } from "@/lib/store/use-store";

interface TopBarProps {
  onMenuToggle: () => void;
}

export function TopBar({ onMenuToggle }: TopBarProps) {
  const pathname = usePathname();
  const { setCommandPaletteOpen, notifications, markNotificationAsRead } = useStore();
  const [showNotifications, setShowNotifications] = useState(false);

  const unreadCount = notifications.filter(n => !n.read).length;

  // Build breadcrumbs from path
  const pathParts = pathname.split("/").filter(Boolean);
  const breadcrumbs = pathParts.map((part, index) => {
    const href = "/" + pathParts.slice(0, index + 1).join("/");
    const label = part.charAt(0).toUpperCase() + part.slice(1).replace("-", " ");
    return { href, label };
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border/60 bg-zinc-950/80 px-6 backdrop-blur-md">
      {/* Left section: Hamburger (mobile) + Breadcrumbs */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="rounded-xl border border-border/80 p-2 text-muted-foreground transition hover:bg-muted/80 hover:text-foreground xl:hidden"
        >
          <Menu className="h-4 w-4" />
        </button>

        <nav className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
          <span className="hover:text-foreground transition cursor-pointer">Sentinel</span>
          {breadcrumbs.map((crumb, idx) => (
            <div key={crumb.href} className="flex items-center gap-1.5">
              <span>/</span>
              <span className={`transition ${idx === breadcrumbs.length - 1 ? "text-foreground font-semibold" : "hover:text-foreground cursor-pointer"}`}>
                {crumb.label}
              </span>
            </div>
          ))}
        </nav>
      </div>

      {/* Right section: Search trigger + Notifications + Profile */}
      <div className="flex items-center gap-4">
        {/* Command Search Button */}
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="flex items-center gap-3 rounded-xl border border-border/70 bg-background/50 px-3 py-1.5 text-xs text-muted-foreground transition hover:bg-muted/40 hover:text-foreground"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="hidden md:inline">Quick command...</span>
          <kbd className="inline-flex h-5 select-none items-center gap-0.5 rounded border border-border bg-background px-1.5 font-mono text-[9px] font-medium text-muted-foreground/80">
            ⌘K
          </kbd>
        </button>

        {/* Notification bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="rounded-xl border border-border/80 p-2 text-muted-foreground transition hover:bg-muted/80 hover:text-foreground relative"
          >
            <Bell className="h-4.5 w-4.5" />
            {unreadCount > 0 && (
              <span className="absolute right-1 top-1 flex h-2 w-2 rounded-full bg-rose-500" />
            )}
          </button>

          {/* Notifications Dropdown */}
          <AnimatePresence>
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 mt-2 z-20 w-80 rounded-2xl border border-border/80 bg-card/95 p-4 shadow-xl backdrop-blur-xl"
                >
                  <div className="flex justify-between items-center border-b border-border/50 pb-2 mb-2">
                    <span className="text-xs font-semibold">Activity Notifications</span>
                    {unreadCount > 0 && (
                      <span className="rounded bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-medium text-rose-400">
                        {unreadCount} unread
                      </span>
                    )}
                  </div>
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {notifications.length === 0 ? (
                      <p className="text-center text-xs text-muted-foreground py-6">No recent notification history.</p>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          onClick={() => {
                            markNotificationAsRead(n.id);
                          }}
                          className={`rounded-xl p-3 border border-border/50 transition cursor-pointer text-left ${
                            n.read ? "bg-background/20 opacity-70" : "bg-muted/30 border-primary/20"
                          }`}
                        >
                          <div className="flex justify-between items-start">
                            <span className={`text-xs font-semibold ${
                              n.type === "error" ? "text-red-400" :
                              n.type === "success" ? "text-emerald-400" :
                              n.type === "warning" ? "text-amber-400" : "text-sky-400"
                            }`}>
                              {n.title}
                            </span>
                            <span className="text-[9px] text-muted-foreground">
                              {new Date(n.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </span>
                          </div>
                          <p className="text-[11px] text-muted-foreground mt-1 line-clamp-2">{n.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* Profile Avatar */}
        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-border/80 bg-muted/40 text-muted-foreground">
          <User className="h-4.5 w-4.5" />
        </div>
      </div>
    </header>
  );
}
export default TopBar;
