import { Card, CardContent, CardHeader, CardTitle } from "@sentinel/ui";

export default function SimulatorPage() {
  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
          Simulator Route
        </p>
        <h1 className="text-3xl font-semibold tracking-tight">Deterministic incident simulator</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Foundation placeholder</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Simulation scenarios, live ingestion, and incident kickoff are intentionally deferred until
          the backend and LangGraph phases.
        </CardContent>
      </Card>
    </section>
  );
}
