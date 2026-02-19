// frontend/lib/types.ts

export interface Task {
    id: string
    description: string
    status: 'pending' | 'planning' | 'running' | 'completed' | 'failed' | 'cancelled'
    result_summary?: string
    total_turns: number
    created_at: string
}

export interface AgentEvent {
    type: 'thought' | 'tool_call' | 'tool_result' | 'screenshot' |
    'plan_update' | 'agent_spawn' | 'agent_complete' |
    'task_started' | 'task_complete' | 'error'
    agent_name?: string
    agent_role?: string
    content: Record<string, any>
    timestamp?: string
}

export interface FileInfo {
    path: string
    size: number
}
