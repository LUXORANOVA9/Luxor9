"""
Neon PostgreSQL database layer — async SQLAlchemy + asyncpg.
Free tier: 512MB storage, autoscaling compute.
"""

import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, text
from datetime import datetime
from typing import Optional, List


# ═══════════════════
# Engine + Session
# ═══════════════════

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Neon requires SSL; asyncpg needs the URL scheme swapped
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg doesn't support channel_binding param — strip it
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
_parsed = urlparse(DATABASE_URL)
_params = parse_qs(_parsed.query)
_params.pop("channel_binding", None)
DATABASE_URL = urlunparse(_parsed._replace(query=urlencode(_params, doseq=True)))

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={"ssl": "require"} if "neon" in DATABASE_URL else {},
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# ═══════════════════
# Models
# ═══════════════════

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending")
    config = Column(JSON, default={})
    result_summary = Column(Text)
    total_turns = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    provider_stats = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


class AgentTurnModel(Base):
    __tablename__ = "agent_turns"

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    agent_name = Column(String)
    turn_number = Column(Integer)
    reasoning = Column(Text)
    tool_name = Column(String)
    tool_input = Column(JSON)
    tool_output = Column(Text)
    model_used = Column(String)
    provider = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    memory_type = Column(String)
    content = Column(Text)
    embedding = Column(Text)  # JSON-serialized vector (pgvector used at query level)
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


# ═══════════════════
# Context manager
# ═══════════════════

@asynccontextmanager
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ═══════════════════
# Database operations
# ═══════════════════

class Database:
    """Async database operations for Neon PostgreSQL."""

    # — TASKS —

    async def create_task(self, task_id: str, description: str, config: dict = {}) -> dict:
        async with get_db() as db:
            task = TaskModel(
                id=task_id,
                description=description,
                status="pending",
                config=config,
            )
            db.add(task)
            await db.flush()
            return {"id": task.id, "status": task.status}

    async def update_task(self, task_id: str, **kwargs) -> dict:
        async with get_db() as db:
            from sqlalchemy import update
            stmt = update(TaskModel).where(TaskModel.id == task_id).values(**kwargs)
            await db.execute(stmt)
            return {"id": task_id, **kwargs}

    async def get_task(self, task_id: str) -> Optional[dict]:
        async with get_db() as db:
            from sqlalchemy import select
            result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                return None
            return {
                "id": task.id,
                "description": task.description,
                "status": task.status,
                "config": task.config,
                "result_summary": task.result_summary,
                "total_turns": task.total_turns or 0,
                "total_tokens": task.total_tokens or 0,
                "provider_stats": task.provider_stats or {},
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }

    async def list_tasks(self, limit: int = 50) -> List[dict]:
        async with get_db() as db:
            from sqlalchemy import select
            result = await db.execute(
                select(TaskModel).order_by(TaskModel.created_at.desc()).limit(limit)
            )
            tasks = result.scalars().all()
            return [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status,
                    "total_turns": t.total_turns or 0,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tasks
            ]

    # — AGENT TURNS —

    async def log_turn(self, task_id: str, agent_name: str, turn_number: int,
                       tool_name: str = None, tool_input: dict = None,
                       tool_output: str = None, reasoning: str = None,
                       model_used: str = None, provider: str = None,
                       input_tokens: int = 0, output_tokens: int = 0,
                       latency_ms: int = 0):
        import uuid
        async with get_db() as db:
            turn = AgentTurnModel(
                id=str(uuid.uuid4()),
                task_id=task_id,
                agent_name=agent_name,
                turn_number=turn_number,
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=(tool_output or "")[:10000],
                reasoning=(reasoning or "")[:5000],
                model_used=model_used,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )
            db.add(turn)

    async def get_task_turns(self, task_id: str) -> List[dict]:
        async with get_db() as db:
            from sqlalchemy import select
            result = await db.execute(
                select(AgentTurnModel)
                .where(AgentTurnModel.task_id == task_id)
                .order_by(AgentTurnModel.turn_number)
            )
            turns = result.scalars().all()
            return [
                {
                    "id": t.id,
                    "turn_number": t.turn_number,
                    "tool_name": t.tool_name,
                    "tool_input": t.tool_input,
                    "tool_output": t.tool_output,
                    "reasoning": t.reasoning,
                    "model_used": t.model_used,
                    "provider": t.provider,
                    "input_tokens": t.input_tokens,
                    "output_tokens": t.output_tokens,
                    "latency_ms": t.latency_ms,
                }
                for t in turns
            ]

    # — INIT —

    async def init_tables(self):
        """Create tables if they don't exist."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# Global instance
db = Database()
