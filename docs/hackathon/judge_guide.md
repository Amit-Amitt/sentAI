# Sentinel AI - Hackathon Judge Guide

Welcome to the Sentinel AI project! This guide will help you evaluate our project efficiently.

## The Problem
SREs and DevOps teams are overwhelmed by "alert fatigue". When a production system fails, they receive hundreds of alerts across Datadog, PagerDuty, and Sentry. Investigating the root cause by correlating logs, traces, and recent code deployments takes hours, costing businesses heavily in downtime.

## Our Solution
**Sentinel AI** is an Autonomous AI Incident Commander. It doesn't just alert you; it actively investigates the failure using LangGraph AI agents, correlates the anomaly with recent GitHub deployments, and automatically opens a Draft Pull Request containing the fix.

## Key Technical Achievements
1. **Production-Ready Architecture**: This isn't just a prototype. We built a true multi-tenant SaaS platform with RBAC, Stripe billing, JWT active session revocation, and Kubernetes Graceful Shutdowns.
2. **Asynchronous Telemetry Pipeline**: Uses Redis queues and background workers to ingest high-volume telemetry without blocking the main API.
3. **Agentic Auto-Remediation**: The AI isn't just a chatbot. It is integrated deeply into the platform, fetching traces, querying GitHub, and writing code patches autonomously.

## Where to Look
- `/apps/api/src/sentinel_api/ai/`: The core LangGraph workflows and LangChain agents.
- `/apps/api/src/sentinel_api/services/telemetry_pipeline.py`: The high-throughput ingestion queue.
- `/apps/web/app/`: The Next.js frontend with Framer Motion animations.

## How to Test
Navigate to the `Hackathon Demo Lab` in the sidebar and trigger a simulated outage. Watch the Live Timeline update as the AI processes the anomaly and generates a Root Cause Story!
