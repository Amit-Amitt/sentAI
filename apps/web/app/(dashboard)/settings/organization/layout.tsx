"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Building2, Users, History } from "lucide-react";

const tabs = [
  { href: "/settings/organization", label: "Profile", icon: Building2 },
  { href: "/settings/organization/members", label: "Members", icon: Users },
  { href: "/settings/organization/activity", label: "Audit Log", icon: History },
];

export default function OrgSettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Organization Settings
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your organization profile, team, and preferences.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-border/50 pb-px">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = pathname === tab.href;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold transition rounded-t-lg border-b-2 ${
                isActive
                  ? "border-primary text-foreground bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/20"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {tab.label}
            </Link>
          );
        })}
      </div>

      {/* Page Content */}
      {children}
    </div>
  );
}
