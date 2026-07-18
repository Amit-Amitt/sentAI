"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

import { CommandPalette } from "@/components/ui/command-palette";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-zinc-950 text-foreground font-sans antialiased selection:bg-primary/30 selection:text-foreground">
      {/* Desktop Sidebar (Left) */}
      <Sidebar />

      {/* Mobile Drawer Backdrop and Navigation Panel */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-40 xl:hidden">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            />
            {/* Panel */}
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="absolute bottom-0 left-0 top-0 flex w-80 flex-col bg-zinc-950 border-r border-border p-6 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-8">
                <span className="text-sm font-semibold tracking-wider text-muted-foreground">MENU</span>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="rounded-xl border border-border p-2 text-muted-foreground transition hover:bg-muted/80"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <Sidebar />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Main content grid (Right) */}
      <div className="flex flex-1 flex-col overflow-x-hidden min-h-screen">
        <TopBar onMenuToggle={() => setMobileMenuOpen(true)} />
        <main className="flex-1 p-6 md:p-8 space-y-8 bg-zinc-950/20 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* Keyboard-accessible Command Shell overlay */}
      <CommandPalette />
    </div>
  );
}
export default AppShell;
