# Sentinel AI

Autonomous AI Incident Commander

Document status: Source of truth for product scope, system architecture, and implementation direction for the Sentinel AI hackathon project.

Repository context: The current repository is a Turbo monorepo starter with `apps/web`, `apps/docs`, and shared packages. This document defines the intended end-state architecture for Sentinel AI and should guide all implementation work from this point onward.

Versioning note: The declared frontend target is Next.js 15, even though the starter currently carries a newer Next.js template dependency. Implementation should align the repo to this specification or consciously revise the spec and code together. This document is the authority.

## 1. Project Vision

Sentinel AI is an incident intelligence platform that acts as an autonomous first responder for engineering teams. Its purpose is not to replace on-call engineers or incident commanders. Its purpose is to compress the time between “something is wrong” and “we understand why.”

The product vision is to create a system that continuously turns fragmented operational signals into a structured, explainable incident investigation. Instead of showing engineers dozens of dashboards and requiring manual correlation, Sentinel AI should assemble evidence, launch multiple specialist agents in parallel, challenge its own assumptions, and present a ranked root-cause narrative with confidence and recommended next actions.

The long-term company vision is to become the operational reasoning layer that sits above observability, deployment, and customer-signal systems. In that future state, Sentinel AI becomes the place where incidents are understood, not merely detected.

The hackathon version must prove five strategic ideas:

- Specialized AI agents outperform a single generic assistant for incident investigation because each agent can reason over a specific evidence class.
- Deterministic orchestration matters because incident workflows need repeatability, observability, and explicit failure handling.
- Explainability is a product feature, not a compliance afterthought, so every conclusion must cite evidence and disclose uncertainty.
- Great architecture is visible in the product because a clean system produces a cleaner investigation experience.
- A polished operator-facing dashboard materially improves trust in AI systems.

Product principles:

- Evidence before opinion. The system must collect and normalize signals before generating conclusions.
- Human stays in command. The system recommends, ranks, and explains. Engineers approve actions.
- Confidence must be legible. Every major claim requires a confidence score and confidence rationale.
- Specialist agents must collaborate through structured state, not free-form chat alone.
- The MVP should be a bounded monolith with strong internal modularity rather than premature microservices.

## 2. Problem Statement

Modern engineering organizations receive a flood of disconnected operational data during incidents:

- Application logs show symptoms but not business impact.
- Infrastructure metrics show degradation but not causal change.
- Deployment events reveal recent changes but not runtime effects.
- Customer reports reveal pain but arrive without technical context.
- Alerting tools surface thresholds but not narratives.

The operational problem is not lack of data. It is lack of fast, reliable correlation.

Today, engineers often perform root-cause analysis manually under time pressure:

- One engineer opens logs.
- Another checks dashboards.
- Another reviews deployments.
- Someone asks whether customers are impacted.
- The incident commander tries to synthesize a shared understanding from fragmented observations.

This manual process is expensive in four ways:

- It increases mean time to acknowledge because teams must verify whether alerts are real incidents.
- It increases mean time to understand because correlation happens through human memory and Slack conversations.
- It increases cognitive load because responders constantly context-switch across tools.
- It increases organizational risk because incident response quality depends on tribal knowledge and whoever happens to be online.

Sentinel AI addresses the specific gap between detection and diagnosis.

## 3. Why Current Solutions Are Not Enough

Current solutions are helpful, but they typically solve only part of the problem.

Observability platforms are excellent at collecting telemetry, visualizing trends, and alerting on thresholds. They are weaker at producing a coherent, explainable, cross-domain investigation narrative. They answer “what changed in this graph” better than “what is the most probable system-level explanation.”

Incident management tools are good at coordination, escalation, and status tracking. They help teams manage the response process, but they do not perform substantive technical reasoning over evidence.

Runbooks provide procedural knowledge, but they are static artifacts. They do not adapt their recommendations to the exact evidence pattern of the current incident.

Generic AI assistants can summarize logs or interpret screenshots, but they usually lack:

- Structured access to multi-source incident state
- Deterministic orchestration across specialist tasks
- Explicit confidence calibration
- Persistent investigation memory
- Verifiable evidence citation
- Productized operator workflows

Many AI demos fail in production incident settings because they optimize for impressive prose instead of trustworthy operations. Sentinel AI is explicitly designed to avoid this failure mode by making structure, evidence, and agent specialization first-class concerns.

## 4. Target Users

Primary target users for the MVP:

- On-call software engineers responsible for first-response triage
- Site Reliability Engineers responsible for incident investigation and mitigation
- Platform engineers who need rapid correlation across services and deployments
- Incident commanders who need a fast, shared technical narrative

Secondary target users:

- Engineering managers who need visibility into incident status and confidence
- Support and customer operations leads who need impact summaries during live incidents
- Post-incident reviewers who need a concise evidence trail for retrospectives

Ideal initial customer profile:

- SaaS teams operating between 5 and 50 services
- Teams with some observability maturity but fragmented tooling
- Organizations where incidents cross application, infrastructure, and deployment boundaries
- Teams that care about AI assistance but require human oversight and explainability

## 5. User Personas

### Persona A: Priya, the On-Call SRE

Role: Primary responder for production issues.

Goals:

- Identify whether an alert is real within minutes.
- Understand probable cause fast enough to pick a safe mitigation.
- Avoid opening six tools before forming a hypothesis.

Pain points:

- Noisy alerts with little context
- Repetitive manual correlation across logs, metrics, and deploys
- High stress during off-hours incidents

What success looks like:

- Sentinel AI assembles the initial evidence automatically.
- Priya sees the top hypotheses with citations and confidence.
- Priya uses the recommendations as a head start, not as blind automation.

### Persona B: Marcus, the Incident Commander

Role: Coordinates responders, communication, and decisions during high-severity incidents.

Goals:

- Maintain a shared technical understanding across the room.
- Communicate clearly to stakeholders without overclaiming.
- Keep the team focused on the highest-probability path.

Pain points:

- Fragmented updates from multiple engineers
- Conflicting theories with no structured ranking
- Time lost converting technical facts into stakeholder language

What success looks like:

- Sentinel AI maintains a live investigation summary.
- Marcus can point to the evidence graph and agent feed during the call.
- Stakeholder updates reflect confidence and uncertainty honestly.

### Persona C: Elena, the Engineering Manager

Role: Oversees service reliability and team execution.

Goals:

- See incident impact, response quality, and recurring failure patterns.
- Understand whether failures are operational, architectural, or deployment related.
- Use incident outcomes to improve team practices.

Pain points:

- Post-incident knowledge is scattered across Slack threads and dashboards
- Reliability work is difficult to prioritize without clear patterns
- Teams repeat the same triage labor incident after incident

What success looks like:

- Sentinel AI produces a reusable investigation artifact.
- Root-cause categories and recommendations become inputs to engineering planning.

### Persona D: Jordan, the Service Owner

Role: Developer responsible for a particular service implicated in an incident.

Goals:

- Quickly confirm whether the issue is in their service.
- Review code or config-related recommendations with enough context to act.
- Avoid being pulled into incidents without concrete evidence.

Pain points:

- Being paged into ambiguous incidents
- Hunting for the exact deploy or config change that matters
- Receiving generic AI advice with low technical signal

What success looks like:

- Sentinel AI links service ownership, deployment history, and root-cause hypotheses.
- Jordan receives evidence-backed suggestions and clear next actions.

## 6. Primary Use Cases

### Use Case 1: Autonomous First-Response Investigation

A new alert or simulated incident enters the system. Sentinel AI immediately gathers normalized signals, launches specialist agents, and presents the incident commander with a ranked set of hypotheses.

### Use Case 2: Cross-Signal Correlation

The platform correlates logs, metrics, deployment events, and customer-impact signals over a shared time window to identify likely causal relationships.

### Use Case 3: Explainable Root-Cause Analysis

The system produces a root-cause narrative that includes evidence citations, timeline alignment, confidence score, contradictory evidence, and unresolved questions.

### Use Case 4: Corrective Action Recommendation

Once a likely cause is identified, Sentinel AI recommends immediate mitigations, short-term fixes, and long-term prevention steps. Recommendations are scoped by confidence and risk.

### Use Case 5: Live Incident Command Dashboard

Users view a visually rich dashboard that shows incident health, investigation progress, evidence flow, specialist agent findings, and system recommendations in real time.

### Use Case 6: Demo-Ready Incident Simulation

Hackathon judges can trigger a fully controlled incident simulation that reliably generates synthetic signals, kicks off the multi-agent workflow, and reveals the product’s reasoning end to end.

## 7. Functional Requirements

### Incident Lifecycle

- `FR-01 Incident Creation:` The system shall create incidents from the simulator and from a generic ingestion API.
- `FR-02 Incident Severity:` The system shall support severity levels `P1`, `P2`, `P3`, and `P4`.
- `FR-03 Incident Status:` The system shall support statuses `open`, `investigating`, `mitigating`, `monitoring`, `resolved`, and `needs-human-review`.
- `FR-04 Incident Ownership:` Each incident shall belong to an organization, project, and optionally a primary service.
- `FR-05 Incident Timeline:` Every meaningful event in the incident lifecycle shall be recorded as a timestamped timeline entry.
- `FR-06 Manual Control:` A human user shall be able to acknowledge, re-run, and resolve an investigation.

### Signal Ingestion and Normalization

- `FR-07 Signal Types:` The platform shall ingest at minimum logs, metrics anomalies, deployment events, alerts, and customer feedback signals.
- `FR-08 Signal Envelope:` Every signal shall be normalized into a common envelope containing source, service, timestamp, severity, raw payload, and extracted metadata.
- `FR-09 Time Windowing:` Signals shall be retrievable within a configurable investigation window, defaulting to 60 minutes before incident creation through incident resolution.
- `FR-10 Evidence Linking:` Signals shall be transformed into evidence items that can be cited by agents and displayed in the UI.
- `FR-11 Deduplication:` Identical or near-identical signals shall be de-duplicated or clustered to reduce noise.

### Agent Orchestration

- `FR-12 Multi-Agent Launch:` A new investigation shall trigger the Coordinator Agent and then specialist agents in parallel.
- `FR-13 Structured Agent State:` Every agent shall read and write structured state rather than unbounded free-form memory.
- `FR-14 Agent Findings:` Each agent shall output findings, supporting evidence IDs, contradictions, unanswered questions, and confidence.
- `FR-15 Re-Planning:` The Coordinator Agent shall be able to trigger targeted re-analysis when evidence is incomplete or conflicting.
- `FR-16 Failure Tolerance:` A failure in one specialist agent shall not invalidate the entire investigation; the system shall continue in degraded mode.
- `FR-17 Confidence Visibility:` Confidence scores and confidence rationale shall be generated for every major conclusion.

### Root-Cause Analysis

- `FR-18 Ranked Hypotheses:` The Root Cause Agent shall produce multiple ranked hypotheses rather than only one answer.
- `FR-19 Evidence Citation:` Every hypothesis shall cite the evidence items that support it.
- `FR-20 Contradiction Handling:` The system shall explicitly note contradictory evidence when present.
- `FR-21 Abstention:` If evidence is insufficient, the system shall produce `needs-human-review` rather than fabricate certainty.

### Recommendations

- `FR-22 Recommendation Categories:` Recommendations shall be grouped into immediate mitigation, short-term remediation, and long-term prevention.
- `FR-23 Action Safety:` Recommendations shall include estimated risk, reversibility, and prerequisites.
- `FR-24 Runbook Association:` When available, the system shall attach a related runbook or knowledge-base reference.
- `FR-25 Engineering Suggestions:` When the incident is code or configuration related, the system may generate engineering-oriented follow-up suggestions, potentially using Codex, but shall never auto-apply them in the MVP.

### Frontend Dashboard

- `FR-26 Overview Dashboard:` Users shall be able to see active incidents, severity distribution, ongoing investigations, and service health at a glance.
- `FR-27 Incident Detail Workspace:` Users shall be able to inspect a single incident in a command-center view containing evidence, agent activity, hypotheses, and recommendations.
- `FR-28 Live Updates:` The incident view shall update in near real time as agents progress through the workflow.
- `FR-29 Evidence Graph:` Users shall be able to inspect evidence relationships visually through a graph view.
- `FR-30 Investigation Replay:` Users shall be able to replay the incident timeline for demo and retrospective purposes.

### Simulation and Demo Support

- `FR-31 Scenario Library:` The system shall support multiple predefined incident scenarios.
- `FR-32 Deterministic Simulation:` Scenario runs shall be reproducible so the demo is stable.
- `FR-33 Seeded Data:` The simulator shall generate or replay logs, metrics, deployments, and customer signals in a controlled order.
- `FR-34 Demo Narrative:` The UI shall guide judges through what the agents are doing and why it matters.

### Admin and Configuration

- `FR-35 Prompt Versioning:` Prompt templates shall be versioned and traceable per agent run.
- `FR-36 Configurability:` Thresholds such as investigation window, confidence gating, and agent retry budget shall be configurable.
- `FR-37 Auditability:` All major system actions shall be auditable, including investigation start, agent retry, incident resolution, and prompt version used.

## 8. Non-Functional Requirements

- `NFR-01 Performance:` Read-only dashboard APIs should target sub-400 ms p95 latency under demo-scale load. Investigation kickoff should start within 5 seconds of incident creation.
- `NFR-02 Investigation Latency:` The end-to-end simulated investigation should usually complete within 30 to 90 seconds so judges can experience the full loop live.
- `NFR-03 Availability:` The architecture should support stateless horizontal scaling for the frontend and API. The hackathon target is functional resilience rather than enterprise uptime guarantees.
- `NFR-04 Explainability:` No root-cause statement may be shown without evidence citations and a confidence breakdown.
- `NFR-05 Reliability:` Agent failures must be visible, recoverable, and isolated. Silent failures are unacceptable.
- `NFR-06 Maintainability:` Domain contracts, prompts, and agent logic must be modular and versioned so each layer can evolve independently.
- `NFR-07 Observability:` The system must log request IDs, incident IDs, run IDs, agent names, durations, and model usage metrics.
- `NFR-08 Security:` Secrets must remain server-side. Sensitive or user-supplied data must be validated and redacted before model submission where necessary.
- `NFR-09 Accessibility:` The dashboard should target WCAG AA contrast and keyboard navigability for critical actions.
- `NFR-10 Portability:` The project must be deployable via Vercel, Railway, and Neon without requiring custom infrastructure.
- `NFR-11 Cost Awareness:` The system should avoid unnecessary model invocations, repeated context packing, and unbounded token growth.
- `NFR-12 Demo Resilience:` The demo must have a seeded backup scenario and a replayable completed investigation in case live inference degrades.

## 9. System Architecture Overview

Sentinel AI should be implemented as a modular monorepo with three major runtime surfaces:

- A Next.js frontend for the operator dashboard and product presentation
- A FastAPI backend that serves as the control plane and API layer
- A Python worker process that executes LangGraph-based investigations asynchronously

The architecture is intentionally a bounded monolith rather than a mesh of microservices. This is the right trade-off for a hackathon and for an early-stage startup because it minimizes operational overhead while preserving strong internal boundaries.

High-level architecture layers:

### 1. Presentation Layer

The frontend renders incident overview, incident detail, evidence graph, charts, simulation controls, and live agent progress. It is optimized for clarity, responsiveness, and trust.

### 2. API and Control Plane

The FastAPI application exposes incident, evidence, simulation, and agent-run endpoints. It validates input, persists state, exposes read models, and triggers background investigations.

### 3. Investigation Orchestration Layer

The worker executes a LangGraph workflow. It loads incident context, gathers evidence, launches specialist agents, evaluates evidence quality, ranks root causes, and emits recommendations.

### 4. Data Layer

PostgreSQL is the system of record. It stores incidents, normalized signals, evidence, agent runs, findings, hypotheses, recommendations, prompt versions, and audit events.

Optional supporting stores:

- Redis for background job queueing, short-lived caching, rate limiting, and server-sent-event fan-out
- ChromaDB for semantic retrieval over runbooks, historical incidents, and past recommendations

### 5. AI Model Layer

The orchestration layer calls reasoning models through a model gateway abstraction. OpenAI or Gemini can power reasoning steps. Codex is reserved for engineering-oriented remediation suggestions when code or configuration interpretation adds value.

### 6. Deployment Topology

- `apps/web` deploys to Vercel
- `apps/api` deploys to Railway as at least two process types: API and worker
- PostgreSQL lives in Neon
- Redis, if enabled, can be hosted via Railway or a managed Redis provider

Architectural trade-off selection:

- Chosen: bounded monolith with worker separation
- Not chosen: many microservices
- Why: the product’s complexity is in reasoning and workflow state, not service decomposition. Separate deployable services would slow the team down without providing meaningful architectural benefit at MVP scale.

## 10. Complete Folder Structure

The intended end-state repository structure is:

```text
sentAI/
  PROJECT.md
  README.md
  package.json
  turbo.json
  bun.lock
  .gitignore
  apps/
    web/
      app/
        (dashboard)/
          layout.tsx
          page.tsx
          incidents/
            page.tsx
            [incidentId]/
              page.tsx
              loading.tsx
              error.tsx
          simulator/
            page.tsx
          settings/
            integrations/
              page.tsx
            prompts/
              page.tsx
            about/
              page.tsx
        api/
          health/route.ts
        globals.css
        favicon.ico
      components/
        layout/
        incidents/
        evidence/
        agents/
        recommendations/
        charts/
        graph/
        simulator/
        shared/
      lib/
        api/
        formatters/
        constants/
        hooks/
        providers/
      public/
        images/
        icons/
      tests/
        e2e/
        integration/
      package.json
      tsconfig.json
      next.config.ts
      tailwind.config.ts
    docs/
      app/
        page.tsx
        architecture/
          page.tsx
        demo/
          page.tsx
        faq/
          page.tsx
      components/
      content/
      package.json
      tsconfig.json
    api/
      pyproject.toml
      alembic.ini
      README.md
      src/
        sentinel_api/
          main.py
          api/
            routers/
              health.py
              dashboard.py
              incidents.py
              evidence.py
              agent_runs.py
              simulations.py
              signals.py
              services.py
            deps.py
            errors.py
          core/
            config.py
            logging.py
            security.py
            telemetry.py
          models/
            organization.py
            project.py
            service.py
            incident.py
            signal_event.py
            evidence_item.py
            deployment.py
            agent_run.py
            agent_finding.py
            hypothesis.py
            recommendation.py
            audit_log.py
            simulation.py
          repositories/
            organizations.py
            projects.py
            services.py
            incidents.py
            signals.py
            evidence.py
            deployments.py
            agent_runs.py
            findings.py
            hypotheses.py
            recommendations.py
            simulations.py
          schemas/
            common.py
            incidents.py
            dashboard.py
            evidence.py
            agent_runs.py
            simulations.py
            signals.py
          services/
            incident_service.py
            dashboard_service.py
            evidence_service.py
            simulation_service.py
            orchestration_service.py
            recommendation_service.py
          agents/
            coordinator_agent.py
            log_agent.py
            metrics_agent.py
            deployment_agent.py
            review_agent.py
            root_cause_agent.py
            recommendation_agent.py
            base.py
          graph/
            state.py
            nodes.py
            edges.py
            workflow.py
          tools/
            log_toolkit.py
            metrics_toolkit.py
            deployment_toolkit.py
            retrieval_toolkit.py
            prompt_loader.py
            confidence.py
          worker/
            runner.py
            queue.py
            stream.py
          db/
            base.py
            session.py
            migrations/
      tests/
        unit/
        integration/
        fixtures/
          scenarios/
          prompts/
      scripts/
        seed_demo.py
        run_worker.py
      Dockerfile
    worker/
      README.md
  packages/
    ui/
      src/
        components/
        tokens/
        utils/
      package.json
      tsconfig.json
    types/
      src/
        incident.ts
        evidence.ts
        agent.ts
        dashboard.ts
        simulation.ts
        api.ts
      package.json
      tsconfig.json
    api-client/
      src/
        index.ts
        incidents.ts
        dashboard.ts
        simulations.ts
        agent-runs.ts
      package.json
      tsconfig.json
    prompts/
      src/
        coordinator.md
        log.md
        metrics.md
        deployment.md
        review.md
        root-cause.md
        recommendation.md
      package.json
    schemas/
      src/
        zod/
        json-schema/
      package.json
    eslint-config/
    typescript-config/
  infra/
    railway/
      api.service.json
      worker.service.json
    vercel/
      project.json
    neon/
      schema-notes.md
  docs/
    adrs/
      0001-bounded-monolith.md
      0002-postgres-source-of-truth.md
      0003-langgraph-workflow.md
    product/
      demo-script.md
      prompt-versioning.md
  scripts/
    bootstrap.sh
    check-env.sh
```

Structural rules:

- `apps/web` is the product experience.
- `apps/docs` is the supporting explanation and judge-facing documentation surface.
- `apps/api` contains both API and worker code so domain logic stays colocated.
- `packages/types` defines shared TypeScript contracts for frontend use.
- `packages/prompts` stores versioned agent prompts outside runtime code.
- There should be no generic `utils` dumping ground at the repository root.

## 11. Technology Stack

### Monorepo and Tooling

`TurboRepo`

- Chosen because the project spans a web app, docs app, backend, and shared packages.
- Enables shared build pipelines, cacheable tasks, and package-boundary discipline.
- Fits the existing repository shape, so it minimizes bootstrap churn.

`Bun`

- Already present in the repository as the workspace package manager.
- Speeds local install and monorepo task startup.
- Good fit for a hackathon where iteration speed matters.

`TypeScript`

- Required for reliable shared contracts between frontend and API client packages.
- Reduces integration bugs in complex dashboard state and API consumption.
- Makes UI architecture, chart inputs, and route models safer to evolve quickly.

### Frontend

`Next.js 15`

- Chosen for App Router, React Server Components, streaming support, and strong deployment fit with Vercel.
- Supports a fast dashboard shell, route-level layouts, and efficient data fetching patterns.
- Better architectural fit than a plain Vite SPA because the project benefits from server rendering, route segmentation, and an opinionated app structure.

`React 19`

- Chosen for modern concurrent rendering, improved form and transition ergonomics, and alignment with the latest Next.js patterns.
- Important for a dashboard that mixes server-driven data with live client updates.

`Tailwind CSS`

- Chosen for rapid UI development, design-token consistency, and low-friction component composition.
- Useful for building a highly polished hackathon UI without spending time on bespoke CSS architecture.

`shadcn/ui`

- Chosen because it provides accessible, composable primitives while preserving direct source ownership.
- Better than black-box component libraries for a project that wants a custom visual identity and clean engineering practices.

`Framer Motion`

- Chosen for meaningful motion in agent progress, timeline reveal, and panel transitions.
- Appropriate for high-signal motion without requiring a large custom animation layer.

`React Flow`

- Chosen for the evidence relationship graph and agent interaction visualization.
- It gives the dashboard a differentiated systems-thinking surface that is visually stronger than a static list or table.

`Recharts`

- Chosen for metrics visualizations, severity charts, anomaly trend overlays, and confidence distribution charts.
- Faster to production for a hackathon than building custom charting primitives from scratch.

### Backend

`FastAPI`

- Chosen for fast iteration, async HTTP support, automatic OpenAPI generation, and strong compatibility with Python AI tooling.
- Better fit than a Node backend because the AI orchestration and data-processing logic live more naturally in Python.

`Python`

- Chosen because LangGraph, model orchestration, data transformation, and evaluation tooling are strongest in the Python ecosystem.
- Simplifies backend and agent development by keeping orchestration and analysis close together.

`Pydantic v2`

- Chosen for strict request validation, typed configuration, and structured agent outputs.
- Critical for keeping AI-generated payloads bounded and parseable.

`SQLAlchemy 2.0`

- Chosen for mature PostgreSQL integration, explicit ORM modeling, and clear repository-layer boundaries.
- Better than ad hoc SQL string management for a project that needs rich relational modeling.

`Alembic`

- Chosen for versioned schema migrations.
- Required for a production-grade posture even in a hackathon setting.

### AI and Agent Runtime

`LangGraph`

- Chosen because the core product idea is graph-based multi-agent orchestration with explicit state and conditional routing.
- Better than a single prompt chain because investigations require branching, retries, specialist coordination, and deterministic transitions.

`OpenAI or Gemini reasoning models`

- Chosen because the product needs high-quality cross-signal reasoning, summarization, and structured analysis.
- The system should use a provider abstraction so model choice is configurable.

`OpenAI Codex`

- Chosen for engineering-oriented tasks where code or configuration interpretation materially improves remediation advice.
- Codex should only be used to draft suggestions or explain likely code/config changes, never to auto-deploy or auto-commit in the MVP.

### Data Layer

`PostgreSQL`

- Chosen as the primary source of truth because the project needs relational integrity, JSONB flexibility, and transactional consistency.
- Stronger MVP choice than a specialized data store because incidents, findings, and recommendations are highly relational.

`Neon`

- Chosen because it provides managed PostgreSQL with a developer-friendly workflow and easy cloud deployment.
- Strong fit for a fast-moving startup and hackathon environment.

`Redis` optional but recommended

- Chosen for queueing background investigations, caching hot read models, rate limiting, and fan-out of live events.
- Optional because the first demo can work without it, but recommended because it improves architecture clarity and scalability.

`ChromaDB` optional

- Chosen only if semantic retrieval is implemented for historical incidents, runbooks, or similar-case lookup.
- Kept optional because Postgres should remain the system of record, and the MVP does not require a vector database to demonstrate the core idea.

### Deployment

`Vercel`

- Chosen for the frontend because Next.js deployment is operationally simple and fast.
- Also valuable for preview URLs during rapid iteration.

`Railway`

- Chosen for backend deployment because it handles Python services, worker processes, and attached data services with minimal setup.
- Good balance between startup velocity and production realism.

`Neon`

- Chosen for managed Postgres with minimal operational overhead.

Technology trade-off summary:

- Chosen: structured, typed, boring where it matters
- Avoided: over-engineered infra, many services, custom data platforms
- Why: the product’s novelty should live in the agent system and operator experience, not in infrastructure complexity

## 12. Frontend Architecture

The frontend architecture should optimize for three things:

- Instant comprehension of incident state
- Trust in AI reasoning through explainable UI
- A visually distinctive SaaS experience suitable for a judged demo

### Pages

`apps/web` should use the Next.js App Router with route groups.

Core product routes:

- `/` should redirect to `/incidents` in the product app.
- `/incidents` should render the incident overview dashboard.
- `/incidents/[incidentId]` should render the Incident Command Center.
- `/simulator` should render the scenario launcher and live demo controls.
- `/settings/integrations` should describe or manage data-source connectors.
- `/settings/prompts` should expose prompt versions and confidence thresholds for demo transparency.
- `/settings/about` should explain the architecture at a high level for judges and collaborators.

`apps/docs` should host the narrative surface:

- `/` product overview and positioning
- `/architecture` system walkthrough
- `/demo` judge-oriented demo instructions
- `/faq` technical FAQ and decision rationale

### Layouts

The product app should use a persistent application shell:

- Left navigation with product logo, routes, and active incident count
- Top bar with environment selector, simulation status, and current investigation health
- Main content region with route-specific content

The incident detail page should use a three-zone layout on desktop:

- Left zone: incident summary and evidence filters
- Center zone: timeline, charts, and evidence graph
- Right zone: agent feed, hypotheses, and recommendations

On tablet, the right zone should collapse into a slide-over panel. On mobile, the experience should become a prioritized stacked flow rather than a squeezed desktop view.

### Components

Component architecture should have four levels:

- Design primitives in `packages/ui`
- Shared product components in `apps/web/components/shared`
- Domain components grouped by feature, such as `incidents`, `evidence`, `agents`, `recommendations`, and `simulator`
- Route composition files that assemble domain components into pages

Important component families:

- `IncidentHeader`, `SeverityBadge`, `StatusPill`
- `TimelineRail`, `EvidenceTable`, `EvidenceCard`
- `AgentRunFeed`, `AgentStatusCard`, `ConfidenceMeter`
- `HypothesisStack`, `RecommendationChecklist`
- `MetricsAnomalyChart`, `SignalVolumeChart`, `ServiceHeatmap`
- `EvidenceGraphCanvas`

### Routing

Routing should follow resource-oriented product semantics.

- Incident collections live under `/incidents`
- Single-incident workflows live under `/incidents/[incidentId]`
- Simulation is a separate top-level experience because it is central to the demo
- Settings are isolated under `/settings` to avoid cluttering the core workflow

Route groups should be used to separate dashboard chrome from docs chrome.

### State Management

State should be deliberately split by responsibility:

- Server state should be fetched from FastAPI and treated as authoritative.
- Initial page data should be loaded through server components where it improves first paint and SEO for docs pages.
- Live investigation updates should arrive through Server-Sent Events and hydrate client-side components.
- URL search parameters should hold shareable filters such as selected service, severity, and time window.
- Route-scoped React context providers should manage complex UI state for the Incident Command Center, such as selected evidence node, focused chart series, and panel visibility.

A separate global client-state library is not required for the MVP. Avoid adding one unless complexity proves it necessary. This keeps the architecture simpler and reduces dependency sprawl.

### UI Architecture

The UI should communicate “operational intelligence,” not “generic AI chat app.”

Design direction:

- Clean, high-contrast operator interface
- Graphite and bone neutrals with alert colors used sparingly
- Signal teal for healthy correlation, ember for warning, crimson for confirmed incident severity
- Technical typography pairing such as `Space Grotesk` or `Sora` for headings and `IBM Plex Sans` or `Geist Sans` for body copy
- Monospace reserved for logs, IDs, and timestamps

The UI should prioritize evidence visibility:

- Root-cause claims must always sit near evidence access
- Confidence displays should be visual but not theatrical
- Agent reasoning should feel inspectable, not magical

### Responsive Strategy

Responsive behavior should be intentional rather than simply fluid.

- Desktop is the primary design target because judges and operators will likely use laptops.
- Tablet must preserve the command-center feel with collapsible side panels.
- Mobile should support incident summary, recommendations, and essential evidence review, but not attempt to show every dense chart at once.
- Heavy visualizations such as React Flow should degrade gracefully on small screens into summarized card views or simplified node lists.

### Animation Strategy

Motion should reinforce system activity and confidence, not distract from it.

- Investigation start should trigger a subtle staged reveal of agent cards.
- Timeline events should stream into view with short vertical motion and opacity changes.
- Confidence changes should animate numerically and visually to reflect evolving understanding.
- Graph focus transitions should help users follow cause-and-effect relationships.
- A reduced-motion mode should disable non-essential animations.

Animation should be used to convey:

- Work in progress
- State transition
- Evidence linkage
- Confidence refinement

Animation should not be used to fake system sophistication.

## 13. Backend Architecture

The backend should be a layered FastAPI application with strict boundaries between transport, business logic, persistence, and agent orchestration.

### Routers

Routers are the HTTP boundary and should remain thin.

Responsibilities:

- Parse requests
- Enforce request validation
- Resolve dependencies
- Invoke services
- Return typed response models

Router groups:

- `health`
- `dashboard`
- `incidents`
- `evidence`
- `agent_runs`
- `signals`
- `simulations`
- `services`

Routers must not:

- Build SQL queries directly
- Contain agent logic
- Contain business rules beyond request-shape validation

### Services

Services contain application business logic.

Examples:

- `IncidentService` manages incident creation, lifecycle changes, and read models.
- `SimulationService` replays or generates scenario data.
- `OrchestrationService` starts investigations and manages worker handoff.
- `DashboardService` assembles overview data projections.
- `RecommendationService` applies recommendation filtering, ranking, and formatting rules.

Service rules:

- Services may coordinate multiple repositories.
- Services may transform persistence models into response DTOs.
- Services may emit audit events.
- Services should be stateless except for injected dependencies.

### Repositories

Repositories are the persistence abstraction.

Responsibilities:

- CRUD and query operations for a specific aggregate or bounded area
- Encapsulation of SQLAlchemy queries
- Transaction-friendly interfaces

Repository examples:

- `IncidentsRepository`
- `EvidenceRepository`
- `AgentRunsRepository`
- `HypothesesRepository`

Repositories must not:

- Call LLMs
- Perform HTTP transport work
- Contain cross-aggregate orchestration logic

### Models

Two model categories should exist:

- ORM models for persistence
- Pydantic schema models for request, response, and structured agent output

Persistence models should use explicit enums and JSONB only where flexibility is necessary. Business-critical fields such as status, severity, agent name, and root-cause rank should not hide inside untyped blobs.

### Dependency Injection

Dependency injection should use FastAPI’s native `Depends` rather than an external container.

Examples of injectable dependencies:

- Database session
- Current organization context
- Configuration object
- Model gateway client
- Queue publisher

Why this choice:

- Native DI is enough for the project’s scale
- External DI frameworks would add complexity without meaningful benefit

### Configuration

Configuration should be centralized in `core/config.py` using typed settings.

Configuration domains:

- App environment and URLs
- Database connection strings
- Model provider keys and model names
- Queue and cache settings
- Agent retry budgets
- Confidence thresholds
- Simulation timing controls

Rules:

- No direct `os.getenv` calls outside the config layer
- No secrets in frontend bundles
- Environment-specific defaults should be explicit and documented

### Logging

Logging must be structured JSON from the beginning.

Required log fields:

- timestamp
- level
- message
- request_id
- incident_id
- run_id
- agent_name
- duration_ms
- model_provider
- token_usage when available

Why:

- Incidents involving AI workflows are hard to debug without structured runtime traces
- Judges evaluating architecture quality will expect evidence of operational thinking

### Validation

Validation should happen at multiple levels:

- Request validation with Pydantic
- Domain validation inside services
- Structured agent-output validation against response schemas
- Database constraints for critical integrity

Examples:

- An incident cannot be resolved before it exists
- A recommendation cannot be linked to a nonexistent hypothesis
- An agent finding without evidence references should be marked degraded or rejected

### Error Handling

Error handling should use a typed exception hierarchy.

Recommended categories:

- `NotFoundError`
- `ValidationError`
- `ConflictError`
- `ExternalDependencyError`
- `AgentExecutionError`
- `InsufficientEvidenceError`

A global exception handler should translate these into stable API error shapes with machine-readable codes.

Design principle:

- Errors are product events, not just stack traces

## 14. Database Design

PostgreSQL is the source of truth. The schema should prioritize clear incident lineage, evidence traceability, and agent-run auditability.

Primary key strategy:

- Use ULIDs or UUIDv7-style sortable identifiers where possible
- Why: time-sortable IDs help both debugging and UI ordering

### Entities

`organizations`

- Purpose: top-level tenant boundary
- Key fields: `id`, `name`, `slug`, `created_at`

`projects`

- Purpose: logical product or environment grouping within an organization
- Key fields: `id`, `organization_id`, `name`, `environment`, `created_at`

`services`

- Purpose: track services or deployable units that can participate in incidents
- Key fields: `id`, `project_id`, `name`, `owner_team`, `tier`, `created_at`

`incidents`

- Purpose: core incident record
- Key fields: `id`, `organization_id`, `project_id`, `primary_service_id`, `title`, `summary`, `severity`, `status`, `opened_at`, `resolved_at`, `source`, `top_hypothesis_id`

`signal_events`

- Purpose: normalized operational signals
- Key fields: `id`, `incident_id`, `service_id`, `signal_type`, `source`, `timestamp`, `severity`, `payload_json`, `metadata_json`, `fingerprint`

`evidence_items`

- Purpose: human- and agent-consumable evidence derived from signals
- Key fields: `id`, `incident_id`, `signal_event_id`, `service_id`, `evidence_type`, `title`, `summary`, `importance_score`, `timestamp`, `attributes_json`

`deployments`

- Purpose: represent deployment and config-change events
- Key fields: `id`, `project_id`, `service_id`, `version`, `environment`, `deployed_at`, `commit_sha`, `change_summary`, `metadata_json`

`agent_runs`

- Purpose: track each investigation run and each agent’s execution
- Key fields: `id`, `incident_id`, `parent_run_id`, `agent_name`, `status`, `started_at`, `completed_at`, `attempt`, `prompt_version`, `model_name`, `confidence_score`

`agent_findings`

- Purpose: structured output from agents
- Key fields: `id`, `agent_run_id`, `finding_type`, `title`, `summary`, `evidence_item_ids`, `contradiction_ids`, `confidence_score`, `output_json`

`hypotheses`

- Purpose: ranked root-cause candidates
- Key fields: `id`, `incident_id`, `rank`, `title`, `summary`, `confidence_score`, `supporting_evidence_ids`, `contradicting_evidence_ids`, `status`

`recommendations`

- Purpose: recommended actions
- Key fields: `id`, `incident_id`, `hypothesis_id`, `category`, `priority`, `title`, `description`, `risk_level`, `reversibility`, `confidence_score`, `status`

`incident_events`

- Purpose: timeline and audit-like incident progression
- Key fields: `id`, `incident_id`, `event_type`, `actor_type`, `actor_id`, `payload_json`, `created_at`

`feedback_entries`

- Purpose: capture human feedback on accuracy and usefulness
- Key fields: `id`, `incident_id`, `run_id`, `rating`, `comment`, `created_by`, `created_at`

`prompt_versions`

- Purpose: trace prompt templates used per agent
- Key fields: `id`, `agent_name`, `version`, `content_hash`, `created_at`, `is_active`

`simulation_scenarios`

- Purpose: store demo scenarios and metadata
- Key fields: `id`, `slug`, `name`, `description`, `difficulty`, `default_duration_sec`, `fixture_path`

`audit_logs`

- Purpose: security and operational audit trail
- Key fields: `id`, `organization_id`, `entity_type`, `entity_id`, `action`, `performed_by`, `context_json`, `created_at`

### Relationships

- One organization has many projects.
- One project has many services.
- One project has many incidents.
- One service can participate in many incidents.
- One incident has many signal events.
- One signal event can produce zero or more evidence items.
- One incident has many agent runs.
- One agent run has many agent findings.
- One incident has many hypotheses.
- One hypothesis can have many recommendations.
- One incident has many timeline events and feedback entries.

### Indexes

Recommended indexes:

- `incidents (organization_id, status, opened_at desc)`
- `incidents (project_id, severity, opened_at desc)`
- `signal_events (incident_id, timestamp)`
- `signal_events (service_id, signal_type, timestamp)`
- `signal_events (fingerprint)`
- `evidence_items (incident_id, timestamp)`
- `agent_runs (incident_id, started_at desc)`
- `agent_runs (agent_name, status, started_at desc)`
- `hypotheses (incident_id, rank)`
- `recommendations (incident_id, category, priority)`
- `incident_events (incident_id, created_at)`
- `deployments (service_id, deployed_at desc)`

JSONB indexes should be added only for proven query paths, such as `payload_json` keys frequently used in filters. Do not over-index early.

Schema design trade-off:

- Chosen: relational core with selective JSONB flexibility
- Avoided: all-blob schema or all-event-sourcing schema
- Why: the dashboard and API need predictable joins and filters, but raw signals still need flexible metadata storage

## 15. API Design

All APIs should be versioned under `/v1`. Responses should use predictable envelopes where helpful, but not at the cost of excessive wrapper noise. Errors should share a common shape with `code`, `message`, and optional `details`.

### 1. `GET /v1/health`

Purpose:

- Liveness check for deployment and monitoring

Request:

- No body

Response:

- `status`
- `service`
- `timestamp`

### 2. `GET /v1/ready`

Purpose:

- Readiness check confirming database and worker dependencies are reachable

Request:

- No body

Response:

- `status`
- `checks`
- `timestamp`

### 3. `GET /v1/dashboard/overview`

Purpose:

- Return the summary data for the overview dashboard

Query parameters:

- `project_id` optional
- `time_range` optional, default `24h`

Response:

- `active_incident_count`
- `severity_breakdown`
- `service_health_summary`
- `recent_incidents`
- `investigation_queue`
- `latest_agent_activity`

### 4. `GET /v1/incidents`

Purpose:

- List incidents with filters for status, severity, project, service, and search

Query parameters:

- `status`
- `severity`
- `project_id`
- `service_id`
- `search`
- `page`
- `page_size`

Response:

- `items` as incident summary records
- `pagination`
- `applied_filters`

### 5. `POST /v1/incidents`

Purpose:

- Create a new incident manually or through a normalized ingestion pathway

Request body:

- `title`
- `summary`
- `severity`
- `project_id`
- `primary_service_id` optional
- `source`
- `opened_at`
- `initial_signal_ids` optional

Response:

- Full incident summary
- `investigation_triggered` boolean

### 6. `GET /v1/incidents/{incidentId}`

Purpose:

- Return the canonical incident detail view model

Response:

- Incident metadata
- Current top hypotheses
- Root-cause summary
- Confidence breakdown
- Recommendation summary
- Linked services
- Investigation status

### 7. `PATCH /v1/incidents/{incidentId}`

Purpose:

- Update editable incident fields such as title, summary, severity, owner, or status

Request body:

- Partial update fields only

Response:

- Updated incident record

### 8. `POST /v1/incidents/{incidentId}/acknowledge`

Purpose:

- Mark the incident as acknowledged by a human user

Request body:

- `acknowledged_by`
- `note` optional

Response:

- Updated status
- Acknowledgement timestamp

### 9. `POST /v1/incidents/{incidentId}/investigate`

Purpose:

- Trigger or re-trigger the LangGraph investigation workflow

Request body:

- `reason` such as `initial`, `manual_rerun`, or `new_evidence`
- `force_reanalysis` boolean
- `time_window_override` optional

Response:

- `run_id`
- `status`
- `queued_at`

### 10. `POST /v1/incidents/{incidentId}/resolve`

Purpose:

- Resolve the incident with human confirmation

Request body:

- `resolved_by`
- `resolution_summary`
- `selected_hypothesis_id` optional

Response:

- Updated incident status
- Resolution metadata

### 11. `GET /v1/incidents/{incidentId}/timeline`

Purpose:

- Return the incident event stream for timeline rendering

Query parameters:

- `limit`
- `cursor`
- `event_type` optional

Response:

- `items` containing ordered timeline entries
- `next_cursor`

### 12. `GET /v1/incidents/{incidentId}/evidence`

Purpose:

- Return evidence items for a specific incident

Query parameters:

- `service_id`
- `evidence_type`
- `importance_min`
- `sort`

Response:

- `items` as evidence records
- `clusters`
- `stats`

### 13. `GET /v1/incidents/{incidentId}/graph`

Purpose:

- Return nodes and edges for the evidence and causality graph

Response:

- `nodes`
- `edges`
- `legend`

### 14. `GET /v1/incidents/{incidentId}/recommendations`

Purpose:

- Return the structured recommendation set

Response:

- `immediate_actions`
- `short_term_actions`
- `long_term_actions`
- `root_cause_dependency`

### 15. `GET /v1/incidents/{incidentId}/agent-runs`

Purpose:

- Return all agent runs associated with an incident

Response:

- `items` containing run summaries and statuses

### 16. `GET /v1/agent-runs/{runId}`

Purpose:

- Return a detailed agent run record

Response:

- Run metadata
- Prompt version
- Model used
- Findings
- Duration
- Failure status if applicable

### 17. `GET /v1/agent-runs/{runId}/stream`

Purpose:

- Stream live updates for a running investigation using Server-Sent Events

Event types:

- `run.started`
- `agent.started`
- `agent.completed`
- `finding.created`
- `hypothesis.updated`
- `recommendation.created`
- `run.completed`
- `run.degraded`

Response:

- SSE event stream

### 18. `POST /v1/signals/ingest`

Purpose:

- Accept normalized or semi-normalized signals from the simulator or future integrations

Request body:

- `organization_id`
- `project_id`
- `service_id` optional
- `signal_type`
- `source`
- `timestamp`
- `severity`
- `payload`
- `metadata` optional

Response:

- `signal_id`
- `incident_id` if linked
- `accepted` boolean

### 19. `GET /v1/simulations`

Purpose:

- List available demo scenarios

Response:

- `items` with scenario metadata, difficulty, and estimated runtime

### 20. `POST /v1/simulations/run`

Purpose:

- Launch a deterministic incident simulation

Request body:

- `scenario_slug`
- `speed_multiplier`
- `auto_investigate` boolean

Response:

- `simulation_id`
- `incident_id`
- `status`
- `started_at`

### 21. `GET /v1/simulations/{simulationId}`

Purpose:

- Return simulation run status and associated incident

Response:

- Simulation metadata
- Incident link
- Replay progress
- Current emitted signals count

### 22. `POST /v1/incidents/{incidentId}/feedback`

Purpose:

- Capture human feedback on root-cause accuracy and recommendation usefulness

Request body:

- `rating`
- `comment`
- `run_id` optional

Response:

- Created feedback record

### 23. `GET /v1/services`

Purpose:

- Return the catalog of services for dashboard filters and service pages

Query parameters:

- `project_id`

Response:

- `items` with service metadata, ownership, and health rollups

### 24. `GET /v1/deployments`

Purpose:

- Return recent deployment records for correlation views and debugging

Query parameters:

- `project_id`
- `service_id`
- `limit`

Response:

- `items` containing deployment summaries

API design principles:

- Prefer noun-based resources over verb-heavy RPC endpoints
- Use action subresources only for state transitions such as `acknowledge`, `resolve`, and `investigate`
- Keep response models dashboard-ready to reduce frontend orchestration complexity

## 16. Agent Architecture

The agent system is the product core. Each agent must have a narrow role, clear inputs, bounded outputs, and explicit failure modes. Agents communicate through shared graph state rather than unconstrained chat transcripts.

### Shared Agent Contract

Every agent should receive:

- Incident metadata
- Time-bounded normalized evidence
- Prior agent outputs where appropriate
- Prompt version and model configuration
- Structured output schema

Every agent should return:

- `summary`
- `key_findings`
- `supporting_evidence_ids`
- `contradicting_evidence_ids`
- `open_questions`
- `confidence_score`
- `confidence_rationale`
- `status`

### Coordinator Agent

Responsibilities:

- Own the investigation lifecycle
- Determine which specialist agents must run
- Set investigation scope and time window
- Trigger retries or targeted follow-up when confidence is low or evidence is incomplete
- Decide whether the investigation can proceed to root-cause synthesis

Inputs:

- Incident metadata
- Available signal inventory
- Current graph state
- Retry budget and confidence thresholds

Outputs:

- Investigation plan
- Agent execution directives
- Re-plan instructions if needed
- Overall investigation status

Failure handling:

- If planning fails, emit a degraded investigation state and fall back to a default agent sequence
- If a child agent fails, record failure, continue with remaining agents, and surface degraded confidence

Confidence scoring:

- Based on evidence completeness, agreement between agents, and number of unresolved critical questions
- This is not root-cause confidence; it is investigation-readiness confidence

### Log Agent

Responsibilities:

- Analyze logs for error fingerprints, temporal spikes, repetitive failures, and likely subsystem involvement
- Cluster noisy logs into actionable patterns
- Identify correlation between log anomalies and incident start time

Inputs:

- Incident time window
- Normalized log signals
- Service metadata
- Optional deployment context

Outputs:

- Top log clusters
- Candidate failure modes
- Affected services and endpoints
- Evidence items supporting or contradicting hypotheses

Failure handling:

- If logs are absent, explicitly return `insufficient_log_data`
- If logs are too noisy, return clustered summaries with reduced confidence rather than raw noise dumps

Confidence scoring:

- Higher when the same error pattern is concentrated around incident onset and linked to the impacted service
- Lower when logs are generic, low-volume, or temporally diffuse

### Metrics Agent

Responsibilities:

- Analyze timeseries anomalies across latency, error rate, saturation, and traffic
- Determine which metrics shifted first and which shifts are downstream symptoms
- Assess blast radius across services and time

Inputs:

- Metric anomaly signals
- Baseline windows
- Service topology metadata

Outputs:

- Primary anomalous metrics
- Start time and magnitude of anomalies
- Suspected bottleneck domain such as CPU, memory, downstream dependency, or request saturation
- Confidence and unresolved ambiguities

Failure handling:

- If there is not enough historical baseline, fall back to relative within-window comparisons
- If metrics conflict, preserve contradictions and reduce confidence

Confidence scoring:

- Higher when multiple related metrics shift coherently and align to the incident window
- Lower when only one weak anomaly exists or when anomalies are system-wide and nonspecific

### Deployment Agent

Responsibilities:

- Inspect recent deployments, config changes, feature-flag flips, and release timing
- Correlate incident onset with deployment events
- Estimate change risk and blast radius

Inputs:

- Deployment records
- Incident onset time
- Service ownership metadata
- Optional commit, config, or release summaries

Outputs:

- Ranked recent changes
- Temporal proximity analysis
- Suspicious deploy or config candidates
- Change-risk interpretation

Failure handling:

- If no recent deployment exists, return a strong negative signal rather than a null result
- If deployment metadata is incomplete, mark conclusions as tentative

Confidence scoring:

- Higher when a recent high-risk change aligns tightly with incident onset and implicated service
- Lower when multiple unrelated deployments occurred or change metadata is weak

### Review Agent

Responsibilities:

- Act as a skeptical verifier of specialist findings
- Identify unsupported claims, missing evidence links, and contradictory observations
- Improve explainability by enforcing evidence discipline

Inputs:

- Findings from Log, Metrics, and Deployment agents
- Evidence graph
- Confidence scores from specialists

Outputs:

- Verified findings
- Rejected or weakened claims
- Additional questions for re-analysis
- Evidence sufficiency assessment

Failure handling:

- If review fails, the system may continue, but the final investigation must be marked degraded because review is key to explainability

Confidence scoring:

- Based on evidence coverage ratio, contradiction density, and citation quality
- Review confidence represents trust in the investigation package, not the system’s final root-cause answer

### Root Cause Agent

Responsibilities:

- Synthesize specialist outputs into ranked hypotheses
- Distinguish probable cause from downstream symptoms
- Produce a concise and defensible root-cause narrative

Inputs:

- Verified specialist findings
- Incident timeline
- Evidence graph
- Confidence breakdown from other agents

Outputs:

- Ranked hypotheses
- Top root-cause summary
- Contradictions and unknowns
- Final confidence breakdown

Failure handling:

- If synthesis fails, preserve specialist outputs and mark the incident `needs-human-review`
- Never fabricate a single root cause if evidence remains ambiguous

Confidence scoring:

- Weighted aggregate of specialist confidence, evidence quality, temporal alignment, and contradiction penalty
- Suggested formula:
- `35% evidence quality`
- `25% cross-agent agreement`
- `20% temporal alignment`
- `20% model certainty`
- Apply a penalty for unresolved contradictions and missing critical evidence

### Recommendation Agent

Responsibilities:

- Translate root-cause hypotheses into safe next actions
- Separate immediate mitigation from structural remediation
- Tailor recommendations to confidence and reversibility
- Optionally generate engineering-oriented follow-up suggestions using Codex for code/config interpretation

Inputs:

- Ranked hypotheses
- Confidence scores
- Service and deployment context
- Historical runbook or retrieval context if available

Outputs:

- Immediate mitigation actions
- Short-term remediation actions
- Long-term prevention actions
- Action risk and reversibility annotations

Failure handling:

- If root-cause confidence is low, recommendations must become more conservative and diagnostic
- If Codex-style engineering suggestions fail, continue with operational recommendations only

Confidence scoring:

- Derived from root-cause confidence and action safety
- High-confidence but high-risk actions should still be labeled carefully

Agent architecture trade-off:

- Chosen: specialist agents with structured coordination
- Avoided: single omniscient agent
- Why: incident investigations benefit from parallel, domain-specific reasoning and explicit synthesis

## 17. LangGraph Workflow

The LangGraph workflow should be deterministic, inspectable, and resilient. Each node should have a single clear responsibility. Each edge should represent a meaningful control-flow decision.

### Workflow Nodes

`Node 1: load_incident_context`

- Load incident record, project metadata, service context, and investigation configuration.

`Node 2: fetch_signal_window`

- Gather all relevant signal events in the configured incident window.

`Node 3: normalize_and_enrich_evidence`

- Convert signals into normalized evidence items and attach metadata such as affected service, deployment link, or severity cluster.

`Node 4: coordinator_plan`

- Produce the initial investigation plan, determine which agents to run, and record retry budget.

`Node 5: run_log_agent`

- Analyze log evidence.

`Node 6: run_metrics_agent`

- Analyze metric evidence.

`Node 7: run_deployment_agent`

- Analyze deployment and change evidence.

`Node 8: review_findings`

- Verify specialist outputs, identify contradictions, and determine evidence sufficiency.

`Node 9: decide_replan_or_synthesize`

- Gate whether the workflow should rerun a specialist, continue to synthesis, or stop for human review.

`Node 10: synthesize_root_cause`

- Generate ranked hypotheses and a root-cause narrative.

`Node 11: generate_recommendations`

- Produce mitigation and remediation actions.

`Node 12: persist_and_stream_results`

- Save outputs to PostgreSQL and publish updates to the live UI stream.

`Node 13: finalize_run`

- Mark the run `completed`, `degraded`, or `needs-human-review`.

### Workflow Edges

`START -> load_incident_context`

- Why: every investigation must begin from canonical incident metadata.

`load_incident_context -> fetch_signal_window`

- Why: the system cannot reason until it knows which evidence window to inspect.

`fetch_signal_window -> normalize_and_enrich_evidence`

- Why: raw signals are too heterogeneous for reliable agent reasoning; normalization is mandatory.

`normalize_and_enrich_evidence -> coordinator_plan`

- Why: the Coordinator Agent needs a complete inventory of available evidence before planning.

`coordinator_plan -> run_log_agent`

- Why: logs are a core evidence source for most software incidents.

`coordinator_plan -> run_metrics_agent`

- Why: metric anomalies establish timing, blast radius, and symptom magnitude.

`coordinator_plan -> run_deployment_agent`

- Why: changes are one of the highest-value root-cause candidates in modern systems.

These three edges should run in parallel.

`run_log_agent -> review_findings`

- Why: log conclusions should not bypass verification.

`run_metrics_agent -> review_findings`

- Why: metrics can indicate symptoms rather than cause, so review is necessary.

`run_deployment_agent -> review_findings`

- Why: temporal correlation alone can overstate causality, so review is necessary.

`review_findings -> decide_replan_or_synthesize`

- Why: the system must assess whether evidence is sufficient before claiming a root cause.

`decide_replan_or_synthesize -> run_log_agent`

- Why: if the reviewer identifies missing or ambiguous log evidence and retry budget remains, targeted re-analysis may improve confidence.

`decide_replan_or_synthesize -> run_metrics_agent`

- Why: the same principle applies when metric evidence is incomplete or conflicting.

`decide_replan_or_synthesize -> run_deployment_agent`

- Why: change analysis may need a narrower window or a different service focus.

`decide_replan_or_synthesize -> synthesize_root_cause`

- Why: proceed only when evidence sufficiency reaches the configured threshold or retry budget is exhausted.

`synthesize_root_cause -> generate_recommendations`

- Why: recommendations should depend on ranked hypotheses rather than raw specialist outputs.

`synthesize_root_cause -> finalize_run`

- Why: if confidence is too low for action guidance, the system may end with `needs-human-review` without generating strong recommendations.

`generate_recommendations -> persist_and_stream_results`

- Why: recommendations are user-facing deliverables that must be stored and streamed.

`persist_and_stream_results -> finalize_run`

- Why: persistence must succeed before the run is marked complete.

`finalize_run -> END`

- Why: the workflow terminates only after state, audit trail, and UI stream are all updated.

### Conditional Logic

Replan conditions:

- Review Agent flags missing critical evidence
- Specialist outputs conflict materially
- Top-hypothesis confidence is below threshold and retry budget remains

Stop-and-abstain conditions:

- Evidence remains insufficient after retries
- Signal ingestion failed materially
- Model outputs repeatedly fail schema validation

Why LangGraph is the correct orchestration choice:

- It makes nodes, edges, state, retries, and conditions explicit
- It is far more debuggable than hidden agent loops
- It supports production-oriented reasoning workflows rather than demo-only prompt chains

## 18. Data Flow

The data flow must be explicit because Sentinel AI’s trust depends on evidence lineage.

### Standard Incident Flow

1. A signal arrives through the simulator or the `/v1/signals/ingest` endpoint.
2. The backend validates the payload and writes a normalized `signal_event` record.
3. Incident correlation logic either attaches the signal to an open incident or creates a new incident.
4. The backend writes an `incident_event` showing that an incident was created or updated.
5. The `OrchestrationService` creates a parent `agent_run` and queues the investigation.
6. The worker loads incident context and gathers all relevant signals in the time window.
7. The worker normalizes signals into `evidence_items`.
8. The Coordinator Agent plans the investigation and launches specialist agents in parallel.
9. Each specialist agent reads the same shared state plus its domain-specific evidence slice.
10. Specialist outputs are validated and persisted as `agent_findings`.
11. The Review Agent verifies the findings and may trigger targeted re-analysis.
12. The Root Cause Agent writes ranked hypotheses.
13. The Recommendation Agent writes recommendation records.
14. The worker emits live status events to the stream layer.
15. The frontend subscribes to the SSE stream and incrementally updates the dashboard.
16. The user sees incident status, evidence, hypotheses, and recommendations converge in real time.
17. A human acknowledges, reruns, or resolves the incident through API actions.
18. Human actions generate new `incident_events` and, where needed, new `agent_runs`.

### Simulation Flow

1. A user launches a scenario from `/simulator`.
2. The backend loads a deterministic fixture sequence.
3. Synthetic deployments, metric spikes, logs, and customer feedback are emitted over time.
4. The system ingests them using the same code path as real signals.
5. The rest of the flow is identical to a real incident, which keeps the demo honest.

### Live Update Flow

1. The frontend opens an SSE connection for a run or incident.
2. The backend publishes `agent.started`, `finding.created`, and `hypothesis.updated` events as the worker progresses.
3. The frontend merges those deltas into the current route-scoped view state.
4. Users see the dashboard update without full refreshes or polling-heavy behavior.

## 19. Shared Types

Shared types should live in `packages/types` and represent the contract between frontend UI and backend responses. They should not mirror database models one-to-one unless that is actually useful.

### Core Enums

`Severity`

- Values: `P1`, `P2`, `P3`, `P4`
- Purpose: incident prioritization

`IncidentStatus`

- Values: `open`, `investigating`, `mitigating`, `monitoring`, `resolved`, `needs-human-review`
- Purpose: lifecycle control

`SignalType`

- Values: `alert`, `log`, `metric`, `deployment`, `customer_feedback`, `incident_note`
- Purpose: normalized signal classification

`AgentName`

- Values: `coordinator`, `log`, `metrics`, `deployment`, `review`, `root_cause`, `recommendation`
- Purpose: consistent agent identification across UI and backend

`RecommendationCategory`

- Values: `immediate`, `short_term`, `long_term`
- Purpose: recommendation grouping

### Shared Interfaces

`IncidentSummary`

- Fields: `id`, `title`, `severity`, `status`, `projectId`, `primaryServiceName`, `openedAt`, `topHypothesisTitle`, `topConfidenceScore`
- Used by: incident list and overview widgets

`IncidentDetail`

- Fields: all `IncidentSummary` fields plus `summary`, `affectedServices`, `rootCauseSummary`, `confidenceBreakdown`, `recommendationSummary`, `timelinePreview`
- Used by: Incident Command Center page

`SignalEvent`

- Fields: `id`, `incidentId`, `serviceId`, `signalType`, `source`, `timestamp`, `severity`, `payload`, `metadata`
- Used by: ingestion debugging and low-level evidence views

`EvidenceItem`

- Fields: `id`, `incidentId`, `signalEventId`, `evidenceType`, `title`, `summary`, `timestamp`, `importanceScore`, `serviceName`, `attributes`
- Used by: evidence table, graph, and agent citations

`DeploymentRecord`

- Fields: `id`, `serviceId`, `version`, `commitSha`, `deployedAt`, `changeSummary`, `riskLevel`
- Used by: deployment correlation cards and timeline

`AgentRunSummary`

- Fields: `id`, `incidentId`, `agentName`, `status`, `startedAt`, `completedAt`, `attempt`, `confidenceScore`
- Used by: agent run list and feed

`AgentFinding`

- Fields: `id`, `agentRunId`, `title`, `summary`, `findingType`, `supportingEvidenceIds`, `contradictingEvidenceIds`, `confidenceScore`, `openQuestions`
- Used by: agent detail panels and synthesis trace

`Hypothesis`

- Fields: `id`, `incidentId`, `rank`, `title`, `summary`, `confidenceScore`, `supportingEvidenceIds`, `contradictingEvidenceIds`, `status`
- Used by: root-cause stack and explanation views

`Recommendation`

- Fields: `id`, `incidentId`, `hypothesisId`, `category`, `priority`, `title`, `description`, `riskLevel`, `reversibility`, `confidenceScore`
- Used by: action checklist and remediation panel

`ConfidenceBreakdown`

- Fields: `overall`, `evidenceQuality`, `crossAgentAgreement`, `temporalAlignment`, `modelCertainty`, `contradictionPenalty`, `notes`
- Used by: confidence meter and tooltip details

`TimelineEntry`

- Fields: `id`, `incidentId`, `eventType`, `actorType`, `label`, `description`, `timestamp`, `payload`
- Used by: investigation timeline and replay mode

`GraphNode`

- Fields: `id`, `type`, `label`, `entityId`, `severity`, `confidenceScore`, `metadata`
- Used by: React Flow graph

`GraphEdge`

- Fields: `id`, `source`, `target`, `relationshipType`, `strength`, `label`
- Used by: React Flow graph

`DashboardOverview`

- Fields: `activeIncidentCount`, `severityBreakdown`, `serviceHealthSummary`, `recentIncidents`, `latestAgentActivity`
- Used by: overview page

`SimulationScenario`

- Fields: `id`, `slug`, `name`, `description`, `difficulty`, `estimatedRuntimeSec`, `primaryService`
- Used by: simulator page

`ApiError`

- Fields: `code`, `message`, `details`, `requestId`
- Used by: global frontend error handling

`PaginatedResponse<T>`

- Fields: `items`, `page`, `pageSize`, `total`
- Used by: list endpoints

Shared type rule:

- Backend response schemas and frontend contracts should be generated from shared intent, not copied manually in divergent forms.

## 20. Dashboard Design

The dashboard is the product’s trust surface. It should feel like an incident command center, not a generic admin panel. Every widget must serve a clear operational purpose.

### Global Design Language

- Dense but readable
- Technically sophisticated without visual clutter
- High contrast with restrained alert colors
- Motion used to indicate system activity and state transitions

### Overview Dashboard Widgets

`1. Active Incidents Table`

- Purpose: primary overview list
- Contents: title, severity, affected service, opened time, current status, top hypothesis, confidence
- Interaction: row click opens Incident Command Center

`2. Severity Distribution Chart`

- Chart type: stacked bar or donut
- Purpose: show the current distribution of incident severity

`3. Service Health Heatmap`

- Chart type: matrix heatmap
- Purpose: help users identify hotspots across services and environments

`4. Ongoing Investigations Strip`

- Purpose: show currently running investigations with agent progress and ETA

`5. Latest Agent Activity Feed`

- Purpose: reveal that the system is actively reasoning, not merely polling for data

`6. MTTA and MTTR Snapshot Cards`

- Purpose: provide operational context and a management-friendly reliability lens
- Note: these can be seeded for demo realism even if historical data is limited

### Incident Command Center Panels

`1. Incident Header Panel`

- Shows severity, status, service ownership, open duration, and affected services
- Must contain the single most important information above the fold

`2. Root-Cause Summary Card`

- Shows the top hypothesis, current confidence, and why the system believes it
- Includes direct links to supporting evidence

`3. Confidence Breakdown Widget`

- Shows overall confidence and component contributors
- Must explain why confidence is not 100 percent

`4. Agent Activity Panel`

- Shows each agent, status, timestamps, summary, and whether it was re-run
- Helps judges and users understand the multi-agent architecture live

`5. Investigation Timeline`

- Shows incident creation, signal ingestion, agent milestones, and human actions in order
- Should support replay mode for demo storytelling

`6. Metrics Anomaly Chart`

- Chart type: multi-series line chart
- Displays latency, error rate, saturation, or custom incident metrics
- Highlights incident start and deployment moments as vertical markers

`7. Log Fingerprint Table`

- Shows clustered error patterns with count, first seen, last seen, affected service, and severity
- Prevents raw log noise from overwhelming the user

`8. Deployment Correlation Card`

- Shows recent deploys, config changes, risk level, and time delta from incident onset
- Visual goal: make change correlation instantly legible

`9. Evidence Graph Panel`

- Uses React Flow to show relationships among incident, services, deployments, evidence clusters, and hypotheses
- This is one of the product’s most differentiated panels

`10. Recommendation Checklist`

- Groups actions into immediate, short-term, and long-term buckets
- Each action includes risk, reversibility, and confidence

`11. Contradictions and Unknowns Panel`

- Shows what the system is unsure about
- Critical for trust because it demonstrates restraint

`12. Customer Impact Panel`

- Shows synthetic or real customer-facing signals such as complaint volume, impacted workflow, and urgency summary

`13. Stakeholder Update Draft Panel`

- Optional but valuable for the demo
- Generates a concise human-readable update summarizing impact, current hypothesis, and next steps

### Charts

Required charts:

- Severity distribution chart
- Metrics anomaly chart
- Signal volume trend chart
- Service health heatmap
- Confidence contribution bar chart

Chart design rules:

- Avoid decorative chart junk
- Use consistent colors for severity and confidence
- Annotate meaningful events directly on the chart

### Panels

Required panels:

- Incident header
- Root-cause summary
- Agent feed
- Timeline
- Evidence graph
- Recommendations
- Contradictions and unknowns

Every panel should answer one operational question.

## 21. Incident Simulation Flow

The demo must be deterministic, visually compelling, and technically honest. It should reuse the real ingestion and orchestration pathways rather than a fake front-end-only animation.

### Primary Demo Scenario

Scenario name:

- `checkout-db-pool-regression`

Narrative:

- A canary deployment to the `checkout-service` changes database pool configuration from a safe value to an aggressively low value.
- Traffic remains normal, but connection acquisition time spikes.
- Users begin reporting checkout failures.
- Error rate and latency rise rapidly.

### Step-by-Step Simulation

1. The judge opens `/simulator`.
2. The simulator presents 2 to 3 scenario cards, with the primary scenario preselected.
3. The judge or presenter clicks `Launch Incident`.
4. The backend creates a `simulation_run` and begins replaying fixture events.
5. A deployment event for `checkout-service` is ingested first.
6. Metric anomalies arrive next: p95 latency climbs, error rate rises, and saturation indicators worsen.
7. Log signals arrive showing repeated connection-pool exhaustion and timeout errors.
8. Customer feedback signals arrive indicating that checkout hangs or fails after payment submission.
9. The backend auto-creates a `P1` incident and starts the investigation workflow.
10. The frontend transitions to the new incident detail page.
11. The Coordinator Agent appears as `planning`.
12. Log, Metrics, and Deployment agents begin in parallel and animate into view.
13. The Log Agent finds clustered `timeout acquiring database connection` fingerprints.
14. The Metrics Agent determines that latency and error rate spiked immediately after the deployment, while traffic remained within expected range.
15. The Deployment Agent identifies the canary deploy as the most suspicious recent change.
16. The Review Agent confirms that the three findings are mutually reinforcing and well-cited.
17. The Root Cause Agent ranks `misconfigured database connection pool in checkout-service canary deployment` as the top hypothesis.
18. The Recommendation Agent proposes rollback of the canary, restoration of prior pool settings, and follow-up guardrails.
19. The dashboard highlights the top hypothesis and reveals the full evidence graph.
20. The presenter resolves the incident manually to show human-in-the-loop control.

### Why This Scenario Works

- It produces strong signals across every required evidence class
- It is easy for judges to understand quickly
- It demonstrates real correlation rather than vague AI summarization
- It ends with a credible operational recommendation

### Backup Scenario

A secondary scenario should exist:

- `payments-dependency-latency`

Purpose:

- Demonstrates that Sentinel AI can distinguish downstream dependency slowness from a direct bad deploy

## 22. Security Considerations

Even as a hackathon project, Sentinel AI should reflect production-grade security thinking.

- Tenant isolation should be designed from day one through organization and project scoping, even if demo mode uses seeded data.
- Secrets must be stored only in Vercel and Railway environment configuration, never in source control.
- All LLM calls must originate server-side. No provider keys may touch the browser.
- Incoming signal payloads must be size-limited and schema-validated to prevent ingestion abuse.
- Potentially sensitive log content should pass through a redaction layer before being sent to external models.
- Prompt injection risk should be treated seriously when ingesting untrusted text such as logs or customer comments. Prompts should explicitly instruct agents to treat evidence as data, not instructions.
- Recommendation outputs must never trigger automated infrastructure changes in the MVP.
- Audit logs should capture human overrides, incident resolution, prompt version used, and recommendation exposure.
- Transport should use TLS in all deployed environments.
- Database access should use least-privilege credentials.
- Rate limiting should protect ingestion and simulation endpoints from abuse.
- If authentication is added beyond demo mode, use a well-supported provider with session expiration, organization membership, and role-based access control.

## 23. Scalability Considerations

The MVP need not solve hyperscale observability ingestion, but the architecture should scale cleanly as the product matures.

- Frontend scaling is straightforward because Vercel can scale stateless web traffic horizontally.
- API scaling should remain stateless; long-running investigation work belongs in the worker process.
- Agent workflows should be queued so spikes in incident volume do not block API responsiveness.
- Redis is recommended to decouple ingestion and orchestration at higher load.
- Postgres tables containing `signal_events` and `incident_events` should eventually support partitioning by time or organization if volume grows materially.
- The evidence transformation layer should summarize and cluster raw data before sending it to models to control token cost.
- Model calls should be cached or short-circuited when identical reruns occur without new evidence.
- Streaming updates should use SSE initially for simplicity; if fan-out becomes a bottleneck, a pub-sub layer can distribute events efficiently.
- Historical incident retrieval should remain optional until there is enough data to justify embedding storage and vector search costs.

Scalability trade-off:

- Chosen: queue-backed async orchestration with relational source of truth
- Avoided: event-stream infrastructure like Kafka for MVP
- Why: the current need is trustworthy workflow execution, not internet-scale telemetry ingestion

## 24. Future Roadmap

### Phase 1: Hackathon MVP

- Deterministic simulator
- Incident overview and command center
- Three specialist agents plus review, root-cause, and recommendation stages
- Confidence breakdown and evidence citations
- Manual resolve workflow

### Phase 2: Real Integrations

- Datadog or OpenTelemetry metric ingestion
- Log provider adapters
- Deployment adapters from CI or GitHub
- Slack or Teams incident notifications

### Phase 3: Learning and Memory

- Similar incident retrieval
- Runbook retrieval with embeddings
- Human feedback loop for recommendation quality
- Incident pattern analytics across services

### Phase 4: Enterprise Readiness

- Authentication and SSO
- RBAC and tenant administration
- Audit dashboards
- Retention controls and compliance posture

### Phase 5: Advanced Operational Assistance

- Guided postmortem generation
- Safe automation suggestions for rollback workflows
- Change-risk forecasting before deployments
- Service ownership and dependency intelligence

## 25. Development Phases

Implementation should be milestone-driven. Each phase must produce something testable and demo-visible.

### Milestone 1: Repo Foundation and Shared Contracts

- Align the Turbo monorepo structure
- Create backend app skeleton
- Create shared type package
- Define design tokens and initial dashboard shell

Exit criteria:

- Monorepo builds cleanly
- Shared contracts are importable
- Frontend and backend stubs run locally

### Milestone 2: Database and Core API

- Model incidents, signals, evidence, agent runs, hypotheses, and recommendations
- Add migrations
- Implement core incident and simulation endpoints

Exit criteria:

- Incidents can be created and read
- Simulations can be listed and launched
- Timeline and evidence records persist correctly

### Milestone 3: Simulation Engine

- Build deterministic scenario fixture format
- Implement seeded signal replay
- Auto-create incidents from scenario data

Exit criteria:

- A scenario produces signals and an incident without manual database steps

### Milestone 4: Agent Workflow

- Implement LangGraph state and nodes
- Add Coordinator, Log, Metrics, and Deployment agents
- Add Review, Root Cause, and Recommendation agents

Exit criteria:

- A simulation run produces persisted findings, hypotheses, and recommendations

### Milestone 5: Dashboard Experience

- Build incident overview page
- Build Incident Command Center page
- Add live SSE updates
- Add charts, graph, and agent feed

Exit criteria:

- A live investigation is visible end to end in the UI

### Milestone 6: Explainability and Confidence

- Implement evidence citations
- Implement confidence breakdown logic
- Add contradictions and unknowns panel

Exit criteria:

- Judges can inspect why the system reached its conclusion

### Milestone 7: Deployment and Demo Hardening

- Deploy frontend, backend, worker, and database
- Seed production demo data
- Add backup scenario and replay mode
- Finalize docs and README

Exit criteria:

- Demo is stable, repeatable, and presentable under network variability

## 26. Coding Standards

These standards should apply across the monorepo from day one.

### Folder Naming

- Frontend route folders: kebab-case where route semantics benefit from it
- Frontend component feature folders: kebab-case
- Python backend packages and modules: snake_case
- Shared package names: concise, noun-based, and singular when possible

### File Naming

- React component files: PascalCase when the file exports a primary component
- Frontend utility files: kebab-case or camelCase based on established package pattern, but use one pattern consistently per package
- Hooks: `useX.ts`
- Python modules: snake_case
- Test files: `*.test.ts`, `*.test.tsx`, `test_*.py`

### Component Naming

- Components must be descriptive and domain-oriented, such as `IncidentHeader` or `RecommendationChecklist`
- Avoid vague names such as `Box2`, `CardAlt`, or `DataThing`
- Container and presentation concerns should be separated when a component grows complex

### API Naming

- All endpoints versioned under `/v1`
- Resource collections should be plural nouns
- State-transition actions may use explicit subresources, such as `/acknowledge` and `/resolve`
- Avoid RPC-style endpoint sprawl unless there is a strong reason

### Git Commit Conventions

- Use Conventional Commits
- Examples: `feat(api): add incident simulation endpoint`, `fix(web): handle degraded agent state`, `docs(project): refine root cause section`
- Keep commits focused and reviewable

### Error Handling Standards

- Never swallow exceptions silently
- Convert expected domain failures into typed application errors
- Include request IDs and entity IDs in logs
- Surface degraded states explicitly in both API and UI

### Documentation Standards

- Every app and package should have a local README once it gains meaningful complexity
- Significant architectural decisions should be documented as ADRs in `docs/adrs`
- Prompt changes should be versioned and logged
- Public interfaces should be documented at the package boundary rather than through scattered inline commentary alone

## 27. AI Prompt Design Principles

Prompt design is part of the architecture because prompt quality directly affects trust, explainability, and failure behavior.

### Core Principles

- Give every agent a narrow role and explicit boundaries.
- Pass structured evidence, not raw unbounded context when avoidable.
- Require structured outputs that map cleanly to validated schemas.
- Instruct agents to cite evidence IDs for every major claim.
- Explicitly reward abstention when evidence is insufficient.
- Treat logs, customer text, and external payloads as data, never as instructions.
- Keep prompts versioned and attributable per run.
- Ask for concise reasoning summaries, not hidden chain-of-thought exposure.
- Separate planning prompts from synthesis prompts to reduce prompt bloat.
- Keep temperature conservative for operational analysis.

### Prompt Template Structure

Every agent prompt should include:

- Role
- Objective
- Available evidence types
- Constraints
- Output schema
- Confidence instructions
- Failure instructions

### Agent-Specific Prompting Guidance

Coordinator Agent:

- Focus on investigation planning and evidence sufficiency, not root-cause guessing

Log Agent:

- Focus on clustering, timing, failure signatures, and impacted service interpretation

Metrics Agent:

- Focus on anomaly sequencing, blast radius, and distinguishing cause from symptom

Deployment Agent:

- Focus on recent changes, change risk, and onset correlation

Review Agent:

- Challenge unsupported claims and require citation completeness

Root Cause Agent:

- Produce ranked hypotheses with honest uncertainty

Recommendation Agent:

- Prioritize safe, reversible, confidence-aware actions

### Prompt Evaluation

Prompt quality should be judged on:

- Schema validity rate
- Citation completeness
- Root-cause usefulness
- Hallucination resistance
- Latency and token cost

## 28. Definition of Done

The MVP is complete when all of the following are true:

- A judge can launch a deterministic simulation from the UI.
- The system creates an incident and begins investigation automatically.
- At least the Coordinator, Log, Metrics, Deployment, Review, Root Cause, and Recommendation stages execute visibly.
- The dashboard updates in near real time as the investigation progresses.
- The system presents a top hypothesis with evidence citations and a confidence breakdown.
- The system presents corrective recommendations grouped by action horizon.
- The UI includes a distinct Incident Command Center rather than a generic CRUD page.
- The architecture is modular, typed, and deployable through the declared stack.
- The backend persists incidents, findings, hypotheses, recommendations, and timeline events.
- The product supports manual human resolution and override.
- The repo contains documentation strong enough that another engineer can continue building without product ambiguity.

## 29. Known Risks

`Risk 1: Hallucinated root causes`

- Mitigation: structured outputs, Review Agent, evidence citations, abstention rules, visible confidence penalties

`Risk 2: Demo appears scripted rather than intelligent`

- Mitigation: reuse real ingestion and orchestration paths, expose agent progress live, show evidence graph and contradictions

`Risk 3: Model latency slows the live demo`

- Mitigation: bounded prompts, small evidence summaries, conservative retry policy, backup completed replay mode

`Risk 4: Too much scope for hackathon duration`

- Mitigation: prioritize one excellent scenario and one excellent dashboard flow over broad integration count

`Risk 5: Frontend becomes visually generic`

- Mitigation: define a strong visual language early and build core panels before polish gets rushed

`Risk 6: Data model becomes blob-heavy`

- Mitigation: keep relational fields explicit for core entities and use JSONB only where needed

`Risk 7: Confidence score looks fake or arbitrary`

- Mitigation: expose contributing factors and penalty logic rather than a single unexplained number

`Risk 8: Worker orchestration becomes brittle`

- Mitigation: keep the graph small, deterministic, and well-instrumented

`Risk 9: Security is under-modeled`

- Mitigation: use synthetic data for demo, keep keys server-side, document tenant and redaction strategy clearly

`Risk 10: Judges ask about production scaling beyond MVP`

- Mitigation: prepare a crisp explanation of the bounded monolith now and the queue-backed scaling path later

## 30. Hackathon Demo Strategy

Judges should experience Sentinel AI as a focused, coherent story:

### Demo Narrative

1. Show the problem in one sentence: modern incidents generate disconnected evidence.
2. Launch a live simulation rather than describing a hypothetical.
3. Let the agents begin in parallel so the multi-agent architecture is visible immediately.
4. Walk through the evidence graph, timeline, and confidence breakdown.
5. Show the top root cause and recommended next actions.
6. Emphasize that a human remains in command by resolving the incident manually.
7. Close with architecture quality: deterministic LangGraph workflow, typed contracts, production-grade monorepo.

### What Judges Should Notice

- The system investigates, not just summarizes
- Multiple agents have distinct roles
- The AI explains why it believes something
- The product feels like a real SaaS control plane
- The architecture is credible beyond the hackathon

### Demo Delivery Guidance

- Keep the primary live flow under 6 minutes
- Have a replayable completed incident ready as backup
- Use one primary scenario and one backup scenario only
- Do not drown judges in infra detail before they understand the product value

## 31. README Outline

The repository `README.md` should eventually include:

1. Project name and tagline
2. What Sentinel AI is
3. Why it exists
4. Demo screenshots or GIFs
5. Architecture overview
6. Monorepo structure
7. Prerequisites
8. Environment variables
9. Local development setup
10. Running the frontend
11. Running the backend and worker
12. Running the simulator
13. Prompt and agent overview
14. Deployment instructions
15. Testing and linting commands
16. Demo script
17. Known limitations
18. Future roadmap

## 32. Judge FAQ

### 1. Why use multiple agents instead of one strong model?

Because incident investigation is naturally decomposable. Logs, metrics, and deployments require different reasoning patterns. Specialist agents improve clarity, parallelism, and debuggability.

### 2. Why use LangGraph?

Because the workflow needs explicit state, parallel branches, retries, and conditional routing. LangGraph makes those control-flow decisions inspectable and production-friendly.

### 3. Why choose a bounded monolith instead of microservices?

The main complexity is reasoning and workflow, not service decomposition. A bounded monolith is faster to build, easier to debug, and still scalable for the MVP.

### 4. How is the system explainable?

Every major finding references evidence items, every top hypothesis has a confidence breakdown, and the Review Agent removes or weakens unsupported claims.

### 5. How do you prevent hallucinated root causes?

We require structured outputs, explicit citations, contradiction tracking, and abstention when evidence is insufficient. The system can end in `needs-human-review`.

### 6. Why FastAPI and Python for the backend?

Python is the strongest ecosystem for AI orchestration, and FastAPI provides typed APIs, async support, and fast iteration for product development.

### 7. Why Postgres as the primary store?

Incidents, findings, recommendations, and timelines are highly relational. Postgres gives strong consistency and enough flexibility through JSONB for raw signal metadata.

### 8. What does Redis add if you include it?

Redis improves queueing, hot caching, rate limiting, and live event fan-out. It is recommended for scale but not strictly required for the first demo.

### 9. Why is ChromaDB optional?

Vector retrieval is useful for historical incidents and runbooks, but it is not necessary to prove the core multi-agent incident workflow in the MVP.

### 10. How is confidence computed?

Confidence is not a guess. It is derived from evidence quality, cross-agent agreement, temporal alignment, model certainty, and contradiction penalties.

### 11. What happens if one agent fails?

The run continues in degraded mode. The failure is logged, shown in the UI, and factored into overall confidence rather than hidden.

### 12. How do you handle human oversight?

Humans can acknowledge, rerun, override, and resolve incidents. Recommendations are advisory. The system never auto-remediates in the MVP.

### 13. Where does Codex fit into this architecture?

Codex is reserved for engineering-oriented interpretation when a root cause points to code or configuration changes. It may draft suggestions but does not change systems automatically.

### 14. How do you keep costs under control?

We normalize and cluster evidence before model calls, keep prompts narrow, avoid unnecessary reruns, and separate specialist analysis from final synthesis.

### 15. Why use React Flow?

It provides a strong way to visualize relationships between services, deployments, evidence, and hypotheses, which makes the investigation more understandable and memorable.

### 16. Why use Recharts instead of custom charts?

It accelerates delivery while still producing clean, readable charts suitable for an operator dashboard.

### 17. How would you productionize authentication?

Add organization-aware auth with RBAC, session management, and least-privilege service credentials. The data model already anticipates tenant boundaries.

### 18. How would this scale to real telemetry volume?

The API remains stateless, investigations move to workers, Redis or a queue handles bursts, and the database can partition high-volume event tables over time.

### 19. What is the biggest intentional shortcut in the hackathon version?

Real vendor integrations are not the focus. We use a deterministic simulator first so we can prove the core reasoning workflow and product experience cleanly.

### 20. What would you build next if given two more weeks?

Real integrations, historical incident retrieval, feedback-driven prompt tuning, and richer stakeholder communication workflows would be the next highest-value steps.
