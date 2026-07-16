import { APP_ROUTES } from "@sentinel/config";

export const primaryNavigation = [
  {
    href: APP_ROUTES.incidents,
    label: "Incidents",
    description: "Operational command center",
  },
  {
    href: APP_ROUTES.simulator,
    label: "Simulator",
    description: "Deterministic demo scenarios",
  },
] as const;

export const settingsNavigation = [
  {
    href: APP_ROUTES.settingsIntegrations,
    label: "Integrations",
  },
  {
    href: APP_ROUTES.settingsPrompts,
    label: "Prompts",
  },
  {
    href: APP_ROUTES.settingsAbout,
    label: "About",
  },
] as const;
