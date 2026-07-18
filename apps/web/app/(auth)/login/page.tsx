"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/providers/auth-provider";
import { Eye, EyeOff, Github, Chrome, Terminal, AlertTriangle, Loader2 } from "lucide-react";
import { Button } from "@sentinel/ui";
import { motion } from "framer-motion";

export default function LoginPage() {
  const { login, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearError();

    if (!email.trim() || !password.trim()) {
      setValidationError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    try {
      await login(email, password, rememberMe);
      // AuthProvider handles redirect
    } catch (err: any) {
      setLoading(false);
      setValidationError(err?.message || "Failed to log in. Please check your credentials.");
    }
  };

  const handleSocialLogin = (provider: string) => {
    // Placeholder social login trigger
    console.log(`OAuth login with ${provider}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="space-y-2 text-center lg:text-left">
        <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
        <p className="text-xs text-muted-foreground">
          Sign in to your Sentinel AI command center.
        </p>
      </div>

      {/* Error alert */}
      {(error || validationError) && (
        <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <p>{validationError || error}</p>
        </div>
      )}

      {/* Sign-in Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            Work Email
          </label>
          <input
            id="login-email"
            type="email"
            placeholder="name@company.com"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (validationError) setValidationError(null);
            }}
            className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2.5 text-sm outline-none focus:border-primary/50 transition"
            required
            autoComplete="email"
          />
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between items-center">
            <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-[11px] font-semibold text-primary hover:underline"
            >
              Forgot?
            </Link>
          </div>
          <div className="relative">
            <input
              id="login-password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (validationError) setValidationError(null);
              }}
              className="w-full rounded-xl border border-border bg-background/50 pl-3.5 pr-10 py-2.5 text-sm outline-none focus:border-primary/50 transition"
              required
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* Remember me */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              id="login-remember"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary/20 accent-primary"
            />
            Remember me for 30 days
          </label>
        </div>

        {/* Submit */}
        <button
          id="login-submit"
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-all cursor-pointer shadow-lg shadow-primary/10"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Authenticating...</span>
            </>
          ) : (
            <span>Sign In</span>
          )}
        </button>
      </form>

      {/* Social login divider */}
      <div className="relative flex py-2 items-center">
        <div className="flex-grow border-t border-border/60"></div>
        <span className="flex-shrink mx-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60">
          Or continue with
        </span>
        <div className="flex-grow border-t border-border/60"></div>
      </div>

      {/* Social options */}
      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => handleSocialLogin("github")}
          className="flex justify-center items-center gap-1.5 rounded-xl border border-border/80 bg-background/50 px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted/40 hover:text-foreground transition"
        >
          <Github className="h-4 w-4" />
          <span>GitHub</span>
        </button>
        <button
          onClick={() => handleSocialLogin("google")}
          className="flex justify-center items-center gap-1.5 rounded-xl border border-border/80 bg-background/50 px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted/40 hover:text-foreground transition"
        >
          <Chrome className="h-4 w-4" />
          <span>Google</span>
        </button>
        <button
          onClick={() => handleSocialLogin("microsoft")}
          className="flex justify-center items-center gap-1.5 rounded-xl border border-border/80 bg-background/50 px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted/40 hover:text-foreground transition"
        >
          <Terminal className="h-4 w-4" />
          <span>Microsoft</span>
        </button>
      </div>

      {/* Footer link */}
      <p className="text-center text-xs text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-semibold text-primary hover:underline">
          Create account
        </Link>
      </p>
    </motion.div>
  );
}
