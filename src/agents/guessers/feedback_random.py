from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.agents.base import Feedback
from src.agents.guessers.base import GuesserAgent


@dataclass
class FeedbackRandomGuesser(GuesserAgent):
    rng: random.Random
    agent_id: str = "feedback_random"
    display_name: str = "Feedback-Constrained Random"
    personality: str = "random_but_follows_feedback"
    guessed: set[int] = field(default_factory=set)

    def reset(self, minimum: int, maximum: int) -> None:
        self.low = minimum
        self.high = maximum
        self.guessed.clear()

    def next_guess(self) -> int:
        candidates = [number for number in range(self.low, self.high + 1) if number not in self.guessed]
        if not candidates:
            raise RuntimeError("No valid guesses remain")
        guess = self.rng.choice(candidates)
        self.guessed.add(guess)
        return guess

    def observe_feedback(self, guess: int, feedback: Feedback) -> None:
        if feedback == "too_low":
            self.low = guess + 1
        elif feedback == "too_high":
            self.high = guess - 1

