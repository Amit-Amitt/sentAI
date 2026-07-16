import { APP_DESCRIPTION, APP_NAME, APP_TAGLINE } from "@sentinel/shared";

export const APP_METADATA = {
  name: APP_NAME,
  tagline: APP_TAGLINE,
  description: APP_DESCRIPTION,
} as const;

export const DEFAULT_PORTS = {
  api: 8000,
  docs: 3001,
  web: 3000,
} as const;

export const API_PREFIX = "/v1";

export const APP_ROUTES = {
  home: "/",
  incidents: "/incidents",
  simulator: "/simulator",
  settings: "/settings",
  settingsAbout: "/settings/about",
  settingsIntegrations: "/settings/integrations",
  settingsPrompts: "/settings/prompts",
} as const;
