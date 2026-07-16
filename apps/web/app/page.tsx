import { redirect } from "next/navigation";

import { APP_ROUTES } from "@sentinel/config";

export default function HomePage() {
  redirect(APP_ROUTES.incidents);
}
