import axios from "axios"

const N8N_API_BASE = import.meta.env.VITE_N8N_API_URL || "http://localhost:5678"
const N8N_API_KEY = import.meta.env.VITE_N8N_API_KEY || ""

export interface Execution {
  id: string
  finished: boolean
  mode: "trigger" | "manual" | "webhook"
  startedAt: string
  stoppedAt?: string
  workflowId: string
  data?: {
    resultData?: {
      runData?: Record<string, unknown[]>
    }
  }
}

export interface Workflow {
  id: string
  name: string
  active: boolean
  createdAt: string
  updatedAt: string
}

export interface N8nResponse<T> {
  data: T
}

export const n8nApi = {
  getWorkflows: async (): Promise<Workflow[]> => {
    const response = await axios.get<N8nResponse<Workflow[]>>(`${N8N_API_BASE}/api/v1/workflows`, {
      headers: { Authorization: `Bearer ${N8N_API_KEY}` },
    })
    return response.data.data
  },

  getWorkflow: async (id: string): Promise<Workflow> => {
    const response = await axios.get<N8nResponse<Workflow>>(`${N8N_API_BASE}/api/v1/workflows/${id}`, {
      headers: { Authorization: `Bearer ${N8N_API_KEY}` },
    })
    return response.data.data
  },

  executeWorkflow: async (id: string): Promise<Execution> => {
    const response = await axios.post<N8nResponse<{ execution: Execution }>>(
      `${N8N_API_BASE}/api/v1/workflows/${id}/execute`,
      {},
      { headers: { Authorization: `Bearer ${N8N_API_KEY}` } }
    )
    return response.data.data.execution
  },

  getExecutions: async (workflowId?: string): Promise<Execution[]> => {
    const url = workflowId
      ? `${N8N_API_BASE}/api/v1/executions?workflowId=${workflowId}`
      : `${N8N_API_BASE}/api/v1/executions`
    const response = await axios.get<N8nResponse<Execution[]>>(url, {
      headers: { Authorization: `Bearer ${N8N_API_KEY}` },
    })
    return response.data.data
  },

  getExecution: async (id: string): Promise<Execution> => {
    const response = await axios.get<N8nResponse<Execution>>(`${N8N_API_BASE}/api/v1/executions/${id}`, {
      headers: { Authorization: `Bearer ${N8N_API_KEY}` },
    })
    return response.data.data
  },
}
