export const APP_NAME = "Sentinel AI";
export const APP_TAGLINE = "The Autonomous AI Incident Commander";

export const APP_DESCRIPTION =
  "Sentinel AI is a multi-agent incident investigation platform for modern engineering teams.";

export const SUPPORTED_THEMES = ["light", "dark", "system"] as const;

export type SupportedTheme = (typeof SUPPORTED_THEMES)[number];
