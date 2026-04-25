from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.agents.guessers import BinarySearchGuesser, FeedbackRandomGuesser
from src.agents.setter import SetterAgent
from src.game import GameConfig, run_competition
from src.outputs.agentmail import AgentMailConfig, send_report_email
from src.outputs.notion import NotionConfig, append_result_to_notion
from src.report import render_email_html, render_markdown, write_text
from src.site import update_results_json, write_dashboard


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily Guess My Number competition.")
    parser.add_argument("--min-number", type=int, default=1)
    parser.add_argument("--max-number", type=int, default=100)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--date", default=None, help="Run date in YYYY-MM-DD format.")
    parser.add_argument("--skip-email", action="store_true")
    parser.add_argument("--skip-notion", action="store_true")
    return parser.parse_args()


def played_at_from_args(date_value: str | None) -> datetime:
    tz = ZoneInfo("America/Los_Angeles")
    if not date_value:
        return datetime.now(tz)
    return datetime.fromisoformat(f"{date_value}T10:00:00").replace(tzinfo=tz)


def main() -> None:
    args = parse_args()
    played_at = played_at_from_args(args.date)
    seed = args.seed if args.seed is not None else int(played_at.strftime("%Y%m%d"))
    rng = random.Random(seed)

    config = GameConfig(minimum=args.min_number, maximum=args.max_number)
    feedback_random_rng = random.Random(rng.randint(1, 1_000_000_000))
    result = run_competition(
        config=config,
        setter=SetterAgent(personality="random"),
        guessers=[
            BinarySearchGuesser(),
            FeedbackRandomGuesser(rng=feedback_random_rng),
        ],
        rng=rng,
        played_at=played_at,
    )

    root = Path.cwd()
    json_path = root / "data" / "runs" / f"{result.run_id}.json"
    markdown_path = root / "data" / "runs" / f"{result.run_id}.md"
    markdown = render_markdown(result)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    write_text(markdown_path, markdown)
    update_results_json(root / "site", result)
    write_dashboard(root / "site")

    print(markdown)

    if not args.skip_email:
        agentmail_config = AgentMailConfig.from_env()
        if agentmail_config:
            send_report_email(
                config=agentmail_config,
                subject=f"Guess My Number - {result.run_id}",
                text=markdown,
                html=render_email_html(result),
            )
            print("AgentMail: sent")
        else:
            print("AgentMail: skipped; missing AGENTMAIL_API_KEY, AGENTMAIL_INBOX_ID, or REPORT_RECIPIENT_EMAIL")

    if not args.skip_notion:
        notion_config = NotionConfig.from_env()
        if notion_config:
            append_result_to_notion(config=notion_config, result=result)
            print("Notion: appended")
        else:
            print("Notion: skipped; using dummy or missing NOTION_API_KEY/NOTION_PAGE_ID")


if __name__ == "__main__":
    main()

