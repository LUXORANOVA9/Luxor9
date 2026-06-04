-- Neon PostgreSQL Schema
-- Run in Neon SQL Editor (console.neon.tech → SQL Editor)
-- pgvector is pre-installed on Neon free tier

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    config JSONB DEFAULT '{}',
    result_summary TEXT,
    total_turns INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    provider_stats JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Agent execution log
CREATE TABLE IF NOT EXISTS agent_turns (
    id TEXT PRIMARY KEY,
    task_id TEXT REFERENCES tasks(id) ON DELETE CASCADE,
    agent_name TEXT,
    turn_number INTEGER,
    reasoning TEXT,
    tool_name TEXT,
    tool_input JSONB,
    tool_output TEXT,
    model_used TEXT,
    provider TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_turns_task ON agent_turns(task_id);

-- Memory with pgvector (nomic-embed-text = 768 dimensions)
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    memory_type TEXT,
    content TEXT,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ════════════════════════════
-- FUNDRAISING OS
-- ════════════════════════════

-- Capital sources: investors, VCs, accelerators, grants, govt schemes, corporates
CREATE TABLE IF NOT EXISTS capital_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,                      -- angel | vc | corporate | government | grant | accelerator
    subtype TEXT,
    stage_focus TEXT,
    sectors TEXT,
    geography TEXT,
    check_size TEXT,
    contact_person TEXT,
    contact_email TEXT,
    contact_method TEXT,            -- email | linkedin | x | portal | warm-intro
    website TEXT,
    thesis TEXT,
    why_fit TEXT,
    probability_score INTEGER DEFAULT 0,   -- 0-100
    pipeline_stage TEXT DEFAULT 'lead',
    -- lead | contacted | replied | meeting | diligence | negotiation | closed
    source TEXT,
    metadata JSONB DEFAULT '{}',
    task_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sources_stage ON capital_sources(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_sources_type ON capital_sources(type);

-- Outreach messages + scheduled follow-up sequence
CREATE TABLE IF NOT EXISTS outreach (
    id TEXT PRIMARY KEY,
    source_id TEXT REFERENCES capital_sources(id) ON DELETE CASCADE,
    channel TEXT,                   -- email | linkedin | x
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'draft',    -- draft | approved | scheduled | sent | failed
    sequence_step INTEGER DEFAULT 0,-- 0 (initial), 3, 7, 14, 21, 30
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outreach_source ON outreach(source_id);
CREATE INDEX IF NOT EXISTS idx_outreach_due ON outreach(status, scheduled_for);

-- CRM interaction log
CREATE TABLE IF NOT EXISTS interactions (
    id TEXT PRIMARY KEY,
    source_id TEXT REFERENCES capital_sources(id) ON DELETE CASCADE,
    type TEXT,                      -- email | call | meeting | note | reply
    content TEXT,
    outcome TEXT,
    next_step TEXT,
    scheduled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_source ON interactions(source_id);
