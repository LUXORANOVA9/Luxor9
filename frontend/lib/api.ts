// frontend/lib/api.ts

import { apiFetch } from './utils'
import type { Task } from './types'

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
