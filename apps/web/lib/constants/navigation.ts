import {
  Activity,
  Building2,
  FileText,
  FolderKanban,
  HelpCircle,
  LayoutDashboard,
  Settings,
  ShieldAlert,
  Users,
} from "lucide-react";

export const primaryNavigation = [
  {
    href: "/dashboard",
    label: "Dashboard",
    description: "Operational system stats",
    icon: LayoutDashboard,
  },
  {
    href: "/incidents",
    label: "Incidents",
    description: "Active SRE incident board",
    icon: ShieldAlert,
  },
  {
    href: "/agent-activity",
    label: "Agent Activity",
    description: "LangGraph sub-agent logs",
    icon: Activity,
  },
  {
    href: "/reports",
    label: "Reports Archive",
    description: "Incident post-mortems",
    icon: FileText,
  },
] as const;

export const settingsNavigation = [
  {
    href: "/settings",
    label: "Settings",
    icon: Settings,
  },
  {
    href: "/settings/organization",
    label: "Organization",
    icon: Building2,
  },
  {
    href: "/settings/organization/members",
    label: "Members",
    icon: Users,
  },
  {
    href: "/settings/workspace",
    label: "Workspace",
    icon: FolderKanban,
  },
  {
    href: "/settings/about",
    label: "About Sentinel",
    icon: HelpCircle,
  },
] as const;
