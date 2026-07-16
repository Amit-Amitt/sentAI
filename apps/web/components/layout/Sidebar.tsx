import Link from "next/link";

import { APP_METADATA } from "@sentinel/config";
import { Badge } from "@sentinel/ui";

import { primaryNavigation, settingsNavigation } from "@/lib/constants/navigation";

export function Sidebar() {
  return (
    <aside className="hidden w-80 shrink-0 border-r border-border/70 bg-card/80 px-6 py-8 backdrop-blur xl:block">
      <div className="space-y-4">
        <Badge variant="warning">Foundation</Badge>
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">
            {APP_METADATA.tagline}
          </p>
          <h1 className="text-2xl font-semibold tracking-tight">{APP_METADATA.name}</h1>
          <p className="text-sm leading-6 text-muted-foreground">{APP_METADATA.description}</p>
        </div>
      </div>

      <nav className="mt-10 space-y-8">
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Product</p>
          <ul className="space-y-2">
            {primaryNavigation.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block rounded-2xl border border-transparent px-4 py-3 transition hover:border-border hover:bg-background/80"
                >
                  <p className="font-medium">{item.label}</p>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Settings</p>
          <ul className="space-y-2">
            {settingsNavigation.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block rounded-2xl px-4 py-3 text-sm text-muted-foreground transition hover:bg-background/80 hover:text-foreground"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </aside>
  );
}
