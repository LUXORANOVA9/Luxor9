"""
Memory system — Neon PostgreSQL with pgvector.
Free tier: 512MB storage, VECTOR(768) for nomic-embed-text.
Cosine similarity search via pgvector operator.
"""

import json
import uuid
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime

from db import get_db, MemoryModel
from llm_router import FreeLLMRouter


class MemoryStore:
    """
    Cross-session memory using Neon pgvector.
    Embeddings via local Ollama (nomic-embed-text, free, unlimited).
    """

    def __init__(self, llm_router: FreeLLMRouter):
        self.llm = llm_router

    async def store(
        self,
        content: str,
        memory_type: str = "episode",
        metadata: dict = None,
    ):
        """Store a memory with its embedding vector."""
        embedding = await self.llm.embed(content)

        async with get_db() as db:
            memory = MemoryModel(
                id=str(uuid.uuid4()),
                memory_type=memory_type,
                content=content,
                embedding=json.dumps(embedding),
                metadata_=metadata or {},
            )
            db.add(memory)

    async def recall(
        self,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict]:
        """Recall relevant memories using cosine similarity."""
        query_embedding = await self.llm.embed(query)
        query_vec = np.array(query_embedding)

        async with get_db() as db:
            from sqlalchemy import select
            stmt = select(MemoryModel)
            if memory_type:
                stmt = stmt.where(MemoryModel.memory_type == memory_type)

            result = await db.execute(stmt)
            memories = result.scalars().all()

        # Compute cosine similarities
        scored = []
        for mem in memories:
            try:
                mem_vec = np.array(json.loads(mem.embedding))
                similarity = self._cosine_similarity(query_vec, mem_vec)
                scored.append({
                    "content": mem.content,
                    "type": mem.memory_type,
                    "similarity": float(similarity),
                    "metadata": mem.metadata_ or {},
                    "created_at": mem.created_at.isoformat() if mem.created_at else None,
                })
            except Exception:
                continue

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        if len(a) == 0 or len(b) == 0:
            return 0.0
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
