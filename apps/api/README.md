# Sentinel AI API

This is the API backend for Sentinel AI, built with Python 3.12/3.13 and FastAPI.

## Directory Structure

- `src/sentinel_api`: Root Python package containing core modules (config, database, logging), APIs, models, schemas, and services.
- `tests`: Unit and integration testing harness.

## Local Setup

1. Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run the development server:
   ```bash
   uvicorn sentinel_api.main:app --reload
   ```

## Workspace API Key Management

API keys are scoped to a workspace and store only hashed secrets.

Supported environments:

- development
- production
- testing

Supported scopes:

- incidents:read
- incidents:write
- reports:read
- reports:write
- logs:upload
- metrics:upload
- deployments:upload
- api-keys:manage

API endpoints:

- `GET /api/v1/apikeys?workspace_id=...`
- `POST /api/v1/apikeys?workspace_id=...`
- `GET /api/v1/apikeys/{id}`
- `PATCH /api/v1/apikeys/{id}`
- `POST /api/v1/apikeys/{id}/rotate`
- `POST /api/v1/apikeys/{id}/revoke`
- `POST /api/v1/apikeys/{id}/copy`
- `DELETE /api/v1/apikeys/{id}`
- `GET /api/v1/apikeys/{id}/usage`
- `GET /api/v1/apikeys/{id}/audits`

## Integrations Marketplace

Connect external DevOps tools (GitHub, Slack, Datadog, PagerDuty, AWS, etc.) to workspaces.

23 seeded providers across 9 categories: Source Control, Communication, Incident Management, Monitoring, Logging, Cloud, Containers, Issue Tracking, General.

Database tables:

- `integration_providers` — Supported provider catalog (seeded on startup)
- `workspace_integrations` — Active workspace connections
- `integration_credentials` — Stored tokens/keys per connection
- `integration_webhooks` — Incoming/outgoing webhook endpoints
- `integration_syncs` — Sync pipeline execution history
- `integration_audits` — User action audit trail

API endpoints:

- `GET /api/v1/integrations` — List all providers (optional `?workspace_id=` for connection overlay)
- `GET /api/v1/integrations/{id}` — Provider details
- `POST /api/v1/integrations?workspace_id=...` — Connect a provider to a workspace
- `PATCH /api/v1/integrations/{id}?workspace_id=...` — Update connection config
- `DELETE /api/v1/integrations/{id}?workspace_id=...` — Delete connection permanently
- `POST /api/v1/integrations/{id}/connect?workspace_id=...` — Establish/restore connection
- `POST /api/v1/integrations/{id}/disconnect?workspace_id=...` — Deactivate connection
- `POST /api/v1/integrations/{id}/test?workspace_id=...` — Test connection health
- `POST /api/v1/integrations/{id}/sync?workspace_id=...` — Trigger manual sync
- `GET /api/v1/integrations/{id}/history?workspace_id=...` — Sync + audit history

