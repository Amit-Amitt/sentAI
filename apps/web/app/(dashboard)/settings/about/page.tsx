import { Card, CardContent, CardHeader, CardTitle } from "@sentinel/ui";

export default function AboutSettingsPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>About Sentinel AI</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm text-muted-foreground">
        <p>Architecture foundation follows the bounded-monolith plan in `PROJECT.md`.</p>
        <p>The web app is Next.js 15, the backend is FastAPI, and the workspace is TurboRepo.</p>
      </CardContent>
    </Card>
  );
}
