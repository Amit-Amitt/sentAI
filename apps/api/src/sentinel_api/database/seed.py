import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.role import Permission, Role
from sentinel_api.models.integration import IntegrationProvider

logger = structlog.get_logger("sentinel_api.database.seed")


async def seed_roles_and_permissions(session: AsyncSession) -> None:
    """Seeds default Roles and Permissions in the database on startup."""
    logger.info("Seeding roles and permissions...")

    # 1. Define all permissions
    permissions_data = {
        "full_access": "Full access to all settings, billing, members, and data.",
        "manage_members": "Invite, update roles, and remove team members.",
        "manage_workspace": "Configure and update workspace preferences.",
        "run_incidents": "Trigger, mitigate, and resolve AI incident responses.",
        "view_reports": "Access post-mortem investigations and reports.",
        "manage_ai_configs": "Modify active SRE agent model prompts and strategies.",
    }

    # Query existing permissions
    existing_perms_res = await session.execute(select(Permission))
    existing_perms_map = {p.name: p for p in existing_perms_res.scalars().all()}

    # Create missing permissions
    for name, desc in permissions_data.items():
        if name not in existing_perms_map:
            p = Permission(name=name, description=desc)
            session.add(p)
            existing_perms_map[name] = p

    # Flush to ensure permissions have IDs generated
    await session.flush()

    # 2. Define all roles with their assigned permissions
    roles_data = {
        "owner": {
            "desc": "Owner of the organization with full transfer/billing permissions.",
            "perms": [
                "full_access",
                "manage_members",
                "manage_workspace",
                "run_incidents",
                "view_reports",
                "manage_ai_configs",
            ],
        },
        "admin": {
            "desc": "Organization administrator with member and workspace management rights.",
            "perms": [
                "manage_members",
                "manage_workspace",
                "run_incidents",
                "view_reports",
                "manage_ai_configs",
            ],
        },
        "engineer": {
            "desc": "SRE Engineer capable of running incidents and viewing reports.",
            "perms": ["run_incidents", "view_reports", "manage_ai_configs"],
        },
        "viewer": {
            "desc": "Read-only access to dashboard data and incident reports.",
            "perms": ["view_reports"],
        },
    }

    # Query existing roles
    existing_roles_res = await session.execute(select(Role))
    existing_roles_map = {r.name: r for r in existing_roles_res.scalars().all()}

    # Create/update roles with relationships
    for name, info in roles_data.items():
        role = existing_roles_map.get(name)
        if not role:
            role = Role(name=name, description=info["desc"])
            session.add(role)
        role.permissions = [existing_perms_map[pname] for pname in info["perms"]]

    await session.commit()
    logger.info("Roles and permissions seeding completed.")


async def seed_integration_providers(session: AsyncSession) -> None:
    """Seeds default IntegrationProviders in the database on startup."""
    logger.info("Seeding integration providers...")

    providers = [
        # Source Control
        {
            "name": "GitHub",
            "key": "github",
            "category": "Source Control",
            "logo": "Github",
            "description": "Sync repository commits, manage branch permissions, and correlation deployments.",
            "overview": "### Connect Sentinel AI to GitHub\n\nAutomate your incident workflows by correlating commits, branches, and PR approvals with live production anomalies.\n\n- **Deployments Correlation**: Map every production commit to incident triggers.\n- **PR Checks**: Automatically post SRE post-mortem notes on failing integration tests.",
            "status": "available",
            "is_oauth_supported": True,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "GitLab",
            "key": "gitlab",
            "category": "Source Control",
            "logo": "Gitlab",
            "description": "Ingest GitLab CI pipelines status, issues logs, and repo updates.",
            "overview": "### Connect Sentinel AI to GitLab\n\nMonitor CI/CD pipeline runs and correlate package updates with incident telemetry streams.",
            "status": "available",
            "is_oauth_supported": True,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Bitbucket",
            "key": "bitbucket",
            "category": "Source Control",
            "logo": "Bitbucket",
            "description": "Integrate Bitbucket repositories and CI/CD pipelines.",
            "overview": "### Connect Sentinel AI to Bitbucket\n\nLink repos and trace anomalies back to development branches.",
            "status": "coming_soon",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        # Communication
        {
            "name": "Slack",
            "key": "slack",
            "category": "Communication",
            "logo": "Slack",
            "description": "Dispatch alerts to workspace channels and trigger interactive incident resolution menus.",
            "overview": "### Connect Sentinel AI to Slack\n\nBring the Autonomous SRE Commander directly to your operations channels.\n\n- **Incident Sync**: Open temporary incident channels dynamically.\n- **Interactive Cards**: Mitigate blockages using Slack buttons.",
            "status": "available",
            "is_oauth_supported": True,
            "default_sync_frequency": "realtime",
        },
        {
            "name": "Microsoft Teams",
            "key": "ms-teams",
            "category": "Communication",
            "logo": "Microsoft",
            "description": "Send notifications and incident cards to Teams channels.",
            "overview": "### Connect Sentinel AI to Teams\n\nIngest updates and page critical responders via Teams groups.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "realtime",
        },
        {
            "name": "Discord",
            "key": "discord",
            "category": "Communication",
            "logo": "Discord",
            "description": "Webhook dispatcher sending real-time logs and severities to Discord channels.",
            "overview": "### Connect Sentinel AI to Discord\n\nPipe alerts directly to Developer/Ops rooms.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "realtime",
        },
        # Incident Management
        {
            "name": "PagerDuty",
            "key": "pagerduty",
            "category": "Incident Management",
            "logo": "PagerDuty",
            "description": "Sync active on-call rosters, page engineers, and resolve escalations.",
            "overview": "### Connect Sentinel AI to PagerDuty\n\nSynchronize alerts, assign on-call commanders, and trigger phone/SMS overrides during SEV1 anomalies.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Opsgenie",
            "key": "opsgenie",
            "category": "Incident Management",
            "logo": "Opsgenie",
            "description": "Ingest Opsgenie alerts and delegate incident paging systems.",
            "overview": "### Connect Sentinel AI to Opsgenie\n\nRoute critical outages to Opsgenie alert streams.",
            "status": "coming_soon",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        # Monitoring
        {
            "name": "Datadog",
            "key": "datadog",
            "category": "Monitoring",
            "logo": "Datadog",
            "description": "Sync application performance monitors, system metric boards, and log errors.",
            "overview": "### Connect Sentinel AI to Datadog\n\nCorrelate APM metrics, latency spikes, and system usage graphs directly with Sentinel AI sub-agents.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Grafana",
            "key": "grafana",
            "category": "Monitoring",
            "logo": "Grafana",
            "description": "Embed dashboard charts, ingest alert triggers, and fetch metrics.",
            "overview": "### Connect Sentinel AI to Grafana\n\nPull active panels and metric metrics to feed anomaly graphs.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Prometheus",
            "key": "prometheus",
            "category": "Monitoring",
            "logo": "Prometheus",
            "description": "Pull time-series metric data and monitor anomaly threshold alerts.",
            "overview": "### Connect Sentinel AI to Prometheus\n\nConfigure custom PromQL queries for continuous background health monitoring.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "New Relic",
            "key": "new-relic",
            "category": "Monitoring",
            "logo": "NewRelic",
            "description": "Ingest telemetry metrics, transaction spans, and distributed logs.",
            "overview": "### Connect Sentinel AI to New Relic\n\nTrace database bottlenecks using APM dashboards.",
            "status": "coming_soon",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        # Logging
        {
            "name": "Elasticsearch",
            "key": "elasticsearch",
            "category": "Logging",
            "logo": "Elasticsearch",
            "description": "Search and ingest structured indexing records, and cluster logs.",
            "overview": "### Connect Sentinel AI to Elasticsearch\n\nIndex and analyze slow database transaction logs.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        {
            "name": "Loki",
            "key": "loki",
            "category": "Logging",
            "logo": "Loki",
            "description": "Sync Loki stream logs with incident timelines.",
            "overview": "### Connect Sentinel AI to Grafana Loki\n\nStream error traces directly to our Log Summarizer sub-agent.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Splunk",
            "key": "splunk",
            "category": "Logging",
            "logo": "Splunk",
            "description": "Ingest Splunk enterprise indexes and run security audit correlation.",
            "overview": "### Connect Sentinel AI to Splunk\n\nSync security events and audit records automatically.",
            "status": "coming_soon",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        # Cloud
        {
            "name": "AWS",
            "key": "aws",
            "category": "Cloud",
            "logo": "Aws",
            "description": "Sync AWS CloudWatch logs, ECS deployment histories, and monitor IAM activities.",
            "overview": "### Connect Sentinel AI to AWS\n\nSync ECS/EKS resource triggers, CloudWatch logs, and monitor auto-scaling group metrics.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Azure",
            "key": "azure",
            "category": "Cloud",
            "logo": "Azure",
            "description": "Ingest Azure Monitor events, App Services traces, and resource metrics.",
            "overview": "### Connect Sentinel AI to Microsoft Azure\n\nTrack App Service status logs and database transactions.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        {
            "name": "Google Cloud",
            "key": "gcp",
            "category": "Cloud",
            "logo": "Gcp",
            "description": "Monitor GCP Cloud Logging, Cloud Run deployments, and Pub/Sub telemetry.",
            "overview": "### Connect Sentinel AI to Google Cloud\n\nCorrelate GCP Cloud Run deployments with live metrics.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        # Containers
        {
            "name": "Docker",
            "key": "docker",
            "category": "Containers",
            "logo": "Docker",
            "description": "Log container builds, image registers, and daemon resource stats.",
            "overview": "### Connect Sentinel AI to Docker Hub\n\nSync image build status logs.",
            "status": "coming_soon",
            "is_oauth_supported": False,
            "default_sync_frequency": "daily",
        },
        {
            "name": "Kubernetes",
            "key": "kubernetes",
            "category": "Containers",
            "logo": "Kubernetes",
            "description": "Monitor pod states, cluster node events, and namespace activities.",
            "overview": "### Connect Sentinel AI to Kubernetes\n\nPull pod crashloop backoffs and namespace node metrics.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "hourly",
        },
        # Issue Tracking
        {
            "name": "Jira",
            "key": "jira",
            "category": "Issue Tracking",
            "logo": "Jira",
            "description": "Create SRE tickets automatically and sync bug progress statuses.",
            "overview": "### Connect Sentinel AI to Jira\n\nGenerate and assign Jira tasks dynamically based on post-mortem action items.",
            "status": "available",
            "is_oauth_supported": True,
            "default_sync_frequency": "daily",
        },
        {
            "name": "Linear",
            "key": "linear",
            "category": "Issue Tracking",
            "logo": "Linear",
            "description": "Sync issues, track bugs, and correlate product tickets with incidents.",
            "overview": "### Connect Sentinel AI to Linear\n\nSynchronize issues and track tasks created during post-mortem audits.",
            "status": "available",
            "is_oauth_supported": True,
            "default_sync_frequency": "daily",
        },
        # General
        {
            "name": "Webhooks",
            "key": "webhooks",
            "category": "General",
            "logo": "Webhook",
            "description": "Configure incoming and outgoing custom webhooks for payload delivery.",
            "overview": "### Configure Webhooks\n\nDeliver alerts to custom systems and ingest events via HTTP POST triggers.",
            "status": "available",
            "is_oauth_supported": False,
            "default_sync_frequency": "realtime",
        },
    ]

    # Query existing providers
    existing_provs_res = await session.execute(select(IntegrationProvider))
    existing_provs_keys = {p.key for p in existing_provs_res.scalars().all()}

    # Create missing providers
    for p_data in providers:
        if p_data["key"] not in existing_provs_keys:
            p = IntegrationProvider(
                name=p_data["name"],
                key=p_data["key"],
                category=p_data["category"],
                logo=p_data["logo"],
                description=p_data["description"],
                overview=p_data["overview"],
                status=p_data["status"],
                is_oauth_supported=p_data["is_oauth_supported"],
                default_sync_frequency=p_data["default_sync_frequency"],
            )
            session.add(p)

    await session.commit()
    logger.info("Integration providers seeding completed.")

