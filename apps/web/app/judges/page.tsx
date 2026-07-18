"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ChevronLeft, CheckCircle2, Award, Zap, Code, Shield } from "lucide-react";

export default function JudgesPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500/30 pb-24">
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center">
          <Link href="/" className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
            <ChevronLeft className="w-5 h-5" />
            Back to Home
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-6 pt-16 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-8 h-8 text-indigo-400" />
            <h1 className="text-4xl font-extrabold tracking-tight">Hackathon Judges Portal</h1>
          </div>
          <p className="text-xl text-gray-400 mb-12">
            Welcome to the Sentinel AI project overview. This document provides a high-level summary of the architecture, innovation, and completeness of our solution.
          </p>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <Section title="Problem Statement" icon={<Zap className="w-6 h-6 text-yellow-400" />}>
              Modern Site Reliability Engineering (SRE) teams are drowning in alerts. When a microservice crashes, it generates thousands of cascading failures across logs, metrics, and traces. Engineers waste hours correlating this data with recent GitHub deployments to find the root cause, leading to extended downtime and lost revenue.
            </Section>

            <Section title="The Solution" icon={<CheckCircle2 className="w-6 h-6 text-green-400" />}>
              Sentinel AI acts as an Autonomous AI Incident Commander. It ingests OTLP telemetry at scale, uses deterministic rules to detect anomalies, and immediately dispatches LangGraph AI Agents. These agents analyze the raw data, correlate it with GitHub deployment intelligence, and automatically generate a Draft Pull Request containing the fix.
            </Section>
          </div>

          <h2 className="text-2xl font-bold mb-6 mt-16 border-b border-white/10 pb-4">Innovation Highlights</h2>
          <div className="space-y-4 mb-16">
            <Highlight 
              title="Agentic Auto-Remediation"
              description="Instead of just generating a slack alert, the AI actually writes code to fix the problem (e.g. reverting a bad database connection pool config) and opens a GitHub PR automatically."
            />
            <Highlight 
              title="Enterprise-Grade Multi-Tenant SaaS"
              description="Built for production from day 1. Features strict JWT RBAC, Organization isolation, MFA support, Stripe Subscription Billing, and immutable Audit Logging."
            />
            <Highlight 
              title="OpenTelemetry Native"
              description="No proprietary agents required. Drop Sentinel AI into any existing Kubernetes cluster emitting standard Prometheus, Loki, or Tempo traces."
            />
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <Section title="Technology Stack" icon={<Code className="w-6 h-6 text-blue-400" />}>
              <ul className="list-disc list-inside text-gray-400 space-y-2">
                <li><strong>Frontend:</strong> Next.js 15, React 19, Tailwind CSS, Framer Motion</li>
                <li><strong>Backend:</strong> FastAPI, Python 3.13, SQLAlchemy, Asyncio</li>
                <li><strong>AI Engine:</strong> LangGraph, LangChain, OpenAI / Gemini APIs</li>
                <li><strong>Data Layer:</strong> PostgreSQL, Redis (RQ), Qdrant (Vector DB)</li>
                <li><strong>Infrastructure:</strong> Docker, Kubernetes (Helm), GitHub Actions</li>
              </ul>
            </Section>

            <Section title="Scalability & Security" icon={<Shield className="w-6 h-6 text-purple-400" />}>
              <p className="text-gray-400 leading-relaxed mb-4">
                The architecture decouples heavy telemetry ingestion from the core API using Redis queues and background workers.
              </p>
              <p className="text-gray-400 leading-relaxed">
                Security features include bcrypt password hashing, JWT active session revocation, Feature Gating via Stripe, and Kubernetes Graceful Shutdown handling.
              </p>
            </Section>
          </div>

          <div className="flex flex-col items-center justify-center p-12 bg-white/5 border border-white/10 rounded-2xl mb-16">
            <h3 className="text-2xl font-bold mb-6">Ready to see it in action?</h3>
            <div className="flex gap-4">
              <Link 
                href="/demo" 
                className="bg-indigo-500 text-white px-8 py-3 rounded-full font-semibold hover:bg-indigo-600 transition-colors shadow-[0_0_20px_rgba(99,102,241,0.3)]"
              >
                Launch Demo Mode
              </Link>
              <Link 
                href="/architecture" 
                className="bg-white/10 text-white px-8 py-3 rounded-full font-semibold hover:bg-white/20 transition-colors"
              >
                View Architecture
              </Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

function Section({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        {icon}
        <h2 className="text-xl font-bold">{title}</h2>
      </div>
      <div className="text-gray-400 leading-relaxed">
        {children}
      </div>
    </div>
  );
}

function Highlight({ title, description }: { title: string, description: string }) {
  return (
    <div className="flex gap-4 items-start p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
      <CheckCircle2 className="w-6 h-6 text-indigo-400 shrink-0 mt-1" />
      <div>
        <h4 className="font-bold text-lg mb-1">{title}</h4>
        <p className="text-gray-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
