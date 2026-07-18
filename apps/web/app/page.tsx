"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bot, Shield, Zap, GitPullRequest, Activity } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-black text-white selection:bg-indigo-500/30">
      {/* Navbar */}
      <header className="fixed top-0 w-full z-50 bg-black/50 backdrop-blur-md border-b border-white/10">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-indigo-500" />
            <span className="font-bold text-xl tracking-tight">Sentinel AI</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-300">
            <Link href="#architecture" className="hover:text-white transition-colors">Architecture</Link>
            <Link href="#features" className="hover:text-white transition-colors">Features</Link>
            <Link href="/judges" className="hover:text-white transition-colors flex items-center gap-1">
              Hackathon Panel
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium hover:text-gray-300 transition-colors">
              Log in
            </Link>
            <Link 
              href="/demo" 
              className="bg-white text-black px-4 py-2 rounded-full text-sm font-semibold hover:bg-gray-200 transition-colors flex items-center gap-2"
            >
              Start Demo <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-grow pt-32 pb-16">
        <section className="container mx-auto px-6 pt-20 pb-32 text-center relative">
          {/* Decorative background glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none" />
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="relative z-10 max-w-4xl mx-auto"
          >
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
              The Autonomous <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                AI Incident Commander
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
              Sentinel AI doesn't just alert you when things break. It investigates the root cause, correlates logs with GitHub deployments, and opens a Draft PR to fix the issue before you even wake up.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link 
                href="/demo" 
                className="w-full sm:w-auto bg-indigo-500 text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-indigo-600 transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(99,102,241,0.4)]"
              >
                Experience the Demo
              </Link>
              <Link 
                href="/architecture" 
                className="w-full sm:w-auto bg-white/5 border border-white/10 text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-white/10 transition-colors"
              >
                View Architecture
              </Link>
            </div>
          </motion.div>
        </section>

        {/* Feature Grid */}
        <section id="features" className="container mx-auto px-6 py-24 border-t border-white/5">
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Activity className="w-8 h-8 text-blue-400" />}
              title="OpenTelemetry Native"
              description="Ingest logs, metrics, and traces directly from your existing OpenTelemetry, Prometheus, or Datadog infrastructure with zero friction."
            />
            <FeatureCard 
              icon={<GitPullRequest className="w-8 h-8 text-green-400" />}
              title="Auto-Remediation"
              description="LangGraph AI agents investigate anomalies, identify bad code deploys, and automatically generate Draft PRs with rollback instructions."
            />
            <FeatureCard 
              icon={<Shield className="w-8 h-8 text-purple-400" />}
              title="Enterprise Grade"
              description="Multi-tenant architecture with strict RBAC, automated Stripe billing, MFA support, and immutable security audit logging."
            />
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="border-t border-white/10 py-12 text-center text-gray-500 text-sm">
        <p>Sentinel AI v1.0 — Hackathon Edition Complete</p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors"
    >
      <div className="mb-6 p-4 bg-black/50 rounded-xl inline-block">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-gray-400 leading-relaxed">
        {description}
      </p>
    </motion.div>
  );
}
