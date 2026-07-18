import uuid
import json
import asyncio
import structlog
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.simulation import SimulationRun
from sentinel_api.ai.schemas.models import IncidentContext, ExecutionContext
from sentinel_api.ai.workflows.executor import WorkflowExecutor

logger = structlog.get_logger("sentinel_api.services.simulation")


class SimulationLibrary:
    """Library of predefined production incident scenarios."""

    SCENARIOS = [
        {
            "id": "db_pool_exhausted",
            "title": "Database Connection Pool Exhausted",
            "description": "The application is unable to acquire database connections due to a sudden surge in traffic or a connection leak.",
            "affected_services": ["api-gateway", "user-service", "database"],
            "expected_root_cause": "Connection Leak in ORM",
        },
        {
            "id": "high_api_latency",
            "title": "High API Latency",
            "description": "API responses are degrading to 5000ms+ due to inefficient queries hitting the primary data store.",
            "affected_services": ["api-gateway", "product-service"],
            "expected_root_cause": "Missing Database Index",
        },
        {
            "id": "redis_cache_failure",
            "title": "Redis Cache Failure",
            "description": "The primary Redis cluster is evicting keys aggressively, causing massive cache misses and database overload.",
            "affected_services": ["cache-cluster", "database", "session-service"],
            "expected_root_cause": "OOM Evictions",
        },
        {
            "id": "k8s_crashloop",
            "title": "Kubernetes Pod CrashLoopBackOff",
            "description": "A recent deployment introduced a misconfiguration, causing pods to continuously crash upon startup.",
            "affected_services": ["payment-service", "kubernetes"],
            "expected_root_cause": "Invalid Environment Variable",
        },
        {
            "id": "memory_leak",
            "title": "Memory Leak",
            "description": "Continuous gradual increase in memory consumption eventually triggering OOMKilled events.",
            "affected_services": ["reporting-worker"],
            "expected_root_cause": "Unbounded Array Growth",
        },
        {
            "id": "high_cpu_usage",
            "title": "High CPU Usage",
            "description": "Thread dumps indicate a tight loop causing CPU spikes to 99% across the cluster.",
            "affected_services": ["image-processing-service"],
            "expected_root_cause": "Infinite Loop in Image Resizer",
        },
        {
            "id": "disk_full",
            "title": "Disk Full",
            "description": "Logs are filling up the ephemeral storage leading to NoSpaceLeftOnDevice errors.",
            "affected_services": ["kafka-broker", "log-collector"],
            "expected_root_cause": "Log Rotation Failure",
        },
        {
            "id": "deployment_failure",
            "title": "Deployment Failure",
            "description": "A schema migration failed midway, leaving the database in an inconsistent state.",
            "affected_services": ["ci-cd-pipeline", "database"],
            "expected_root_cause": "Incompatible Schema Change",
        },
        {
            "id": "auth_down",
            "title": "Authentication Service Down",
            "description": "OAuth provider integration is failing with 401s, locking all users out of the system.",
            "affected_services": ["auth-service", "api-gateway"],
            "expected_root_cause": "Expired SSL Certificate",
        },
        {
            "id": "payment_gateway",
            "title": "Payment Gateway Failure",
            "description": "External Stripe API calls are timing out, causing checkout drops and cart abandonment.",
            "affected_services": ["checkout-service", "stripe-integration"],
            "expected_root_cause": "External Provider Outage",
        },
    ]

    @classmethod
    def get_scenario(cls, scenario_id: str) -> Optional[Dict[str, Any]]:
        for s in cls.SCENARIOS:
            if s["id"] == scenario_id:
                return s
        return None

    @classmethod
    def generate_synthetic_signals(cls, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generates mock telemetry data matching the scenario profile."""
        now_str = datetime.now(UTC).isoformat()
        
        # Base template for signals
        signals = {
            "log_agent_output": [
                f"{now_str} [WARN] System degraded in {scenario['affected_services'][0]}"
            ],
            "metrics_agent_output": [
                "cpu_usage_percent > 85%",
                "error_rate = 15%"
            ],
            "deployment_agent_output": [
                f"{now_str} Deploying v2.1.4 to {scenario['affected_services'][0]}"
            ],
            "review_agent_output": [
                "User reported failure to load page."
            ]
        }
        
        sid = scenario["id"]
        
        if sid == "db_pool_exhausted":
            signals["log_agent_output"].append(f"{now_str} [ERROR] FATAL: remaining connection slots are reserved for non-replication superuser connections")
            signals["log_agent_output"].append(f"{now_str} [ERROR] Timeout waiting for a connection from pool")
            signals["metrics_agent_output"].append("db_connections_active == 1000")
            signals["metrics_agent_output"].append("db_connection_wait_time_ms > 5000")
            
        elif sid == "high_api_latency":
            signals["log_agent_output"].append(f"{now_str} [WARN] POST /api/v1/search took 6200ms")
            signals["metrics_agent_output"].append("p99_latency_ms = 6200")
            
        elif sid == "redis_cache_failure":
            signals["log_agent_output"].append(f"{now_str} [ERROR] Redis connection refused: max memory reached")
            signals["metrics_agent_output"].append("cache_miss_rate = 98%")
            signals["metrics_agent_output"].append("redis_evictions_total > 50000")
            
        elif sid == "k8s_crashloop":
            signals["log_agent_output"].append(f"{now_str} [FATAL] KeyError: 'DATABASE_URL' not found in environment")
            signals["metrics_agent_output"].append("kube_pod_container_status_restarts_total > 5")
            signals["deployment_agent_output"].append(f"{now_str} HELM Upgrade failed for {scenario['affected_services'][0]}")
            
        elif sid == "memory_leak":
            signals["log_agent_output"].append(f"{now_str} [WARN] Garbage collection overhead limit exceeded")
            signals["log_agent_output"].append(f"{now_str} [FATAL] OutOfMemoryError: Java heap space")
            signals["metrics_agent_output"].append("jvm_memory_bytes_used > 8GB")
            
        elif sid == "high_cpu_usage":
            signals["log_agent_output"].append(f"{now_str} [WARN] Thread 'main' is hogging CPU")
            signals["metrics_agent_output"].append("node_cpu_seconds_total > 99%")
            
        elif sid == "disk_full":
            signals["log_agent_output"].append(f"{now_str} [ERROR] IOException: No space left on device")
            signals["metrics_agent_output"].append("node_filesystem_avail_bytes == 0")
            
        elif sid == "deployment_failure":
            signals["log_agent_output"].append(f"{now_str} [ERROR] Migration V12__Drop_User_Table.sql failed")
            signals["deployment_agent_output"].append(f"{now_str} Rolling back deployment v1.12.0")
            
        elif sid == "auth_down":
            signals["log_agent_output"].append(f"{now_str} [ERROR] Certificate validation failed for auth.provider.com")
            signals["metrics_agent_output"].append("http_requests_total{status='401'} > 500/sec")
            
        elif sid == "payment_gateway":
            signals["log_agent_output"].append(f"{now_str} [ERROR] Connection timed out after 30000ms: api.stripe.com")
            signals["metrics_agent_output"].append("payment_failures_total > 150/min")
            signals["review_agent_output"].append("Multiple customers complaining about checkout hanging.")
            
        return signals


class SimulationService:
    def __init__(self):
        self.executor = WorkflowExecutor()

    async def start_simulation(
        self,
        db: AsyncSession,
        workspace_id: str,
        scenario_id: str,
        severity: str
    ) -> SimulationRun:
        """Sets up the synthetic incident and runs the LangGraph simulation."""
        
        scenario = SimulationLibrary.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")

        incident_id = f"sim-{uuid.uuid4().hex[:8]}"

        # 1. Create Simulation Run record
        run_record = SimulationRun(
            id=str(uuid.uuid4()).replace("-", ""),
            workspace_id=workspace_id,
            scenario_id=scenario_id,
            severity=severity,
            status="RUNNING",
            incident_id=incident_id
        )
        db.add(run_record)
        await db.commit()
        await db.refresh(run_record)
        
        # 2. Build Context
        signals = SimulationLibrary.generate_synthetic_signals(scenario)
        
        incident_ctx = IncidentContext(
            incident_id=incident_id,
            severity=severity,
            status="ACTIVE",
            summary=f"[SIMULATION] {scenario['title']}",
            signals=signals
        )
        
        exec_ctx = ExecutionContext(
            request_id=f"req-sim-{uuid.uuid4()}",
            correlation_id=f"corr-sim-{uuid.uuid4()}",
            agent_id="simulation-engine"
        )

        # 3. Trigger LangGraph execution in background
        # We don't await the graph completion here so the API responds instantly.
        # The executor updates its state internally and handles memory persistence.
        asyncio.create_task(self._run_and_update(db, run_record.id, incident_ctx, exec_ctx))
        
        return run_record

    async def _run_and_update(self, db: AsyncSession, run_id: str, incident_ctx: IncidentContext, exec_ctx: ExecutionContext):
        """Background task wrapper to run LangGraph and update simulation status."""
        try:
            logger.info(f"Starting simulation LangGraph run for {incident_ctx.incident_id}")
            result_state = await self.executor.start(incident_ctx, exec_ctx)
            
            # The executor state might contain the final status.
            # Assuming it completed successfully if it reaches here without exception.
            final_status = "COMPLETED"
        except Exception as e:
            logger.error(f"Simulation workflow failed: {e}")
            final_status = "FAILED"
            
        # Update simulation record
        try:
            # We need a new session or to merge it if db is closed.
            # But the passed db session might be closed by FastAPI dependency injection!
            # It's better to just log it for now if we can't reliably reconnect here,
            # or rely on the LangGraph executor's native persistence mechanism which already 
            # stores the investigation and memory.
            # We'll just update the SimulationRun if the session is still active.
            # Actually, standard practice for async background tasks is they get their own session.
            from sentinel_api.database.session import AsyncSessionLocal
            async with AsyncSessionLocal() as bg_db:
                stmt = select(SimulationRun).where(SimulationRun.id == run_id)
                res = await bg_db.execute(stmt)
                run_record = res.scalar_one_or_none()
                if run_record:
                    run_record.status = final_status
                    await bg_db.commit()
        except Exception as e:
            logger.error(f"Failed to update simulation status: {e}")

    async def get_history(self, db: AsyncSession, workspace_id: str) -> List[SimulationRun]:
        stmt = select(SimulationRun).where(SimulationRun.workspace_id == workspace_id).order_by(SimulationRun.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())
