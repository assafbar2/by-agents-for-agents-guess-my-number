from __future__ import annotations

import html
from pathlib import Path

from src.game import GameResult


def feedback_label(feedback: str) -> str:
    return feedback.replace("_", " ")


def render_markdown(result: GameResult) -> str:
    lines = [
        "# Guess My Number - Daily Competition",
        "",
        f"- Date: {result.run_id}",
        f"- Played at: {result.played_at}",
        f"- Range: {result.config.minimum}-{result.config.maximum}",
        f"- Setter personality: {result.setter_personality}",
        f"- Secret number: {result.secret_number}",
        f"- Result: {result.summary}",
        "",
    ]

    for competitor in result.competitors:
        lines.extend(
            [
                f"## {competitor.display_name}",
                "",
                f"- Personality: `{competitor.personality}`",
                f"- Attempts: {competitor.attempt_count}",
                f"- Solved: {'yes' if competitor.solved else 'no'}",
                "",
                "| Turn | Guess | Feedback |",
                "| ---: | ---: | --- |",
            ]
        )
        for attempt in competitor.attempts:
            lines.append(f"| {attempt.turn} | {attempt.guess} | {feedback_label(attempt.feedback)} |")
        lines.append("")

    return "\n".join(lines)


def render_email_html(result: GameResult) -> str:
    sections = []
    for competitor in result.competitors:
        rows = "\n".join(
            "<tr>"
            f"<td>{attempt.turn}</td>"
            f"<td>{attempt.guess}</td>"
            f"<td>{html.escape(feedback_label(attempt.feedback))}</td>"
            "</tr>"
            for attempt in competitor.attempts
        )
        sections.append(
            f"""
            <h2>{html.escape(competitor.display_name)}</h2>
            <p><strong>Personality:</strong> {html.escape(competitor.personality)}<br>
            <strong>Attempts:</strong> {competitor.attempt_count}<br>
            <strong>Solved:</strong> {"yes" if competitor.solved else "no"}</p>
            <table border="1" cellpadding="6" cellspacing="0">
              <thead><tr><th>Turn</th><th>Guess</th><th>Feedback</th></tr></thead>
              <tbody>{rows}</tbody>
            </table>
            """
        )

    return f"""
    <html>
      <body>
        <h1>Guess My Number - Daily Competition</h1>
        <p>
          <strong>Date:</strong> {html.escape(result.run_id)}<br>
          <strong>Range:</strong> {result.config.minimum}-{result.config.maximum}<br>
          <strong>Secret number:</strong> {result.secret_number}<br>
          <strong>Result:</strong> {html.escape(result.summary)}
        </p>
        {''.join(sections)}
      </body>
    </html>
    """


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

