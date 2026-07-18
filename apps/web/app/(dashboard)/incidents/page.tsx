"use client";

import Link from "next/link";
import { AlertCircle, ArrowRight, Search, ShieldCheck } from "lucide-react";

import { useStore } from "@/lib/store/use-store";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { useIncidents } from "@/lib/api/hooks/useIncidents";
import { ListSkeleton } from "@/components/ui/skeletons";

export default function IncidentsPage() {
  const {
    searchQuery,
    setSearchQuery,
    severityFilter,
    setSeverityFilter,
    statusFilter,
    setStatusFilter
  } = useStore();

  const { data, isLoading } = useIncidents({
    status: statusFilter === "ALL" ? undefined : statusFilter.toLowerCase(),
  });

  const incidents = data?.results || [];

  // Apply search query filters client-side
  const filteredIncidents = incidents.filter((inc) => {
    const matchesSearch = inc.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          inc.incident_id.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesSeverity = severityFilter === "ALL" || inc.severity === severityFilter;

    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Incidents Outpost</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Historical archive and real-time active investigation boards.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-border/60 pb-6">
        {/* Search */}
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by ID, summary..."
            aria-label="Search incidents"
            className="w-full bg-background rounded-xl border border-border/80 pl-9 pr-4 py-2 text-sm text-foreground outline-none focus:border-primary transition"
          />
        </div>

        {/* Severity + Status selectors */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Severity */}
          <div className="flex rounded-xl border border-border/80 bg-background/50 p-1 text-xs">
            {["ALL", "SEV1", "SEV2", "SEV3"].map((val) => (
              <button
                key={val}
                onClick={() => setSeverityFilter(val as any)}
                className={`rounded-lg px-3 py-1 font-semibold transition ${
                  severityFilter === val
                    ? "bg-primary text-primary-foreground shadow"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {val}
              </button>
            ))}
          </div>

          {/* Status */}
          <div className="flex rounded-xl border border-border/80 bg-background/50 p-1 text-xs">
            {["ALL", "ACTIVE", "RESOLVED"].map((val) => (
              <button
                key={val}
                onClick={() => setStatusFilter(val as any)}
                className={`rounded-lg px-3 py-1 font-semibold transition ${
                  statusFilter === val
                    ? "bg-primary text-primary-foreground shadow"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {val}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Incidents Table / List */}
      <div className="space-y-4">
        {isLoading ? (
          <ListSkeleton />
        ) : filteredIncidents.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-card/10 p-16 text-center">
            <ShieldCheck className="h-10 w-10 text-muted-foreground/60 mb-4" />
            <h3 className="text-sm font-semibold">No Incidents Found</h3>
            <p className="text-xs text-muted-foreground mt-1 max-w-xs">
              Check your search query or filters. All services are currently nominal.
            </p>
          </div>
        ) : (
          filteredIncidents.map((inc) => (
            <div
              key={inc.id}
              className="group relative flex flex-col gap-4 rounded-2xl border border-border/80 bg-card/40 p-6 backdrop-blur transition-all duration-200 hover:border-primary/20 hover:bg-card/65 md:flex-row md:items-center md:justify-between"
            >
              <div className="space-y-2 max-w-xl">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-primary">{inc.incident_id}</span>
                  <SeverityBadge severity={inc.severity as any} />
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold border ${
                    inc.status.toUpperCase() === "ACTIVE"
                      ? "bg-red-500/10 text-red-400 border-red-500/20 animate-pulse"
                      : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  }`}>
                    {inc.status}
                  </span>
                  <span className="text-[10px] text-muted-foreground">
                    {inc.created_at
                      ? new Date(inc.created_at).toLocaleString([], { dateStyle: "short", timeStyle: "short" })
                      : "N/A"}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition">
                  {inc.summary}
                </h3>
              </div>

              {/* Action columns */}
              <div className="flex items-center justify-between gap-6 border-t border-border/50 pt-4 md:border-transparent md:pt-0">
                <div className="text-left md:text-right text-xs">
                  <p className="font-semibold text-muted-foreground">Owner</p>
                  <p className="font-medium text-foreground mt-0.5">on-call-sre</p>
                </div>
                <div className="text-left md:text-right text-xs">
                  <p className="font-semibold text-muted-foreground">Confidence</p>
                  <p className="font-bold mt-0.5 text-emerald-400">
                    {inc.confidence ? `${Math.round(inc.confidence * 100)}%` : "92%"}
                  </p>
                </div>
                <Link
                  href={`/incidents/${inc.incident_id}`}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-muted/40 border border-border/80 text-muted-foreground transition hover:bg-primary hover:text-primary-foreground hover:border-transparent"
                >
                  <ArrowRight className="h-4.5 w-4.5" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
