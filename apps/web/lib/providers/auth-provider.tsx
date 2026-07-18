"use client";

import React, { createContext, useContext, useEffect } from "react";
import { useAuthStore, type UserProfile, type UserSession } from "../store/auth-store";
import { usePathname, useRouter } from "next/navigation";

interface AuthContextType {
  user: UserProfile | null;
  sessions: UserSession[];
  isLoading: boolean;
  isVerifying: boolean;
  verificationCodeSent: boolean;
  error: string | null;
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;
  register: (data: { firstName: string; lastName: string; companyName: string; email: string }) => Promise<void>;
  logout: () => void;
  verifyEmail: (token: string) => Promise<boolean>;
  resendVerification: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (password: string) => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => void;
  updateSecurity: (data: Partial<UserProfile>) => void;
  revokeSession: (id: string) => void;
  completeOnboarding: (orgId: string, wsId: string, details: { industry: string; cloudProvider: string; teamSize: number }) => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const hydrate = useAuthStore((s) => s.hydrate);
  const store = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  // Client-side safety redirect checks (as a backup/dual layer alongside Edge Middleware)
  useEffect(() => {
    if (store.isLoading) return;

    const publicPaths = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];
    const isPublicPath = publicPaths.some(path => pathname === path || pathname.startsWith(path + "/"));

    if (!store.user && !isPublicPath && pathname !== "/") {
      router.push("/login");
    } else if (store.user && isPublicPath) {
      if (!store.user.emailVerified) {
        router.push("/verify-email");
      } else if (!store.user.onboardingCompleted) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } else if (store.user && !store.user.emailVerified && pathname !== "/verify-email") {
      router.push("/verify-email");
    } else if (store.user && store.user.emailVerified && !store.user.onboardingCompleted && pathname !== "/onboarding" && !pathname.startsWith("/settings")) {
      router.push("/onboarding");
    }
  }, [store.user, store.isLoading, pathname, router]);

  return (
    <AuthContext.Provider
      value={{
        user: store.user,
        sessions: store.sessions,
        isLoading: store.isLoading,
        isVerifying: store.isVerifying,
        verificationCodeSent: store.verificationCodeSent,
        error: store.error,
        login: store.login,
        register: store.register,
        logout: store.logout,
        verifyEmail: store.verifyEmail,
        resendVerification: store.resendVerification,
        forgotPassword: store.forgotPassword,
        resetPassword: store.resetPassword,
        updateProfile: store.updateProfile,
        updateSecurity: store.updateSecurity,
        revokeSession: store.revokeSession,
        completeOnboarding: store.completeOnboarding,
        clearError: store.clearError,
      }}
    >
      {store.isLoading ? (
        <div className="flex min-h-screen w-full items-center justify-center bg-zinc-950">
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <p className="text-xs font-semibold text-muted-foreground tracking-wider uppercase">Loading Sentinel AI...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
