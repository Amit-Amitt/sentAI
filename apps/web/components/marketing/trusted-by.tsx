"use client";

export function TrustedBy() {
  const companies = [
    "Vercel", "Stripe", "Datadog", "PagerDuty", "Cloudflare",
    "HashiCorp", "Grafana", "Elastic", "Confluent", "MongoDB",
  ];

  return (
    <section className="relative border-y border-border/30 py-12 overflow-hidden">
      <div className="mx-auto max-w-7xl px-6">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-muted-foreground/60 mb-8">
          Trusted by engineering teams at
        </p>
      </div>
      <div className="relative">
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-background to-transparent z-10" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-background to-transparent z-10" />
        <div className="flex animate-marquee">
          {[...companies, ...companies].map((name, i) => (
            <div key={`${name}-${i}`} className="flex items-center justify-center px-10 shrink-0">
              <span className="text-lg font-bold text-muted-foreground/30 hover:text-muted-foreground/60 transition whitespace-nowrap">
                {name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
