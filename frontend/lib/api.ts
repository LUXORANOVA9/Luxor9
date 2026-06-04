// frontend/lib/api.ts

import { apiFetch } from './utils'
import type {
    Task, CapitalSource, Outreach, Interaction, CapitalReport, FundraisingRole,
} from './types'

export const api = {
    async createTask(description: string, config = {}): Promise<{ task_id: string }> {
        return apiFetch('/api/tasks', {
            method: 'POST',
            body: JSON.stringify({ description, config }),
        })
    },

    async listTasks(): Promise<Task[]> {
        const data = await apiFetch('/api/tasks')
        return data
    },

    async getTask(id: string): Promise<Task> {
        return apiFetch(`/api/tasks/${id}`)
    },

    async getTaskFiles(id: string): Promise<{ files: { path: string; size: number }[] }> {
        return apiFetch(`/api/tasks/${id}/files`)
    },

    async sendMessage(taskId: string, message: string, action = 'message') {
        return apiFetch(`/api/tasks/${taskId}/message`, {
            method: 'POST',
            body: JSON.stringify({ message, action }),
        })
    },

    async cancelTask(id: string) {
        return apiFetch(`/api/tasks/${id}`, { method: 'DELETE' })
    },

    getFileUrl(taskId: string, path: string): string {
        const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        return `${base}/api/tasks/${taskId}/files/${path}`
    },
}

export const fundraisingApi = {
    async getReport(): Promise<CapitalReport> {
        return apiFetch('/api/fundraising/report')
    },

    async listSources(params: { stage?: string; type?: string } = {}): Promise<CapitalSource[]> {
        const qs = new URLSearchParams(params as Record<string, string>).toString()
        return apiFetch(`/api/fundraising/sources${qs ? `?${qs}` : ''}`)
    },

    async getSource(id: string): Promise<CapitalSource & { interactions: Interaction[]; outreach: Outreach[] }> {
        return apiFetch(`/api/fundraising/sources/${id}`)
    },

    async updateSource(id: string, payload: Partial<CapitalSource>): Promise<CapitalSource> {
        return apiFetch(`/api/fundraising/sources/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(payload),
        })
    },

    async listOutreach(params: { source_id?: string; status?: string } = {}): Promise<Outreach[]> {
        const qs = new URLSearchParams(params as Record<string, string>).toString()
        return apiFetch(`/api/fundraising/outreach${qs ? `?${qs}` : ''}`)
    },

    async approveOutreach(id: string): Promise<Outreach> {
        return apiFetch(`/api/fundraising/outreach/${id}`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'approved' }),
        })
    },

    async listRoles(): Promise<FundraisingRole[]> {
        return apiFetch('/api/fundraising/roles')
    },

    async runAgent(role: string, description?: string): Promise<{ task_id: string; role: string }> {
        return apiFetch('/api/fundraising/run', {
            method: 'POST',
            body: JSON.stringify({ role, description }),
        })
    },
}
