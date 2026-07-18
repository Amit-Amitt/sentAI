"use client";

import { motion } from "framer-motion";
import { Sparkles, GitPullRequest, Code, TrendingUp } from "lucide-react";

export function RootCauseStory() {
  return (
    <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-2xl p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
        <Sparkles className="w-48 h-48 text-indigo-400" />
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2 text-indigo-400">
            <Sparkles className="w-5 h-5" />
            <h3 className="font-bold text-lg">AI Root Cause Analysis</h3>
          </div>
          <div className="flex items-center gap-2 bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-xs font-bold border border-green-500/30">
            95% Confidence
          </div>
        </div>

        <div className="space-y-4 text-gray-300 leading-relaxed text-lg mb-8">
          <p>
            A deployment was completed <strong className="text-white">6 minutes before</strong> latency increased.
          </p>
          <p>
            The deployment modified <code className="text-indigo-300 bg-indigo-500/10 px-1 rounded">database connection pooling</code> configurations in the API Gateway.
          </p>
          <p>
            OpenTelemetry traces show database wait time increased by <strong className="text-red-400">430%</strong> immediately following the restart, while Kubernetes reports no infrastructure or memory pressure issues.
          </p>
        </div>

        <div className="bg-black/40 rounded-xl p-5 border border-white/5">
          <h4 className="font-semibold text-sm text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Code className="w-4 h-4" /> Recommended Remediation
          </h4>
          <p className="text-gray-300 mb-4">
            Revert the connection pool `max_size` setting from 10 to 100 in `settings.py` to restore throughput capacity.
          </p>
          <button className="w-full sm:w-auto bg-green-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-600 transition-colors flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(34,197,94,0.3)]">
            <GitPullRequest className="w-5 h-5" />
            Merge Draft PR #842
          </button>
        </div>
      </div>
    </div>
  );
}
