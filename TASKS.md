# Sentinel AI Implementation Backlog

Document status: Implementation source of truth derived from [PROJECT.md](/home/amit/Desktop/sentAI/PROJECT.md).

Planning assumptions:

- Planning date: Thursday, July 16, 2026
- Hackathon duration assumption: 3 days, from Thursday, July 16, 2026 through Saturday, July 18, 2026
- Team size: 3 developers
- Developer A focus: Frontend, product UX, docs app
- Developer B focus: Backend, database, infrastructure
- Developer C focus: AI orchestration, simulation, integration
- Task sizing rule: every task should fit into a 30 to 90 minute implementation session

Backlog conventions:

- `Critical` means the MVP cannot ship without it.
- `High` means required for the judged demo or a stable architecture.
- `Medium` means valuable, but can slip if time becomes constrained.
- `Low` means polish or supporting work.
- Owners identify the default driver; pair review is still encouraged.

## Epic 1

Project Foundation

### TASK-001
**Title:** Normalize the monorepo structure to match the architecture plan  
**Description:** Reshape the starter TurboRepo layout so it supports `apps/web`, `apps/docs`, `apps/api`, shared packages, infra notes, docs, and scripts without ad hoc folder creation later.  
**Objective:** Create the canonical repository skeleton before implementation fans out.  
**Dependencies:** None  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `chore/task-001-monorepo-layout`  
**Definition of Done:** The repo structure matches the intended end-state closely enough that each workstream has a stable home.  
**Acceptance Criteria:**
- Required top-level folders exist
- Existing `apps/web` and `apps/docs` remain functional
- Placeholder folders for backend, packages, docs, and infra are added intentionally
- No temporary or ambiguous folder names remain
**Potential Risks:**
- Early path changes can cause merge conflicts
- Teams may start coding against outdated folder assumptions
**Testing Checklist:**
- Run file tree inspection for expected folders
- Run workspace install or build command
- Confirm `apps/web` still resolves correctly

### TASK-002
**Title:** Scaffold the Python backend application workspace  
**Description:** Create the `apps/api` skeleton with `pyproject.toml`, source layout, test folders, script folders, and placeholder modules for FastAPI and the worker runtime.  
**Objective:** Give backend and AI work a stable application boundary.  
**Dependencies:** TASK-001  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `chore/task-002-api-scaffold`  
**Definition of Done:** `apps/api` exists with a production-style Python application layout and importable package root.  
**Acceptance Criteria:**
- `apps/api/src/sentinel_api` package exists
- Test, migration, script, and worker folders are present
- Python dependency manifest is committed
- Local import path is documented in the backend README stub
**Potential Risks:**
- Inconsistent Python tooling choices can slow later work
- Weak initial layout creates churn when agent code lands
**Testing Checklist:**
- Run Python package discovery or import smoke check
- Verify source and tests directories resolve correctly
- Confirm workspace paths do not conflict with frontend apps

### TASK-003
**Title:** Scaffold shared packages for contracts, API client, prompts, and schemas  
**Description:** Add `packages/types`, `packages/api-client`, `packages/prompts`, and `packages/schemas` with package manifests and starter source folders.  
**Objective:** Prevent contract drift by giving frontend and backend a shared package strategy early.  
**Dependencies:** TASK-001  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `chore/task-003-shared-packages`  
**Definition of Done:** All planned shared packages exist and can be referenced by the workspace.  
**Acceptance Criteria:**
- Package manifests exist for all planned shared packages
- Source folders reflect the architecture plan
- Turbo workspace recognizes the new packages
- No placeholder package uses unclear naming
**Potential Risks:**
- Package naming drift can leak into imports everywhere
- Missing package boundaries can force later refactors
**Testing Checklist:**
- Run workspace package discovery
- Verify package names resolve from the root manifest
- Confirm no duplicate package names exist

### TASK-004
**Title:** Align Turbo tasks and workspace scripts for multi-surface development  
**Description:** Extend root scripts and Turbo task definitions so frontend, backend, tests, linting, and type checks have predictable command names.  
**Objective:** Make the repo operable as one product rather than isolated app islands.  
**Dependencies:** TASK-002, TASK-003  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `chore/task-004-turbo-scripts`  
**Definition of Done:** Root-level commands cover the full stack and reflect the implementation plan.  
**Acceptance Criteria:**
- Root scripts exist for build, dev, lint, type-check, and test flows
- Turbo tasks include backend-aware entries
- Workspace commands are named consistently
- Script expectations are documented briefly
**Potential Risks:**
- Incomplete task wiring creates invisible broken workflows
- Overly clever task naming confuses contributors
**Testing Checklist:**
- Run root script listing or package script inspection
- Smoke test build and lint commands
- Confirm no script references missing apps or packages

### TASK-005
**Title:** Create environment template files and configuration inventory  
**Description:** Define expected environment variables for Vercel, Railway, Neon, model providers, and optional Redis in one authoritative place.  
**Objective:** Eliminate hidden config dependencies before feature work starts.  
**Dependencies:** TASK-002, TASK-004  
**Estimated Time:** 45 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `docs/task-005-env-inventory`  
**Definition of Done:** Every runtime dependency has a named environment variable and documented owner.  
**Acceptance Criteria:**
- `.env.example` or equivalent template exists where appropriate
- Frontend-safe and server-only variables are clearly separated
- Optional dependencies are labeled as optional
- Missing-secret failure behavior is documented
**Potential Risks:**
- Secret sprawl can cause blocked deploys late in the hackathon
- Client/server env confusion can introduce security issues
**Testing Checklist:**
- Compare template names against config plan
- Verify no secret values are committed
- Confirm backend and frontend env scopes are explicit

### TASK-006
**Title:** Add ADR, contribution, and implementation standards skeleton  
**Description:** Create the initial docs structure for ADRs, contribution guidelines, naming conventions, and backlog usage so the team works from one playbook.  
**Objective:** Reduce ambiguity across three developers moving quickly.  
**Dependencies:** TASK-001  
**Estimated Time:** 45 minutes  
**Priority:** High  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `docs/task-006-team-standards`  
**Definition of Done:** Core implementation conventions are documented in the repo.  
**Acceptance Criteria:**
- `docs/adrs` exists with placeholders
- Contribution or working-agreement notes exist
- Naming and commit conventions are discoverable
- Backlog usage rules are documented briefly
**Potential Risks:**
- Without written standards, code style diverges rapidly
- Architectural decisions may get lost in chat
**Testing Checklist:**
- Review docs paths for completeness
- Confirm links from the root docs are valid
- Ensure conventions match `PROJECT.md`

## Epic 2

Shared Types and Contracts

### TASK-007
**Title:** Define core cross-platform enums and vocabulary  
**Description:** Create shared definitions for severity, incident status, signal type, agent name, recommendation category, and common status-like values.  
**Objective:** Lock the product language before API and UI implementation diverge.  
**Dependencies:** TASK-003  
**Estimated Time:** 45 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-007-core-enums`  
**Definition of Done:** Core enums exist in the shared contract package and match `PROJECT.md`.  
**Acceptance Criteria:**
- Enum names and values mirror the architecture document
- No duplicate local enum copies exist in the web app
- Backend contract mapping is straightforward
- Naming is stable and human-readable
**Potential Risks:**
- Divergent status strings cause API/UI bugs
- Renaming later creates wide churn
**Testing Checklist:**
- Validate exports from the shared types package
- Compare values against `PROJECT.md`
- Confirm downstream import paths are ergonomic

### TASK-008
**Title:** Define incident, service, deployment, and evidence interfaces  
**Description:** Add shared interfaces for incident summaries, incident detail payloads, service records, deployment records, signal events, and evidence items.  
**Objective:** Establish the MVP read-model shape for dashboard development.  
**Dependencies:** TASK-007  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-008-incident-contracts`  
**Definition of Done:** Core domain interfaces exist and are usable by the frontend and API client packages.  
**Acceptance Criteria:**
- Types cover the main incident and evidence screens
- Optional versus required fields are intentionally chosen
- Naming aligns with API design
- No database-only fields leak unnecessarily into UI contracts
**Potential Risks:**
- Overfitting to ORM fields can make the UI brittle
- Missing fields can force duplicate ad hoc interfaces
**Testing Checklist:**
- Type-check package exports
- Compare interfaces against planned endpoint responses
- Spot-check incident detail coverage for dashboard needs

### TASK-009
**Title:** Define agent, finding, hypothesis, recommendation, and confidence contracts  
**Description:** Model the shared shapes used by the agent feed, root-cause stack, recommendation panels, and confidence visualizations.  
**Objective:** Keep AI outputs structured and UI-ready from the start.  
**Dependencies:** TASK-007  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-009-agent-contracts`  
**Definition of Done:** Shared AI-related interfaces cover the full investigation experience without local duplication.  
**Acceptance Criteria:**
- `AgentRunSummary`, `AgentFinding`, `Hypothesis`, and `Recommendation` types exist
- Confidence breakdown shape is defined
- Citation and contradiction fields are represented explicitly
- Types are ready for both live and replay modes
**Potential Risks:**
- Weak output contracts increase hallucination-handling complexity
- UI may need last-minute rewrites if fields are underspecified
**Testing Checklist:**
- Type-check exports
- Compare fields against agent architecture section
- Verify confidence and citation fields exist where required

### TASK-010
**Title:** Define dashboard, simulation, pagination, and API error contracts  
**Description:** Add read models for overview widgets, simulation scenarios, paginated lists, graph nodes and edges, timeline entries, and error responses.  
**Objective:** Support the overview page, simulator, and shared API UX patterns.  
**Dependencies:** TASK-007, TASK-008, TASK-009  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-010-dashboard-contracts`  
**Definition of Done:** Shared supporting contracts exist for overview pages, graph data, and reusable API patterns.  
**Acceptance Criteria:**
- Overview and simulation interfaces map to planned pages
- Error and pagination shapes are consistent
- Graph node and edge types support React Flow needs
- Timeline types support live and replay rendering
**Potential Risks:**
- Missing support types lead to inconsistent API responses
- Graph and timeline adapters may become harder to implement
**Testing Checklist:**
- Type-check exports
- Compare interfaces against API and dashboard sections
- Verify graph and timeline fields are sufficient

### TASK-011
**Title:** Add schema validation mirrors for critical frontend-facing payloads  
**Description:** Create runtime validation schemas for the most important shared contracts, especially incident detail, overview data, agent outputs, and recommendation payloads.  
**Objective:** Catch malformed API or model output early at integration boundaries.  
**Dependencies:** TASK-008, TASK-009, TASK-010  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-011-runtime-schemas`  
**Definition of Done:** Critical payloads have runtime schema coverage in the shared schema package.  
**Acceptance Criteria:**
- Schema package structure mirrors key contract groupings
- At least the incident, agent, hypothesis, and recommendation models are covered
- Validation failure handling strategy is documented
- Schema naming matches shared type naming
**Potential Risks:**
- Type and schema drift can create false confidence
- Over-validating everything can burn time unnecessarily
**Testing Checklist:**
- Validate schema exports
- Run sample object parse checks
- Compare schema fields against shared interfaces

### TASK-012
**Title:** Bootstrap the typed API client package boundary  
**Description:** Create the package structure and endpoint modules for incidents, dashboard, simulations, agent runs, and shared transport helpers.  
**Objective:** Give the frontend one consistent data access layer.  
**Dependencies:** TASK-010  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-012-api-client-scaffold`  
**Definition of Done:** The API client package has clear module boundaries and shared request/response typing hooks.  
**Acceptance Criteria:**
- Endpoint modules are scaffolded by domain
- Shared fetch helper boundary exists
- Exports are clean and minimal
- Package is ready for implementation tasks later
**Potential Risks:**
- Frontend may bypass the client package if setup is unclear
- Inconsistent request wrappers can appear in pages
**Testing Checklist:**
- Type-check package exports
- Verify import ergonomics from `apps/web`
- Confirm endpoint module naming matches API design

## Epic 3

Backend Infrastructure

### TASK-013
**Title:** Bootstrap the FastAPI application entrypoint and router registry  
**Description:** Create the backend application bootstrap with versioned API registration, base middleware hooks, and router namespaces that match the planned resources.  
**Objective:** Establish the control plane entrypoint for all backend work.  
**Dependencies:** TASK-002, TASK-004  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-013-fastapi-bootstrap`  
**Definition of Done:** The backend starts with a versioned API structure and empty resource routers wired in.  
**Acceptance Criteria:**
- `main.py` exposes the FastAPI app
- `/v1` router namespace exists
- Planned router modules have placeholders
- Startup path is documented in the backend README
**Potential Risks:**
- Inconsistent route registration becomes painful later
- Skipping versioning now creates avoidable migration work
**Testing Checklist:**
- Start the backend locally
- Verify route registry loads without errors
- Check placeholder endpoints appear in OpenAPI

### TASK-014
**Title:** Implement typed application configuration and settings loading  
**Description:** Centralize environment parsing for app URLs, database connections, model providers, queue settings, investigation thresholds, and simulation timing.  
**Objective:** Keep configuration explicit, validated, and server-side only.  
**Dependencies:** TASK-005, TASK-013  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-014-typed-config`  
**Definition of Done:** The backend can boot from a validated settings object without scattered environment reads.  
**Acceptance Criteria:**
- Config module covers all known runtime settings
- Required versus optional config is explicit
- Defaults are intentional and documented
- No direct environment reads are needed outside config
**Potential Risks:**
- Missing config fields can block deploys late
- Weak typing can hide broken environment values
**Testing Checklist:**
- Load config with sample env values
- Verify missing required values fail clearly
- Confirm optional values have sane defaults

### TASK-015
**Title:** Set up SQLAlchemy base, session management, and database bootstrap  
**Description:** Add database engine, session factory, declarative base, and lifecycle helpers for request-scoped database access.  
**Objective:** Provide safe and reusable persistence infrastructure.  
**Dependencies:** TASK-013, TASK-014  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-015-db-bootstrap`  
**Definition of Done:** Backend services can obtain database sessions through a consistent mechanism.  
**Acceptance Criteria:**
- Declarative base exists
- Session factory and engine configuration exist
- Request-safe session dependency is planned or stubbed
- Local connection bootstrapping is documented
**Potential Risks:**
- Poor session handling can cause transaction leaks
- Connection setup mistakes will block all backend work
**Testing Checklist:**
- Run a database connectivity smoke check
- Verify a test session can be created and closed
- Confirm session module import paths are stable

### TASK-016
**Title:** Add structured logging, request IDs, and runtime context middleware  
**Description:** Implement JSON logging and middleware that attaches request IDs and other contextual fields needed for incident and agent observability.  
**Objective:** Make the system debuggable before complex workflows are added.  
**Dependencies:** TASK-013, TASK-014  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-016-structured-logging`  
**Definition of Done:** Backend logs are structured and ready to carry request, incident, and run context.  
**Acceptance Criteria:**
- Log formatter outputs structured fields
- Request ID middleware or equivalent context exists
- Logging helper is reusable by API and worker code
- Required log fields are documented
**Potential Risks:**
- Unstructured logs make agent debugging painful
- Context propagation may break across worker boundaries
**Testing Checklist:**
- Start the app and inspect sample logs
- Confirm request IDs appear on HTTP requests
- Verify logging helper can be imported in worker modules

### TASK-017
**Title:** Implement typed exception classes and global error handlers  
**Description:** Add domain-oriented exception types and centralized error translation into stable API error responses.  
**Objective:** Prevent inconsistent error shapes and make failures product-visible.  
**Dependencies:** TASK-013, TASK-014  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-017-error-handling`  
**Definition of Done:** Known application failures can be raised and returned consistently.  
**Acceptance Criteria:**
- Core exception hierarchy exists
- Global handlers map exceptions to predictable responses
- Error codes and messages are machine-readable
- Unexpected errors still log with context
**Potential Risks:**
- Hidden raw exceptions leak internal details
- Overbroad handlers can swallow important debugging information
**Testing Checklist:**
- Trigger sample error paths locally
- Verify response shape matches the contract
- Confirm unexpected errors are logged with stack traces

### TASK-018
**Title:** Wire dependency injection helpers for settings, sessions, and services  
**Description:** Create FastAPI dependency helpers for config, database sessions, repositories, and service-layer composition.  
**Objective:** Keep routers thin and backend construction consistent.  
**Dependencies:** TASK-014, TASK-015, TASK-017  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-018-di-wiring`  
**Definition of Done:** Core backend dependencies can be resolved through a standard injection layer.  
**Acceptance Criteria:**
- Dependency module exists
- Session and settings dependencies are reusable
- Service construction path is clear
- Router code will not need ad hoc initialization
**Potential Risks:**
- Manual object creation in routers will create duplication
- Cyclic imports may appear if modules are organized poorly
**Testing Checklist:**
- Import dependencies from sample router modules
- Verify session and config helpers compose cleanly
- Run backend startup smoke test

### TASK-019
**Title:** Bootstrap the worker runtime and queue abstraction  
**Description:** Create the worker entrypoint, basic run loop, and queue publisher/consumer interfaces for background investigations.  
**Objective:** Separate long-running orchestration from synchronous API handling.  
**Dependencies:** TASK-002, TASK-014, TASK-015  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-019-worker-bootstrap`  
**Definition of Done:** A worker process can be started independently and is ready to receive investigation work.  
**Acceptance Criteria:**
- Worker entrypoint exists
- Queue abstraction is defined even if backed by a simple implementation initially
- API-side publishing boundary is identifiable
- Worker and API can share config and logging
**Potential Risks:**
- Tight coupling between API and worker can block scaling later
- Queue choice may introduce avoidable complexity
**Testing Checklist:**
- Start the worker process locally
- Verify the worker loads config and logging successfully
- Smoke test a no-op job through the abstraction

### TASK-020
**Title:** Add health and readiness services for API and worker dependencies  
**Description:** Implement liveness and readiness checks that validate app startup, database connectivity, and worker dependency availability.  
**Objective:** Make local and deployed environments easier to verify quickly.  
**Dependencies:** TASK-013, TASK-015, TASK-019  
**Estimated Time:** 45 minutes  
**Priority:** High  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-020-health-ready`  
**Definition of Done:** Health and readiness checks exist and reflect key dependency status.  
**Acceptance Criteria:**
- Liveness and readiness boundaries are separate
- Database readiness is checked explicitly
- Worker or queue readiness is represented
- Endpoint behavior is documented
**Potential Risks:**
- Shallow readiness checks can create false confidence
- Overly strict readiness can slow local iteration
**Testing Checklist:**
- Hit health endpoints locally
- Verify failure behavior when dependencies are unavailable
- Confirm response shapes are stable

## Epic 4

Database and Persistence

### TASK-021
**Title:** Initialize Alembic migration workflow and database conventions  
**Description:** Set up migration tooling, naming conventions, revision strategy, and baseline database documentation for local and cloud environments.  
**Objective:** Establish a safe schema evolution workflow before tables are added.  
**Dependencies:** TASK-015  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-021-alembic-setup`  
**Definition of Done:** Database migrations can be created and applied through a documented workflow.  
**Acceptance Criteria:**
- Alembic is initialized under `apps/api`
- Naming conventions for revisions are documented
- Local migration commands are discoverable
- Baseline migration process works against the configured database
**Potential Risks:**
- Weak migration discipline creates broken environments later
- Team members may hand-edit schema without migrations
**Testing Checklist:**
- Generate or inspect baseline revision
- Apply migration to a local database
- Confirm downgrade strategy is understood

### TASK-022
**Title:** Model organizations, projects, and services with migrations  
**Description:** Implement the tenant and service catalog entities, including relationships, indexes, and explicit enums where needed.  
**Objective:** Create the ownership backbone for incidents and simulations.  
**Dependencies:** TASK-021  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-022-org-project-service-models`  
**Definition of Done:** Core catalog tables exist and can represent demo tenants, projects, and services.  
**Acceptance Criteria:**
- ORM models exist for organizations, projects, and services
- Relationships and key indexes match the plan
- Migration is generated and reviewed
- Fields align with `PROJECT.md`
**Potential Risks:**
- Weak service modeling hurts correlation and filtering later
- Missing indexes slow common lookup paths
**Testing Checklist:**
- Apply migration
- Create and query sample records
- Verify foreign key relationships work

### TASK-023
**Title:** Model incidents, signal events, and evidence items with migrations  
**Description:** Add the incident core tables, normalized signal storage, evidence records, and their essential constraints and indexes.  
**Objective:** Create the canonical evidence pipeline storage layer.  
**Dependencies:** TASK-022  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-023-incident-signal-evidence-models`  
**Definition of Done:** Incident and evidence persistence can store the full MVP investigation input set.  
**Acceptance Criteria:**
- ORM models exist for incidents, signal events, and evidence items
- Severity and status are typed explicitly
- Time-based and incident-based indexes are in place
- Evidence records can link back to original signal records
**Potential Risks:**
- Overusing JSON fields can weaken queryability
- Missing relationships can complicate graph and timeline views
**Testing Checklist:**
- Apply migration
- Insert and fetch sample incidents and evidence
- Verify foreign keys and indexes exist as expected

### TASK-024
**Title:** Model deployments, agent runs, and agent findings with migrations  
**Description:** Add persistence for deployment/change events, orchestration runs, and structured specialist outputs.  
**Objective:** Capture the full investigation execution trail.  
**Dependencies:** TASK-023  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-024-deployments-agent-runs-models`  
**Definition of Done:** The database can store change events, orchestration runs, and agent findings cleanly.  
**Acceptance Criteria:**
- ORM models exist for deployments, agent runs, and agent findings
- Parent-child run relationships are supported
- Confidence and prompt version fields are included
- Indexes support recent-run and service deployment lookups
**Potential Risks:**
- Weak run modeling makes replay and debugging harder
- Missing prompt references reduce traceability
**Testing Checklist:**
- Apply migration
- Insert run and finding sample data
- Query recent runs by incident and agent name

### TASK-025
**Title:** Model hypotheses, recommendations, and incident timeline events with migrations  
**Description:** Add root-cause hypothesis storage, actionable recommendation records, and ordered incident events for the timeline.  
**Objective:** Support explainability, recommendations, and replay.  
**Dependencies:** TASK-024  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-025-hypothesis-recommendation-models`  
**Definition of Done:** Root-cause and recommendation outputs can be persisted with timeline context.  
**Acceptance Criteria:**
- ORM models exist for hypotheses, recommendations, and incident events
- Rank, category, confidence, and event-type fields are explicit
- Relationship paths support incident detail queries
- Recommended indexes are included
**Potential Risks:**
- Poor event modeling can break timeline ordering
- Loose recommendation linkage weakens root-cause traceability
**Testing Checklist:**
- Apply migration
- Insert sample hypotheses and recommendations
- Query timeline entries in order

### TASK-026
**Title:** Model feedback, prompt versions, simulation scenarios, and audit logs with migrations  
**Description:** Add the supporting tables needed for prompt traceability, human feedback, scenario management, and auditability.  
**Objective:** Finish the MVP data model around governance and demo operations.  
**Dependencies:** TASK-025  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-026-supporting-models`  
**Definition of Done:** Governance and simulation support tables exist and are queryable.  
**Acceptance Criteria:**
- ORM models exist for feedback entries, prompt versions, simulation scenarios, and audit logs
- Prompt version table supports active-version lookup
- Simulation scenario metadata maps to planned demo flows
- Audit log table can store contextual JSON safely
**Potential Risks:**
- Missing prompt traceability weakens architecture credibility
- Audit logging gaps hurt demo questions on safety and control
**Testing Checklist:**
- Apply migration
- Insert sample prompt version and scenario records
- Query audit rows by entity type

### TASK-027
**Title:** Implement repository layer for incident-centered query paths  
**Description:** Build repositories for incidents, evidence, deployments, agent runs, hypotheses, recommendations, simulations, and shared list/query helpers.  
**Objective:** Keep persistence logic out of routers and services.  
**Dependencies:** TASK-022, TASK-023, TASK-024, TASK-025, TASK-026  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-027-repository-layer`  
**Definition of Done:** Common data-access paths are encapsulated behind repository interfaces.  
**Acceptance Criteria:**
- Repository modules exist for the main aggregates
- Queries for incident detail, timeline, evidence, and runs are centralized
- Write paths for findings, hypotheses, and recommendations are defined
- No router needs raw SQLAlchemy query assembly
**Potential Risks:**
- Query duplication will spread quickly without this layer
- Poor repository boundaries can create circular dependencies
**Testing Checklist:**
- Run repository-level smoke tests
- Fetch an incident detail aggregate through repositories
- Verify create/update methods handle transactions correctly

### TASK-028
**Title:** Add seed scripts for tenant, service, and demo baseline data  
**Description:** Create baseline data loading for organizations, projects, services, prompt versions, and scenario metadata needed before the simulator runs.  
**Objective:** Make demo environments reproducible.  
**Dependencies:** TASK-026, TASK-027  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-028-baseline-seed-data`  
**Definition of Done:** A fresh database can be seeded into a demo-ready starting state.  
**Acceptance Criteria:**
- Seed script creates base org, project, and service records
- Prompt version metadata can be seeded
- Simulation scenarios are registered
- Seed flow is documented
**Potential Risks:**
- Hard-coded IDs can make seeds brittle
- Missing baseline data blocks frontend and simulator work
**Testing Checklist:**
- Run seed script on a clean database
- Verify expected counts for key tables
- Confirm rerun behavior is understood

## Epic 5

API Layer

### TASK-029
**Title:** Define common API schema modules and response envelopes  
**Description:** Implement shared Pydantic models for common responses, pagination, filters, and API error envelopes used across routers.  
**Objective:** Keep the API consistent and aligned with the shared frontend contracts.  
**Dependencies:** TASK-017, TASK-027  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-029-api-common-schemas`  
**Definition of Done:** Core response shapes are defined once and reused across routers.  
**Acceptance Criteria:**
- Common schema modules exist
- Error shape matches the shared API contract
- Pagination helper schema is reusable
- Router authors have a standard pattern to follow
**Potential Risks:**
- Inconsistent responses create frontend adapter churn
- Overly generic envelopes can make APIs noisy
**Testing Checklist:**
- Validate schema imports in sample routers
- Compare shapes against shared types
- Ensure OpenAPI output looks consistent

### TASK-030
**Title:** Implement dashboard overview service and endpoint  
**Description:** Build the read model and endpoint for active incident count, severity breakdown, service health summary, recent incidents, and current investigation activity.  
**Objective:** Unlock the overview dashboard first screen.  
**Dependencies:** TASK-027, TASK-029  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-030-dashboard-overview-api`  
**Definition of Done:** The backend exposes a dashboard overview payload that matches the planned widget set.  
**Acceptance Criteria:**
- Overview endpoint exists under `/v1/dashboard/overview`
- Service layer aggregates the planned summary data
- Response shape matches the shared dashboard contract
- Empty-state behavior is deliberate
**Potential Risks:**
- Summary queries can become slow if modeled carelessly
- Missing fields can block multiple widgets at once
**Testing Checklist:**
- Call the overview endpoint with seeded data
- Verify severity and recent incident data are correct
- Check behavior with zero incidents

### TASK-031
**Title:** Implement incident list and incident creation endpoints  
**Description:** Add `/v1/incidents` support for filtering, pagination, search-ready shape, and manual incident creation.  
**Objective:** Provide the foundation for the incident overview table and simulation-created incidents.  
**Dependencies:** TASK-023, TASK-027, TASK-029  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-031-incidents-list-create-api`  
**Definition of Done:** Incidents can be created and listed through a typed API.  
**Acceptance Criteria:**
- `GET /v1/incidents` supports planned filters and pagination
- `POST /v1/incidents` creates a record cleanly
- Response models match shared contracts
- Validation rejects malformed status or severity inputs
**Potential Risks:**
- Filter semantics can drift from frontend expectations
- Creation path may skip audit or timeline side effects
**Testing Checklist:**
- Create an incident via API
- List incidents with and without filters
- Verify pagination metadata

### TASK-032
**Title:** Implement incident detail and patch endpoints  
**Description:** Add `/v1/incidents/{incidentId}` read and update support with a composed detail view model that includes top hypothesis, confidence, and summary sections.  
**Objective:** Provide the primary data source for the Incident Command Center.  
**Dependencies:** TASK-025, TASK-027, TASK-029  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-032-incident-detail-api`  
**Definition of Done:** The incident detail API returns the canonical command-center payload and supports controlled updates.  
**Acceptance Criteria:**
- `GET /v1/incidents/{incidentId}` returns a rich detail payload
- `PATCH /v1/incidents/{incidentId}` supports allowed fields only
- Not-found and validation errors are consistent
- Top hypothesis and recommendation summary fields are included when available
**Potential Risks:**
- Overly heavy detail queries can slow page load
- Update semantics may conflict with human resolution flow
**Testing Checklist:**
- Fetch incident detail for seeded scenarios
- Patch allowed fields and verify persistence
- Check not-found handling

### TASK-033
**Title:** Implement incident action endpoints for acknowledge, investigate, and resolve  
**Description:** Add the explicit state-transition endpoints that let humans acknowledge an incident, trigger investigations, and resolve the incident with outcome metadata.  
**Objective:** Preserve human-in-the-loop control.  
**Dependencies:** TASK-019, TASK-025, TASK-027, TASK-029  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-033-incident-actions-api`  
**Definition of Done:** Human control actions are exposed through dedicated API endpoints with audit-friendly behavior.  
**Acceptance Criteria:**
- Acknowledge, investigate, and resolve endpoints exist
- Investigation requests create or queue run records
- Resolve action records resolution metadata
- Invalid state transitions return typed errors
**Potential Risks:**
- Race conditions can create duplicate runs
- Resolve logic may skip important timeline events
**Testing Checklist:**
- Acknowledge an open incident
- Trigger an investigation and verify run creation
- Resolve an incident and verify status/timestamp updates

### TASK-034
**Title:** Implement incident timeline, evidence, and graph endpoints  
**Description:** Expose timeline entries, filtered evidence lists, and graph node/edge payloads for a single incident.  
**Objective:** Support the core explainability surfaces in the UI.  
**Dependencies:** TASK-023, TASK-025, TASK-027, TASK-029  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-034-incident-evidence-api`  
**Definition of Done:** Timeline, evidence, and graph data can be fetched independently for an incident.  
**Acceptance Criteria:**
- Timeline endpoint supports ordered retrieval
- Evidence endpoint supports planned filters
- Graph endpoint returns UI-ready nodes and edges
- Empty and partial-data states are handled intentionally
**Potential Risks:**
- Graph modeling may be underspecified without real data
- Evidence endpoint could leak raw noise if clustering is weak
**Testing Checklist:**
- Fetch timeline for a seeded incident
- Filter evidence by type or service
- Verify graph payload structure

### TASK-035
**Title:** Implement recommendation and agent-run read endpoints  
**Description:** Add read APIs for recommendation groups, incident agent runs, and individual agent run detail views.  
**Objective:** Power the agent feed and recommendation panels with dedicated resources.  
**Dependencies:** TASK-024, TASK-025, TASK-027, TASK-029  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-035-recommendations-agent-runs-api`  
**Definition of Done:** The frontend can fetch recommendations and investigation run data without overloading the incident detail endpoint.  
**Acceptance Criteria:**
- Recommendation endpoint groups items by category
- Incident agent-runs endpoint lists related runs
- Agent run detail endpoint exposes findings and metadata
- Response shapes match the shared contracts
**Potential Risks:**
- Run detail responses can become too verbose or too sparse
- Recommendation grouping logic can drift from UI assumptions
**Testing Checklist:**
- Fetch recommendations for a seeded incident
- List runs for an incident
- Fetch a single run detail payload

### TASK-036
**Title:** Implement server-sent event streaming for investigation runs  
**Description:** Add the SSE endpoint that streams run lifecycle, agent progress, findings, hypotheses, and degraded-completion events to the frontend.  
**Objective:** Support near real-time incident investigation updates.  
**Dependencies:** TASK-019, TASK-024, TASK-035  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-036-sse-run-stream`  
**Definition of Done:** A browser client can subscribe to a run stream and receive ordered investigation events.  
**Acceptance Criteria:**
- SSE endpoint exists at the planned route
- Event types match the architecture document
- Event payloads include run and incident context
- Stream closes cleanly on completion or failure
**Potential Risks:**
- Event ordering bugs can confuse the UI
- Worker-to-stream integration may be brittle at first
**Testing Checklist:**
- Open an SSE client locally
- Simulate event emission through the stream layer
- Verify completion and degraded events arrive correctly

### TASK-037
**Title:** Implement the signal ingest endpoint and incident-correlation handoff  
**Description:** Add normalized signal ingestion, validation, fingerprint capture, and the first-pass handoff into incident creation or incident attachment logic.  
**Objective:** Give the simulator and future integrations one real ingestion path.  
**Dependencies:** TASK-023, TASK-027, TASK-029, TASK-033  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-037-signal-ingest-api`  
**Definition of Done:** Signals can be ingested through the public API and either create or enrich incidents.  
**Acceptance Criteria:**
- `/v1/signals/ingest` validates and stores supported signal types
- Signals capture source, timestamp, severity, payload, and metadata
- Correlation hook determines create-versus-attach behavior
- Response includes accepted signal metadata
**Potential Risks:**
- Weak correlation rules can create duplicate incidents
- Unbounded payloads can create security or cost issues
**Testing Checklist:**
- Ingest each planned signal type
- Verify incident creation or attachment behavior
- Confirm invalid payloads are rejected

### TASK-038
**Title:** Implement simulation, services, deployments, and feedback endpoints  
**Description:** Add the remaining supporting APIs needed for the simulator page, service filters, deployment views, and human feedback capture.  
**Objective:** Complete the MVP resource surface without leaving demo features blocked.  
**Dependencies:** TASK-026, TASK-027, TASK-029  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-038-supporting-resource-apis`  
**Definition of Done:** The supporting product APIs exist for simulations, service filters, deployments, and feedback.  
**Acceptance Criteria:**
- Simulation list and status read endpoints exist
- Services endpoint supports project filtering
- Deployments endpoint returns recent change summaries
- Feedback endpoint stores human response cleanly
**Potential Risks:**
- Packing too many small resources into one task can hide edge cases
- Feedback and simulation shapes may change as the demo evolves
**Testing Checklist:**
- Fetch services and deployments
- Create feedback on an incident
- Fetch available simulations and a simulation status record

## Epic 6

Agent System and LangGraph

### TASK-039
**Title:** Define the shared graph state and structured agent output schemas  
**Description:** Implement the typed state container and agent result schemas that all LangGraph nodes and agents will read and write.  
**Objective:** Prevent free-form orchestration drift.  
**Dependencies:** TASK-009, TASK-011, TASK-024  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-039-graph-state-schemas`  
**Definition of Done:** Graph state and agent output contracts are explicit, typed, and reusable across the workflow.  
**Acceptance Criteria:**
- State model includes incident context, evidence, run metadata, and agent outputs
- Agent output schema aligns with the architecture doc
- Validation hooks are ready for model outputs
- No agent requires unstructured shared memory
**Potential Risks:**
- Weak state modeling will destabilize all workflow nodes
- Missing fields can force prompt or persistence rework
**Testing Checklist:**
- Validate sample state objects
- Validate sample agent output payloads
- Compare state keys against planned workflow nodes

### TASK-040
**Title:** Implement prompt loading and prompt version persistence helpers  
**Description:** Create the loader that reads prompt templates from `packages/prompts`, resolves the active version, and maps prompt usage to persisted prompt version records.  
**Objective:** Make prompt choice traceable per run.  
**Dependencies:** TASK-003, TASK-026, TASK-039  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-040-prompt-loader`  
**Definition of Done:** Agents can request prompts through a shared loader that surfaces version metadata.  
**Acceptance Criteria:**
- Prompt files are addressable by agent name
- Active-version lookup is deterministic
- Prompt metadata can be attached to run records
- Failure behavior for missing prompts is explicit
**Potential Risks:**
- Prompt version drift reduces reproducibility
- File naming mismatches can break agent startup
**Testing Checklist:**
- Load each planned prompt by agent key
- Verify version metadata lookup
- Simulate missing prompt failure behavior

### TASK-041
**Title:** Build the model gateway abstraction for reasoning and engineering models  
**Description:** Create a provider-agnostic interface for reasoning-model calls and optional Codex-style engineering suggestion calls.  
**Objective:** Keep model selection configurable and testable.  
**Dependencies:** TASK-014, TASK-039, TASK-040  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-041-model-gateway`  
**Definition of Done:** Agent code can call a unified model interface without depending directly on one provider SDK shape.  
**Acceptance Criteria:**
- Gateway interface supports structured outputs
- Provider configuration is read from typed settings
- Separate path exists for engineering-oriented suggestion calls
- Mockable interface exists for tests
**Potential Risks:**
- Provider-specific logic can leak into agents
- Model output parsing failures can cascade broadly
**Testing Checklist:**
- Run gateway smoke test with mock responses
- Verify provider selection from config
- Confirm structured-output parsing path exists

### TASK-042
**Title:** Implement evidence normalization and enrichment toolkit  
**Description:** Build the utility layer that converts normalized signals into evidence items with severity, affected-service, and correlation metadata suitable for agent consumption.  
**Objective:** Ensure agents reason over curated evidence instead of raw event noise.  
**Dependencies:** TASK-023, TASK-027, TASK-037, TASK-039  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-042-evidence-toolkit`  
**Definition of Done:** Signal windows can be transformed into enriched evidence bundles for the graph workflow.  
**Acceptance Criteria:**
- Toolkit handles logs, metrics, deployments, and customer signals
- Evidence items preserve source linkage
- Basic clustering or dedup behavior is included
- Output is compatible with shared graph state
**Potential Risks:**
- Weak enrichment will produce low-signal agent prompts
- Overcomplicated clustering can burn valuable time
**Testing Checklist:**
- Run toolkit against sample fixture events
- Verify evidence IDs and source references are preserved
- Inspect clustered output for readability

### TASK-043
**Title:** Implement confidence scoring utility functions  
**Description:** Add reusable helpers for evidence quality, cross-agent agreement, temporal alignment, contradiction penalties, and overall confidence composition.  
**Objective:** Make confidence explainable and consistent across the workflow.  
**Dependencies:** TASK-039, TASK-042  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-043-confidence-utils`  
**Definition of Done:** Confidence scores can be computed with transparent contributing factors rather than opaque guesswork.  
**Acceptance Criteria:**
- Utility exposes component scores and overall score
- Penalty logic is explicit
- Output maps to the planned confidence breakdown shape
- Low-confidence thresholds are configurable
**Potential Risks:**
- Overly arbitrary scoring can hurt trust
- Scoring logic may need iteration once real outputs exist
**Testing Checklist:**
- Run utility against sample scenarios
- Verify contradictions lower the score
- Confirm output fields map to UI needs

### TASK-044
**Title:** Implement the Coordinator Agent  
**Description:** Build the planning agent that determines execution scope, selected specialists, retry budget, and investigation readiness.  
**Objective:** Establish deterministic orchestration control.  
**Dependencies:** TASK-039, TASK-040, TASK-041, TASK-042  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-044-coordinator-agent`  
**Definition of Done:** The workflow can produce an initial investigation plan from incident context and evidence inventory.  
**Acceptance Criteria:**
- Coordinator input and output are structured
- Retry budget and scope decisions are represented explicitly
- Failure fallback path is defined
- Confidence reflects investigation readiness, not root-cause certainty
**Potential Risks:**
- Overly broad planning can waste tokens and time
- Weak fallback logic can stall the graph
**Testing Checklist:**
- Run coordinator on sample incident context
- Validate output schema
- Simulate planning failure behavior

### TASK-045
**Title:** Implement the Log Agent  
**Description:** Build the specialist agent that clusters error patterns, identifies affected services or endpoints, and highlights temporal log anomalies tied to incident onset.  
**Objective:** Turn noisy log data into actionable failure signatures.  
**Dependencies:** TASK-039, TASK-040, TASK-041, TASK-042  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-045-log-agent`  
**Definition of Done:** The log agent returns structured findings with evidence citations and confidence.  
**Acceptance Criteria:**
- Handles missing-log and noisy-log cases explicitly
- Returns findings, citations, contradictions, and open questions
- Output schema is validated
- Confidence reflects concentration and timing of error patterns
**Potential Risks:**
- Logs may overwhelm prompts if not summarized enough
- Clustering heuristics may initially miss the important pattern
**Testing Checklist:**
- Run agent on sample log bundles
- Validate output schema and evidence references
- Inspect behavior when log input is empty

### TASK-046
**Title:** Implement the Metrics Agent  
**Description:** Build the specialist agent that interprets anomaly sequences across latency, error rate, traffic, and saturation.  
**Objective:** Identify the timing and blast-radius dimension of incidents.  
**Dependencies:** TASK-039, TASK-040, TASK-041, TASK-042  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-046-metrics-agent`  
**Definition of Done:** The metrics agent can summarize meaningful anomaly patterns with structured confidence.  
**Acceptance Criteria:**
- Detects primary anomalous metrics and timing
- Handles limited baseline gracefully
- Distinguishes likely causes from downstream symptoms where possible
- Returns structured citations and open questions
**Potential Risks:**
- Flat synthetic metric data can produce weak outputs
- Prompt may overstate causality from correlations alone
**Testing Checklist:**
- Run agent on sample metric bundles
- Inspect anomaly sequence output
- Validate behavior with sparse baseline data

### TASK-047
**Title:** Implement the Deployment Agent  
**Description:** Build the specialist agent that analyzes recent deploys, config changes, and rollout timing against incident onset.  
**Objective:** Surface suspicious changes as high-value root-cause candidates.  
**Dependencies:** TASK-039, TASK-040, TASK-041, TASK-042  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-047-deployment-agent`  
**Definition of Done:** The deployment agent returns ranked suspicious changes with time-aware confidence.  
**Acceptance Criteria:**
- Handles no-deployment and weak-metadata cases explicitly
- Returns recent change ranking and change-risk interpretation
- Links findings back to deployment evidence
- Output schema is validated
**Potential Risks:**
- Temporal proximity may be overstated as causality
- Weak fixture metadata can reduce result quality
**Testing Checklist:**
- Run agent on sample deployment events
- Validate ranked output
- Inspect behavior with no recent deploy

### TASK-048
**Title:** Implement the Review Agent  
**Description:** Build the skeptical verification agent that checks citation completeness, contradictions, and unsupported claims across specialist outputs.  
**Objective:** Make explainability a built-in workflow stage.  
**Dependencies:** TASK-043, TASK-045, TASK-046, TASK-047  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-048-review-agent`  
**Definition of Done:** The review stage can validate or weaken specialist findings before synthesis.  
**Acceptance Criteria:**
- Review input includes all specialist outputs
- Review output includes verified findings and contradictions
- Missing citation or weak evidence paths are called out explicitly
- Review confidence is distinct from root-cause confidence
**Potential Risks:**
- Review prompts may become too verbose
- Overly harsh review can suppress useful hypotheses
**Testing Checklist:**
- Run review on sample specialist outputs
- Validate rejection and contradiction cases
- Confirm output schema consistency

### TASK-049
**Title:** Implement the Root Cause Agent  
**Description:** Build the synthesis agent that ranks multiple hypotheses, identifies the most probable cause, and preserves uncertainty honestly.  
**Objective:** Produce the product’s core root-cause output.  
**Dependencies:** TASK-043, TASK-048  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-049-root-cause-agent`  
**Definition of Done:** The workflow can produce ranked, cited hypotheses with a confidence breakdown.  
**Acceptance Criteria:**
- Returns multiple ranked hypotheses
- Cites supporting and contradicting evidence
- Can abstain or lower confidence when evidence is weak
- Output maps cleanly to UI-facing contracts
**Potential Risks:**
- The model may collapse to one overconfident answer
- Ranking logic may need tuning after first live runs
**Testing Checklist:**
- Run synthesis on reviewed findings
- Verify multiple-hypothesis output
- Inspect low-confidence and abstention behavior

### TASK-050
**Title:** Implement the Recommendation Agent  
**Description:** Build the action-generation agent that produces immediate, short-term, and long-term recommendations with risk and reversibility annotations.  
**Objective:** Translate analysis into operationally safe next steps.  
**Dependencies:** TASK-041, TASK-043, TASK-049  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-050-recommendation-agent`  
**Definition of Done:** Recommendations are structured, confidence-aware, and linked to root-cause hypotheses.  
**Acceptance Criteria:**
- Recommendations are grouped into planned categories
- Risk and reversibility fields are populated
- Low-confidence cases produce conservative diagnostic guidance
- Optional engineering-suggestion path is isolated from core output
**Potential Risks:**
- Recommendations may sound strong even when confidence is low
- Codex-style path could distract from MVP if overbuilt
**Testing Checklist:**
- Run recommendation generation on sample hypotheses
- Validate category grouping and metadata
- Inspect low-confidence fallback output

### TASK-051
**Title:** Assemble LangGraph nodes and baseline workflow transitions  
**Description:** Implement the initial node graph covering context loading, signal window fetch, evidence enrichment, planning, specialist execution, review, synthesis, recommendation, persistence, and finalize stages.  
**Objective:** Turn isolated agents into a deterministic investigation system.  
**Dependencies:** TASK-019, TASK-039, TASK-042, TASK-044, TASK-045, TASK-046, TASK-047, TASK-048, TASK-049, TASK-050  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-051-langgraph-workflow`  
**Definition of Done:** The graph can execute the planned happy path from incident context to final recommendations.  
**Acceptance Criteria:**
- Core nodes exist for the planned workflow
- Parallel specialist branch execution is represented
- State handoff between nodes is explicit
- Finalization stage updates run status
**Potential Risks:**
- State mutation bugs can be hard to debug
- Parallel branch coordination may be brittle initially
**Testing Checklist:**
- Execute the graph on a deterministic fixture
- Trace node execution order
- Verify state completeness after each major stage

### TASK-052
**Title:** Add replan logic, persistence hooks, and degraded-state handling  
**Description:** Implement conditional routing for retries, run persistence for findings and hypotheses, and final degraded or `needs-human-review` completion behavior.  
**Objective:** Make the workflow resilient and product-safe under imperfect evidence.  
**Dependencies:** TASK-024, TASK-025, TASK-027, TASK-036, TASK-043, TASK-048, TASK-051  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-052-replan-and-persistence`  
**Definition of Done:** The graph can retry selectively, persist outputs, stream updates, and terminate safely under low-confidence conditions.  
**Acceptance Criteria:**
- Replan conditions are configurable
- Retry budget is enforced
- Findings, hypotheses, and recommendations persist as runs execute
- Degraded and abstention outcomes are visible and stored
**Potential Risks:**
- Retry loops can explode runtime if not bounded
- Persistence timing bugs can create partial state
**Testing Checklist:**
- Simulate low-confidence replan case
- Verify persisted records after each stage
- Confirm degraded completion path is emitted correctly

## Epic 7

Simulation Engine

### TASK-053
**Title:** Define the simulation fixture format and scenario metadata model  
**Description:** Create the canonical file format and metadata conventions for deterministic incident scenarios, emitted events, timing controls, and scenario descriptions.  
**Objective:** Standardize how demo scenarios are authored and replayed.  
**Dependencies:** TASK-026, TASK-028  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-053-simulation-fixture-spec`  
**Definition of Done:** Scenario authors have one agreed-upon format for fixtures and metadata.  
**Acceptance Criteria:**
- Fixture file structure is documented
- Scenario metadata fields match simulator UI needs
- Event ordering and timing fields are explicit
- Format supports all required signal types
**Potential Risks:**
- Ambiguous fixture format will slow scenario authoring
- Overly complex schema can burn hackathon time
**Testing Checklist:**
- Validate a sample fixture against the format
- Confirm metadata maps to the simulator page
- Review event ordering rules

### TASK-054
**Title:** Author the primary `checkout-db-pool-regression` scenario fixtures  
**Description:** Build the primary scenario’s deployment, metrics, log, alert, and customer-feedback fixture data according to the agreed format.  
**Objective:** Create the main live demo narrative.  
**Dependencies:** TASK-053  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-054-primary-scenario`  
**Definition of Done:** The primary scenario has complete, coherent, time-ordered fixture data.  
**Acceptance Criteria:**
- Deployment event precedes the anomaly window
- Metrics, logs, and customer signals tell one consistent story
- Event timestamps support a believable 30 to 90 second run
- Scenario metadata includes clear description and difficulty
**Potential Risks:**
- Weak fixtures can make the AI output feel fake
- Overly noisy logs may drown the important pattern
**Testing Checklist:**
- Review fixture order and timing
- Run basic parse/validation on the scenario file
- Confirm every required signal class is present

### TASK-055
**Title:** Author the backup `payments-dependency-latency` scenario fixtures  
**Description:** Build the backup scenario that emphasizes downstream dependency degradation rather than a direct bad deploy.  
**Objective:** Ensure the demo has a credible fallback and a contrast case.  
**Dependencies:** TASK-053  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-055-backup-scenario`  
**Definition of Done:** A second scenario exists and demonstrates a materially different causal pattern.  
**Acceptance Criteria:**
- Scenario differs clearly from the primary deploy-driven case
- Metrics and logs support dependency slowness as the cause
- Scenario metadata is complete
- Data quality is sufficient for agent reasoning
**Potential Risks:**
- Backup scenario may feel redundant if too similar
- Sparse signals can weaken comparative value
**Testing Checklist:**
- Validate fixture structure
- Review causal narrative for distinctness
- Confirm all required event classes are present

### TASK-056
**Title:** Implement the simulation runner and timed signal emission engine  
**Description:** Build the backend process that replays scenario fixtures in order, applies a speed multiplier, and emits signals through the same ingestion path as real data.  
**Objective:** Keep the demo honest by using production-like flows.  
**Dependencies:** TASK-037, TASK-053, TASK-054  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-056-simulation-runner`  
**Definition of Done:** A scenario can be launched and its events emitted deterministically over time.  
**Acceptance Criteria:**
- Runner accepts scenario slug and speed multiplier
- Events are emitted in deterministic order
- Emission uses the real signal-ingest pathway
- Simulation run status is persisted
**Potential Risks:**
- Timing drift can make live demos inconsistent
- Bypassing the real ingest path would weaken credibility
**Testing Checklist:**
- Launch a simulation locally
- Inspect emitted event order
- Verify signals reach ingestion successfully

### TASK-057
**Title:** Implement incident auto-correlation and investigation kickoff for simulation events  
**Description:** Ensure the first emitted signals create the right incident and that later simulation events attach to it while triggering the investigation workflow automatically.  
**Objective:** Complete the end-to-end simulator-to-investigation loop.  
**Dependencies:** TASK-033, TASK-037, TASK-056  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `feat/task-057-simulation-correlation`  
**Definition of Done:** A running scenario creates one coherent incident and starts the agent workflow automatically.  
**Acceptance Criteria:**
- Initial event sequence creates or identifies the target incident
- Later events attach correctly
- Investigation kickoff occurs without manual intervention when configured
- Timeline events reflect simulation activity
**Potential Risks:**
- Duplicate incidents can break the demo narrative
- Bad correlation rules can attach events incorrectly
**Testing Checklist:**
- Run the primary scenario end to end
- Verify one incident is created
- Confirm investigation run starts automatically

### TASK-058
**Title:** Add replay mode and a completed-investigation fallback artifact  
**Description:** Provide a replayable completed run or captured state so the team can still present the product if live model latency or connectivity becomes unreliable.  
**Objective:** De-risk the live demo.  
**Dependencies:** TASK-052, TASK-056, TASK-057  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer C  
**Suggested Branch Name:** `feat/task-058-replay-fallback`  
**Definition of Done:** The demo can be shown using a stable replay path if live investigation quality degrades.  
**Acceptance Criteria:**
- A completed run can be loaded or replayed reliably
- Replay mode uses real persisted outputs
- UI can distinguish live from replay when needed
- Fallback steps are documented for presenters
**Potential Risks:**
- Replay data can drift from the latest UI contracts
- Team may forget to refresh the fallback after major changes
**Testing Checklist:**
- Load replay mode locally
- Verify charts, timeline, and agent outputs render correctly
- Confirm presenter instructions are clear

## Epic 8

Frontend Foundation

### TASK-059
**Title:** Replace the starter Next.js structure with the dashboard route architecture  
**Description:** Rework `apps/web` into route groups and planned top-level routes for incidents, simulator, and settings while preserving a clean app-router structure.  
**Objective:** Prepare the product shell for real feature work.  
**Dependencies:** TASK-001, TASK-003  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-059-web-route-architecture`  
**Definition of Done:** The product app reflects the planned routing structure rather than the starter template.  
**Acceptance Criteria:**
- `/incidents`, `/simulator`, and `/settings/*` route paths exist
- Root route behavior is intentional
- Dashboard and docs chrome are separable
- Starter placeholder content is removed
**Potential Risks:**
- Route churn can create merge conflicts if delayed
- Inconsistent folder naming can spread quickly
**Testing Checklist:**
- Start the web app
- Navigate to planned top-level routes
- Confirm route files match the intended structure

### TASK-060
**Title:** Establish the visual system, typography, and global style tokens  
**Description:** Define the dashboard’s design tokens, spacing, colors, typographic hierarchy, and base theme styles so the product looks intentional from the first real screen.  
**Objective:** Prevent the UI from falling back to a generic starter aesthetic.  
**Dependencies:** TASK-059  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-060-design-system-foundation`  
**Definition of Done:** Global styles and tokens reflect the product’s command-center design direction.  
**Acceptance Criteria:**
- Color tokens cover severity, confidence, and neutral UI surfaces
- Typography choices are applied globally
- Base layout and card styling are consistent
- Reduced visual noise compared with the starter template
**Potential Risks:**
- Late design decisions can force expensive component restyling
- Over-design can consume time needed for functionality
**Testing Checklist:**
- Review the app on desktop and mobile widths
- Check contrast on key surfaces
- Verify global styles do not break default components

### TASK-061
**Title:** Build shared layout, navigation, and dashboard shell primitives  
**Description:** Create the persistent navigation shell, top bar, section containers, badges, and common layout primitives used across the product.  
**Objective:** Give all pages a consistent operator-facing frame.  
**Dependencies:** TASK-059, TASK-060  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-061-dashboard-shell`  
**Definition of Done:** Core layout primitives exist and can host the incident overview and detail pages.  
**Acceptance Criteria:**
- App shell includes left nav and top bar
- Shared panels and status badges exist
- Layout works on desktop and tablet widths
- Shell leaves clear slots for route content
**Potential Risks:**
- Poor shell structure will complicate every page
- Over-nesting layout components can make responsiveness harder
**Testing Checklist:**
- Render shell across planned routes
- Verify active navigation states
- Check tablet collapse behavior at a basic level

### TASK-062
**Title:** Integrate the API client package and frontend data helpers  
**Description:** Wire the web app to the shared API client package and create data access helpers or hooks for overview, incident detail, runs, and simulations.  
**Objective:** Ensure the frontend consumes backend data through one disciplined layer.  
**Dependencies:** TASK-012, TASK-030, TASK-031, TASK-032  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-062-web-data-client`  
**Definition of Done:** The web app has a reusable path for fetching and typing API data.  
**Acceptance Criteria:**
- API client package is imported from the web app
- Shared fetch helpers or hooks exist for core resources
- Error paths map to the shared API error shape
- No page fetches raw endpoints ad hoc
**Potential Risks:**
- Bypassing the client layer creates inconsistent error handling
- Data-fetch patterns may diverge between pages
**Testing Checklist:**
- Fetch overview and incident detail data locally
- Verify type safety in the web app
- Confirm basic error rendering behavior

### TASK-063
**Title:** Create route-scoped incident state and URL-filter handling  
**Description:** Add the React context or local provider pattern for selected evidence, active panels, focused graph node, and shareable URL filter state.  
**Objective:** Support complex Incident Command Center interactions without introducing unnecessary global state.  
**Dependencies:** TASK-059, TASK-062  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-063-incident-page-state`  
**Definition of Done:** The incident detail route has a local state management pattern ready for rich interactions.  
**Acceptance Criteria:**
- Provider or equivalent exists only where needed
- URL search params cover planned filter cases
- Selected evidence and panel state are modeled explicitly
- No global client-state library is introduced unnecessarily
**Potential Risks:**
- Under-modeled local state can cause prop drilling later
- Overbuilt state tooling can waste time
**Testing Checklist:**
- Toggle sample panel and filter states
- Verify URL parameter behavior
- Confirm state resets appropriately on incident changes

### TASK-064
**Title:** Scaffold settings routes and the docs app information architecture  
**Description:** Add basic settings route shells in the product app and shape the docs app for architecture, demo, and FAQ content.  
**Objective:** Reserve the explanatory surfaces needed for judges and collaborators.  
**Dependencies:** TASK-059, TASK-061  
**Estimated Time:** 60 minutes  
**Priority:** Medium  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-064-settings-and-docs-shells`  
**Definition of Done:** The product’s supporting routes and docs app pages exist with intentional navigation.  
**Acceptance Criteria:**
- Settings routes exist for integrations, prompts, and about
- Docs app top-level pages are scaffolded
- Navigation between docs sections is clear
- Placeholder copy indicates intended content
**Potential Risks:**
- Supporting pages may get forgotten until the last hour
- Docs app layout drift can create rushed polish work
**Testing Checklist:**
- Navigate through settings routes
- Start the docs app and inspect page structure
- Verify shell styling is consistent

## Epic 9

Dashboard Experience

### TASK-065
**Title:** Build the incidents overview page scaffold  
**Description:** Create the overview page structure with placeholder zones for the incident table, charts, health widgets, and investigation activity sections.  
**Objective:** Establish the first major product screen.  
**Dependencies:** TASK-061, TASK-062  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-065-overview-page-scaffold`  
**Definition of Done:** The overview page exists with the right information architecture and loading states.  
**Acceptance Criteria:**
- Overview page uses the dashboard shell
- Major widget zones are laid out intentionally
- Loading and empty states are present
- Route is wired to overview data access
**Potential Risks:**
- Weak initial information architecture can force repeated layout churn
- Missing loading states can make the app feel broken
**Testing Checklist:**
- Load the overview page with and without data
- Review desktop layout
- Confirm navigation into incident detail is planned

### TASK-066
**Title:** Implement the active incidents table and filter bar  
**Description:** Build the primary incident list view with severity badges, status indicators, search-ready structure, and filter controls.  
**Objective:** Make open incidents scannable and clickable.  
**Dependencies:** TASK-031, TASK-065  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-066-incidents-table`  
**Definition of Done:** The overview page can display and filter incidents cleanly.  
**Acceptance Criteria:**
- Incident table renders planned summary fields
- Filters reflect API capabilities
- Row click opens the incident detail route
- Empty and no-match states are handled
**Potential Risks:**
- Table density may hurt readability if rushed
- Filter semantics can drift from backend behavior
**Testing Checklist:**
- Render seeded incidents
- Apply filters and verify changes
- Navigate from table rows to incident detail

### TASK-067
**Title:** Build overview analytics widgets for severity, reliability, and health  
**Description:** Implement the severity chart, MTTA/MTTR summary cards, service health heatmap, and ongoing investigation strip.  
**Objective:** Turn the overview page into a real operational dashboard.  
**Dependencies:** TASK-030, TASK-065  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-067-overview-widgets`  
**Definition of Done:** The overview screen includes meaningful at-a-glance charts and health summaries.  
**Acceptance Criteria:**
- Severity distribution renders cleanly
- Health heatmap uses service data meaningfully
- MTTA/MTTR cards have deliberate labels and states
- Ongoing investigations strip communicates active work clearly
**Potential Risks:**
- Sparse demo data can make widgets look empty
- Too many chart colors can reduce clarity
**Testing Checklist:**
- Render widgets with seeded data
- Verify chart legends and labels
- Check layout on tablet width

### TASK-068
**Title:** Build the latest agent activity feed on the overview page  
**Description:** Add the activity rail that surfaces recent investigation events, completed stages, and current agent movement so the product feels live.  
**Objective:** Make AI system activity visible at the dashboard level.  
**Dependencies:** TASK-030, TASK-036, TASK-065  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-068-activity-feed`  
**Definition of Done:** The overview page shows recent investigation activity in a readable feed.  
**Acceptance Criteria:**
- Feed items include timestamps and agent context
- Supports empty and active states
- Visual hierarchy emphasizes recency
- Data source is consistent with run activity output
**Potential Risks:**
- Feed content may feel noisy if events are too granular
- Backend summary shape may need slight iteration
**Testing Checklist:**
- Render active and empty states
- Verify timestamps and labels
- Confirm feed updates when new activity arrives

### TASK-069
**Title:** Build the incident detail page scaffold and route states  
**Description:** Create the three-zone command-center layout with loading, error, and not-found handling for an individual incident route.  
**Objective:** Prepare the central product experience for feature panels.  
**Dependencies:** TASK-061, TASK-062, TASK-063  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-069-incident-detail-scaffold`  
**Definition of Done:** The incident detail route has a stable layout and state framework for all planned panels.  
**Acceptance Criteria:**
- Left, center, and right zones are defined on desktop
- Loading and error states are intentional
- Route reads incident ID and fetches detail data
- Tablet collapse behavior is planned structurally
**Potential Risks:**
- Weak scaffolding can make panel integration painful
- Missing error states will hurt demo resilience
**Testing Checklist:**
- Load a valid incident route
- Check not-found route behavior
- Inspect the layout on desktop and tablet widths

### TASK-070
**Title:** Implement the incident header and service summary panel  
**Description:** Build the top-of-page summary area with severity, status, service ownership, open duration, and affected services.  
**Objective:** Surface the most important incident context immediately.  
**Dependencies:** TASK-032, TASK-069  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-070-incident-header`  
**Definition of Done:** The incident detail page opens with a clear high-signal summary.  
**Acceptance Criteria:**
- Severity and status are visually prominent
- Ownership and service context are present
- Open duration or timing context is shown
- Panel works with partial detail payloads
**Potential Risks:**
- Too much metadata can dilute the main signal
- Timing formatting inconsistencies can reduce polish
**Testing Checklist:**
- Render header for seeded incident data
- Verify severity/status styling
- Check fallback behavior for missing optional fields

### TASK-071
**Title:** Implement the root-cause summary and confidence breakdown widgets  
**Description:** Build the card that presents the current top hypothesis plus a separate confidence component that explains how certain the system is and why.  
**Objective:** Deliver the core explainability surface.  
**Dependencies:** TASK-032, TASK-035, TASK-043, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-071-root-cause-confidence-ui`  
**Definition of Done:** Users can see the top hypothesis and inspect confidence contributors from the incident page.  
**Acceptance Criteria:**
- Top hypothesis title and summary are rendered clearly
- Supporting evidence access is linked visibly
- Confidence breakdown shows component drivers and penalties
- Low-confidence states are understandable
**Potential Risks:**
- Confidence UI can feel fake if overly flashy
- Hypothesis text may need truncation or expansion rules
**Testing Checklist:**
- Render high- and low-confidence examples
- Verify confidence component labels
- Check evidence-link affordances

### TASK-072
**Title:** Build the agent activity panel and status cards  
**Description:** Create the panel that shows each agent, current status, start and end times, summary output, and rerun history.  
**Objective:** Make the multi-agent architecture visible and trustworthy.  
**Dependencies:** TASK-035, TASK-036, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-072-agent-activity-panel`  
**Definition of Done:** The incident page displays agent progress and results in a readable execution feed.  
**Acceptance Criteria:**
- Each planned agent has a clear card or row representation
- Running, completed, failed, and degraded states are distinct
- Agent summaries and timestamps are shown
- The panel can update live
**Potential Risks:**
- Too much detail may clutter the right column
- Live updates may reorder content awkwardly
**Testing Checklist:**
- Render a completed run
- Simulate live status transitions
- Verify degraded-state presentation

### TASK-073
**Title:** Build the investigation timeline and replay controls  
**Description:** Implement the ordered timeline view for incident events, ingestion milestones, agent stages, and human actions, with basic replay interaction.  
**Objective:** Support incident storytelling and post-hoc review.  
**Dependencies:** TASK-034, TASK-058, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-073-timeline-replay`  
**Definition of Done:** The incident page can render a coherent timeline and step through replayable states.  
**Acceptance Criteria:**
- Timeline entries render in correct order
- Event types are visually differentiated
- Replay controls exist for the demo path
- Timeline remains usable when data is still arriving
**Potential Risks:**
- Timeline ordering bugs will be highly visible in demos
- Replay mode can drift from live behavior
**Testing Checklist:**
- Render seeded timeline entries
- Test replay interaction using fallback data
- Verify live and replay states are distinct

### TASK-074
**Title:** Build the metrics anomaly and signal trend charts  
**Description:** Implement the main metrics chart and supporting signal volume trend chart with incident and deployment annotations.  
**Objective:** Visualize the temporal shape of the incident.  
**Dependencies:** TASK-034, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-074-metrics-charts`  
**Definition of Done:** The incident page includes readable trend charts that support the investigation narrative.  
**Acceptance Criteria:**
- Metrics chart handles multiple series
- Incident start and deployment markers are annotated
- Signal trend chart complements the main metrics view
- Charts remain legible on dense data points
**Potential Risks:**
- Chart clutter can hurt comprehension
- Synthetic data may need shaping for visual clarity
**Testing Checklist:**
- Render charts with primary scenario data
- Check axis labeling and legends
- Verify marker annotations appear at the correct times

### TASK-075
**Title:** Build the log fingerprint, customer impact, and deployment correlation panels  
**Description:** Implement the clustered log table plus supporting panels for customer impact and recent deployment correlation.  
**Objective:** Surface the three highest-signal operational evidence classes together.  
**Dependencies:** TASK-034, TASK-038, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-075-evidence-side-panels`  
**Definition of Done:** The incident page shows clustered logs, customer pain signals, and suspicious changes in focused panels.  
**Acceptance Criteria:**
- Log table shows fingerprint, count, service, and timing
- Customer impact panel summarizes user-facing symptoms
- Deployment panel highlights suspicious changes and time deltas
- Panels handle missing data gracefully
**Potential Risks:**
- Packing three evidence views together can stress layout density
- Log clusters may look weak until fixture tuning is done
**Testing Checklist:**
- Render all three panels with seeded data
- Verify sorting and labels
- Check behavior when one evidence class is missing

### TASK-076
**Title:** Build the recommendation checklist and action-safety presentation  
**Description:** Implement grouped recommendation sections with risk, reversibility, and confidence cues.  
**Objective:** Turn analysis into usable next steps without over-automating.  
**Dependencies:** TASK-035, TASK-050, TASK-069  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-076-recommendation-checklist`  
**Definition of Done:** Recommendations render as operationally useful, categorized action items.  
**Acceptance Criteria:**
- Immediate, short-term, and long-term sections are distinct
- Risk and reversibility are legible
- Low-confidence recommendations are presented conservatively
- Empty-state behavior is clear
**Potential Risks:**
- Recommendations may read like generic AI output if styling is weak
- Category grouping can drift from API shape
**Testing Checklist:**
- Render grouped recommendations
- Verify risk badge styling
- Check low-confidence presentation

### TASK-077
**Title:** Build the evidence graph panel and graph legend  
**Description:** Implement the React Flow graph view for incidents, services, deploys, evidence nodes, and hypotheses, plus a small legend and focus behavior.  
**Objective:** Deliver the most differentiated visual surface in the product.  
**Dependencies:** TASK-034, TASK-069  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-077-evidence-graph`  
**Definition of Done:** The incident page includes an inspectable evidence graph with meaningful node and edge semantics.  
**Acceptance Criteria:**
- Graph renders nodes and edges from API data
- Legend explains major node and edge types
- Selected-node state is reflected in the page
- Graph remains readable at demo-scale data volume
**Potential Risks:**
- Poor layout choices can make the graph feel gimmicky
- Graph data may need adapter tuning after first real runs
**Testing Checklist:**
- Render graph for a seeded incident
- Select nodes and verify UI reactions
- Check basic keyboard or pointer interactions

### TASK-078
**Title:** Build the contradictions, unknowns, and stakeholder update panels  
**Description:** Implement the section that shows what the system is unsure about, plus the optional stakeholder-update draft card.  
**Objective:** Make restraint and communication quality visible.  
**Dependencies:** TASK-032, TASK-035, TASK-049, TASK-069  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-078-unknowns-and-update`  
**Definition of Done:** The incident page surfaces uncertainty explicitly and provides a concise status-summary artifact.  
**Acceptance Criteria:**
- Contradictions and open questions are visible
- Panel styling distinguishes uncertainty from error
- Stakeholder update card is concise and readable
- Sections degrade gracefully when data is absent
**Potential Risks:**
- This panel may be skipped late even though it is trust-critical
- Generated update text may need tighter formatting rules
**Testing Checklist:**
- Render contradictions and unknowns from sample data
- Review stakeholder update length and clarity
- Check empty-state behavior

### TASK-079
**Title:** Implement manual acknowledge, rerun, and resolve controls in the incident view  
**Description:** Add the human-control action bar or controls that call the incident action endpoints and update page state.  
**Objective:** Reinforce that engineers remain in command.  
**Dependencies:** TASK-033, TASK-069, TASK-072  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-079-human-control-actions`  
**Definition of Done:** The incident page supports the full human control loop for demo purposes.  
**Acceptance Criteria:**
- Acknowledge, rerun, and resolve actions are available where appropriate
- Loading and success states are visible
- Invalid action attempts surface helpful errors
- Timeline or page state updates after actions complete
**Potential Risks:**
- Action UX can feel unsafe if confirmations are unclear
- Rerun behavior may confuse users if multiple runs exist
**Testing Checklist:**
- Acknowledge an incident from the UI
- Trigger a rerun and confirm status updates
- Resolve an incident and confirm the page refreshes correctly

## Epic 10

Integration and Real-Time Experience

### TASK-080
**Title:** Connect the simulator page to backend scenario APIs and incident handoff  
**Description:** Build the simulator page interactions that list scenarios, launch a run, show launch status, and route the user into the created incident.  
**Objective:** Make the demo start from a polished, controlled entry point.  
**Dependencies:** TASK-038, TASK-056, TASK-059, TASK-062  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-080-simulator-ui-integration`  
**Definition of Done:** A user can launch a scenario from the UI and land in the associated investigation flow.  
**Acceptance Criteria:**
- Simulator page lists available scenarios
- Launch action calls the backend correctly
- Loading and failure states are present
- Successful launch navigates to the incident or run view
**Potential Risks:**
- Launch UX can feel broken if navigation timing is unclear
- Scenario metadata changes can ripple into the page
**Testing Checklist:**
- Launch the primary scenario from the UI
- Verify failure handling on invalid scenario selection
- Confirm incident navigation after launch

### TASK-081
**Title:** Wire SSE client behavior and live event merging on the incident page  
**Description:** Implement the client-side subscription, reconnection policy, and event-merge logic for live investigation updates.  
**Objective:** Make the investigation feel active rather than static.  
**Dependencies:** TASK-036, TASK-063, TASK-072, TASK-073  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-081-live-sse-client`  
**Definition of Done:** The incident page updates incrementally as the worker emits events.  
**Acceptance Criteria:**
- Page subscribes to run events when appropriate
- Event handlers update agent, hypothesis, and recommendation state
- Completion and degraded states are reflected without reload
- Basic reconnect or retry behavior is defined
**Potential Risks:**
- Out-of-order events can corrupt client state
- Reconnect loops can create duplicate UI updates
**Testing Checklist:**
- Watch a live simulation update the incident page
- Simulate a temporary stream interruption
- Confirm final state matches persisted API data

### TASK-082
**Title:** Build frontend adapters for graph, timeline, and view-model composition  
**Description:** Add the transformation layer that converts API responses into the shapes needed by charts, React Flow, replay controls, and complex page panels.  
**Objective:** Keep presentational components simple and resilient to backend evolution.  
**Dependencies:** TASK-034, TASK-062, TASK-077  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-082-view-model-adapters`  
**Definition of Done:** Complex UI components receive clean, UI-friendly data instead of raw API payloads.  
**Acceptance Criteria:**
- Graph adapter normalizes nodes and edges for React Flow
- Timeline adapter handles ordering and label formatting
- Panel components consume adapter outputs cleanly
- Shared formatting rules are centralized
**Potential Risks:**
- Without adapters, UI logic will sprawl into components
- Over-transforming data can hide useful source fields
**Testing Checklist:**
- Run adapter logic against seeded responses
- Inspect graph and timeline rendering after transformations
- Confirm formatting remains consistent across panels

### TASK-083
**Title:** Implement responsive tablet and mobile behavior for the dashboard  
**Description:** Add the planned layout collapse rules, panel stacking behavior, and simplified graph fallback for smaller screens.  
**Objective:** Ensure the product feels finished beyond one desktop breakpoint.  
**Dependencies:** TASK-061, TASK-069, TASK-077  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-083-responsive-dashboard`  
**Definition of Done:** The product remains usable and visually coherent on tablet and mobile sizes.  
**Acceptance Criteria:**
- Right-side panels collapse appropriately on tablet
- Mobile stacks critical content in a sensible order
- Graph degrades gracefully on small screens
- Navigation remains accessible
**Potential Risks:**
- Dense command-center layouts can break quickly on small screens
- Late responsive work may surface component assumptions
**Testing Checklist:**
- Review key routes at desktop, tablet, and mobile widths
- Check graph fallback behavior
- Verify primary actions stay accessible

### TASK-084
**Title:** Add motion polish and reduced-motion support  
**Description:** Implement the high-value animations for agent reveals, timeline updates, confidence transitions, and panel changes, plus a reduced-motion mode.  
**Objective:** Make the product feel polished without relying on gimmicks.  
**Dependencies:** TASK-060, TASK-072, TASK-073, TASK-081  
**Estimated Time:** 75 minutes  
**Priority:** Medium  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `feat/task-084-motion-polish`  
**Definition of Done:** Motion reinforces system activity and remains respectful of reduced-motion preferences.  
**Acceptance Criteria:**
- Key transitions use intentional, lightweight animation
- Reduced-motion behavior disables non-essential motion
- Motion supports readability rather than distracting from it
- Animation timings feel consistent across the app
**Potential Risks:**
- Over-animation can make the product feel less trustworthy
- Motion work can become a time sink late in the schedule
**Testing Checklist:**
- Watch live investigation transitions
- Toggle reduced-motion mode
- Verify animations do not block core interactions

## Epic 11

Testing and Quality

### TASK-085
**Title:** Set up backend unit test harness, fixtures, and factories  
**Description:** Establish the baseline Python test structure, common fixtures, and data factories needed for repository, service, and utility tests.  
**Objective:** Make backend and AI work testable without repetitive boilerplate.  
**Dependencies:** TASK-002, TASK-015, TASK-021  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `test/task-085-backend-test-harness`  
**Definition of Done:** Backend contributors have a stable pattern for adding fast tests.  
**Acceptance Criteria:**
- Test directory structure matches major backend modules
- Shared fixtures support database and non-database tests
- Factories exist for core entities
- Test command is documented
**Potential Risks:**
- No harness means tests slip until too late
- Overbuilt factories can slow initial momentum
**Testing Checklist:**
- Run the backend test command
- Execute at least one fixture-backed smoke test
- Verify fixture isolation between tests

### TASK-086
**Title:** Add API integration tests for incidents, simulations, and SSE resources  
**Description:** Cover the highest-value API flows including incident creation, overview reads, simulation launch, signal ingest, and streaming endpoint behavior.  
**Objective:** Protect the core demo pathways from regression.  
**Dependencies:** TASK-030, TASK-031, TASK-033, TASK-036, TASK-037, TASK-038, TASK-085  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer B  
**Suggested Branch Name:** `test/task-086-api-integration-tests`  
**Definition of Done:** The most important backend user journeys have automated integration coverage.  
**Acceptance Criteria:**
- Incident CRUD and action flows are covered
- Simulation launch flow is covered
- Signal ingest path is covered
- SSE endpoint behavior has at least smoke-level validation
**Potential Risks:**
- Streaming tests can be brittle if over-specified
- Integration tests may need careful fixture setup
**Testing Checklist:**
- Run integration suite locally
- Verify seeded fixture usage
- Confirm failures are readable

### TASK-087
**Title:** Add deterministic agent workflow tests with mocked model responses  
**Description:** Create end-to-end graph tests that use mocked model outputs to verify happy path, degraded path, and low-confidence replan behavior.  
**Objective:** Make the agent system debuggable without depending on live model calls.  
**Dependencies:** TASK-041, TASK-048, TASK-049, TASK-050, TASK-051, TASK-052, TASK-085  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Hard  
**Owner:** Developer C  
**Suggested Branch Name:** `test/task-087-agent-workflow-tests`  
**Definition of Done:** The investigation workflow has deterministic automated coverage for its key execution branches.  
**Acceptance Criteria:**
- Happy path graph execution is covered
- Low-confidence or contradiction-triggered replan path is covered
- Degraded completion path is covered
- Tests do not require live model keys
**Potential Risks:**
- Mock responses may drift from real prompt output
- Overly brittle graph assertions can slow iteration
**Testing Checklist:**
- Run workflow tests locally
- Inspect persisted outputs in test runs
- Verify mocked model outputs validate against schemas

### TASK-088
**Title:** Add frontend component and integration tests for core dashboard routes  
**Description:** Cover the overview page, incident detail route, critical panels, and major loading or error states with frontend tests.  
**Objective:** Protect the UI from regression during fast polish work.  
**Dependencies:** TASK-066, TASK-071, TASK-072, TASK-073, TASK-077  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `test/task-088-frontend-dashboard-tests`  
**Definition of Done:** The most important dashboard surfaces have test coverage for rendering and key behaviors.  
**Acceptance Criteria:**
- Overview page renders seeded data
- Incident detail route handles loading, error, and success states
- At least one live-update or state-transition behavior is exercised
- Key panels have smoke coverage
**Potential Risks:**
- Frontend tests can get flaky if they rely on animations or timing
- Over-testing visuals can waste time
**Testing Checklist:**
- Run frontend tests locally
- Mock API responses for main routes
- Verify tests remain stable with reduced-motion mode enabled

### TASK-089
**Title:** Create an end-to-end demo smoke test flow  
**Description:** Script or document the minimum automated smoke flow that launches a simulation, opens the incident page, and confirms the core investigation surfaces appear.  
**Objective:** Catch catastrophic integration regressions before the live demo.  
**Dependencies:** TASK-080, TASK-081, TASK-088  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `test/task-089-e2e-demo-smoke`  
**Definition of Done:** The team has a repeatable smoke validation for the main demo path.  
**Acceptance Criteria:**
- Test covers simulator launch
- Test verifies navigation into the incident experience
- Test confirms at least one agent/status surface is visible
- Failures are easy to interpret
**Potential Risks:**
- Full E2E tests can be brittle under time pressure
- Demo smoke may need to tolerate variable live timing
**Testing Checklist:**
- Run the smoke flow locally
- Inspect failure output on a forced error
- Confirm the flow works with replay mode if needed

### TASK-090
**Title:** Run the quality pass for performance, logging, accessibility, and security basics  
**Description:** Perform a focused checklist-driven pass over performance hotspots, structured logs, contrast and keyboard access, secret handling, and ingest payload safety.  
**Objective:** Raise the demo from functional to credible.  
**Dependencies:** TASK-016, TASK-017, TASK-083, TASK-084, TASK-089  
**Estimated Time:** 90 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `chore/task-090-quality-pass`  
**Definition of Done:** Major quality gaps that would be obvious in a judged review are identified and addressed or consciously accepted.  
**Acceptance Criteria:**
- Performance hotspots are noted and obvious regressions fixed
- Logs contain required context fields in major flows
- Critical UI paths are keyboard-usable and readable
- Server-side secret and payload safeguards are reviewed
**Potential Risks:**
- This task can expand endlessly without a fixed checklist
- Late quality findings may force scope cuts
**Testing Checklist:**
- Review main routes and APIs against a checklist
- Inspect logs during a simulation run
- Check contrast and keyboard navigation on critical actions

## Epic 12

Deployment, Demo Hardening, and Documentation

### TASK-091
**Title:** Create Vercel, Railway, and Neon deployment configuration artifacts  
**Description:** Add the infrastructure metadata, service definitions, and environment mapping notes needed to deploy the frontend, API, worker, and database cleanly.  
**Objective:** Make deployment repeatable instead of improvised.  
**Dependencies:** TASK-005, TASK-020, TASK-019  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `ops/task-091-deployment-configs`  
**Definition of Done:** The repo contains the configuration and notes required to deploy every MVP surface.  
**Acceptance Criteria:**
- Vercel, Railway, and Neon notes or config files exist
- API and worker process separation is represented
- Env variable mapping is documented
- Deployment dependencies are explicit
**Potential Risks:**
- Missing config details can block deploys at the worst moment
- Worker deployment may be forgotten if treated like the API
**Testing Checklist:**
- Review deployment configs for completeness
- Validate env inventory against runtime needs
- Confirm service boundaries match the architecture

### TASK-092
**Title:** Build production seed, bootstrap, and verification scripts  
**Description:** Create the scripts and documented steps needed to seed a fresh deployed environment, register scenarios, and validate demo readiness quickly.  
**Objective:** Reduce setup risk before the judge session.  
**Dependencies:** TASK-028, TASK-058, TASK-091  
**Estimated Time:** 75 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer B  
**Suggested Branch Name:** `ops/task-092-demo-bootstrap`  
**Definition of Done:** A clean environment can be brought to a demo-ready state with minimal manual work.  
**Acceptance Criteria:**
- Seed flow covers baseline data and scenarios
- Verification checklist includes health, data, and simulation checks
- Replay fallback can be seeded or loaded
- Bootstrap steps are documented clearly
**Potential Risks:**
- Manual seeding steps can be missed under stress
- Seed data may drift from the latest schema
**Testing Checklist:**
- Run bootstrap flow against a clean environment
- Verify scenario availability afterward
- Confirm replay/fallback data is present

### TASK-093
**Title:** Rewrite the root README for developers and judges  
**Description:** Replace the starter README with a project-specific guide covering product overview, architecture, setup, commands, simulator usage, deployment notes, and limitations.  
**Objective:** Make the repository self-explanatory.  
**Dependencies:** TASK-004, TASK-091, TASK-092  
**Estimated Time:** 75 minutes  
**Priority:** High  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `docs/task-093-readme-rewrite`  
**Definition of Done:** The root README reflects Sentinel AI rather than the starter template.  
**Acceptance Criteria:**
- Product value proposition is clear
- Setup and run instructions cover web, API, worker, and simulator
- Architecture summary matches `PROJECT.md`
- Known limitations and demo notes are included
**Potential Risks:**
- README drift can confuse future contributors
- Overlong docs can hide the most important setup steps
**Testing Checklist:**
- Read README from a fresh-user perspective
- Verify commands and paths match the repo
- Check links to docs and project files

### TASK-094
**Title:** Write the initial ADRs and architecture-supporting documentation  
**Description:** Capture the bounded-monolith, Postgres source-of-truth, and LangGraph workflow decisions as ADRs and sync supporting architecture notes.  
**Objective:** Preserve architectural intent for judges and future contributors.  
**Dependencies:** TASK-006, TASK-051, TASK-091  
**Estimated Time:** 60 minutes  
**Priority:** High  
**Difficulty:** Easy  
**Owner:** Developer B  
**Suggested Branch Name:** `docs/task-094-adrs`  
**Definition of Done:** The repo includes concise ADRs covering the most important architectural trade-offs.  
**Acceptance Criteria:**
- At least three ADRs exist for the key architecture decisions
- ADR language matches implemented reality
- Docs are short, scannable, and linked from the repo
- No starter-template architecture notes remain misleadingly active
**Potential Risks:**
- ADRs written too late may describe an outdated system
- Overly long ADRs will not be read
**Testing Checklist:**
- Review ADR paths and links
- Compare ADR content against implementation
- Confirm docs are easy to discover

### TASK-095
**Title:** Build docs app pages for architecture, demo, and judge FAQ  
**Description:** Fill the docs app with the architecture walkthrough, demo guidance, and FAQ content needed for external reviewers.  
**Objective:** Turn the docs app into a supporting asset instead of a placeholder.  
**Dependencies:** TASK-064, TASK-093, TASK-094  
**Estimated Time:** 90 minutes  
**Priority:** Medium  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `docs/task-095-docs-app-content`  
**Definition of Done:** The docs app contains real project-specific content aligned with the implementation.  
**Acceptance Criteria:**
- Architecture page reflects the actual MVP
- Demo page explains how to experience the product
- FAQ page answers likely technical judge questions
- Content is styled consistently with the product
**Potential Risks:**
- Docs app content may lag behind the real implementation
- Too much prose can dilute the most important takeaways
**Testing Checklist:**
- Start the docs app and review all pages
- Check navigation and formatting
- Compare technical claims against the codebase and `PROJECT.md`

### TASK-096
**Title:** Write the demo script, presenter notes, and fallback talk track  
**Description:** Create the exact spoken and operational flow for the live demo, including scenario selection, timing, transitions, and what to do if live inference degrades.  
**Objective:** Make the presentation crisp and resilient.  
**Dependencies:** TASK-058, TASK-080, TASK-095  
**Estimated Time:** 60 minutes  
**Priority:** Critical  
**Difficulty:** Easy  
**Owner:** Developer C  
**Suggested Branch Name:** `docs/task-096-demo-script`  
**Definition of Done:** The team has a concrete, rehearsable demo playbook with a backup plan.  
**Acceptance Criteria:**
- Primary live flow is under 6 minutes
- Backup replay flow is explicitly documented
- Key architecture talking points are included
- Human-in-the-loop resolution step is in the script
**Potential Risks:**
- Without a script, the demo can wander or over-explain
- Backup handling may be forgotten under pressure
**Testing Checklist:**
- Read through the script end to end
- Time the planned flow
- Validate fallback instructions against the actual product

### TASK-097
**Title:** Perform the final MVP scope cut review and demo rehearsal  
**Description:** Run a deliberate go/no-go pass on optional features, rehearse the primary and backup demo paths, and capture final fixes or cuts before presenting.  
**Objective:** Arrive at the judging session with a stable, defendable MVP instead of a half-finished broader scope.  
**Dependencies:** TASK-090, TASK-092, TASK-093, TASK-095, TASK-096  
**Estimated Time:** 90 minutes  
**Priority:** Critical  
**Difficulty:** Medium  
**Owner:** Developer A  
**Suggested Branch Name:** `chore/task-097-final-rehearsal`  
**Definition of Done:** The team has a final scoped MVP, a rehearsed demo, and a clear list of what will not be touched before presentation.  
**Acceptance Criteria:**
- Must-have features are verified explicitly
- Optional features are cut or accepted consciously
- Primary and backup demo paths are both rehearsed
- Final issue list is short and triaged
**Potential Risks:**
- Last-minute feature churn can destabilize the demo
- Teams often skip this step and discover issues live
**Testing Checklist:**
- Rehearse the full demo on the target environment
- Run the smoke checklist one final time
- Verify rollback or fallback plan is ready

## Milestone Plan

### Milestone 1

Foundation

- Target tasks: TASK-001 through TASK-020
- Outcome: monorepo structure, backend scaffolding, shared package scaffolding, config, logging, worker bootstrap, and health checks are in place
- Exit criteria:
- Frontend and backend skeletons run locally
- Shared package boundaries exist
- Database and worker bootstraps are wired

### Milestone 2

Backend

- Target tasks: TASK-021 through TASK-038
- Outcome: database schema, repositories, seed data, and core APIs are functional
- Exit criteria:
- Incidents, signals, simulations, and runs can be persisted and queried
- Main dashboard and incident endpoints respond with typed payloads

### Milestone 3

AI

- Target tasks: TASK-039 through TASK-058
- Outcome: agents, LangGraph workflow, simulation runner, and replay fallback operate end to end
- Exit criteria:
- A scenario can launch and produce persisted findings, hypotheses, and recommendations
- Workflow supports degraded or low-confidence outcomes safely

### Milestone 4

Frontend

- Target tasks: TASK-059 through TASK-079
- Outcome: dashboard shell, overview page, Incident Command Center, graph, charts, and human-control surfaces are usable
- Exit criteria:
- Users can navigate the full product experience
- Core investigation panels render from real API data

### Milestone 5

Integration

- Target tasks: TASK-080 through TASK-090
- Outcome: simulator UI, live SSE updates, responsive behavior, and quality validation are complete
- Exit criteria:
- Live investigation updates stream into the incident page
- Demo smoke tests pass and major quality gaps are closed

### Milestone 6

Demo Ready

- Target tasks: TASK-091 through TASK-097
- Outcome: deployment, seeding, documentation, demo script, and final rehearsal are complete
- Exit criteria:
- The deployed environment is demo-ready
- The team can execute both primary and backup demo flows confidently

## Dependency Graph

### Must Happen First

- TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, and TASK-006 form the initial repository and process foundation
- TASK-013 through TASK-015 must land before meaningful backend, database, or API implementation
- TASK-021 through TASK-028 must land before most API and simulation work
- TASK-039 through TASK-043 must land before specialist agents and confidence-aware workflow logic
- TASK-059 through TASK-062 must land before most dashboard feature work

### Core Backend Chain

- TASK-013 -> TASK-014 -> TASK-015 -> TASK-021 -> TASK-022 -> TASK-023 -> TASK-024 -> TASK-025 -> TASK-026 -> TASK-027 -> TASK-029 -> TASK-030 through TASK-038

### Core AI Chain

- TASK-019 -> TASK-039 -> TASK-040 -> TASK-041 -> TASK-042 -> TASK-043 -> TASK-044 through TASK-050 -> TASK-051 -> TASK-052

### Core Frontend Chain

- TASK-059 -> TASK-060 -> TASK-061 -> TASK-062 -> TASK-063 -> TASK-065 -> TASK-069 -> TASK-070 through TASK-079 -> TASK-080 through TASK-084

### Simulation Chain

- TASK-053 -> TASK-054 and TASK-055 -> TASK-056 -> TASK-057 -> TASK-058 -> TASK-080

### Tasks That Can Run in Parallel After Foundation

- After TASK-003, Developer A can execute TASK-007 through TASK-012 while Developer B executes TASK-013 through TASK-020
- After TASK-021 starts, Developer C can begin TASK-039 and TASK-040 using shared contracts while Developer B continues schema work
- After TASK-030 through TASK-032 are stable, Developer A can move on TASK-062, TASK-065, and TASK-066 while Developer C builds agents
- TASK-054 and TASK-055 can run in parallel once TASK-053 is complete
- TASK-067, TASK-068, and TASK-076 through TASK-078 can progress in parallel once the incident page and overview scaffolds exist
- TASK-093, TASK-094, and TASK-095 can run in parallel after the product flow stabilizes

## Critical Path

The minimum working MVP path is:

1. TASK-001 Normalize the monorepo structure
2. TASK-002 Scaffold the Python backend application workspace
3. TASK-004 Align Turbo tasks and workspace scripts
4. TASK-013 Bootstrap the FastAPI application entrypoint and router registry
5. TASK-014 Implement typed application configuration
6. TASK-015 Set up SQLAlchemy base and session management
7. TASK-021 Initialize Alembic migration workflow
8. TASK-022 Model organizations, projects, and services
9. TASK-023 Model incidents, signal events, and evidence items
10. TASK-024 Model deployments, agent runs, and agent findings
11. TASK-025 Model hypotheses, recommendations, and incident timeline events
12. TASK-027 Implement repository layer
13. TASK-029 Define common API schema modules
14. TASK-031 Implement incident list and creation endpoints
15. TASK-033 Implement incident action endpoints
16. TASK-037 Implement the signal ingest endpoint
17. TASK-039 Define graph state and agent output schemas
18. TASK-041 Build the model gateway abstraction
19. TASK-042 Implement evidence normalization and enrichment
20. TASK-044 through TASK-050 Implement all agents
21. TASK-051 Assemble the LangGraph workflow
22. TASK-052 Add replan logic, persistence, and degraded handling
23. TASK-053 through TASK-057 Build and run the simulation engine
24. TASK-059 through TASK-063 Establish the frontend shell and data layer
25. TASK-065, TASK-069, TASK-071, TASK-072, TASK-074, TASK-076, TASK-077, and TASK-079 Build the essential dashboard and control surfaces
26. TASK-080 and TASK-081 Connect the simulator and live updates
27. TASK-091 and TASK-092 Prepare deployment and demo bootstrap
28. TASK-097 Run final scope cut review and rehearsal

## Parallel Development Plan

### Developer A

Primary lane: frontend, design system, dashboard UX, docs app

- Wave 1: TASK-003, TASK-006, TASK-007 through TASK-012
- Wave 2: TASK-059 through TASK-064
- Wave 3: TASK-065 through TASK-079
- Wave 4: TASK-080 through TASK-084
- Wave 5: TASK-088, TASK-089, TASK-093, TASK-095, TASK-097

### Developer B

Primary lane: backend, database, APIs, deployment

- Wave 1: TASK-001, TASK-002, TASK-004, TASK-005
- Wave 2: TASK-013 through TASK-020
- Wave 3: TASK-021 through TASK-028
- Wave 4: TASK-029 through TASK-038
- Wave 5: TASK-085, TASK-086, TASK-090, TASK-091, TASK-092, TASK-094

### Developer C

Primary lane: AI orchestration, simulation, workflow integration

- Wave 1: TASK-019 and design review on shared contracts
- Wave 2: TASK-039 through TASK-052
- Wave 3: TASK-053 through TASK-058
- Wave 4: Partner with Developer A on TASK-081 and with Developer B on TASK-036
- Wave 5: TASK-087 and TASK-096

### Blocking-Minimization Strategy

- Developer A should not wait for the full AI system; use stable shared contracts and mocked data early
- Developer B should prioritize TASK-031, TASK-032, TASK-033, and TASK-037 because they unblock both simulation and frontend work
- Developer C should begin state, prompt, and gateway work before all APIs are finished, then switch to deterministic mocks until live integration is ready
- Shared contract changes should be batched twice daily to reduce merge churn

## Daily Schedule

Assumption: 3-day hackathon running from Thursday, July 16, 2026 through Saturday, July 18, 2026, with final demo on Saturday evening.

### Day 1

Thursday, July 16, 2026

Morning:

- Developer A: TASK-003, TASK-007, TASK-008
- Developer B: TASK-001, TASK-002, TASK-004
- Developer C: review `PROJECT.md`, align on agent contracts, start TASK-019

Afternoon:

- Developer A: TASK-009, TASK-010, TASK-059
- Developer B: TASK-005, TASK-013, TASK-014, TASK-015
- Developer C: TASK-039, TASK-040, TASK-041

Night:

- Developer A: TASK-060, TASK-061
- Developer B: TASK-016, TASK-017, TASK-018, TASK-021
- Developer C: TASK-042, TASK-043

### Day 2

Friday, July 17, 2026

Morning:

- Developer A: TASK-062, TASK-063, TASK-065
- Developer B: TASK-022, TASK-023, TASK-024
- Developer C: TASK-044, TASK-045, TASK-046

Afternoon:

- Developer A: TASK-066, TASK-067, TASK-069
- Developer B: TASK-025, TASK-026, TASK-027
- Developer C: TASK-047, TASK-048, TASK-049

Night:

- Developer A: TASK-070, TASK-071, TASK-072
- Developer B: TASK-029, TASK-030, TASK-031, TASK-032
- Developer C: TASK-050, TASK-051, TASK-052, TASK-053, TASK-054

### Day 3

Saturday, July 18, 2026

Morning:

- Developer A: TASK-073, TASK-074, TASK-076
- Developer B: TASK-033, TASK-034, TASK-037, TASK-038
- Developer C: TASK-055, TASK-056, TASK-057

Afternoon:

- Developer A: TASK-077, TASK-078, TASK-079, TASK-080
- Developer B: TASK-085, TASK-086, TASK-091, TASK-092
- Developer C: TASK-058, TASK-081, TASK-087

Night:

- Developer A: TASK-083, TASK-084, TASK-088, TASK-089, TASK-093, TASK-095
- Developer B: TASK-090, TASK-094
- Developer C: TASK-096
- Whole team: TASK-097 final scope cut review, demo rehearsal, backup check, and fix-only window

## Risk Register

| # | Risk | Mitigation Strategy | Backup Plan |
| --- | --- | --- | --- |
| 1 | Agent outputs are too vague or hallucinated | Keep structured schemas, review stage, citations, and abstention logic | Use replay mode with validated outputs and demo the explainability controls |
| 2 | Backend schema work takes longer than expected | Freeze schema to MVP entities only and avoid extra optional tables until later | Cut feedback or lower-priority audit surfaces temporarily |
| 3 | SSE live updates are unstable | Keep event types minimal and use persisted refresh fallback | Poll incident detail after key run transitions |
| 4 | Simulation feels fake or overly scripted | Use real ingestion and orchestration paths with believable timing | Use the backup scenario and emphasize deterministic reproducibility |
| 5 | Frontend looks too generic | Lock the visual system on Day 1 and build within it | Drop lower-value panels before sacrificing core polish |
| 6 | React Flow graph becomes unreadable | Keep the node set small and use clear node classes | Show a simplified evidence list view on smaller screens |
| 7 | Confidence score feels arbitrary | Expose component breakdown and contradiction penalties | Present confidence as bands with explanation rather than over-precise numbers |
| 8 | Model latency exceeds demo tolerance | Keep prompts narrow and fixture data concise | Use completed-run replay mode during the demo |
| 9 | Queue or worker integration breaks | Keep the queue abstraction simple and well logged | Fall back to an in-process job runner for the MVP if necessary |
| 10 | Duplicate incidents are created during simulation | Keep correlation rules narrow for demo scenarios | Pre-seed or hard-bind scenario events to one incident |
| 11 | Deployment configuration is incomplete | Create env inventory early and validate on Day 2 | Run the demo locally with stable seed data if cloud deploy slips |
| 12 | Database migrations drift across branches | Keep migrations small and merge them early each day | Rebuild a clean migration chain before final deploy |
| 13 | Frontend and backend contracts drift | Use shared types and adapter layers, and review contract changes twice daily | Freeze contracts for the last integration window |
| 14 | Accessibility and keyboard support are forgotten | Include a dedicated quality pass and test checklist | Prioritize keyboard access for primary actions only if time is short |
| 15 | Docs remain starter-template quality | Assign explicit documentation tasks rather than leaving them as cleanup | Use a concise README plus docs app essentials only |
| 16 | Too many features are attempted | Hold a strict must-have list and run a scope cut review | Cut stakeholder draft, extra settings polish, and nonessential visuals |
| 17 | Tests are skipped under time pressure | Add lightweight smoke tests before full coverage | Use manual regression checklist if automated coverage is incomplete |
| 18 | Replay fallback becomes stale | Refresh replay artifacts after major contract changes | Capture one final completed run on Saturday afternoon |
| 19 | Judges ask about production scaling beyond MVP | Prepare ADRs and FAQ answers in the docs app | Use a concise architecture talk track focused on queue-backed scaling |
| 20 | Final rehearsal is rushed or skipped | Reserve a fixed Saturday night rehearsal block | Use the backup script and fallback environment if late bugs appear |

## MVP Checklist

### Must Have

- Deterministic simulation launch from the UI
- Automatic incident creation from simulation signals
- Coordinator, Log, Metrics, Deployment, Review, Root Cause, and Recommendation stages
- Persisted findings, hypotheses, recommendations, and timeline events
- Incident overview page with active incidents and health context
- Incident detail page with root cause, confidence, agent feed, charts, recommendations, and evidence graph
- Human controls for acknowledge, rerun, and resolve
- Live or replayable investigation updates
- Deployed or locally stable demo environment with seed data

### Should Have

- Backup scenario with different causal pattern
- Docs app with architecture, demo, and FAQ content
- Replay mode for demo resilience
- Structured logging and basic quality pass
- Automated API and workflow smoke coverage

### Nice to Have

- Stakeholder update draft panel
- Settings pages with prompt/version visibility
- MTTA and MTTR summary cards seeded for realism
- Optional engineering-oriented follow-up suggestions

### Won't Build

- Real external observability vendor integrations
- Automated remediation or deployment rollback
- Enterprise auth, RBAC, or SSO
- Historical incident retrieval with vector search
- Broad connector ecosystem beyond the simulator

## Final Demo Checklist

- Frontend loads cleanly on the target device and network
- Backend health and readiness checks pass
- Database is seeded with base org, project, service, and scenario data
- Primary scenario launches successfully from the simulator
- Incident auto-navigation works
- Live or replay investigation shows all seven planned stages
- Root-cause summary displays with confidence breakdown
- Evidence graph renders correctly
- Metrics, log, deployment, and recommendation panels render correctly
- Human control actions work on the incident page
- Backup scenario is available
- Replay fallback is available
- Demo script is printed or pinned
- Presenter knows the architecture talking points
- Logs are visible for debugging if something stalls
- Last-minute feature branches are closed or merged
- Only fix-critical changes are allowed after rehearsal
