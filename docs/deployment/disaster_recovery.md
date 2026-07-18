# Disaster Recovery & Backups

This document outlines the standard operating procedures for Disaster Recovery (DR) and Data Backups for Sentinel AI in production.

## 1. PostgreSQL Database Backups
Sentinel AI relies on PostgreSQL for authoritative state. 

### Recommended Strategy
Use a managed database service (e.g., AWS RDS, Neon, Google Cloud SQL) with **Point-in-Time Recovery (PITR)** enabled.
- **Retention**: Keep automated snapshots for a minimum of 7 days.
- **Continuous Archiving**: Enable WAL (Write-Ahead Logging) archiving to S3/GCS to support restoring to any precise second.

### Manual Backups (pg_dump)
If self-hosting PostgreSQL, implement a cronjob to run daily backups:
```bash
pg_dump -U postgres -h $DB_HOST -F c -d sentinel_ai > /backups/sentinel_ai_$(date +%F).dump
```
Ensure backups are encrypted at rest and transferred off-site (e.g., AWS S3).

## 2. Redis State
Sentinel AI uses Redis heavily for message queuing (RQ), caching, pub/sub, and rate limiting.

### Recommended Strategy
While most Redis data is ephemeral, long-running AI Remediation tasks are queued here.
- Enable `appendonly yes` (AOF) for durability.
- Configure daily RDB snapshots.
- If Redis fails, queued tasks will be lost. The system is designed to handle this gracefully, but users will need to re-trigger incomplete Auto-Remediations.

## 3. Object Storage (S3 / R2)
Incident attachments, AI-generated reports, and logs are stored in Object Storage.

### Lifecycle Policies
1. **Intelligent Tiering**: Transition objects older than 30 days to infrequent access tiers.
2. **Version Control**: Enable Bucket Versioning to prevent accidental deletion of critical incident post-mortems.

## 4. Secret Management
Sentinel AI configuration relies heavily on encrypted environment variables (`JWT_SECRET`, `AUTH_ENCRYPTION_KEY`, `STRIPE_SECRET_KEY`).
- Store these in AWS Secrets Manager or HashiCorp Vault.
- Do NOT store `.env` files in plain text on production servers. Use Kubernetes Secrets managed by `ExternalSecrets` operator.
