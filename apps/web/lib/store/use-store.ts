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
  })
}));
