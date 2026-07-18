import {
  Activity,
  Building2,
  FileText,
  FolderKanban,
  HelpCircle,
  LayoutDashboard,
  Puzzle,
  Settings,
  ShieldAlert,
  Users,
  User,
  ShieldCheck,
  Binary,
  Key,
  Database,
  TerminalSquare,
  Wrench
} from "lucide-react";

export const primaryNavigation = [
  {
    href: "/command-center",
    label: "AI Command Center",
    description: "Live Executive Ops Dashboard",
    icon: LayoutDashboard,
  },
  {
    href: "/dashboard",
    label: "Metrics & Status",
    description: "Operational system stats",
    icon: Activity,
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
  {
    href: "/memory",
    label: "Memory & Context",
    description: "Historical incident repository",
    icon: Database,
  },
  {
    href: "/simulation",
    label: "Simulation Center",
    description: "Trigger synthetic incidents",
    icon: TerminalSquare,
  },
  {
    href: "/remediation",
    label: "Remediation Center",
    description: "AI-generated fixes and patches",
    icon: Wrench,
  },
  {
    href: "/projects",
    label: "Projects & Apps",
    description: "Connected telemetry apps",
    icon: FolderKanban,
  },
  {
    href: "/demo",
    label: "Live Demo Controls",
    description: "Trigger real-world failures",
    icon: Binary,
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
    href: "/settings/apikeys",
    label: "Workspace API Keys",
    icon: Key,
  },
  {
    href: "/settings/integrations",
    label: "Integrations",
    icon: Puzzle,
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
