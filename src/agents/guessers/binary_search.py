from __future__ import annotations

from dataclasses import dataclass

from src.agents.base import Feedback
from src.agents.guessers.base import GuesserAgent


@dataclass
class BinarySearchGuesser(GuesserAgent):
    agent_id: str = "binary_search"
    display_name: str = "Binary Search"
    personality: str = "binary_search"

    def reset(self, minimum: int, maximum: int) -> None:
        self.low = minimum
        self.high = maximum

    def next_guess(self) -> int:
        return (self.low + self.high) // 2

    def observe_feedback(self, guess: int, feedback: Feedback) -> None:
        if feedback == "too_low":
            self.low = guess + 1
        elif feedback == "too_high":
            self.high = guess - 1

