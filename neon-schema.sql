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
