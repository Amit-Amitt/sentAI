"use client";

import { useState } from "react";
import { useAuth } from "@/lib/providers/auth-provider";
import { PasswordStrengthMeter } from "@/components/ui/password-strength-meter";
import { motion, AnimatePresence } from "framer-motion";
import {
  Key,
  ShieldCheck,
  Smartphone,
  Fingerprint,
  Mail,
  Chrome,
  Github,
  Terminal,
  Trash2,
  Lock,
  History,
  AlertTriangle,
  Clipboard,
  Check,
  Save,
  Loader2,
  Bell,
  Eye,
  EyeOff,
} from "lucide-react";

export default function SecurityPage() {
  const { user, sessions, updateSecurity, revokeSession } = useAuth();

  // Password fields
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [passLoading, setPassLoading] = useState(false);
  const [passMessage, setPassMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Recovery codes
  const [showRecoveryCodes, setShowRecoveryCodes] = useState(false);
  const [copiedCodes, setCopiedCodes] = useState(false);
  const mockRecoveryCodes = ["SENT-7F2A-89E1", "SENT-10BC-49D2", "SENT-9E28-FF3A", "SENT-3351-AA88", "SENT-552E-E99A"];

  // Connected OAuth simulation
  const [oauthState, setOauthState] = useState(
    user?.oauthConnected || { google: false, github: false, microsoft: false }
  );

  // Notification preferences
  const [notifSecurity, setNotifSecurity] = useState(true);
  const [notifCritical, setNotifCritical] = useState(true);
  const [notifWeekly, setNotifWeekly] = useState(false);

  // Danger Zone
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [deleting, setDeleting] = useState(false);

  // Password update handler
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setPassMessage(null);

    if (newPassword !== confirmPassword) {
      setPassMessage({ type: "error", text: "New passwords do not match." });
      return;
    }

    if (newPassword.length < 8) {
      setPassMessage({ type: "error", text: "Password must be at least 8 characters." });
      return;
    }

    setPassLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    setPassLoading(false);
    setPassMessage({ type: "success", text: "Your password has been updated." });
    setOldPassword("");
    setNewPassword("");
    setConfirmPassword("");
  };

  // Toggle MFA features
  const handleSecurityToggle = (key: "twoFactorEnabled" | "passkeysEnabled" | "magicLinksEnabled") => {
    if (!user) return;
    const currentVal = !!user[key];
    updateSecurity({ [key]: !currentVal });
    
    // Auto show recovery codes if enabling 2FA
    if (key === "twoFactorEnabled" && !currentVal) {
      setShowRecoveryCodes(true);
    }
  };

  // Toggle OAuth provider
  const handleOAuthToggle = (provider: "google" | "github" | "microsoft") => {
    const updated = { ...oauthState, [provider]: !oauthState[provider] };
    setOauthState(updated);
    updateSecurity({ oauthConnected: updated });
  };

  // Copy recovery codes
  const copyCodesToClipboard = () => {
    navigator.clipboard.writeText(mockRecoveryCodes.join("\n"));
    setCopiedCodes(true);
    setTimeout(() => setCopiedCodes(false), 2000);
  };

  // Account deletion handler
  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== "DELETE") return;
    setDeleting(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setDeleting(false);
    setShowDeleteModal(false);
    // Logout and redirect
    window.location.href = "/login";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8 max-w-3xl pb-16"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Security & Account Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage system passwords, active logins, connected integrations, and factor settings.
        </p>
      </div>

      {/* Change Password Card */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Key className="h-4.5 w-4.5 text-primary" /> Update Credentials
        </h2>

        {passMessage && (
          <div
            className={`rounded-xl border p-3 text-xs flex items-center gap-2 ${
              passMessage.type === "success"
                ? "border-emerald-500/20 bg-emerald-500/5 text-emerald-400"
                : "border-rose-500/20 bg-rose-500/5 text-rose-400"
            }`}
          >
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <p>{passMessage.text}</p>
          </div>
        )}

        <form onSubmit={handlePasswordUpdate} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Current Password
            </label>
            <input
              id="security-old-password"
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              className="w-full max-w-md rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              New Password
            </label>
            <div className="relative max-w-md">
              <input
                id="security-new-password"
                type={showPass ? "text" : "password"}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background/50 pl-4 pr-10 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition"
              >
                {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {newPassword && (
              <div className="max-w-md">
                <PasswordStrengthMeter value={newPassword} />
              </div>
            )}
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              Confirm New Password
            </label>
            <input
              id="security-confirm-password"
              type={showPass ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full max-w-md rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
              required
            />
          </div>

          <button
            id="password-save-btn"
            type="submit"
            disabled={passLoading || !newPassword || !oldPassword}
            className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition shadow-lg shadow-primary/10"
          >
            {passLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            <span>Save Password</span>
          </button>
        </form>
      </div>

      {/* Advanced Security Factors */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <ShieldCheck className="h-4.5 w-4.5 text-primary" /> Advanced Security Factors
        </h2>
        <p className="text-xs text-muted-foreground">
          Double-secure SRE incident feeds with biometric factors and recovery tools.
        </p>

        <div className="space-y-3.5 pt-2">
          {/* 2FA Toggle */}
          <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/50 bg-background/30 hover:bg-background/50 transition">
            <div className="flex gap-3 items-center">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-900 border border-border/40 text-muted-foreground">
                <Smartphone className="h-4.5 w-4.5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-foreground">Two-Factor Authentication (2FA)</p>
                <p className="text-[10px] text-muted-foreground">Require an OTP from Google/Microsoft Authenticator.</p>
              </div>
            </div>
            <button
              onClick={() => handleSecurityToggle("twoFactorEnabled")}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                user?.twoFactorEnabled ? "bg-primary" : "bg-zinc-800"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  user?.twoFactorEnabled ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          {/* Passkeys Toggle */}
          <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/50 bg-background/30 hover:bg-background/50 transition">
            <div className="flex gap-3 items-center">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-900 border border-border/40 text-muted-foreground">
                <Fingerprint className="h-4.5 w-4.5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-foreground">Passkeys & Biometrics</p>
                <p className="text-[10px] text-muted-foreground">Sign in securely using Apple TouchID / Windows Hello.</p>
              </div>
            </div>
            <button
              onClick={() => handleSecurityToggle("passkeysEnabled")}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                user?.passkeysEnabled ? "bg-primary" : "bg-zinc-800"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  user?.passkeysEnabled ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          {/* Magic Links Toggle */}
          <div className="flex items-center justify-between p-3.5 rounded-xl border border-border/50 bg-background/30 hover:bg-background/50 transition">
            <div className="flex gap-3 items-center">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-900 border border-border/40 text-muted-foreground">
                <Mail className="h-4.5 w-4.5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-foreground">Passwordless Magic Links</p>
                <p className="text-[10px] text-muted-foreground">Request one-time login links directly to your inbox.</p>
              </div>
            </div>
            <button
              onClick={() => handleSecurityToggle("magicLinksEnabled")}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                user?.magicLinksEnabled ? "bg-primary" : "bg-zinc-800"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  user?.magicLinksEnabled ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Recovery codes display */}
        {showRecoveryCodes && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="rounded-xl border border-border/60 bg-background/50 p-4 space-y-3 mt-4"
          >
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold text-foreground">Emergency Recovery Codes</span>
              <button
                onClick={copyCodesToClipboard}
                className="inline-flex items-center gap-1 text-[10px] font-semibold text-primary hover:underline"
              >
                {copiedCodes ? <Check className="h-3 w-3" /> : <Clipboard className="h-3 w-3" />}
                {copiedCodes ? "Copied" : "Copy Codes"}
              </button>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] text-zinc-300">
              {mockRecoveryCodes.map((code) => (
                <div key={code} className="bg-zinc-900 border border-border/30 rounded-lg p-2 text-center">
                  {code}
                </div>
              ))}
            </div>
            <p className="text-[9px] text-muted-foreground leading-normal">
              Store these codes safely. They can bypass 2FA checkups to recover your incident console.
            </p>
          </motion.div>
        )}
      </div>

      {/* Connected Accounts */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Terminal className="h-4.5 w-4.5 text-primary" /> Identity Provider Links
        </h2>
        <p className="text-xs text-muted-foreground">
          Sign in faster by linking social authentication providers.
        </p>

        <div className="grid grid-cols-3 gap-3 pt-2">
          {[
            { id: "github", label: "GitHub", icon: Github },
            { id: "google", label: "Google", icon: Chrome },
            { id: "microsoft", label: "Microsoft", icon: Terminal },
          ].map((prov) => {
            const Icon = prov.icon;
            const isConnected = (oauthState as any)[prov.id];
            return (
              <button
                key={prov.id}
                type="button"
                onClick={() => handleOAuthToggle(prov.id as any)}
                className={`rounded-xl border p-4 text-center transition flex flex-col items-center justify-center gap-2 ${
                  isConnected
                    ? "border-emerald-500/30 bg-emerald-500/5 text-foreground"
                    : "border-border/50 bg-background/40 text-muted-foreground hover:text-foreground"
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-[11px] font-bold">{prov.label}</span>
                <span className={`text-[9px] uppercase font-bold tracking-wider ${isConnected ? "text-emerald-400" : "text-muted-foreground/60"}`}>
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Session Management */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Lock className="h-4.5 w-4.5 text-primary" /> Session Controller
        </h2>
        <p className="text-xs text-muted-foreground">
          Inspect and revoke active login tokens assigned to SRE devices.
        </p>

        <div className="space-y-3 pt-2">
          {sessions.map((sess) => (
            <div
              key={sess.id}
              className="flex justify-between items-center p-3.5 border border-border/40 rounded-xl bg-background/40 hover:bg-background/60 transition"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-foreground">{sess.device}</span>
                  {sess.active ? (
                    <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-semibold text-emerald-400 border border-emerald-500/20">
                      CURRENT SESSION
                    </span>
                  ) : (
                    <span className="text-[9px] text-muted-foreground font-mono">{sess.lastActive}</span>
                  )}
                </div>
                <div className="flex gap-2 text-[10px] text-muted-foreground">
                  <span>Browser: <strong className="text-zinc-400">{sess.browser}</strong></span>
                  <span>•</span>
                  <span>IP: <strong className="text-zinc-400">{sess.ipAddress}</strong></span>
                  <span>•</span>
                  <span>Location: <strong className="text-zinc-400">{sess.location}</strong></span>
                </div>
              </div>
              
              {!sess.active && (
                <button
                  onClick={() => revokeSession(sess.id)}
                  className="rounded-lg border border-rose-500/20 bg-rose-500/5 px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-rose-400 hover:bg-rose-500/10 transition"
                >
                  Revoke
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Login History */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <History className="h-4.5 w-4.5 text-primary" /> Login History Log
        </h2>
        <div className="rounded-xl border border-border/40 bg-zinc-950/40 overflow-hidden text-xs">
          <div className="grid grid-cols-3 bg-muted/20 px-4 py-2 border-b border-border/40 font-bold text-muted-foreground text-[10px] uppercase tracking-wider">
            <span>Timestamp</span>
            <span>Device / IP</span>
            <span className="text-right">Action</span>
          </div>
          <div className="divide-y divide-border/40 font-mono text-[11px] text-zinc-300">
            <div className="grid grid-cols-3 px-4 py-2.5">
              <span>2026-07-18 11:53</span>
              <span>Linux (Chrome) / 192.168.1.45</span>
              <span className="text-emerald-400 text-right font-semibold">Success Login</span>
            </div>
            <div className="grid grid-cols-3 px-4 py-2.5">
              <span>2026-07-17 18:24</span>
              <span>iPhone 15 (Safari) / 103.241.12.89</span>
              <span className="text-emerald-400 text-right font-semibold">Success Login</span>
            </div>
            <div className="grid grid-cols-3 px-4 py-2.5">
              <span>2026-07-16 09:12</span>
              <span>Linux (Chrome) / 192.168.1.45</span>
              <span className="text-rose-400 text-right font-semibold">Failed Attempt</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Alerts and Notifications */}
      <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Bell className="h-4.5 w-4.5 text-primary" /> Incident Notification Preferences
        </h2>
        <p className="text-xs text-muted-foreground">
          Configure security alert emails and login push notifications.
        </p>

        <div className="space-y-2 pt-2">
          <label className="flex items-center gap-3 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={notifSecurity}
              onChange={(e) => setNotifSecurity(e.target.checked)}
              className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary/20 accent-primary"
            />
            <span>Email alerts for new session logins and password changes (High Priority)</span>
          </label>

          <label className="flex items-center gap-3 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={notifCritical}
              onChange={(e) => setNotifCritical(e.target.checked)}
              className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary/20 accent-primary"
            />
            <span>SMS/Slack notifications for Critical (SEV1) anomalies and deadlocks</span>
          </label>

          <label className="flex items-center gap-3 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={notifWeekly}
              onChange={(e) => setNotifWeekly(e.target.checked)}
              className="h-4 w-4 rounded border-border bg-background text-primary focus:ring-primary/20 accent-primary"
            />
            <span>Weekly executive incident MTTR report digest</span>
          </label>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="rounded-2xl border border-rose-500/25 bg-rose-500/5 p-6 space-y-4 backdrop-blur-xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
          <AlertTriangle className="h-4.5 w-4.5" /> Danger Zone
        </h2>
        <p className="text-xs text-rose-400/80">
          Permanently delete your Sentinel commander profile and revoke all agent connections. This cannot be undone.
        </p>
        <div>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="inline-flex items-center gap-1.5 rounded-xl bg-rose-500 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-600 transition shadow-lg shadow-rose-500/10"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete Account</span>
          </button>
        </div>
      </div>

      {/* Delete Account Modal Dialog */}
      <AnimatePresence>
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowDeleteModal(false)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            />
            
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative w-full max-w-md rounded-2xl border border-rose-500/30 bg-zinc-950 p-6 space-y-5 shadow-2xl"
            >
              <div className="space-y-2 text-center">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <h3 className="text-base font-bold">Permanently Delete Account?</h3>
                <p className="text-xs text-muted-foreground leading-normal">
                  All your active workspaces, incident log archives, and agent rules will be immediately destroyed.
                </p>
              </div>

              <div className="space-y-2.5">
                <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground text-center">
                  Type <strong className="text-rose-400 font-mono">DELETE</strong> below to confirm:
                </label>
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  className="w-full rounded-xl border border-rose-500/20 bg-background/50 px-4 py-2 text-sm text-center font-bold tracking-widest outline-none focus:border-rose-500/50 transition uppercase"
                  placeholder="DELETE"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="flex-1 rounded-xl border border-border px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted/20 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={deleteConfirmText !== "DELETE" || deleting}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl bg-rose-500 px-4 py-2.5 text-xs font-semibold text-white hover:bg-rose-600 disabled:opacity-40 transition shadow-lg shadow-rose-500/15"
                >
                  {deleting ? <Loader2 className="h-4.5 w-4.5 animate-spin" /> : <Trash2 className="h-4.5 w-4.5" />}
                  <span>Delete Profile</span>
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
