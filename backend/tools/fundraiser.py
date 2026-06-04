# backend/tools/fundraiser.py
"""Fundraising CRM tools — let agents persist execution-ready results.

Each tool writes structured records to the Fundraising OS CRM (capital_sources,
outreach, interactions) and is registered in ``tools/base.get_all_tools()``.
"""

from datetime import datetime

from tools.base import BaseTool, ToolResult
from fundraising.store import fdb
from fundraising.email import send_email


class SaveCapitalSourceTool(BaseTool):
    name = "save_capital_source"
    description = (
        "Save or update a funding target (investor, VC, accelerator, grant, "
        "government scheme, strategic corporate) in the fundraising CRM. "
        "Upserts by name. Use this for every target you discover or enrich."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the fund/investor/program"},
            "type": {"type": "string", "description": "angel | vc | corporate | government | grant | accelerator"},
            "subtype": {"type": "string"},
            "stage_focus": {"type": "string", "description": "e.g. 'pre-seed, seed'"},
            "sectors": {"type": "string", "description": "e.g. 'AI, SaaS, deep tech'"},
            "geography": {"type": "string"},
            "check_size": {"type": "string", "description": "e.g. '$50k-$250k'"},
            "contact_person": {"type": "string"},
            "contact_email": {"type": "string"},
            "contact_method": {"type": "string", "description": "email | linkedin | x | portal | warm-intro"},
            "website": {"type": "string"},
            "thesis": {"type": "string", "description": "Investment thesis"},
            "why_fit": {"type": "string", "description": "Why Luxor9 fits this investor"},
            "pipeline_stage": {"type": "string", "description": "lead | contacted | replied | meeting | diligence | negotiation | closed"},
            "source": {"type": "string", "description": "Where it was found (crunchbase, openvc, linkedin, ...)"},
        },
        "required": ["name"],
    }

    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        try:
            arguments["task_id"] = context.get("task_id")
            src = await fdb.upsert_source(**arguments)
            return ToolResult(
                success=True,
                output=f"Saved capital source '{src['name']}' "
                       f"(type={src['type']}, stage={src['pipeline_stage']}, id={src['id']}).",
                artifacts={"source": src},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"save_capital_source error: {e}")


class ScoreCapitalSourceTool(BaseTool):
    name = "score_capital_source"
    description = (
        "Set the qualification score (0-100) and optionally the pipeline stage for "
        "a capital source. Identify it by name (preferred) or id."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the source to score"},
            "id": {"type": "string", "description": "Source id (if known)"},
            "probability_score": {"type": "integer", "description": "0-100 fit score"},
            "rationale": {"type": "string", "description": "Short scoring rationale"},
            "pipeline_stage": {"type": "string"},
        },
        "required": ["probability_score"],
    }

    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        try:
            source_id = arguments.get("id") or await fdb.find_source_id(arguments.get("name", ""))
            if not source_id:
                return ToolResult(success=False, output="",
                                  error="Source not found — save it first with save_capital_source.")
            score = max(0, min(100, int(arguments.get("probability_score", 0))))
            fields = {"probability_score": score}
            if arguments.get("pipeline_stage"):
                fields["pipeline_stage"] = arguments["pipeline_stage"]
            src = await fdb.update_source(source_id, **fields)
            if arguments.get("rationale"):
                await fdb.log_interaction(
                    source_id=source_id, type_="note",
                    content=f"Qualification score {score}/100: {arguments['rationale']}",
                )
            return ToolResult(success=True,
                              output=f"Scored '{src['name']}' at {score}/100.",
                              artifacts={"source": src})
        except Exception as e:
            return ToolResult(success=False, output="", error=f"score_capital_source error: {e}")


class DraftOutreachTool(BaseTool):
    name = "draft_outreach"
    description = (
        "Draft a personalized outreach message for a capital source and auto-schedule "
        "the day 3/7/14/21/30 follow-up sequence. Identify the source by name or id. "
        "Email follow-ups are sent automatically by the system once approved; "
        "LinkedIn/X messages are queued as drafts for the founder."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the target source"},
            "id": {"type": "string", "description": "Source id (if known)"},
            "channel": {"type": "string", "description": "email | linkedin | x (default email)"},
            "subject": {"type": "string"},
            "body": {"type": "string", "description": "The personalized message body"},
        },
        "required": ["body"],
    }

    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        try:
            source_id = arguments.get("id") or await fdb.find_source_id(arguments.get("name", ""))
            if not source_id:
                return ToolResult(success=False, output="",
                                  error="Source not found — save it first with save_capital_source.")
            channel = arguments.get("channel", "email")
            out = await fdb.create_outreach(
                source_id=source_id,
                channel=channel,
                subject=arguments.get("subject", ""),
                body=arguments["body"],
                status="draft",
                schedule_followups=True,
            )
            await fdb.update_source(source_id, pipeline_stage="contacted")
            await fdb.log_interaction(
                source_id=source_id, type_=channel,
                content=f"Drafted outreach: {arguments.get('subject', '(no subject)')}",
                next_step="Approve to send; follow-ups scheduled day 3/7/14/21/30.",
            )
            return ToolResult(
                success=True,
                output=f"Drafted {channel} outreach (id={out['id']}) and scheduled "
                       f"the day 3/7/14/21/30 follow-up sequence. Status: draft "
                       f"(approve in the dashboard to send).",
                artifacts={"outreach": out},
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"draft_outreach error: {e}")


class LogInteractionTool(BaseTool):
    name = "log_interaction"
    description = (
        "Record a CRM interaction (note, call, meeting, reply, email) with an "
        "outcome and next step for a capital source. Identify by name or id."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the source"},
            "id": {"type": "string", "description": "Source id (if known)"},
            "type": {"type": "string", "description": "note | call | meeting | reply | email"},
            "content": {"type": "string"},
            "outcome": {"type": "string"},
            "next_step": {"type": "string"},
        },
        "required": ["content"],
    }

    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        try:
            source_id = arguments.get("id") or await fdb.find_source_id(arguments.get("name", ""))
            if not source_id:
                return ToolResult(success=False, output="",
                                  error="Source not found — save it first with save_capital_source.")
            i = await fdb.log_interaction(
                source_id=source_id,
                type_=arguments.get("type", "note"),
                content=arguments["content"],
                outcome=arguments.get("outcome"),
                next_step=arguments.get("next_step"),
            )
            return ToolResult(success=True, output=f"Logged interaction (id={i['id']}).",
                              artifacts={"interaction": i})
        except Exception as e:
            return ToolResult(success=False, output="", error=f"log_interaction error: {e}")


class SendEmailTool(BaseTool):
    name = "send_email"
    description = (
        "Send an email immediately via SMTP (only works when AUTO_SEND is enabled and "
        "SMTP is configured; otherwise it is recorded as a draft). Use for time-sensitive "
        "outreach; routine follow-ups are sent automatically by the scheduler."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the source (to log + resolve email)"},
            "to_email": {"type": "string", "description": "Recipient email (overrides source email)"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["subject", "body"],
    }

    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        try:
            source_id = await fdb.find_source_id(arguments.get("name", ""))
            to_email = arguments.get("to_email")
            if not to_email and source_id:
                src = await fdb.get_source(source_id)
                to_email = src.get("contact_email") if src else None

            result = await send_email(to_email, arguments["subject"], arguments["body"])
            if source_id:
                await fdb.log_interaction(
                    source_id=source_id, type_="email",
                    content=f"send_email: {arguments['subject']}",
                    outcome="sent" if result.get("sent") else result.get("reason") or result.get("error"),
                )
            if result.get("sent"):
                return ToolResult(success=True, output=f"Email sent to {to_email}.")
            return ToolResult(
                success=True,
                output=f"Email NOT sent ({result.get('reason') or result.get('error')}). "
                       f"Recorded as a draft/interaction instead.",
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"send_email error: {e}")


def get_fundraiser_tools():
    return [
        SaveCapitalSourceTool(),
        ScoreCapitalSourceTool(),
        DraftOutreachTool(),
        LogInteractionTool(),
        SendEmailTool(),
    ]
