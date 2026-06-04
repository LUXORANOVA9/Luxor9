"""Fundraising OS REST API (mounted under /api/fundraising)."""

import uuid
from datetime import datetime
from typing import Optional, Callable, Awaitable

from fastapi import APIRouter, HTTPException

from db import db
from fundraising.store import fdb
from fundraising.roles import get_role_prompt, ROLE_CATALOG, FUNDRAISING_ROLES

router = APIRouter(prefix="/api/fundraising", tags=["fundraising"])

# Injected by main.py to launch an agent task without a circular import.
# Signature: launch(task_id: str, description: str, config: dict) -> Awaitable
_task_launcher: Optional[Callable[[str, str, dict], Awaitable]] = None


def set_task_launcher(fn: Callable[[str, str, dict], Awaitable]) -> None:
    global _task_launcher
    _task_launcher = fn


# — Capital sources / CRM —

@router.get("/sources")
async def list_sources(stage: Optional[str] = None, type: Optional[str] = None):
    return await fdb.list_sources(stage=stage, type_=type)


@router.post("/sources")
async def create_source(payload: dict):
    if not (payload.get("name") or "").strip():
        raise HTTPException(400, "name required")
    return await fdb.upsert_source(**payload)


@router.get("/sources/{source_id}")
async def get_source(source_id: str):
    src = await fdb.get_source(source_id)
    if not src:
        raise HTTPException(404, "Source not found")
    src["interactions"] = await fdb.list_interactions(source_id)
    src["outreach"] = await fdb.list_outreach(source_id=source_id)
    return src


@router.patch("/sources/{source_id}")
async def update_source(source_id: str, payload: dict):
    src = await fdb.update_source(source_id, **payload)
    if not src:
        raise HTTPException(404, "Source not found")
    return src


@router.get("/sources/{source_id}/interactions")
async def list_interactions(source_id: str):
    return await fdb.list_interactions(source_id)


@router.post("/sources/{source_id}/interactions")
async def add_interaction(source_id: str, payload: dict):
    return await fdb.log_interaction(
        source_id=source_id,
        type_=payload.get("type", "note"),
        content=payload.get("content", ""),
        outcome=payload.get("outcome"),
        next_step=payload.get("next_step"),
    )


# — Outreach —

@router.get("/outreach")
async def list_outreach(source_id: Optional[str] = None, status: Optional[str] = None):
    return await fdb.list_outreach(source_id=source_id, status=status)


@router.patch("/outreach/{outreach_id}")
async def update_outreach(outreach_id: str, payload: dict):
    out = await fdb.update_outreach(outreach_id, **payload)
    if not out:
        raise HTTPException(404, "Outreach not found")
    return out


# — Dashboard report —

@router.get("/report")
async def report():
    return await fdb.report()


@router.get("/roles")
async def roles():
    return ROLE_CATALOG


# — Launch a fundraising agent —

@router.post("/run")
async def run(payload: dict):
    role = payload.get("role", "chief_capital_officer")
    if role not in FUNDRAISING_ROLES:
        raise HTTPException(400, f"Unknown role: {role}")
    if _task_launcher is None:
        raise HTTPException(503, "Task launcher not ready")

    description = payload.get("description") or _default_description(role)
    config = {"role": role, "fundraising": True}

    task_id = str(uuid.uuid4())
    await db.create_task(task_id, description, config)
    await _task_launcher(task_id, description, config)
    return {"task_id": task_id, "role": role, "status": "pending"}


def _default_description(role: str) -> str:
    return {
        "chief_capital_officer":
            "Run a full autonomous fundraising cycle for Luxor9: discover new "
            "capital sources, qualify and score them, research the best fits, "
            "write personalized narratives, and draft + schedule outreach.",
        "capital_intelligence":
            "Discover 50+ new funding targets for Luxor9 (angels, VCs, "
            "accelerators, grants, government schemes) and save them to the CRM.",
        "qualification":
            "Score all un-scored capital sources 0-100 on fit for Luxor9.",
        "research":
            "Deep-research the top capital sources and enrich their CRM records.",
        "narrative":
            "Write a personalized 'why Luxor9 fits' narrative for the top targets.",
        "pitch_deck":
            "Generate Luxor9 fundraising collateral: exec summary, one-pager, "
            "data room outline, pitch deck outline, investor FAQ, financial model.",
        "outreach":
            "Draft personalized outreach for qualified Luxor9 targets and schedule "
            "the day 3/7/14/21/30 follow-up sequences.",
        "followup":
            "Ensure every contacted target has a complete follow-up sequence.",
        "crm": "Clean up and update pipeline stages across all capital sources.",
        "grant_hunter":
            "Find non-dilutive funding (grants, government programs, competitions) "
            "for Luxor9 and save them to the CRM.",
        "meeting_prep":
            "Prepare investor meeting briefs for sources in the meeting stage.",
    }.get(role, f"Run the {role} fundraising agent for Luxor9.")
