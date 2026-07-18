"use client";

import { useState } from "react";
import { FileText, Download, ShieldAlert, Loader2 } from "lucide-react";
import { useIncidents } from "@/lib/api/hooks/useIncidents";
import { incidentsService } from "@/lib/api/services/incidents";
import { mapReportToIncident } from "@/lib/api/types/mapper";
import { ListSkeleton } from "@/components/ui/skeletons";

export default function ReportsPage() {
  const { data, isLoading } = useIncidents();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const incidents = data?.results || [];

  const handleDownload = async (incidentId: string, format: "json" | "markdown") => {
    try {
      setDownloadingId(incidentId);
      const report = await incidentsService.getIncident(incidentId);
      const mappedIncident = mapReportToIncident(report);

      let content = "";
      let filename = `${mappedIncident.id}-post-mortem`;

      if (format === "json") {
        content = JSON.stringify(report, null, 2);
        filename += ".json";
      } else {
        content = `# Sentinel AI Post-Mortem: ${mappedIncident.id}
## Incident Summary: ${mappedIncident.summary}
- **Severity**: ${mappedIncident.severity}
- **Status**: ${mappedIncident.status}
- **Owner**: ${mappedIncident.owner}
- **Confidence**: ${Math.round(mappedIncident.confidence * 100)}%

### Description
${mappedIncident.description}

### Root Cause Analysis
- **Primary Driver**: ${mappedIncident.root_cause.primary}
${mappedIncident.root_cause.supporting_evidence.map((ev) => `- ${ev}`).join("\n")}

### Remediation Action Plan
${mappedIncident.recommendations
  .map(
    (rec) =>
      `#### Action ${rec.execution_order}: ${rec.title}\n*Priority*: ${rec.priority}\n\n${rec.description}`
  )
  .join("\n\n")}
`;
        filename += ".md";
      }

      const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Failed to generate report export", err);
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports Archive</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Exportable post-mortem summaries generated automatically upon incident mitigation.
        </p>
      </div>

      {/* Reports Listing */}
      <div className="space-y-4">
        {isLoading ? (
          <ListSkeleton />
        ) : incidents.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-card/10 p-16 text-center">
            <ShieldAlert className="h-10 w-10 text-muted-foreground/60 mb-4" />
            <h3 className="text-sm font-semibold">No Reports Generated</h3>
            <p className="text-xs text-muted-foreground mt-1 max-w-xs">
              Reports are constructed automatically once sub-agent pipelines finish analyzing incidents.
            </p>
          </div>
        ) : (
          incidents.map((inc) => (
            <div
              key={inc.id}
              className="flex flex-col gap-4 rounded-2xl border border-border/80 bg-card/45 p-6 backdrop-blur transition hover:border-primary/20 md:flex-row md:items-center md:justify-between"
            >
              <div className="flex items-start gap-4">
                <div className="rounded-xl bg-primary/10 p-3 text-primary hidden sm:block">
                  <FileText className="h-6 w-6" />
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-primary">{inc.incident_id}</span>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[9px] font-semibold border ${
                      inc.status.toUpperCase() === "ACTIVE"
                        ? "bg-red-500/10 text-red-400 border-red-500/20"
                        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    }`}>
                      {inc.status}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-foreground">{inc.summary}</h3>
                </div>
              </div>

              {/* Export Actions */}
              <div className="flex items-center gap-3 border-t border-border/50 pt-4 md:border-transparent md:pt-0 justify-end">
                <button
                  onClick={() => handleDownload(inc.incident_id, "markdown")}
                  disabled={downloadingId === inc.incident_id}
                  className="flex items-center gap-1.5 rounded-xl border border-border/80 bg-background px-3.5 py-2 text-xs font-semibold text-foreground transition hover:bg-muted disabled:opacity-50"
                >
                  {downloadingId === inc.incident_id ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Download className="h-3.5 w-3.5" />
                  )}
                  Markdown
                </button>
                <button
                  onClick={() => handleDownload(inc.incident_id, "json")}
                  disabled={downloadingId === inc.incident_id}
                  className="flex items-center gap-1.5 rounded-xl border border-border/80 bg-background px-3.5 py-2 text-xs font-semibold text-foreground transition hover:bg-muted disabled:opacity-50"
                >
                  {downloadingId === inc.incident_id ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Download className="h-3.5 w-3.5" />
                  )}
                  JSON Metadata
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
