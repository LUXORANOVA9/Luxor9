"""SQLAlchemy models for the Fundraising OS.

These subclass the SAME declarative ``Base`` as the core models in ``db.py`` so
that ``db.init_tables()`` (``Base.metadata.create_all``) creates them. This
module must be imported during app startup BEFORE ``init_tables`` runs.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON

from db import Base


class CapitalSourceModel(Base):
    """A funding target: angel, VC, corporate, government scheme, grant, accelerator."""

    __tablename__ = "capital_sources"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)          # angel | vc | corporate | government | grant | accelerator
    subtype = Column(String)       # e.g. "pre-seed", "AI-focused angel", "non-dilutive"
    stage_focus = Column(String)   # e.g. "pre-seed, seed"
    sectors = Column(String)       # e.g. "AI, SaaS, deep tech"
    geography = Column(String)
    check_size = Column(String)
    contact_person = Column(String)
    contact_email = Column(String)
    contact_method = Column(String)  # email | linkedin | x | portal | warm-intro
    website = Column(String)
    thesis = Column(Text)
    why_fit = Column(Text)
    probability_score = Column(Integer, default=0)  # 0-100
    pipeline_stage = Column(String, default="lead")
    # lead | contacted | replied | meeting | diligence | negotiation | closed
    source = Column(String)        # where it was discovered (crunchbase, openvc, manual, seed)
    metadata_ = Column("metadata", JSON, default={})
    task_id = Column(String)       # agent run that produced/updated this
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class OutreachModel(Base):
    """A drafted/scheduled/sent outreach message in a follow-up sequence."""

    __tablename__ = "outreach"

    id = Column(String, primary_key=True)
    source_id = Column(String)     # FK -> capital_sources.id
    channel = Column(String)       # email | linkedin | x
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="draft")
    # draft | approved | scheduled | sent | failed
    sequence_step = Column(Integer, default=0)  # 0 (initial), 3, 7, 14, 21, 30
    scheduled_for = Column(DateTime)
    sent_at = Column(DateTime)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class InteractionModel(Base):
    """A CRM touch / outcome / next-step log entry for a capital source."""

    __tablename__ = "interactions"

    id = Column(String, primary_key=True)
    source_id = Column(String)     # FK -> capital_sources.id
    type = Column(String)          # email | call | meeting | note | reply
    content = Column(Text)
    outcome = Column(String)
    next_step = Column(Text)
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
