from __future__ import annotations

from abc import ABC, abstractmethod

from src.agents.base import Feedback


class GuesserAgent(ABC):
    agent_id: str
    display_name: str
    personality: str

    @abstractmethod
    def reset(self, minimum: int, maximum: int) -> None:
        """Prepare the agent for a new isolated game."""

    @abstractmethod
    def next_guess(self) -> int:
        """Return the next guess using only this agent's private state."""

    @abstractmethod
    def observe_feedback(self, guess: int, feedback: Feedback) -> None:
        """Update private state after setter feedback."""

