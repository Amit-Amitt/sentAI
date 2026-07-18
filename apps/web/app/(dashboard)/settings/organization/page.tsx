"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Building2, Globe, MapPin, Clock, Save, Loader2 } from "lucide-react";
import { useOrgStore } from "@/lib/store/org-store";
import { useUpdateOrganization } from "@/lib/api/hooks";

const industries = [
  "Technology",
  "Finance",
  "Healthcare",
  "E-Commerce",
  "Education",
  "Media",
  "Manufacturing",
  "SaaS",
  "Other",
];

const regions = [
  "North America",
  "Europe",
  "Asia Pacific",
  "Latin America",
  "Middle East",
  "Africa",
];

const timezones = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Berlin",
  "Europe/Paris",
  "Asia/Tokyo",
  "Asia/Shanghai",
  "Asia/Kolkata",
  "Australia/Sydney",
];

export default function OrganizationSettingsPage() {
  const { activeOrganization, setActiveOrganization, setOrganizations, organizations } =
    useOrgStore();
  const updateOrg = useUpdateOrganization();

  const [form, setForm] = useState({
    name: "",
    industry: "",
    region: "",
    timezone: "UTC",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (activeOrganization) {
      setForm({
        name: activeOrganization.name || "",
        industry: activeOrganization.industry || "",
        region: activeOrganization.region || "",
        timezone: activeOrganization.timezone || "UTC",
      });
    }
  }, [activeOrganization]);

  const handleSave = async () => {
    if (!activeOrganization) return;
    try {
      const updated = await updateOrg.mutateAsync({
        orgId: activeOrganization.id,
        payload: {
          name: form.name || undefined,
          industry: form.industry || undefined,
          region: form.region || undefined,
          timezone: form.timezone || undefined,
        },
      });
      // Update store
      setActiveOrganization(updated);
      setOrganizations(
        organizations.map((o) => (o.id === updated.id ? updated : o))
      );
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error("Failed to update organization:", err);
    }
  };

  if (!activeOrganization) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-muted-foreground">
          No organization selected. Create one to get started.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-2xl"
    >
      {/* Logo Upload Area */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6">
        <div className="flex items-center gap-6">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 border border-primary/20">
            <span className="text-3xl font-bold text-primary">
              {activeOrganization.name?.charAt(0)?.toUpperCase() || "O"}
            </span>
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">
              Organization Logo
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Logo upload will be available in a future update.
            </p>
          </div>
        </div>
      </div>

      {/* Company Name */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <Building2 className="h-4 w-4 text-primary" />
          Company Name
        </div>
        <input
          id="org-name-input"
          type="text"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition"
          placeholder="Organization name"
        />
      </div>

      {/* Industry */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <Globe className="h-4 w-4 text-primary" />
          Industry
        </div>
        <select
          id="org-industry-select"
          value={form.industry}
          onChange={(e) => setForm({ ...form, industry: e.target.value })}
          className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition appearance-none cursor-pointer"
        >
          <option value="">Select industry</option>
          {industries.map((ind) => (
            <option key={ind} value={ind}>
              {ind}
            </option>
          ))}
        </select>
      </div>

      {/* Region */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <MapPin className="h-4 w-4 text-primary" />
          Region
        </div>
        <select
          id="org-region-select"
          value={form.region}
          onChange={(e) => setForm({ ...form, region: e.target.value })}
          className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition appearance-none cursor-pointer"
        >
          <option value="">Select region</option>
          {regions.map((reg) => (
            <option key={reg} value={reg}>
              {reg}
            </option>
          ))}
        </select>
      </div>

      {/* Timezone */}
      <div className="rounded-2xl border border-border/60 bg-card/50 p-6 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <Clock className="h-4 w-4 text-primary" />
          Timezone
        </div>
        <select
          id="org-timezone-select"
          value={form.timezone}
          onChange={(e) => setForm({ ...form, timezone: e.target.value })}
          className="w-full rounded-xl border border-border/60 bg-background/50 px-4 py-2.5 text-sm text-foreground outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition appearance-none cursor-pointer"
        >
          {timezones.map((tz) => (
            <option key={tz} value={tz}>
              {tz}
            </option>
          ))}
        </select>
      </div>

      {/* Save Button */}
      <div className="flex items-center gap-3 pt-2">
        <button
          id="org-save-button"
          onClick={handleSave}
          disabled={updateOrg.isPending}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90 disabled:opacity-50"
        >
          {updateOrg.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          Save Changes
        </button>
        {saved && (
          <motion.span
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-xs font-medium text-emerald-400"
          >
            ✓ Saved successfully
          </motion.span>
        )}
      </div>
    </motion.div>
  );
}
