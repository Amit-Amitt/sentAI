import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("sentinel_session_token")?.value;
  const { pathname } = request.nextUrl;

  // Paths requiring authentication
  const protectedRoutes = [
    "/dashboard",
    "/incidents",
    "/settings",
    "/team",
    "/workspaces",
    "/agent-activity",
    "/reports",
    "/onboarding",
  ];
  const isProtected = protectedRoutes.some((route) => pathname === route || pathname.startsWith(route + "/"));

  // Paths for unauthenticated users
  const authRoutes = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];
  const isAuthRoute = authRoutes.some((route) => pathname === route || pathname.startsWith(route + "/"));

  // Redirect unauthenticated requests to login
  if (!token && isProtected) {
    const url = new URL("/login", request.url);
    return NextResponse.redirect(url);
  }

  // Redirect authenticated requests away from login/register
  if (token && isAuthRoute) {
    if (token === "sentinel-mock-session-token-unverified") {
      if (pathname !== "/verify-email") {
        return NextResponse.redirect(new URL("/verify-email", request.url));
      }
    } else {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - fonts (custom local fonts)
     * - SVG / Image files (any standard images)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|fonts|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
