"""Autonomous follow-up scheduler.

A lightweight asyncio loop (started in the FastAPI lifespan) that periodically
sends due, approved/scheduled email outreach via SMTP — this is what makes the
day 3/7/14/21/30 follow-up sequence fire without the founder.

LinkedIn/X have no public send API, so those channels are skipped (left as
drafts) and surfaced in the UI instead.
"""

import asyncio
from datetime import datetime

from config import settings
from fundraising.store import fdb
from fundraising.email import send_email, is_send_enabled


async def _process_due_once() -> int:
    """Send all currently-due email outreach. Returns count sent."""
    due = await fdb.due_outreach(datetime.utcnow())
    sent = 0
    for item in due:
        if item["channel"] != "email":
            continue  # LinkedIn/X stay as drafts
        result = await send_email(item.get("contact_email"), item["subject"], item["body"])
        if result.get("sent"):
            await fdb.update_outreach(item["id"], status="sent", sent_at=datetime.utcnow())
            await fdb.log_interaction(
                source_id=item["source_id"],
                type_="email",
                content=f"Sent (step {item['sequence_step']}): {item['subject']}",
                outcome="sent",
            )
            sent += 1
        elif "error" in result:
            await fdb.update_outreach(item["id"], status="failed", error=result["error"])
    return sent


async def followup_scheduler_loop(stop_event: asyncio.Event):
    """Run until ``stop_event`` is set, processing due outreach each interval."""
    interval = max(1, settings.FOLLOWUP_INTERVAL_MIN) * 60
    while not stop_event.is_set():
        try:
            if is_send_enabled():
                sent = await _process_due_once()
                if sent:
                    print(f"📤 Fundraising scheduler sent {sent} follow-up email(s)")
        except Exception as e:  # noqa: BLE001 — never let the loop die
            print(f"⚠️  Follow-up scheduler error: {e}")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass
