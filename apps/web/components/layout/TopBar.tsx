import { Badge } from "@sentinel/ui";

export function TopBar() {
  return (
    <header className="flex items-center justify-between gap-4 border-b border-border/70 bg-background/70 px-6 py-4 backdrop-blur">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
          Project Foundation
        </p>
        <h2 className="text-lg font-semibold tracking-tight">Sentinel AI workspace ready</h2>
      </div>

      <div className="flex items-center gap-3">
        <Badge variant="success">Web Ready</Badge>
        <Badge>Dark Mode Ready</Badge>
      </div>
    </header>
  );
}
