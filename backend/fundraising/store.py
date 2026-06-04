"""Async CRM operations for the Fundraising OS.

Mirrors the style of ``Database`` in ``db.py`` and reuses its ``get_db()``
async session context manager.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy import select, update, func

from db import get_db
from fundraising.models import CapitalSourceModel, OutreachModel, InteractionModel

# Follow-up cadence (days after the initial touch).
FOLLOWUP_SEQUENCE = [3, 7, 14, 21, 30]


def _source_dict(s: CapitalSourceModel) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "type": s.type,
        "subtype": s.subtype,
        "stage_focus": s.stage_focus,
        "sectors": s.sectors,
        "geography": s.geography,
        "check_size": s.check_size,
        "contact_person": s.contact_person,
        "contact_email": s.contact_email,
        "contact_method": s.contact_method,
        "website": s.website,
        "thesis": s.thesis,
        "why_fit": s.why_fit,
        "probability_score": s.probability_score or 0,
        "pipeline_stage": s.pipeline_stage,
        "source": s.source,
        "metadata": s.metadata_ or {},
        "task_id": s.task_id,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _outreach_dict(o: OutreachModel) -> dict:
    return {
        "id": o.id,
        "source_id": o.source_id,
        "channel": o.channel,
        "subject": o.subject,
        "body": o.body,
        "status": o.status,
        "sequence_step": o.sequence_step,
        "scheduled_for": o.scheduled_for.isoformat() if o.scheduled_for else None,
        "sent_at": o.sent_at.isoformat() if o.sent_at else None,
        "error": o.error,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _interaction_dict(i: InteractionModel) -> dict:
    return {
        "id": i.id,
        "source_id": i.source_id,
        "type": i.type,
        "content": i.content,
        "outcome": i.outcome,
        "next_step": i.next_step,
        "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }


class FundraisingDB:
    """CRM persistence layer for capital sources, outreach, and interactions."""

    # — CAPITAL SOURCES —

    async def upsert_source(self, **fields) -> dict:
        """Insert a source, or update the existing one matching name (case-insensitive)."""
        name = (fields.get("name") or "").strip()
        async with get_db() as db:
            existing = None
            if name:
                res = await db.execute(
                    select(CapitalSourceModel).where(
                        func.lower(CapitalSourceModel.name) == name.lower()
                    )
                )
                existing = res.scalar_one_or_none()

            if existing:
                for k, v in fields.items():
                    if k == "metadata":
                        existing.metadata_ = v
                    elif v is not None and hasattr(existing, k):
                        setattr(existing, k, v)
                existing.updated_at = datetime.utcnow()
                await db.flush()
                return _source_dict(existing)

            src = CapitalSourceModel(
                id=str(uuid.uuid4()),
                name=name or "Unnamed source",
                type=fields.get("type"),
                subtype=fields.get("subtype"),
                stage_focus=fields.get("stage_focus"),
                sectors=fields.get("sectors"),
                geography=fields.get("geography"),
                check_size=fields.get("check_size"),
                contact_person=fields.get("contact_person"),
                contact_email=fields.get("contact_email"),
                contact_method=fields.get("contact_method"),
                website=fields.get("website"),
                thesis=fields.get("thesis"),
                why_fit=fields.get("why_fit"),
                probability_score=fields.get("probability_score") or 0,
                pipeline_stage=fields.get("pipeline_stage") or "lead",
                source=fields.get("source"),
                metadata_=fields.get("metadata") or {},
                task_id=fields.get("task_id"),
            )
            db.add(src)
            await db.flush()
            return _source_dict(src)

    async def list_sources(self, stage: Optional[str] = None,
                           type_: Optional[str] = None,
                           limit: int = 500) -> List[dict]:
        async with get_db() as db:
            stmt = select(CapitalSourceModel)
            if stage:
                stmt = stmt.where(CapitalSourceModel.pipeline_stage == stage)
            if type_:
                stmt = stmt.where(CapitalSourceModel.type == type_)
            stmt = stmt.order_by(
                CapitalSourceModel.probability_score.desc(),
                CapitalSourceModel.updated_at.desc(),
            ).limit(limit)
            res = await db.execute(stmt)
            return [_source_dict(s) for s in res.scalars().all()]

    async def get_source(self, source_id: str) -> Optional[dict]:
        async with get_db() as db:
            res = await db.execute(
                select(CapitalSourceModel).where(CapitalSourceModel.id == source_id)
            )
            s = res.scalar_one_or_none()
            return _source_dict(s) if s else None

    async def update_source(self, source_id: str, **fields) -> Optional[dict]:
        async with get_db() as db:
            values = {k: v for k, v in fields.items() if v is not None}
            if "metadata" in values:
                values["metadata_"] = values.pop("metadata")
            values["updated_at"] = datetime.utcnow()
            await db.execute(
                update(CapitalSourceModel)
                .where(CapitalSourceModel.id == source_id)
                .values(**values)
            )
            res = await db.execute(
                select(CapitalSourceModel).where(CapitalSourceModel.id == source_id)
            )
            s = res.scalar_one_or_none()
            return _source_dict(s) if s else None

    async def find_source_id(self, name: str) -> Optional[str]:
        if not name:
            return None
        async with get_db() as db:
            res = await db.execute(
                select(CapitalSourceModel.id).where(
                    func.lower(CapitalSourceModel.name) == name.strip().lower()
                )
            )
            row = res.scalar_one_or_none()
            return row

    # — OUTREACH —

    async def create_outreach(self, source_id: str, channel: str, subject: str,
                              body: str, status: str = "draft",
                              schedule_followups: bool = True) -> dict:
        """Create the initial outreach message and (optionally) schedule the sequence."""
        async with get_db() as db:
            now = datetime.utcnow()
            initial = OutreachModel(
                id=str(uuid.uuid4()),
                source_id=source_id,
                channel=channel,
                subject=subject,
                body=body,
                status=status,
                sequence_step=0,
                scheduled_for=now,
            )
            db.add(initial)

            if schedule_followups:
                for day in FOLLOWUP_SEQUENCE:
                    db.add(OutreachModel(
                        id=str(uuid.uuid4()),
                        source_id=source_id,
                        channel=channel,
                        subject=f"Re: {subject}" if subject else subject,
                        body=body,
                        status="draft",
                        sequence_step=day,
                        scheduled_for=now + timedelta(days=day),
                    ))
            await db.flush()
            return _outreach_dict(initial)

    async def list_outreach(self, source_id: Optional[str] = None,
                            status: Optional[str] = None,
                            limit: int = 500) -> List[dict]:
        async with get_db() as db:
            stmt = select(OutreachModel)
            if source_id:
                stmt = stmt.where(OutreachModel.source_id == source_id)
            if status:
                stmt = stmt.where(OutreachModel.status == status)
            stmt = stmt.order_by(OutreachModel.scheduled_for).limit(limit)
            res = await db.execute(stmt)
            return [_outreach_dict(o) for o in res.scalars().all()]

    async def update_outreach(self, outreach_id: str, **fields) -> Optional[dict]:
        async with get_db() as db:
            await db.execute(
                update(OutreachModel)
                .where(OutreachModel.id == outreach_id)
                .values(**fields)
            )
            res = await db.execute(
                select(OutreachModel).where(OutreachModel.id == outreach_id)
            )
            o = res.scalar_one_or_none()
            return _outreach_dict(o) if o else None

    async def due_outreach(self, now: Optional[datetime] = None) -> List[dict]:
        """Outreach that is approved/scheduled and due to send (joined with contact email)."""
        now = now or datetime.utcnow()
        async with get_db() as db:
            stmt = (
                select(OutreachModel, CapitalSourceModel)
                .join(CapitalSourceModel, CapitalSourceModel.id == OutreachModel.source_id)
                .where(
                    OutreachModel.status.in_(["approved", "scheduled"]),
                    OutreachModel.scheduled_for <= now,
                )
                .order_by(OutreachModel.scheduled_for)
            )
            res = await db.execute(stmt)
            out = []
            for o, s in res.all():
                d = _outreach_dict(o)
                d["contact_email"] = s.contact_email
                d["source_name"] = s.name
                out.append(d)
            return out

    # — INTERACTIONS —

    async def log_interaction(self, source_id: str, type_: str, content: str,
                              outcome: Optional[str] = None,
                              next_step: Optional[str] = None,
                              scheduled_at: Optional[datetime] = None) -> dict:
        async with get_db() as db:
            i = InteractionModel(
                id=str(uuid.uuid4()),
                source_id=source_id,
                type=type_,
                content=content,
                outcome=outcome,
                next_step=next_step,
                scheduled_at=scheduled_at,
            )
            db.add(i)
            await db.flush()
            return _interaction_dict(i)

    async def list_interactions(self, source_id: str, limit: int = 200) -> List[dict]:
        async with get_db() as db:
            res = await db.execute(
                select(InteractionModel)
                .where(InteractionModel.source_id == source_id)
                .order_by(InteractionModel.created_at.desc())
                .limit(limit)
            )
            return [_interaction_dict(i) for i in res.scalars().all()]

    # — DASHBOARD REPORT —

    async def report(self) -> dict:
        """Aggregate the daily Capital Report metrics."""
        async with get_db() as db:
            day_ago = datetime.utcnow() - timedelta(days=1)

            async def _count(stmt) -> int:
                res = await db.execute(stmt)
                return int(res.scalar() or 0)

            total_sources = await _count(select(func.count(CapitalSourceModel.id)))
            new_sources = await _count(
                select(func.count(CapitalSourceModel.id))
                .where(CapitalSourceModel.created_at >= day_ago)
            )
            qualified = await _count(
                select(func.count(CapitalSourceModel.id))
                .where(CapitalSourceModel.probability_score >= 60)
            )
            emails_sent = await _count(
                select(func.count(OutreachModel.id))
                .where(OutreachModel.status == "sent")
            )
            replies = await _count(
                select(func.count(InteractionModel.id))
                .where(InteractionModel.type == "reply")
            )
            meetings = await _count(
                select(func.count(CapitalSourceModel.id))
                .where(CapitalSourceModel.pipeline_stage == "meeting")
            )
            grants = await _count(
                select(func.count(CapitalSourceModel.id))
                .where(CapitalSourceModel.type.in_(["grant", "government"]))
            )

            # Pipeline value: sum of probability-weighted midpoint check sizes.
            res = await db.execute(
                select(CapitalSourceModel.check_size, CapitalSourceModel.probability_score)
            )
            pipeline_value = 0.0
            for check_size, score in res.all():
                pipeline_value += _check_midpoint(check_size) * ((score or 0) / 100.0)

            # Stage breakdown.
            res = await db.execute(
                select(CapitalSourceModel.pipeline_stage, func.count(CapitalSourceModel.id))
                .group_by(CapitalSourceModel.pipeline_stage)
            )
            stages = {stage or "lead": int(cnt) for stage, cnt in res.all()}

            # Highest-priority source.
            res = await db.execute(
                select(CapitalSourceModel)
                .order_by(CapitalSourceModel.probability_score.desc())
                .limit(1)
            )
            top = res.scalar_one_or_none()
            highest_priority = _source_dict(top) if top else None

            return {
                "generated_at": datetime.utcnow().isoformat(),
                "total_sources": total_sources,
                "new_sources": new_sources,
                "qualified_targets": qualified,
                "emails_sent": emails_sent,
                "replies_received": replies,
                "meetings_booked": meetings,
                "grant_opportunities": grants,
                "pipeline_value": round(pipeline_value),
                "stages": stages,
                "highest_priority": highest_priority,
                "action_required": (
                    f"Engage {highest_priority['name']} "
                    f"({highest_priority['probability_score']}% fit)"
                    if highest_priority else "Run the Capital Intelligence agent to find targets"
                ),
            }


def _check_midpoint(check_size: Optional[str]) -> float:
    """Best-effort parse of a check-size string like '$50k-$250k' into a USD midpoint."""
    if not check_size:
        return 0.0
    import re
    nums = []
    for m in re.finditer(r"(\d[\d,\.]*)\s*([kmb]?)", check_size.lower()):
        val = float(m.group(1).replace(",", ""))
        unit = m.group(2)
        if unit == "k":
            val *= 1_000
        elif unit == "m":
            val *= 1_000_000
        elif unit == "b":
            val *= 1_000_000_000
        nums.append(val)
    if not nums:
        return 0.0
    return sum(nums) / len(nums)


# Global instance.
fdb = FundraisingDB()
