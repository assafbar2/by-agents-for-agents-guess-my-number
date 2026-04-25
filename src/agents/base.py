from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Feedback = Literal["too_low", "too_high", "correct"]


@dataclass(frozen=True)
class GuessAttempt:
    turn: int
    guess: int
    feedback: Feedback


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    display_name: str
    personality: str
    attempts: list[GuessAttempt]

    @property
    def solved(self) -> bool:
        return bool(self.attempts) and self.attempts[-1].feedback == "correct"

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

