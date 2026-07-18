"use client";

import { create } from "zustand";

export interface UserProfile {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  companyName: string;
  industry?: string;
  cloudProvider?: string;
  invitedTeamSize?: number;
  avatarUrl?: string | null;
  timezone: string;
  language: string;
  theme: "dark" | "light" | "system";
  emailVerified: boolean;
  onboardingCompleted: boolean;
  twoFactorEnabled: boolean;
  passkeysEnabled: boolean;
  magicLinksEnabled: boolean;
  oauthConnected: {
    google: boolean;
    github: boolean;
    microsoft: boolean;
  };
}

export interface UserSession {
  id: string;
  device: string;
  browser: string;
  ipAddress: string;
  location: string;
  active: boolean;
  lastActive: string;
}

interface AuthState {
  user: UserProfile | null;
  sessions: UserSession[];
  isLoading: boolean;
  isVerifying: boolean;
  verificationCodeSent: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string, rememberMe: boolean) => Promise<void>;
  register: (data: {
    firstName: string;
    lastName: string;
    companyName: string;
    email: string;
  }) => Promise<void>;
  logout: () => void;
  verifyEmail: (token: string) => Promise<boolean>;
  resendVerification: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (password: string) => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => void;
  updateSecurity: (data: Partial<UserProfile>) => void;
  revokeSession: (id: string) => void;
  completeOnboarding: (orgId: string, wsId: string, details: { industry: string; cloudProvider: string; teamSize: number }) => void;
  hydrate: () => void;
  clearError: () => void;
}

const STORAGE_KEY_USER = "sentinel_auth_user";
const STORAGE_KEY_SESSIONS = "sentinel_auth_sessions";
const COOKIE_TOKEN_NAME = "sentinel_session_token";

// Helper to set cookie
function setCookie(name: string, value: string, days: number = 7) {
  if (typeof window === "undefined") return;
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax; Secure";
}

// Helper to delete cookie
function deleteCookie(name: string) {
  if (typeof window === "undefined") return;
  document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax; Secure";
}

const DEFAULT_SESSIONS: UserSession[] = [
  {
    id: "session-1",
    device: "Linux (Desktop)",
    browser: "Chrome",
    ipAddress: "192.168.1.45",
    location: "Mumbai, India",
    active: true,
    lastActive: "Just now",
  },
  {
    id: "session-2",
    device: "Apple iPhone 15 Pro",
    browser: "Safari",
    ipAddress: "103.241.12.89",
    location: "Pune, India",
    active: false,
    lastActive: "2 hours ago",
  },
  {
    id: "session-3",
    device: "macOS (MacBook Pro)",
    browser: "Firefox",
    ipAddress: "124.8.42.17",
    location: "Bengaluru, India",
    active: false,
    lastActive: "3 days ago",
  },
];

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  sessions: [],
  isLoading: true,
  isVerifying: false,
  verificationCodeSent: false,
  error: null,

  clearError: () => set({ error: null }),

  hydrate: () => {
    if (typeof window === "undefined") return;
    try {
      const userStr = localStorage.getItem(STORAGE_KEY_USER);
      const sessionsStr = localStorage.getItem(STORAGE_KEY_SESSIONS);
      const user = userStr ? JSON.parse(userStr) : null;
      const sessions = sessionsStr ? JSON.parse(sessionsStr) : DEFAULT_SESSIONS;

      set({
        user,
        sessions,
        isLoading: false,
      });
    } catch (err) {
      console.error("Hydration error:", err);
      set({ isLoading: false });
    }
  },

  login: async (email, password, rememberMe) => {
    set({ isLoading: true, error: null });
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Simple validation
    if (!email.includes("@")) {
      set({ error: "Please enter a valid email address.", isLoading: false });
      throw new Error("Invalid email");
    }

    const emailParts = email.split("@")[0] || "";
    const nameParts = emailParts.split(".");
    const firstName = nameParts[0] || "Jane";
    const lastName = nameParts[1] || "Doe";

    const mockUser: UserProfile = {
      id: "usr-" + Math.random().toString(36).substr(2, 9),
      firstName,
      lastName,
      email,
      companyName: "Sentinel Enterprises",
      timezone: "Asia/Kolkata",
      language: "en",
      theme: "dark",
      emailVerified: true,
      onboardingCompleted: true, // Default to true if already configured, or false for new register
      twoFactorEnabled: false,
      passkeysEnabled: false,
      magicLinksEnabled: false,
      oauthConnected: {
        google: false,
        github: false,
        microsoft: false,
      },
    };

    // If logging in with a new email, we let it simulate onboarding as well if they wish.
    // For demo/consistency, let's keep it onboardingCompleted: true unless it's a specific test case.
    
    // Save to localStorage & cookie
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));
    const activeSessions = [
      {
        id: "sess-" + Date.now(),
        device: "Linux (Desktop)",
        browser: "Chrome",
        ipAddress: "192.168.1.45",
        location: "Mumbai, India",
        active: true,
        lastActive: "Just now",
      },
      ...DEFAULT_SESSIONS.slice(1),
    ];
    localStorage.setItem(STORAGE_KEY_SESSIONS, JSON.stringify(activeSessions));
    
    // Set cookie token
    setCookie(COOKIE_TOKEN_NAME, "sentinel-mock-session-token", rememberMe ? 30 : 1);

    set({
      user: mockUser,
      sessions: activeSessions,
      isLoading: false,
    });
  },

  register: async (data) => {
    set({ isLoading: true, error: null });
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const mockUser: UserProfile = {
      id: "usr-" + Math.random().toString(36).substr(2, 9),
      firstName: data.firstName,
      lastName: data.lastName,
      email: data.email,
      companyName: data.companyName,
      timezone: "Asia/Kolkata",
      language: "en",
      theme: "dark",
      emailVerified: false, // New user needs email verification
      onboardingCompleted: false, // Needs onboarding
      twoFactorEnabled: false,
      passkeysEnabled: false,
      magicLinksEnabled: false,
      oauthConnected: {
        google: false,
        github: false,
        microsoft: false,
      },
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(mockUser));
    setCookie(COOKIE_TOKEN_NAME, "sentinel-mock-session-token-unverified", 1);

    set({
      user: mockUser,
      verificationCodeSent: true,
      isLoading: false,
    });
  },

  logout: () => {
    localStorage.removeItem(STORAGE_KEY_USER);
    localStorage.removeItem(STORAGE_KEY_SESSIONS);
    deleteCookie(COOKIE_TOKEN_NAME);
    set({
      user: null,
      sessions: [],
    });
  },

  verifyEmail: async (token) => {
    set({ isVerifying: true });
    await new Promise((resolve) => setTimeout(resolve, 1200));

    const { user } = get();
    if (!user) {
      set({ isVerifying: false });
      return false;
    }

    // Mark verified
    const updatedUser = {
      ...user,
      emailVerified: true,
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(updatedUser));
    // Update session token to fully authorized
    setCookie(COOKIE_TOKEN_NAME, "sentinel-mock-session-token", 1);

    set({
      user: updatedUser,
      isVerifying: false,
    });
    return true;
  },

  resendVerification: async () => {
    set({ isLoading: true });
    await new Promise((resolve) => setTimeout(resolve, 800));
    set({ verificationCodeSent: true, isLoading: false });
  },

  forgotPassword: async (email) => {
    set({ isLoading: true });
    await new Promise((resolve) => setTimeout(resolve, 800));
    set({ isLoading: false });
  },

  resetPassword: async (password) => {
    set({ isLoading: true });
    await new Promise((resolve) => setTimeout(resolve, 1000));
    set({ isLoading: false });
  },

  updateProfile: (data) => {
    const { user } = get();
    if (!user) return;

    const updatedUser = { ...user, ...data };
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(updatedUser));
    set({ user: updatedUser });
  },

  updateSecurity: (data) => {
    const { user } = get();
    if (!user) return;

    const updatedUser = { ...user, ...data };
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(updatedUser));
    set({ user: updatedUser });
  },

  revokeSession: (id) => {
    const { sessions } = get();
    const updatedSessions = sessions.filter((s) => s.id !== id);
    localStorage.setItem(STORAGE_KEY_SESSIONS, JSON.stringify(updatedSessions));
    set({ sessions: updatedSessions });
  },

  completeOnboarding: (orgId, wsId, details) => {
    const { user } = get();
    if (!user) return;

    const updatedUser: UserProfile = {
      ...user,
      industry: details.industry,
      cloudProvider: details.cloudProvider,
      invitedTeamSize: details.teamSize,
      onboardingCompleted: true,
    };

    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(updatedUser));
    set({ user: updatedUser });
  },
}));
