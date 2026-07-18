"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/providers/auth-provider";
import { PasswordStrengthMeter } from "@/components/ui/password-strength-meter";
import { ArrowLeft, CheckCircle, Eye, EyeOff, Loader2, AlertTriangle, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "mock-token";
  const isExpired = token === "expired";

  const { resetPassword } = useAuth();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const checkPasswordStrength = (pass: string) => {
    return (
      pass.length >= 8 &&
      /[A-Z]/.test(pass) &&
      /[a-z]/.test(pass) &&
      /[0-9]/.test(pass) &&
      /[^A-Za-z0-9]/.test(pass)
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match.");
      return;
    }

    if (!checkPasswordStrength(password)) {
      setValidationError("Password does not meet complexity requirements.");
      return;
    }

    setLoading(true);
    try {
      await resetPassword(password);
      setSuccess(true);
    } catch (err) {
      setValidationError("Failed to reset password. Please request a new link.");
    } finally {
      setLoading(false);
    }
  };

  if (isExpired) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 text-center"
      >
        <div className="flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/25">
            <AlertTriangle className="h-6 w-6 text-rose-400" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-xl font-bold">Reset Link Expired</h1>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
            For security reasons, password reset links expire after 1 hour. Please request a new link to reset your credentials.
          </p>
        </div>

        <Link
          href="/forgot-password"
          className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Request New Link</span>
        </Link>

        <div className="flex justify-center border-t border-border/50 pt-4">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition font-semibold"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Back to sign in</span>
          </Link>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {!success ? (
        <>
          <div className="space-y-2 text-center lg:text-left">
            <h1 className="text-2xl font-bold tracking-tight">Reset password</h1>
            <p className="text-xs text-muted-foreground">
              Create a strong, unique password to secure your account.
            </p>
          </div>

          {validationError && (
            <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <p>{validationError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                New Password
              </label>
              <div className="relative">
                <input
                  id="reset-password-input"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-border bg-background/50 pl-3.5 pr-10 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {password && <PasswordStrengthMeter value={password} />}
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                Confirm Password
              </label>
              <input
                id="reset-password-confirm"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>

            <button
              id="reset-submit"
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-all cursor-pointer shadow-lg shadow-primary/10"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Saving changes...</span>
                </>
              ) : (
                <span>Reset Password</span>
              )}
            </button>
          </form>
        </>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-5"
        >
          <div className="flex justify-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/25">
              <CheckCircle className="h-6 w-6 text-emerald-400" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-bold">Password Updated</h2>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
              Your password has been successfully updated. You can now use your new credentials to sign in.
            </p>
          </div>

          <Link
            id="reset-success-login-btn"
            href="/login"
            className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition shadow-lg shadow-primary/10"
          >
            <span>Sign In</span>
          </Link>
        </motion.div>
      )}
    </motion.div>
  );
}
