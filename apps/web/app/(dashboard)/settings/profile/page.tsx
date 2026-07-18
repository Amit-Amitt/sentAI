"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/providers/auth-provider";
import { useTheme } from "next-themes";
import { motion } from "framer-motion";
import { User, Save, Upload, Check, Loader2, Sparkles, Globe, Clock, Shield } from "lucide-react";

const AVATAR_OPTIONS = [
  { id: "cyber_commander", name: "Cyber Commander", url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=150&q=80" },
  { id: "log_agent", name: "Log Scanner Agent", url: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=150&q=80" },
  { id: "root_cause_agent", name: "Root Cause Analyzer", url: "https://images.unsplash.com/photo-1614741118887-7a4ee193a5fa?auto=format&fit=crop&w=150&q=80" },
  { id: "security_agent", name: "Net Sentry", url: "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?auto=format&fit=crop&w=150&q=80" },
];

const TIMEZONES = [
  "UTC (Coordinated Universal Time)",
  "Asia/Kolkata (IST)",
  "America/New_York (EST)",
  "America/Los_Angeles (PST)",
  "Europe/London (GMT)",
  "Europe/Paris (CET)",
  "Asia/Tokyo (JST)",
];

const LANGUAGES = [
  { code: "en", name: "English (US)" },
  { code: "es", name: "Español (Spanish)" },
  { code: "de", name: "Deutsch (German)" },
  { code: "fr", name: "Français (French)" },
  { code: "ja", name: "日本語 (Japanese)" },
];

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const { theme, setTheme } = useTheme();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [timezone, setTimezone] = useState("");
  const [language, setLanguage] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState("");
  
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setFirstName(user.firstName || "");
      setLastName(user.lastName || "");
      setEmail(user.email || "");
      setCompanyName(user.companyName || "");
      setTimezone(user.timezone || "Asia/Kolkata");
      setLanguage(user.language || "en");
      setSelectedAvatar(user.avatarUrl || AVATAR_OPTIONS[0]?.url || "");
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 600));

    updateProfile({
      firstName,
      lastName,
      email,
      companyName,
      timezone,
      language,
      avatarUrl: selectedAvatar,
    });

    setLoading(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleAvatarSelect = (url: string) => {
    setSelectedAvatar(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-3xl"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Customize your commander details, avatar, regional formats, and UI theme.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        
        {/* Avatar Select Section */}
        <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <User className="h-4 w-4 text-primary" /> Incident Commander Avatar
          </h2>
          <div className="flex flex-col sm:flex-row gap-5 items-center">
            {/* Display active avatar */}
            <div className="relative group">
              <div className="absolute inset-0 bg-primary/20 blur-[15px] rounded-full opacity-60" />
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                suppressHydrationWarning
                src={selectedAvatar}
                alt="Avatar Preview"
                className="relative h-20 w-20 rounded-2xl object-cover border border-border/80"
              />
            </div>
            {/* Grid options */}
            <div className="space-y-2 text-center sm:text-left">
              <p className="text-xs text-muted-foreground">Select an AI Agent model representing your role:</p>
              <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
                {AVATAR_OPTIONS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => handleAvatarSelect(opt.url)}
                    className={`relative rounded-xl overflow-hidden border p-1 transition-all ${
                      selectedAvatar === opt.url
                        ? "border-primary bg-primary/10 shadow-[0_0_8px_rgba(239,68,68,0.2)]"
                        : "border-border/60 hover:border-border/80 bg-background/40"
                    }`}
                    title={opt.name}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={opt.url} alt={opt.name} className="h-10 w-10 rounded-lg object-cover" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Basic Information */}
        <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" /> Identity Details
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                First Name
              </label>
              <input
                id="profile-first-name"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                Last Name
              </label>
              <input
                id="profile-last-name"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                Work Email
              </label>
              <input
                id="profile-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                Company Name
              </label>
              <input
                id="profile-company"
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm outline-none focus:border-primary/50 transition"
                required
              />
            </div>
          </div>
        </div>

        {/* Regional & UI Settings */}
        <div className="rounded-2xl border border-border/60 bg-card/45 p-6 space-y-4 backdrop-blur-xl">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <Globe className="h-4 w-4 text-primary" /> Regional & Theme Config
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" /> Timezone
              </label>
              <select
                id="profile-timezone"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background px-3 py-2.5 text-sm outline-none cursor-pointer"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>
            
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
                <Globe className="h-3 w-3" /> Language
              </label>
              <select
                id="profile-language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-xl border border-border/60 bg-background px-3 py-2.5 text-sm outline-none cursor-pointer"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>{lang.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
              <Shield className="h-3 w-3" /> UI Theme Preference
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: "dark", label: "Midnight Dark" },
                { id: "light", label: "Sleek Light" },
                { id: "system", label: "OS Default" },
              ].map((th) => (
                <button
                  key={th.id}
                  type="button"
                  onClick={() => {
                    setTheme(th.id);
                  }}
                  className={`rounded-xl border p-3 text-center transition ${
                    theme === th.id
                      ? "border-primary bg-primary/5 text-foreground font-bold shadow-[0_0_8px_rgba(239,68,68,0.1)]"
                      : "border-border/50 bg-background/40 hover:border-border text-muted-foreground"
                  }`}
                >
                  <p className="text-xs">{th.label}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center gap-3">
          <button
            id="profile-save"
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            <span>Save Profile</span>
          </button>
          {saved && (
            <motion.span
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-xs font-semibold text-emerald-400 flex items-center gap-1"
            >
              <Check className="h-3.5 w-3.5" /> Saved successfully
            </motion.span>
          )}
        </div>

      </form>
    </motion.div>
  );
}
