import { z } from "zod";

export const simulationScenarioSchema = z.object({
  id: z.string(),
  slug: z.string(),
  name: z.string(),
  description: z.string(),
  difficulty: z.enum(["easy", "medium", "hard"]),
  estimatedRuntimeSec: z.number().int().positive(),
  primaryService: z.string(),
});
