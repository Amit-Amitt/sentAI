# Sentinel AI Architecture

## Telemetry Flow

The entire lifecycle of a system event flows automatically from the monitored applications up to the AI-driven resolution, without requiring manual intervention.

### 1. Ingestion
- **Sentinel SDK:** Agents push logs, metrics, exceptions, and heartbeats via REST API endpoints (`/telemetry/...`).
- **OpenTelemetry:** Native support for OTLP HTTP (`/otlp/v1/...`). Any OpenTelemetry SDK or Collector can push `ResourceSpans`, `ResourceLogs`, and `ResourceMetrics`.
- The `OTLPParser` normalizes nested OTLP payloads (including Resource Attributes, Span Events, Links) into the Sentinel batch structures.
- Validated payloads from both pipelines are stored temporarily in Redis and consumed via the exact same RQ background workers.

### 2. Incident Detection Engine
- **Normalization:** Raw metrics/logs map to standardized dictionary formats.
- **Rule Engine:** Evaluates static thresholds based on configured bounds (e.g. error rate > 5%).
- **Incident Correlation:** Merges repeated triggers within a specific time window into a single `Incident` to reduce alert fatigue.
- **Deployment & K8s Correlation:** Automatically queries the latest synced `GithubDeployment` prior to the incident, and extracts Kubernetes attributes (e.g. `k8s.pod.name`) from telemetry to append `kubernetes_context` (Pod phase, container status, recent K8s events).
- **Severity Engine:** Calculates severity scaling linearly with the magnitude of the threshold breach (e.g. Low -> Medium -> Critical).

### 3. Infrastructure & Deployment Intelligence
- GitHub Apps or OAuth tokens continuously synchronize `GithubRepository`, `GithubCommit`, `GithubPullRequest`, and `GithubDeployment` state into PostgreSQL via background workers (`github_tasks.py`).
- Kubernetes clients synchronize `K8sCluster`, `K8sNode`, `K8sPod`, and `K8sEvent` metadata into PostgreSQL via background workers (`kubernetes_tasks.py`).
- Enterprise Observability platforms (Grafana, Prometheus) synchronize Dashboards and Alert Rules into PostgreSQL via background workers (`observability_tasks.py`).
- Incoming webhooks (GitHub, Alertmanager) are securely validated and processed asynchronously.
- The `GithubRiskAnalyzer` automatically scores incoming commits and deployments (0.0 to 1.0).

### 4. Orchestration & Remediation
- An Incident triggers the `IntegrationTriggerService`.
- The `WorkflowExecutor` executes the configured `LangGraph` pipeline.
- Specialized AI Agents (Root Cause, Log Analyzer, Metrics Analyst) investigate the telemetry signals.
- If the Root Cause Agent finds a definitive issue, it forwards context to the **Remediation Engine**.
- The Remediation Engine generates a patch (application code, YAML, Terraform).
- **Sandbox Validation:** The backend simulates or runs linting/tests on the generated patch (`ValidationResult`).
- **GitHub Automation:** If validation passes, the system uses the GitHub API to create a new branch and open a Draft Pull Request containing the fix and Rollback Instructions.
- **Approval Workflow:** Execution halts. The fix is stored as `pending_approval`. The UI presents the fix to a human, who must hit "Approve" before any destructive or production changes are merged.
- **Enterprise Notification Hub:** The `NotificationEngine` evaluates dynamic policies and dispatches AI Incident Briefings asynchronously to Slack, Teams, PagerDuty, or Email based on escalation tiers.
- **Enterprise Identity & Access Management:** Comprehensive multi-tenant RBAC, MFA enforcement, and active session revocation tracked immutably in an `AuditLog`.
- **SaaS Monetization Engine:** A centralized `BillingService` gating all premium features and mapping Organization usage metrics to active Stripe Subscriptions dynamically.
- **Cloud-Native Deployment:** Fully containerized, orchestrated via Kubernetes Helm charts, and protected by Liveness/Readiness probes and Graceful Shutdown handling.
- **Hackathon Demo Engine:** Synthetic Telemetry Generators (`api/v1/routers/demo.py`) simulate production outages, triggering the real detection engine and AI without requiring external clusters.
- Real-time state updates are broadcast over Server-Sent Events (SSE) via Redis PubSub for the Dashboard command center.

### 5. Technologies Used
- **Configuration:** Pydantic `BaseSettings` with strict runtime validation and explicit environment variable scoping.
- **Database:** PostgreSQL (Relational schema, indexing), Alembic (Migrations).
- **Caching & PubSub:** Redis.
- **AI Orchestration:** LangGraph (Agents, Workflows).
