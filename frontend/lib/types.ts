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

// ── Fundraising OS ──

export type PipelineStage =
    | 'lead' | 'contacted' | 'replied' | 'meeting'
    | 'diligence' | 'negotiation' | 'closed'

export interface CapitalSource {
    id: string
    name: string
    type?: string
    subtype?: string
    stage_focus?: string
    sectors?: string
    geography?: string
    check_size?: string
    contact_person?: string
    contact_email?: string
    contact_method?: string
    website?: string
    thesis?: string
    why_fit?: string
    probability_score: number
    pipeline_stage: PipelineStage
    source?: string
    metadata?: Record<string, any>
    task_id?: string
    created_at?: string
    updated_at?: string
}

export interface Outreach {
    id: string
    source_id: string
    channel: string
    subject?: string
    body?: string
    status: 'draft' | 'approved' | 'scheduled' | 'sent' | 'failed'
    sequence_step: number
    scheduled_for?: string
    sent_at?: string
    error?: string
    created_at?: string
}

export interface Interaction {
    id: string
    source_id: string
    type: string
    content?: string
    outcome?: string
    next_step?: string
    scheduled_at?: string
    created_at?: string
}

export interface CapitalReport {
    generated_at: string
    total_sources: number
    new_sources: number
    qualified_targets: number
    emails_sent: number
    replies_received: number
    meetings_booked: number
    grant_opportunities: number
    pipeline_value: number
    stages: Record<string, number>
    highest_priority: CapitalSource | null
    action_required: string
}

export interface FundraisingRole {
    role: string
    label: string
    description: string
}
