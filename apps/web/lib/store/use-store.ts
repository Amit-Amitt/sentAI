import { create } from "zustand";
import axios from "axios";
import { queryClient } from "../api/query-client";

export interface AgentRunState {
  name: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  duration_ms: number;
  confidence: number;
  summary: string;
  findings: Array<Record<string, any>>;
}

export interface Incident {
  id: string;
  severity: "SEV1" | "SEV2" | "SEV3";
  status: "ACTIVE" | "RESOLVED";
  summary: string;
  created_at: string;
  affected_services: string[];
  owner: string;
  confidence: number;
  description: string;
  logs: string;
  metrics: string;
  deployment_history: string;
  customer_reports: string;
  
  // Agent states
  agents: Record<string, AgentRunState>;
  
  // Report sections
  root_cause: {
    primary: string;
    supporting_evidence: string[];
    alternative_hypotheses: Array<{ type: string; confidence: number; description: string }>;
  };
  recommendations: Array<{
    id: string;
    title: string;
    description: string;
    priority: "Critical" | "High" | "Medium" | "Low";
    execution_order: number;
  }>;
  recovery_checklist: Array<{
    title: string;
    command: string;
    success_criteria: string;
    completed: boolean;
  }>;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  timestamp: string;
  read: boolean;
}

interface SentinelStore {
  selectedIncidentId: string | null;
  searchQuery: string;
  severityFilter: "ALL" | "SEV1" | "SEV2" | "SEV3";
  statusFilter: "ALL" | "ACTIVE" | "RESOLVED";
  commandPaletteOpen: boolean;
  notifications: Notification[];
  isSimulating: boolean;
  activeSimulationAgent: string | null;
  checkedPlaybookItems: Record<string, boolean>;
  
  // Actions
  setSearchQuery: (query: string) => void;
  setSeverityFilter: (filter: "ALL" | "SEV1" | "SEV2" | "SEV3") => void;
  setStatusFilter: (filter: "ALL" | "ACTIVE" | "RESOLVED") => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setSelectedIncidentId: (id: string | null) => void;
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;
  addNotification: (notification: Omit<Notification, "id" | "timestamp" | "read">) => void;
  toggleChecklistItem: (incidentId: string, checklistTitle: string) => void;
  triggerSimulation: (incidentSummary: string, severity: "SEV1" | "SEV2" | "SEV3") => Promise<void>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const useStore = create<SentinelStore>((set, get) => ({
  selectedIncidentId: null,
  searchQuery: "",
  severityFilter: "ALL",
  statusFilter: "ALL",
  commandPaletteOpen: false,
  notifications: [],
  isSimulating: false,
  activeSimulationAgent: null,
  checkedPlaybookItems: {},

  setSearchQuery: (query) => set({ searchQuery: query }),
  setSeverityFilter: (filter) => set({ severityFilter: filter }),
  setStatusFilter: (filter) => set({ statusFilter: filter }),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  setSelectedIncidentId: (id) => set({ selectedIncidentId: id }),
  
  markNotificationAsRead: (id) => set((state) => ({
    notifications: state.notifications.map((n) => n.id === id ? { ...n, read: true } : n)
  })),
  
  clearNotifications: () => set({ notifications: [] }),
  
  addNotification: (notification) => set((state) => ({
    notifications: [
      {
        ...notification,
        id: `nt-${Date.now()}`,
        timestamp: new Date().toISOString(),
        read: false
      },
      ...state.notifications
    ]
  })),

  toggleChecklistItem: (incidentId, checklistTitle) => set((state) => {
    const key = `${incidentId}-${checklistTitle}`;
    return {
      checkedPlaybookItems: {
        ...state.checkedPlaybookItems,
        [key]: !state.checkedPlaybookItems[key]
      }
    };
  }),

  triggerSimulation: async (incidentSummary, severity) => {
    const { isSimulating } = get();
    if (isSimulating) return;

    set({ isSimulating: true });
    const incidentId = `INC-${Math.floor(100 + Math.random() * 900)}`;

    get().addNotification({
      title: "Simulation Initialized",
      message: `Incident ${incidentId} workflow dispatched in LangGraph`,
      type: "info"
    });

    const updateAgent = (agent: string, status: "RUNNING" | "COMPLETED", duration: number, confidence: number, summary: string) => {
      set({
        activeSimulationAgent: status === "RUNNING" ? agent : null
      });
    };

    const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

    // 1. Coordinator Planning
    updateAgent("Coordinator", "RUNNING", 0, 0, "Analyzing signals schema");
    await sleep(1500);
    updateAgent("Coordinator", "COMPLETED", 140, 0.95, "LangGraph scheduler plan initialized with 3 levels");
    get().addNotification({ title: "Coordinator Plan Built", message: `${incidentId} topology mapped to 3 execution batches`, type: "info" });

    // 2. Parallel Ingestion: Log, Metrics, Deploy
    updateAgent("Deployment Agent", "RUNNING", 0, 0, "Scanning git deployments");
    updateAgent("Log Agent", "RUNNING", 0, 0, "Ingesting log archives");
    updateAgent("Metrics Agent", "RUNNING", 0, 0, "Running anomaly query scan");
    await sleep(2500);
    updateAgent("Deployment Agent", "COMPLETED", 480, 0.90, "Identified recent database schema migration v1.1.2");
    updateAgent("Log Agent", "COMPLETED", 750, 0.88, "Spotted DB Deadlock error in transaction locks");
    updateAgent("Metrics Agent", "COMPLETED", 530, 0.94, "Deadlock count surged from 0 to 45 / min");

    // 3. Review & Root Cause
    updateAgent("Review Agent", "RUNNING", 0, 0, "Filtering customer tickets");
    updateAgent("Root Cause Agent", "RUNNING", 0, 0, "Generating causal graph");
    await sleep(2500);
    updateAgent("Review Agent", "COMPLETED", 610, 0.80, "Found 4 customer reports of checkout locks");
    updateAgent("Root Cause Agent", "COMPLETED", 810, 0.92, "Lock constraints in v1.1.2 caused index scan deadlocks");

    // 4. Playbook & Recommendations
    updateAgent("Recommendation Agent", "RUNNING", 0, 0, "Matching remediation templates");
    await sleep(1500);
    updateAgent("Recommendation Agent", "COMPLETED", 390, 0.90, "Matched DB Lock Contention mitigation plan");

    // Dispatch to real FastAPI backend so it persists as a real investigation record in SQLite
    try {
      await axios.post(`${API_BASE}/incidents/analyze`, {
        incident_id: incidentId,
        severity,
        status: "active",
        summary: incidentSummary,
        logs: [
          "2026-07-18T00:46:11Z [ERROR] transaction-service: postgres deadlock detected",
          "2026-07-18T00:46:15Z [INFO] pg-pool: transaction retries exhausted"
        ],
        metrics: [
          "deadlock_retries_failed_total 45 transactions/min",
          "active_db_locks 240 locks"
        ],
        deployment_history: [
          "2026-07-18T00:35:00Z Deployed version v1.1.2 for transaction-service (Added lock constraints to cart queries)"
        ],
        customer_reports: [
          "Users report checkout failures and timeouts on payment screens."
        ]
      });
      // Invalidate React Query cache so lists immediately update
      await queryClient.invalidateQueries({ queryKey: ["incidents"] });
    } catch (err) {
      console.error("FastAPI backend simulation dispatch failed", err);
    }

    set({
      isSimulating: false,
      selectedIncidentId: incidentId
    });

    get().addNotification({
      title: "Investigation Finalized",
      message: `Root Cause identified for ${incidentId}: DATABASE_DEADLOCK`,
      type: "success"
    });
  }
}));
