from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass

from src.game import GameResult


@dataclass(frozen=True)
class NotionConfig:
    api_key: str
    page_id: str

    @classmethod
    def from_env(cls) -> "NotionConfig | None":
        api_key = os.getenv("NOTION_API_KEY", "dummy-notion-api-key")
        page_id = os.getenv("NOTION_PAGE_ID", "dummy-notion-page-id")

        if api_key.startswith("dummy-") or page_id.startswith("dummy-"):
            return None

        return cls(api_key=api_key, page_id=page_id)


def rich_text(content: str) -> list[dict]:
    return [{"type": "text", "text": {"content": content[:2000]}}]


def result_blocks(result: GameResult) -> list[dict]:
    children: list[dict] = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": rich_text(f"Guess My Number - {result.run_id}")},
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text(
                    f"Secret: {result.secret_number}. Result: {result.summary}"
                )
            },
        },
    ]

    for competitor in result.competitors:
        transcript = "; ".join(
            f"{attempt.turn}. {attempt.guess} -> {attempt.feedback.replace('_', ' ')}"
            for attempt in competitor.attempts
        )
        children.append(
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": rich_text(
                        f"{competitor.display_name}: {competitor.attempt_count} attempts. {transcript}"
                    )
                },
            }
        )

    return children


def append_result_to_notion(*, config: NotionConfig, result: GameResult) -> None:
    payload = {"children": result_blocks(result)}
    request = urllib.request.Request(
        f"https://api.notion.com/v1/blocks/{config.page_id}/children",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2026-03-11",
        },
        method="PATCH",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status >= 300:
            raise RuntimeError(f"Notion returned HTTP {response.status}")

