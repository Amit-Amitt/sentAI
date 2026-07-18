# Sentinel AI

Sentinel AI is an autonomous incident response platform that monitors real applications, detects production issues automatically, correlates telemetry across logs, metrics, traces, and deployments, and generates root-cause analysis, remediation guidance, and GitHub draft pull requests.

It is built as a Turborepo monorepo with a real multi-agent AI workflow, enterprise integrations, and production deployment support.

## What Sentinel AI does

Sentinel AI helps engineering teams:

* Detect incidents automatically from real telemetry
* Correlate logs, metrics, traces, deployments, and Kubernetes events
* Run a multi-agent LangGraph investigation workflow
* Identify likely root causes with confidence scoring
* Suggest safe remediations and rollback plans
* Generate incident reports and executive summaries
* Create draft GitHub pull requests for fixes
* Store incident memory for faster future investigations
* Send notifications through collaboration channels
* Support multi-tenant SaaS billing and enterprise access control

## Key features

* Multi-agent incident investigation
* Real telemetry ingestion pipeline
* Monitoring SDK for Node.js applications
* OpenTelemetry support
* GitHub deployment intelligence
* Kubernetes and Docker runtime intelligence
* Prometheus, Loki, Grafana, Tempo, and Jaeger integrations
* AI auto-remediation and GitHub PR automation
* AI memory and historical incident retrieval
* Enterprise notifications and on-call workflows
* Multi-tenant organizations, workspaces, RBAC, and billing
* Production deployment and scalability support
* Hackathon-friendly demo and incident replay experience

## Architecture overview

Sentinel AI is organized as a production SaaS platform with the following core layers:

1. **Application Monitoring Layer**
   SDKs and telemetry collectors send logs, metrics, traces, and events from real applications.

2. **Telemetry Ingestion Layer**
   A secure backend receives telemetry, validates it, normalizes it, and forwards it to detection and streaming systems.

3. **Incident Detection Layer**
   Rule-based and anomaly-based detection creates incidents automatically when abnormal behavior is observed.

4. **AI Orchestration Layer**
   LangGraph coordinates specialized agents for logs, metrics, deployments, root cause analysis, remediation, and reporting.

5. **Memory and Correlation Layer**
   Historical incidents, similar fixes, and deployment context are stored and reused to improve investigation quality.

6. **Remediation and GitHub Layer**
   Safe fixes are suggested, validated, and prepared as draft pull requests when appropriate.

7. **Experience Layer**
   The dashboard shows live investigations, timelines, confidence, evidence, and executive summaries.

## Monorepo structure

* `apps/web` — Next.js frontend
* `apps/api` — backend services and APIs
* `packages/ui` — shared UI components
* `packages/types` — shared types
* `packages/prompts` — AI prompt definitions
* `packages/shared` — reusable utilities
* `deploy/helm/sentinel-ai` — Helm chart for production deployment
* `docs` — design docs, architecture, and guides
* `scripts` — helper scripts for local and production workflows

## Tech stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui
* Framer Motion
* Recharts

### Backend

* FastAPI
* Python
* PostgreSQL
* Prisma where applicable
* Redis for queueing and streaming

### AI and automation

* LangGraph
* OpenAI / GPT
* Gemini
* GitHub API

### Observability and infrastructure

* OpenTelemetry
* Prometheus
* Loki
* Grafana
* Tempo
* Jaeger
* Kubernetes
* Docker
* Helm

## Getting started

### Prerequisites

* Bun
* Docker and Docker Compose
* PostgreSQL
* Redis
* OpenAI API key or Gemini API key

### Install dependencies

```bash
bun install
```

### Configure environment variables

Copy the example environment file and fill in the required values:

```bash
cp .env.example .env
```

If you are running production-style integrations, also review:

* `.env.production.example`
* `apps/api/.env.example` if present
* `apps/web/.env.example` if present

### Start local services

```bash
docker compose up -d
```

### Run the development environment

```bash
bun run dev
```

Or run the monorepo tasks with Turbo directly:

```bash
bunx turbo dev
```

## Environment setup

At minimum, configure:

* PostgreSQL connection string
* Redis connection string
* OpenAI or Gemini API key
* GitHub integration secrets if using deployment intelligence
* Any observability URLs or tokens used by the dashboard and ingestion pipeline

See `.env.example` for the full list.

## Build

```bash
bun run build
```

Or:

```bash
bunx turbo build
```

## Lint

```bash
bun run lint
```

Or:

```bash
bunx turbo lint
```

## Test

```bash
bun run test
```

Or:

```bash
bunx turbo test
```

## Type check

```bash
bun run typecheck
```

Or:

```bash
bunx turbo typecheck
```

## Production deployment

Sentinel AI is designed to deploy with:

* Frontend on Vercel or equivalent
* Backend on a container platform such as Railway, Render, Fly.io, or Kubernetes
* PostgreSQL on Neon or production Postgres
* Redis on Upstash or production Redis
* Helm / Kubernetes for enterprise deployments

See the deployment docs in `docs/` and the Helm chart under `deploy/helm/sentinel-ai`.

## Demo workflow

A typical judge demo looks like this:

1. Open Sentinel AI
2. Connect a sample project or monitored application
3. Trigger a live incident
4. Watch telemetry arrive
5. See agents investigate the issue
6. Review the root cause and confidence
7. Inspect the remediation plan
8. View the GitHub draft PR
9. Read the incident report and executive summary

## What makes Sentinel AI different

Most tools stop at dashboards and alerts. Sentinel AI continues into investigation, memory, remediation, and engineering handoff.

It is designed to behave like an autonomous incident commander, not just a passive monitoring UI.

## Roadmap

* Deeper OpenTelemetry support
* More native observability integrations
* Stronger remediation workflows
* Expanded enterprise IAM
* Better incident replay and postmortems
* Additional SDK support for more runtimes

## Project status

Sentinel AI is actively being built as a production-grade hackathon submission and future SaaS platform.

## License

MIT

## Acknowledgements

Built with Bun, Turborepo, Next.js, FastAPI, LangGraph, GitHub, and modern observability tooling.
