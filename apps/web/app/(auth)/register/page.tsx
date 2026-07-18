"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/providers/auth-provider";
import { PasswordStrengthMeter } from "@/components/ui/password-strength-meter";
import { Eye, EyeOff, Loader2, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export default function RegisterPage() {
  const { register, error, clearError } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);
  
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Helper to validate password criteria
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
    clearError();

    if (!firstName.trim() || !lastName.trim() || !companyName.trim() || !email.trim()) {
      setValidationError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match.");
      return;
    }

    if (!checkPasswordStrength(password)) {
      setValidationError("Password does not meet the complexity requirements.");
      return;
    }

    if (!termsAccepted) {
      setValidationError("You must accept the Terms of Service and Privacy Policy.");
      return;
    }

    setLoading(true);
    try {
      await register({
        firstName,
        lastName,
        companyName,
        email,
      });
      // AuthProvider redirects to /verify-email since emailVerified is false
    } catch (err: any) {
      setLoading(false);
      setValidationError(err?.message || "Failed to create account. Please try again.");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-5"
    >
      {/* Header */}
      <div className="space-y-1.5 text-center lg:text-left">
        <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
        <p className="text-xs text-muted-foreground">
          Deploy Sentinel AI in your environment.
        </p>
      </div>

      {/* Error Alert */}
      {(error || validationError) && (
        <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <p>{validationError || error}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              First Name
            </label>
            <input
              id="register-firstname"
              type="text"
              placeholder="Sarah"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="w-full rounded-xl border border-border bg-background/50 px-3 py-2 text-sm outline-none focus:border-primary/50 transition"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Last Name
            </label>
            <input
              id="register-lastname"
              type="text"
              placeholder="Chen"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="w-full rounded-xl border border-border bg-background/50 px-3 py-2 text-sm outline-none focus:border-primary/50 transition"
              required
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Company Name
          </label>
          <input
            id="register-company"
            type="text"
            placeholder="Acme Inc."
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2 text-sm outline-none focus:border-primary/50 transition"
            required
          />
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Work Email
          </label>
          <input
            id="register-email"
            type="email"
            placeholder="sarah.chen@acme.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2 text-sm outline-none focus:border-primary/50 transition"
            required
          />
        </div>

        {/* Password input */}
        <div className="space-y-1">
          <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Password
          </label>
          <div className="relative">
            <input
              id="register-password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-border bg-background/50 pl-3.5 pr-10 py-2 text-sm outline-none focus:border-primary/50 transition"
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

        {/* Confirm password */}
        <div className="space-y-1">
          <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Confirm Password
          </label>
          <input
            id="register-confirm-password"
            type={showPassword ? "text" : "password"}
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2 text-sm outline-none focus:border-primary/50 transition"
            required
          />
        </div>

        {/* Terms Agreement Checkboxes */}
        <div className="space-y-2 py-1">
          <label className="flex items-start gap-2.5 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              id="register-terms"
              type="checkbox"
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              className="h-4 w-4 mt-0.5 rounded border-border bg-background text-primary focus:ring-primary/20 accent-primary shrink-0"
              required
            />
            <span>
              I accept the{" "}
              <a href="#" className="font-semibold text-primary hover:underline">
                Terms of Service
              </a>{" "}
              and acknowledge the{" "}
              <a href="#" className="font-semibold text-primary hover:underline">
                Privacy Policy
              </a>
              .
            </span>
          </label>
        </div>

        {/* Submit */}
        <button
          id="register-submit"
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-all cursor-pointer shadow-lg shadow-primary/10"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Creating Account...</span>
            </>
          ) : (
            <span>Create Account</span>
          )}
        </button>
      </form>

      {/* Footer link */}
      <p className="text-center text-xs text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-semibold text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </motion.div>
  );
}
