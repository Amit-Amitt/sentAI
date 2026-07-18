import structlog
from typing import Dict, Any, List, Optional
import os

logger = structlog.get_logger("sentinel_api.services.kubernetes_client")

class KubernetesClient:
    """Wrapper around Kubernetes API for synchronization."""

    def __init__(self, in_cluster: bool = False, kubeconfig_path: Optional[str] = None):
        self.in_cluster = in_cluster
        self.kubeconfig_path = kubeconfig_path or os.getenv("SENTINEL_K8S_KUBECONFIG_PATH", "~/.kube/config")
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Kubernetes Python client."""
        try:
            from kubernetes import client, config
            if self.in_cluster:
                config.load_incluster_config()
            else:
                config.load_kubeconfig(config_file=os.path.expanduser(self.kubeconfig_path))
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.initialized = True
        except ImportError:
            logger.warning("kubernetes package not installed. Operating in mock mode.")
            self.initialized = False
        except Exception as e:
            logger.error("Failed to initialize Kubernetes client", error=str(e))
            self.initialized = False

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Fetch all cluster nodes."""
        if not self.initialized:
            return []
        
        nodes_out = []
        try:
            nodes = self.v1.list_node()
            for node in nodes.items:
                status = "NotReady"
                for condition in node.status.conditions:
                    if condition.type == "Ready" and condition.status == "True":
                        status = "Ready"
                        break
                        
                nodes_out.append({
                    "name": node.metadata.name,
                    "status": status,
                    "os_image": node.status.node_info.os_image,
                    "kernel_version": node.status.node_info.kernel_version,
                    "container_runtime_version": node.status.node_info.container_runtime_version,
                    "cpu_capacity": node.status.capacity.get("cpu"),
                    "memory_capacity": node.status.capacity.get("memory")
                })
        except Exception as e:
            logger.error("Failed to list nodes", error=str(e))
            
        return nodes_out

    def list_pods(self) -> List[Dict[str, Any]]:
        """Fetch all cluster pods."""
        if not self.initialized:
            return []
            
        pods_out = []
        try:
            pods = self.v1.list_pod_for_all_namespaces()
            for pod in pods.items:
                
                containers = []
                if pod.status.container_statuses:
                    for c_status in pod.status.container_statuses:
                        state_obj = c_status.state
                        state_str = "unknown"
                        reason = None
                        if state_obj.running:
                            state_str = "running"
                        elif state_obj.waiting:
                            state_str = "waiting"
                            reason = state_obj.waiting.reason
                        elif state_obj.terminated:
                            state_str = "terminated"
                            reason = state_obj.terminated.reason
                            
                        containers.append({
                            "name": c_status.name,
                            "image": c_status.image,
                            "restart_count": c_status.restart_count,
                            "ready": c_status.ready,
                            "state": state_str,
                            "state_reason": reason
                        })
                
                pods_out.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "node_name": pod.spec.node_name,
                    "phase": pod.status.phase,
                    "pod_ip": pod.status.pod_ip,
                    "host_ip": pod.status.host_ip,
                    "creation_timestamp": pod.metadata.creation_timestamp,
                    "containers": containers
                })
        except Exception as e:
            logger.error("Failed to list pods", error=str(e))
            
        return pods_out

    def list_events(self) -> List[Dict[str, Any]]:
        """Fetch recent cluster events."""
        if not self.initialized:
            return []
            
        events_out = []
        try:
            events = self.v1.list_event_for_all_namespaces()
            for event in events.items:
                events_out.append({
                    "namespace": event.metadata.namespace,
                    "event_type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "involved_object_kind": event.involved_object.kind,
                    "involved_object_name": event.involved_object.name,
                    "first_timestamp": event.first_timestamp,
                    "last_timestamp": event.last_timestamp,
                    "count": event.count
                })
        except Exception as e:
            logger.error("Failed to list events", error=str(e))
            
        return events_out
