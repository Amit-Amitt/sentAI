"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { Command, CornerDownLeft, ShieldAlert, Sliders, Terminal, X } from "lucide-react";

import { useStore } from "@/lib/store/use-store";

export function CommandPalette() {
  const router = useRouter();
  const { commandPaletteOpen, setCommandPaletteOpen, triggerSimulation, clearNotifications } = useStore();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Toggle command palette on Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if (e.key === "Escape") {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  // Focus input when opened
  useEffect(() => {
    if (commandPaletteOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
      setQuery("");
    }
  }, [commandPaletteOpen]);

  const items = [
    {
      category: "Navigation",
      commands: [
        { label: "Go to Dashboard", action: () => router.push("/dashboard"), shortcut: "G D" },
        { label: "Go to Incidents List", action: () => router.push("/incidents"), shortcut: "G I" },
        { label: "Go to Agent Activity", action: () => router.push("/agent-activity"), shortcut: "G A" },
        { label: "Go to Reports Archive", action: () => router.push("/reports"), shortcut: "G R" },
        { label: "Go to Settings", action: () => router.push("/settings"), shortcut: "G S" },
      ]
    },
    {
      category: "Simulation / Commands",
      commands: [
        {
          label: "Trigger SEV1 Database Pool Saturation Simulation",
          action: () => triggerSimulation("Database connection pool exhausted on checkout flow", "SEV1"),
          shortcut: "T S 1"
        },
        {
          label: "Trigger SEV2 Cache Memory Saturation Simulation",
          action: () => triggerSimulation("Redis cache maxmemory eviction crashes", "SEV2"),
          shortcut: "T S 2"
        },
        {
          label: "Clear All Activity Notifications",
          action: () => clearNotifications(),
          shortcut: "C N"
        }
      ]
    }
  ];

  const filteredItems = items.map(cat => ({
    ...cat,
    commands: cat.commands.filter(cmd => cmd.label.toLowerCase().includes(query.toLowerCase()))
  })).filter(cat => cat.commands.length > 0);

  const flatCommands = filteredItems.flatMap(cat => cat.commands);

  // Reset active index when query changes
  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  // Handle arrow navigation and enter selection
  useEffect(() => {
    if (!commandPaletteOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIndex((prev) => (flatCommands.length > 0 ? (prev + 1) % flatCommands.length : 0));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIndex((prev) => (flatCommands.length > 0 ? (prev - 1 + flatCommands.length) % flatCommands.length : 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (flatCommands[activeIndex]) {
          flatCommands[activeIndex].action();
          setCommandPaletteOpen(false);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen, activeIndex, flatCommands, setCommandPaletteOpen]);

  return (
    <AnimatePresence>
      {commandPaletteOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setCommandPaletteOpen(false)}
            className="absolute inset-0 bg-background/60 backdrop-blur-md"
          />

          {/* Dialog Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -10 }}
            transition={{ duration: 0.15 }}
            className="relative z-10 w-full max-w-2xl overflow-hidden rounded-2xl border border-border/80 bg-card/90 shadow-2xl backdrop-blur-xl"
          >
            <div className="flex items-center border-b border-border/70 px-4 py-4">
              <Command className="mr-3 h-5 w-5 text-muted-foreground" />
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search command palette... (e.g. Trigger SEV1, Go to Settings)"
                className="flex-1 bg-transparent text-foreground placeholder-muted-foreground outline-none text-sm"
              />
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="rounded-lg p-1 text-muted-foreground transition hover:bg-muted/80 hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="max-h-[350px] overflow-y-auto px-2 py-3">
              {filteredItems.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No matching commands found.
                </div>
              ) : (
                (() => {
                  let globalCmdIdx = 0;
                  return filteredItems.map((cat, catIdx) => (
                    <div key={cat.category} className={catIdx > 0 ? "mt-4" : ""}>
                      <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/80">
                        {cat.category}
                      </p>
                      <ul className="mt-1 space-y-0.5">
                        {cat.commands.map((cmd) => {
                          const currentIdx = globalCmdIdx++;
                          const isActive = currentIdx === activeIndex;
                          return (
                            <li key={cmd.label}>
                              <button
                                onClick={() => {
                                  cmd.action();
                                  setCommandPaletteOpen(false);
                                }}
                                className={`flex w-full items-center justify-between rounded-xl px-3 py-3 text-left text-sm transition group ${
                                  isActive
                                    ? "bg-muted text-foreground"
                                    : "text-muted-foreground hover:bg-muted/70"
                                }`}
                              >
                                <span className={`font-medium transition ${isActive ? "text-foreground" : "text-muted-foreground group-hover:text-foreground"}`}>
                                  {cmd.label}
                                </span>
                                <div className="flex items-center gap-1.5">
                                  {cmd.shortcut && (
                                    <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border border-border bg-background px-1.5 font-mono text-[9px] font-medium text-muted-foreground">
                                      {cmd.shortcut}
                                    </kbd>
                                  )}
                                  <CornerDownLeft className={`h-3.5 w-3.5 transition ${isActive ? "text-muted-foreground/80 opacity-100" : "text-muted-foreground/0 group-hover:text-muted-foreground/80"}`} />
                                </div>
                              </button>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  ));
                })()
              )}
            </div>
            
            <div className="flex items-center justify-between border-t border-border/70 bg-muted/20 px-4 py-3 text-[10px] text-muted-foreground font-medium">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-muted px-1 font-mono text-[9px]">↑↓</kbd> Navigation
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-muted px-1 font-mono text-[9px]">Enter</kbd> Select
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="rounded bg-muted px-1 font-mono text-[9px]">Esc</kbd> Close
                </span>
              </div>
              <div>Sentinel AI Command Shell</div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
