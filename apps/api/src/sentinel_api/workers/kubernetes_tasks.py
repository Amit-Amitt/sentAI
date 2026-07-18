import uuid
import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from sentinel_api.database.session import engine
from sentinel_api.models.kubernetes import K8sCluster, K8sNode, K8sPod, K8sContainer, K8sEvent
from sentinel_api.services.kubernetes_client import KubernetesClient

logger = structlog.get_logger("sentinel_api.workers.kubernetes_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _sync_cluster_state_async(cluster_id: str):
    """Periodically fetches Pods, Nodes, and Events and persists them."""
    
    async with AsyncSessionLocal() as db:
        stmt = select(K8sCluster).where(K8sCluster.id == uuid.UUID(cluster_id))
        result = await db.execute(stmt)
        cluster = result.scalar_one_or_none()
        
        if not cluster:
            logger.error("Cluster not found for sync", cluster_id=cluster_id)
            return

        client = KubernetesClient(
            in_cluster=False, 
            kubeconfig_path=None # In a real scenario, this would come from the cluster config/credentials
        )
        
        if not client.initialized:
            logger.warning("Kubernetes client not initialized. Skipping sync.")
            return

        # Sync Nodes
        nodes = client.list_nodes()
        for node_data in nodes:
            stmt_node = select(K8sNode).where(
                K8sNode.cluster_id == cluster.id,
                K8sNode.name == node_data["name"]
            )
            res_node = await db.execute(stmt_node)
            existing_node = res_node.scalar_one_or_none()
            
            if existing_node:
                existing_node.status = node_data["status"]
            else:
                db.add(K8sNode(
                    id=uuid.uuid4(),
                    cluster_id=cluster.id,
                    name=node_data["name"],
                    status=node_data["status"],
                    os_image=node_data.get("os_image"),
                    kernel_version=node_data.get("kernel_version"),
                    container_runtime_version=node_data.get("container_runtime_version"),
                    cpu_capacity=node_data.get("cpu_capacity"),
                    memory_capacity=node_data.get("memory_capacity")
                ))

        # Sync Pods and Containers
        pods = client.list_pods()
        for pod_data in pods:
            stmt_pod = select(K8sPod).where(
                K8sPod.cluster_id == cluster.id,
                K8sPod.name == pod_data["name"],
                K8sPod.namespace == pod_data["namespace"]
            )
            res_pod = await db.execute(stmt_pod)
            existing_pod = res_pod.scalar_one_or_none()
            
            # Identify if any container is in CrashLoopBackOff or similar error state
            status_message = None
            for c in pod_data.get("containers", []):
                if c["state_reason"] in ["CrashLoopBackOff", "OOMKilled", "ImagePullBackOff", "CreateContainerConfigError"]:
                    status_message = c["state_reason"]
                    break
            
            if existing_pod:
                existing_pod.phase = pod_data["phase"]
                existing_pod.status_message = status_message
                existing_pod.pod_ip = pod_data.get("pod_ip")
                existing_pod.host_ip = pod_data.get("host_ip")
                pod_id = existing_pod.id
            else:
                new_pod = K8sPod(
                    id=uuid.uuid4(),
                    cluster_id=cluster.id,
                    namespace=pod_data["namespace"],
                    node_name=pod_data.get("node_name"),
                    name=pod_data["name"],
                    phase=pod_data["phase"],
                    pod_ip=pod_data.get("pod_ip"),
                    host_ip=pod_data.get("host_ip"),
                    creation_timestamp=pod_data.get("creation_timestamp"),
                    status_message=status_message
                )
                db.add(new_pod)
                await db.flush()
                pod_id = new_pod.id
                
            # Upsert Containers
            for container_data in pod_data.get("containers", []):
                stmt_c = select(K8sContainer).where(
                    K8sContainer.pod_id == pod_id,
                    K8sContainer.name == container_data["name"]
                )
                res_c = await db.execute(stmt_c)
                existing_container = res_c.scalar_one_or_none()
                
                if existing_container:
                    existing_container.state = container_data["state"]
                    existing_container.state_reason = container_data.get("state_reason")
                    existing_container.restart_count = container_data["restart_count"]
                    existing_container.ready = container_data["ready"]
                else:
                    db.add(K8sContainer(
                        id=uuid.uuid4(),
                        pod_id=pod_id,
                        name=container_data["name"],
                        image=container_data["image"],
                        restart_count=container_data["restart_count"],
                        ready=container_data["ready"],
                        state=container_data["state"],
                        state_reason=container_data.get("state_reason")
                    ))
        
        # Sync Events
        events = client.list_events()
        for event_data in events:
            # Upsert event based on involved object and reason
            stmt_event = select(K8sEvent).where(
                K8sEvent.cluster_id == cluster.id,
                K8sEvent.involved_object_name == event_data["involved_object_name"],
                K8sEvent.reason == event_data["reason"]
            )
            res_event = await db.execute(stmt_event)
            existing_event = res_event.scalar_one_or_none()
            
            if existing_event:
                existing_event.count = event_data["count"]
                existing_event.last_timestamp = event_data.get("last_timestamp")
            else:
                db.add(K8sEvent(
                    id=uuid.uuid4(),
                    cluster_id=cluster.id,
                    namespace=event_data["namespace"],
                    event_type=event_data["event_type"],
                    reason=event_data["reason"],
                    message=event_data["message"],
                    involved_object_kind=event_data["involved_object_kind"],
                    involved_object_name=event_data["involved_object_name"],
                    first_timestamp=event_data.get("first_timestamp"),
                    last_timestamp=event_data.get("last_timestamp"),
                    count=event_data["count"]
                ))
                
        cluster.last_synced_at = datetime.datetime.utcnow()
        await db.commit()


def sync_cluster_state(cluster_id: str):
    """Entry point for RQ worker"""
    import asyncio
    asyncio.run(_sync_cluster_state_async(cluster_id))
