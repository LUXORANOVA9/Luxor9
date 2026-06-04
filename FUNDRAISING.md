# Luxor9 Autonomous Fundraising OS

Turn Luxor9 into a 24/7 capital-raising machine that continuously **discovers,
qualifies, researches, personalizes, contacts, follows up with, and tracks**
investors, grants, accelerators, strategic partners, government schemes, and
non-dilutive funding — so the founder is needed only for:

- Final pitch calls
- Due diligence
- Legal signatures
- Investor meetings

Everything else is agentized.

## Architecture

```
Capital Intelligence → Qualification → Research → Narrative → Pitch Deck
   → Outreach → Follow-up → CRM → (Founder only when a meeting is booked)
```

Each layer is the generic Luxor9 `Agent` engine running a fundraising **role
prompt** (`backend/fundraising/roles.py`) with access to fundraiser **tools**
that persist execution-ready results to the CRM.

## Agent workforce (roles)

| Role | Mission |
|------|---------|
| `chief_capital_officer` | Orchestrator — full discover → qualify → outreach cycle (master prompt) |
| `capital_intelligence` | Find 50-200 new funding targets/day |
| `qualification` | Score targets 0-100 (stage/sector/geo/check/portfolio/response fit) |
| `research` | Partner, portfolio, interests, warm-intro paths |
| `narrative` | Personalized "why Luxor9 fits" per investor |
| `pitch_deck` | Exec summary, one-pager, data room, deck, FAQ, financial model |
| `outreach` | Cold email / LinkedIn / X drafts + follow-up sequence |
| `followup` | Day 3/7/14/21/30 sequences |
| `crm` | Maintain pipeline stages & records |
| `grant_hunter` | Government grants, innovation programs, non-dilutive funding |
| `meeting_prep` | Pre-meeting briefs (background, objections, questions, negotiation) |

## Fundraiser tools (used by agents)

- `save_capital_source` — upsert a funding target (by name).
- `score_capital_source` — set 0-100 fit score + pipeline stage.
- `draft_outreach` — save a message **and auto-schedule** the day 3/7/14/21/30 sequence.
- `log_interaction` — CRM touch / outcome / next step.
- `send_email` — send now via SMTP (gated by `AUTO_SEND`).

Discovery uses the built-in `web_search` (DuckDuckGo) and `browser_*` tools — no
external data accounts required.

## Capital sources pipeline (seeded on boot)

VCs (Antler, Entrepreneur First, Pioneer, Sequoia Scout, Peak XV Surge, Accel
Atoms, Y Combinator, Village Global, 500 Global, First Round, Hustle Fund),
strategic corporates (Microsoft / Google / NVIDIA / AWS / IBM / Oracle for
Startups), India government (Startup India Seed Fund, SIDBI, MeitY, NIDHI PRAYAS,
DST, BIRAC, TIDE 2.0, MSME), and accelerators (Techstars, Plug and Play,
Alchemist). Seeded idempotently by `backend/fundraising/seed.py`.

## Outreach & auto-send

The backend sends real cold emails and scheduled follow-ups over **SMTP**.

- `AUTO_SEND=false` (default): outreach is **drafted only** and queued — approve
  in the dashboard. Nothing is sent.
- `AUTO_SEND=true` + SMTP configured: the **follow-up scheduler**
  (`backend/fundraising/scheduler.py`) sends due, approved/scheduled **email**
  outreach automatically at `FOLLOWUP_INTERVAL_MIN` intervals, logging each send.

LinkedIn/X have no public send API, so those channels are stored as queued
drafts for the founder rather than auto-sent.

### Env (see `.env.example`)

```
SMTP_HOST=         SMTP_PORT=587      SMTP_USER=   SMTP_PASSWORD=
FROM_EMAIL=        FOUNDER_EMAIL=
AUTO_SEND=false    FOLLOWUP_INTERVAL_MIN=30
```

## API (under `/api/fundraising`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/report` | Daily Capital Report metrics |
| GET/POST | `/sources` | List / create capital sources |
| GET/PATCH | `/sources/{id}` | Get (with interactions+outreach) / update |
| GET/POST | `/sources/{id}/interactions` | List / add CRM interactions |
| GET | `/outreach` | List outreach (filter by source/status) |
| PATCH | `/outreach/{id}` | Approve / update outreach |
| GET | `/roles` | Launchable agent roles |
| POST | `/run` | Launch a fundraising agent (`{role, description?}`) |

## Founder dashboard

`/fundraising` (Next.js) shows the morning **Capital Report**, the pipeline board
grouped by stage, and one-click agent launch buttons that route into the existing
live task view.
