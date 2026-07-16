export const PUBLIC_ENV_KEYS = ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_APP_NAME"] as const;

export const SERVER_ENV_KEYS = [
  "SENTINEL_API_HOST",
  "SENTINEL_API_PORT",
  "SENTINEL_APP_ENV",
  "SENTINEL_CORS_ORIGINS",
  "SENTINEL_DATABASE_URL",
  "SENTINEL_GEMINI_API_KEY",
  "SENTINEL_LOG_LEVEL",
  "SENTINEL_OPENAI_API_KEY",
] as const;

export const ENVIRONMENT_NAMES = ["development", "staging", "production", "test"] as const;

export type PublicEnvKey = (typeof PUBLIC_ENV_KEYS)[number];
export type ServerEnvKey = (typeof SERVER_ENV_KEYS)[number];
export type EnvironmentName = (typeof ENVIRONMENT_NAMES)[number];
