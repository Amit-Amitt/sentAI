"use client";

import { Check, X } from "lucide-react";

interface PasswordStrengthMeterProps {
  value: string;
}

export function PasswordStrengthMeter({ value }: PasswordStrengthMeterProps) {
  const requirements = [
    { label: "Minimum 8 characters", met: value.length >= 8 },
    { label: "At least one uppercase letter", met: /[A-Z]/.test(value) },
    { label: "At least one lowercase letter", met: /[a-z]/.test(value) },
    { label: "At least one number", met: /[0-9]/.test(value) },
    { label: "At least one special character", met: /[^A-Za-z0-9]/.test(value) },
  ];

  const score = requirements.filter((r) => r.met).length;

  const strengthColor = () => {
    switch (score) {
      case 0:
      case 1:
        return "bg-rose-500";
      case 2:
      case 3:
        return "bg-amber-500";
      case 4:
        return "bg-emerald-500";
      case 5:
        return "bg-teal-400 shadow-[0_0_8px_rgba(45,212,191,0.4)]";
      default:
        return "bg-zinc-800";
    }
  };

  const strengthLabel = () => {
    switch (score) {
      case 0:
        return "Very Weak";
      case 1:
        return "Weak";
      case 2:
        return "Fair";
      case 3:
        return "Good";
      case 4:
        return "Strong";
      case 5:
        return "Excellent & Secure";
      default:
        return "None";
    }
  };

  return (
    <div className="space-y-3.5 mt-2.5">
      {/* Strength indicator bar */}
      <div className="space-y-1">
        <div className="flex justify-between items-center text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          <span>Password Strength</span>
          <span className={score >= 4 ? "text-emerald-400" : score >= 2 ? "text-amber-400" : "text-rose-400"}>
            {strengthLabel()}
          </span>
        </div>
        <div className="flex gap-1 h-1.5 w-full bg-zinc-800/60 rounded-full overflow-hidden">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className={`h-full flex-1 rounded-full transition-all duration-300 ${
                i < score ? strengthColor() : "bg-zinc-800"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Requirements checklist */}
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
        {requirements.map((req, idx) => (
          <li key={idx} className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span
              className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border transition-all ${
                req.met
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                  : "bg-zinc-900 border-border/40 text-muted-foreground/40"
              }`}
            >
              {req.met ? <Check className="h-2.5 w-2.5" /> : <X className="h-2 w-2" />}
            </span>
            <span className={req.met ? "text-zinc-300" : "text-muted-foreground"}>{req.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
