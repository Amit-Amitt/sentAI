"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/providers/auth-provider";
import { ArrowLeft, CheckCircle, Loader2, Mail } from "lucide-react";
import { motion } from "framer-motion";

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (resendTimer > 0) {
      interval = setInterval(() => {
        setResendTimer((t) => t - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [resendTimer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    try {
      await forgotPassword(email);
      setSent(true);
      setResendTimer(60);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendTimer > 0) return;
    setLoading(true);
    try {
      await forgotPassword(email);
      setResendTimer(60);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {!sent ? (
        <>
          {/* Form State */}
          <div className="space-y-2 text-center lg:text-left">
            <h1 className="text-2xl font-bold tracking-tight">Forgot password?</h1>
            <p className="text-xs text-muted-foreground">
              Enter your work email address and we will send you a secure link to reset your credentials.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                Work Email
              </label>
              <input
                id="forgot-email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-border bg-background/50 px-3.5 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>

            <button
              id="forgot-submit"
              type="submit"
              disabled={loading || !email}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-all cursor-pointer shadow-lg shadow-primary/10"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Sending Link...</span>
                </>
              ) : (
                <span>Send Reset Link</span>
              )}
            </button>
          </form>
        </>
      ) : (
        /* Success State */
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
            <h2 className="text-xl font-bold">Reset link sent</h2>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
              We have sent a secure password reset link to <strong className="text-foreground">{email}</strong>.
              The link is valid for 1 hour.
            </p>
          </div>

          <div className="pt-2">
            <button
              onClick={handleResend}
              disabled={resendTimer > 0 || loading}
              className="text-xs font-semibold text-primary hover:underline disabled:opacity-50 disabled:no-underline"
            >
              {loading ? (
                <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" /> Resending...</span>
              ) : resendTimer > 0 ? (
                `Resend link in ${resendTimer}s`
              ) : (
                "Resend link"
              )}
            </button>
          </div>
        </motion.div>
      )}

      {/* Back to sign in */}
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
