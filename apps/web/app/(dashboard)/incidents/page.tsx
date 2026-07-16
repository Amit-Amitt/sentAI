import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@sentinel/ui";

export default function IncidentsPage() {
  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
          Foundation Route
        </p>
        <h1 className="text-3xl font-semibold tracking-tight">Incident Command Center shell</h1>
        <p className="max-w-3xl text-muted-foreground">
          The monorepo, route structure, theme system, shared packages, and backend foundation are
          ready. Incident investigation panels arrive in later tasks.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="shadow-ambient">
          <CardHeader>
            <CardTitle>What is ready now</CardTitle>
            <CardDescription>
              This route intentionally stops at project setup and workspace structure.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>Shared type, config, prompt, schema, and API client packages are wired.</p>
            <p>Tailwind, shadcn-style UI primitives, and dark mode support are configured.</p>
            <p>FastAPI foundation, typed settings, logging, and the health endpoint are scaffolded.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Next implementation slice</CardTitle>
            <CardDescription>
              Database models, repositories, and the first incident APIs begin after foundation.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Task chain: TASK-016 through TASK-028.</p>
            <p>Focus: structured logging enrichment, migrations, models, repositories, seed data.</p>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
