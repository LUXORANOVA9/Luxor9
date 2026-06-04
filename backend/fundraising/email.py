"""SMTP email sending for the Fundraising OS.

Self-contained (stdlib smtplib), env-configured, and gated by ``AUTO_SEND``.
If sending is disabled or credentials are missing, ``send_email`` returns a
non-fatal result so the agent/scheduler can keep the message as a draft.
"""

import asyncio
import smtplib
from email.message import EmailMessage
from typing import Optional

from config import settings


def _send_sync(to_email: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.FROM_EMAIL or settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject or "(no subject)"
    msg.set_content(body or "")

    port = settings.SMTP_PORT
    if port == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, port, timeout=30) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, port, timeout=30) as server:
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPException:
                pass  # server may not support STARTTLS (e.g. local test relays)
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)


def is_send_enabled() -> bool:
    return bool(settings.AUTO_SEND and settings.SMTP_HOST)


async def send_email(to_email: str, subject: str, body: str) -> dict:
    """Attempt to send an email. Returns {sent: bool, reason/error: str}."""
    if not settings.AUTO_SEND:
        return {"sent": False, "reason": "AUTO_SEND disabled — kept as draft"}
    if not settings.SMTP_HOST:
        return {"sent": False, "reason": "SMTP not configured — kept as draft"}
    if not to_email:
        return {"sent": False, "reason": "no recipient email"}
    try:
        await asyncio.to_thread(_send_sync, to_email, subject, body)
        return {"sent": True}
    except Exception as e:  # noqa: BLE001 — surface the SMTP error to the caller
        return {"sent": False, "error": str(e)}
