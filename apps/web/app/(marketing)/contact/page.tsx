"use client";

import { useState } from "react";
import { Mail, MapPin, Phone, Send } from "lucide-react";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  return (
    <section className="py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <div className="text-center mb-16">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Contact</p>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
            Get in touch
          </h1>
          <p className="mt-4 text-muted-foreground">Have questions? We&apos;d love to hear from you.</p>
        </div>

        <div className="grid gap-12 lg:grid-cols-5">
          {/* Contact Info */}
          <div className="lg:col-span-2 space-y-8">
            <div className="space-y-6">
              {[
                { icon: Mail, label: "Email", value: "hello@sentinel-ai.dev" },
                { icon: MapPin, label: "Office", value: "San Francisco, CA" },
                { icon: Phone, label: "Phone", value: "+1 (555) 123-4567" },
              ].map(c => (
                <div key={c.label} className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 border border-primary/10">
                    <c.icon className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{c.label}</p>
                    <p className="text-sm text-muted-foreground">{c.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Form */}
          <div className="lg:col-span-3">
            {submitted ? (
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-12 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 mb-4">
                  <Send className="h-7 w-7 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold">Message sent!</h3>
                <p className="text-sm text-muted-foreground mt-2">We&apos;ll get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-5">
                <div className="grid gap-5 sm:grid-cols-2">
                  <div>
                    <label htmlFor="name" className="block text-xs font-semibold text-foreground mb-1.5">Name</label>
                    <input id="name" required className="w-full rounded-xl border border-border/60 bg-muted/20 px-4 py-2.5 text-sm outline-none focus:border-primary transition" />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-xs font-semibold text-foreground mb-1.5">Email</label>
                    <input id="email" type="email" required className="w-full rounded-xl border border-border/60 bg-muted/20 px-4 py-2.5 text-sm outline-none focus:border-primary transition" />
                  </div>
                </div>
                <div>
                  <label htmlFor="company" className="block text-xs font-semibold text-foreground mb-1.5">Company</label>
                  <input id="company" className="w-full rounded-xl border border-border/60 bg-muted/20 px-4 py-2.5 text-sm outline-none focus:border-primary transition" />
                </div>
                <div>
                  <label htmlFor="message" className="block text-xs font-semibold text-foreground mb-1.5">Message</label>
                  <textarea id="message" rows={5} required className="w-full rounded-xl border border-border/60 bg-muted/20 px-4 py-2.5 text-sm outline-none focus:border-primary transition resize-none" />
                </div>
                <button type="submit" className="flex items-center gap-2 rounded-xl bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 hover:bg-primary/90 transition">
                  <Send className="h-4 w-4" /> Send Message
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
