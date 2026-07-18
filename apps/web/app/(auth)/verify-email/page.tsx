"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/providers/auth-provider";
import { AlertTriangle, CheckCircle, Loader2, Mail, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export default function VerifyEmailPage() {
  const router = useRouter();
  const { verifyEmail, resendVerification, user } = useAuth();
  const [code, setCode] = useState<string[]>(Array(6).fill(""));
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);
  const [resendTimer, setResendTimer] = useState(60);
  const [expiryTimer, setExpiryTimer] = useState(600); // 10 minutes

  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

  // Expiration countdown
  useEffect(() => {
    if (expiryTimer <= 0) return;
    const interval = setInterval(() => {
      setExpiryTimer((t) => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [expiryTimer]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendTimer <= 0) return;
    const interval = setInterval(() => {
      setResendTimer((t) => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [resendTimer]);

  // Format time remaining
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const handleInputChange = (index: number, val: string) => {
    if (!/^[0-9]?$/.test(val)) return; // Allow digits only

    const newCode = [...code];
    newCode[index] = val;
    setCode(newCode);
    setErrorText(null);

    // Auto-focus next input
    if (val && index < 5) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").trim();
    if (!/^[0-9]{6}$/.test(pastedData)) return;

    const newCode = pastedData.split("");
    setCode(newCode);
    inputsRef.current[5]?.focus();
  };

  const triggerVerification = async (otpCode: string) => {
    setLoading(true);
    setErrorText(null);
    try {
      if (otpCode === "000000") {
        throw new Error("Invalid or expired verification code.");
      }
      
      const verified = await verifyEmail(otpCode);
      if (verified) {
        setSuccess(true);
        setTimeout(() => {
          router.push("/welcome");
        }, 1500);
      } else {
        setErrorText("Verification failed. Please try again.");
      }
    } catch (err: any) {
      setErrorText(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Auto-submit when code is complete
  useEffect(() => {
    const fullCode = code.join("");
    if (fullCode.length === 6) {
      triggerVerification(fullCode);
    }
  }, [code]);

  const handleResend = async () => {
    if (resendTimer > 0) return;
    setLoading(true);
    try {
      await resendVerification();
      setResendTimer(60);
      setExpiryTimer(600); // Reset expiry to 10 mins
      setCode(Array(6).fill(""));
      inputsRef.current[0]?.focus();
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
      {!success ? (
        <>
          {/* Header */}
          <div className="space-y-2 text-center lg:text-left">
            <h1 className="text-2xl font-bold tracking-tight font-sans">Verify your email</h1>
            <p className="text-xs text-muted-foreground leading-normal">
              We sent a 6-digit verification code to <span className="text-foreground font-semibold">{user?.email || "your work email"}</span>.
            </p>
          </div>

          {expiryTimer <= 0 && (
            <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <p>The verification code has expired. Please request a new one below.</p>
            </div>
          )}

          {errorText && (
            <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/5 p-3 text-xs text-rose-400">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <p>{errorText}</p>
            </div>
          )}

          {/* Code Inputs */}
          <div className="space-y-4">
            <div className="flex justify-between gap-2.5">
              {code.map((num, idx) => (
                <input
                  key={idx}
                  type="text"
                  maxLength={1}
                  value={num}
                  disabled={expiryTimer <= 0 || loading}
                  ref={(el) => {
                    inputsRef.current[idx] = el;
                  }}
                  onChange={(e) => handleInputChange(idx, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(idx, e)}
                  onPaste={handlePaste}
                  className="h-12 w-12 rounded-xl border border-border bg-background/50 text-center text-lg font-bold outline-none focus:border-primary/50 transition disabled:opacity-50"
                />
              ))}
            </div>

            <div className="flex justify-between items-center text-[11px] text-muted-foreground font-medium px-1">
              <span>Code expires in: <strong className="text-foreground">{formatTime(expiryTimer)}</strong></span>
              <button
                onClick={handleResend}
                disabled={resendTimer > 0 || loading}
                className="font-semibold text-primary hover:underline disabled:opacity-50 disabled:no-underline flex items-center gap-1"
              >
                {loading ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : resendTimer > 0 ? (
                  `Resend code (${resendTimer}s)`
                ) : (
                  <>
                    <RefreshCw className="h-3 w-3" />
                    <span>Resend code</span>
                  </>
                )}
              </button>
            </div>
          </div>
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
              <CheckCircle className="h-6 w-6 text-emerald-400 animate-bounce" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-bold">Email Verified!</h2>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
              Your email has been verified. Preparing your onboarding dashboard.
            </p>
          </div>

          <div className="flex justify-center py-2">
            <Loader2 className="h-5 w-5 text-primary animate-spin" />
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
