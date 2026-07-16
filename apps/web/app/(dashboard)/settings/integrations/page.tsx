import { Card, CardContent, CardHeader, CardTitle } from "@sentinel/ui";

export default function IntegrationsSettingsPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Integrations</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Integration management will be added after the ingestion and simulation foundations are in
        place.
      </CardContent>
    </Card>
  );
}
