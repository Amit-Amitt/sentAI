"use client";

import { BrainCircuit, Search, ChevronRight, Clock, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { useMemories, useSimilarMemories } from "@/lib/api/hooks/useMemory";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import Link from "next/link";
import { ListSkeleton } from "@/components/ui/skeletons";
import { useOrgStore } from "@/lib/store/org-store";

export default function MemoryDashboardPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const { activeWorkspace } = useOrgStore();
  const workspaceId = activeWorkspace?.id || null;
  
  const { data: recentMemories, isLoading: isLoadingRecent } = useMemories(workspaceId, 20, 0);
  const { data: searchResults, isLoading: isLoadingSearch } = useSimilarMemories(workspaceId, searchQuery, 10);
  
  const memories = searchQuery.length > 2 ? searchResults : recentMemories;
  const isLoading = searchQuery.length > 2 ? isLoadingSearch : isLoadingRecent;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Incident Memory</h1>
        <p className="text-muted-foreground mt-2">
          Historical repository of resolved incidents used by Sentinel AI to contextualize future responses.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Search by summary, root cause, or error signature..."
            className="w-full bg-background rounded-xl border border-border/80 pl-9 pr-4 py-2 text-sm text-foreground outline-none focus:border-primary transition"
            value={searchQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <ListSkeleton />
        </div>
      ) : memories && memories.length > 0 ? (
        <div className="grid gap-4">
          {memories.map((memory) => (
            <Link href={`/incidents/${memory.incident_id}`} key={memory.id}>
              <div className="group rounded-xl border border-border/60 bg-card/40 p-5 hover:bg-card/60 hover:border-border transition-all">
                <div className="flex flex-col md:flex-row gap-4 md:items-center justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs font-semibold text-primary">{memory.incident_id}</span>
                      <SeverityBadge severity={memory.severity as "SEV1" | "SEV2" | "SEV3"} />
                      <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400">
                        <CheckCircle2 className="h-3 w-3" /> RESOLVED
                      </span>
                    </div>
                    <h3 className="font-semibold text-base text-foreground group-hover:text-primary transition-colors">
                      {memory.summary}
                    </h3>
                    
                    {/* Tags row */}
                    <div className="flex gap-2 flex-wrap pt-1">
                      {memory.tags.map(tag => (
                        <span key={`${tag.name}-${tag.value}`} className="inline-flex items-center rounded bg-muted/60 px-2 py-0.5 text-[10px] font-medium text-muted-foreground border border-border/50">
                          {tag.name}: {tag.value}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Right side stats */}
                  <div className="flex items-center gap-8 text-xs text-muted-foreground border-t md:border-t-0 md:border-l border-border/40 pt-4 md:pt-0 md:pl-8">
                    <div className="space-y-1">
                      <p className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" /> MTTR</p>
                      <p className="font-bold text-foreground text-sm">{Math.round((memory.time_taken_ms || 0) / 1000)}s</p>
                    </div>
                    <div className="space-y-1 flex flex-col items-center">
                      <p className="flex items-center gap-1.5"><BrainCircuit className="h-3.5 w-3.5" /> AI Conf.</p>
                      <ConfidenceIndicator confidence={memory.confidence} size={32} strokeWidth={3} />
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground/40 group-hover:text-primary transition-colors" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-border/60 bg-card/20 p-12 text-center">
          <BrainCircuit className="mx-auto h-12 w-12 text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-bold">No memories found</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-sm mx-auto">
            {searchQuery 
              ? "We couldn't find any historical incidents matching your search criteria." 
              : "Sentinel AI hasn't memorized any completed incidents in this workspace yet."}
          </p>
        </div>
      )}
    </div>
  );
}
