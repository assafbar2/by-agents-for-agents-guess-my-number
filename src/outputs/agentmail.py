from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentMailConfig:
    api_key: str
    inbox_id: str
    recipient_email: str

    @classmethod
    def from_env(cls) -> "AgentMailConfig | None":
        api_key = os.getenv("AGENTMAIL_API_KEY")
        inbox_id = os.getenv("AGENTMAIL_INBOX_ID")
        recipient_email = os.getenv("REPORT_RECIPIENT_EMAIL")

        if not api_key or not inbox_id or not recipient_email:
            return None

        return cls(api_key=api_key, inbox_id=inbox_id, recipient_email=recipient_email)


def send_report_email(*, config: AgentMailConfig, subject: str, text: str, html: str) -> None:
    payload = {
        "to": config.recipient_email,
        "subject": subject,
        "text": text,
        "html": html,
    }
    request = urllib.request.Request(
        f"https://api.agentmail.to/v0/inboxes/{config.inbox_id}/messages/send",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status >= 300:
            raise RuntimeError(f"AgentMail returned HTTP {response.status}")

