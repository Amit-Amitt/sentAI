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
  User,
  ShieldCheck,
  Binary,
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
    href: "/settings/profile",
    label: "Profile",
    icon: User,
  },
  {
    href: "/settings/security",
    label: "Security & Account",
    icon: ShieldCheck,
  },
  {
    href: "/settings",
    label: "System Configuration",
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
    href: "/settings/auth-tests",
    label: "Auth Test Harness",
    icon: Binary,
  },
  {
    href: "/settings/about",
    label: "About Sentinel",
    icon: HelpCircle,
  },
] as const;
