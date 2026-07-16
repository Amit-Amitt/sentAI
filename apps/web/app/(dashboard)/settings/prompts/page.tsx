import { Card, CardContent, CardHeader, CardTitle } from "@sentinel/ui";

export default function PromptSettingsPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Prompt Registry</CardTitle>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Prompt placeholders now live in `packages/prompts`. Versioned runtime prompt management
        begins in the AI implementation phase.
      </CardContent>
    </Card>
  );
}
