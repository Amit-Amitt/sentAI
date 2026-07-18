import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class K8sCluster(BaseModel):
    """Connected Kubernetes Clusters."""
    __tablename__ = "k8s_clusters"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=True) # e.g., EKS, GKE, Minikube
    kubernetes_version: Mapped[str] = mapped_column(String, nullable=True)
    
    auth_method: Mapped[str] = mapped_column(String, nullable=False) # service_account, kubeconfig
    status: Mapped[str] = mapped_column(String, default="connected", nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class K8sNode(BaseModel):
    """Kubernetes Nodes within a cluster."""
    __tablename__ = "k8s_nodes"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_clusters.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False) # Ready, NotReady
    
    os_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    kernel_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    container_runtime_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    cpu_capacity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    memory_capacity: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class K8sNamespace(BaseModel):
    """Kubernetes Namespaces."""
    __tablename__ = "k8s_namespaces"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_clusters.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)


class K8sDeployment(BaseModel):
    """Kubernetes Deployments."""
    __tablename__ = "k8s_deployments"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_clusters.id", ondelete="CASCADE"), index=True, nullable=False)
    namespace: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    replicas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_replicas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ready_replicas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    creation_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class K8sPod(BaseModel):
    """Kubernetes Pods."""
    __tablename__ = "k8s_pods"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_clusters.id", ondelete="CASCADE"), index=True, nullable=False)
    namespace: Mapped[str] = mapped_column(String, index=True, nullable=False)
    node_name: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    phase: Mapped[str] = mapped_column(String, index=True, nullable=False) # Running, Pending, Failed, Succeeded, Unknown
    
    pod_ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    host_ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    creation_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Store dynamic state like CrashLoopBackOff as a string derived from container statuses
    status_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class K8sContainer(BaseModel):
    """Containers running within a Pod."""
    __tablename__ = "k8s_containers"

    pod_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_pods.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=False)
    
    restart_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    state: Mapped[str] = mapped_column(String, nullable=False) # running, waiting, terminated
    state_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True) # e.g. CrashLoopBackOff, OOMKilled


class K8sEvent(BaseModel):
    """Kubernetes cluster events."""
    __tablename__ = "k8s_events"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("k8s_clusters.id", ondelete="CASCADE"), index=True, nullable=False)
    namespace: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    event_type: Mapped[str] = mapped_column(String, nullable=False) # Normal, Warning
    reason: Mapped[str] = mapped_column(String, index=True, nullable=False) # e.g. FailedScheduling, OOMKilling
    message: Mapped[str] = mapped_column(String, nullable=False)
    
    involved_object_kind: Mapped[str] = mapped_column(String, index=True, nullable=False)
    involved_object_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    first_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
