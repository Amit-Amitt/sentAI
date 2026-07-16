import type { HealthResponse } from "@sentinel/types";

import { ApiClient } from "./client";
import { apiRoutes } from "./routes";

export async function getHealth(client: ApiClient) {
  return client.get<HealthResponse>(apiRoutes.health);
}
