from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from src.agents.base import AgentResult, Feedback, GuessAttempt
from src.agents.guessers.base import GuesserAgent
from src.agents.setter import SetterAgent


@dataclass(frozen=True)
class GameConfig:
    minimum: int = 1
    maximum: int = 100
    max_attempts: int | None = None

    def resolved_max_attempts(self) -> int:
        return self.max_attempts or (self.maximum - self.minimum + 1)


@dataclass(frozen=True)
class GameResult:
    run_id: str
    played_at: str
    config: GameConfig
    setter_personality: str
    secret_number: int
    competitors: list[AgentResult]
    winner_agent_id: str | None
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def feedback_for(secret_number: int, guess: int) -> Feedback:
    if guess < secret_number:
        return "too_low"
    if guess > secret_number:
        return "too_high"
    return "correct"


def play_session(
    *,
    secret_number: int,
    config: GameConfig,
    guesser: GuesserAgent,
) -> AgentResult:
    guesser.reset(config.minimum, config.maximum)
    attempts: list[GuessAttempt] = []

    for turn in range(1, config.resolved_max_attempts() + 1):
        guess = guesser.next_guess()
        feedback = feedback_for(secret_number, guess)
        guesser.observe_feedback(guess, feedback)
        attempts.append(GuessAttempt(turn=turn, guess=guess, feedback=feedback))

        if feedback == "correct":
            break

    return AgentResult(
        agent_id=guesser.agent_id,
        display_name=guesser.display_name,
        personality=guesser.personality,
        attempts=attempts,
    )


def choose_winner(results: list[AgentResult]) -> str | None:
    solved = [result for result in results if result.solved]
    if not solved:
        return None

    solved.sort(key=lambda result: result.attempt_count)
    if len(solved) > 1 and solved[0].attempt_count == solved[1].attempt_count:
        return None

    return solved[0].agent_id


def summarize_winner(results: list[AgentResult], winner_agent_id: str | None) -> str:
    if winner_agent_id is None:
        solved_counts = {result.attempt_count for result in results if result.solved}
        if len(solved_counts) == 1:
            attempt_count = solved_counts.pop()
            return f"Tie: both agents solved it in {attempt_count} attempts."
        return "No winner: no agent solved the game."

    winner = next(result for result in results if result.agent_id == winner_agent_id)
    loser = next((result for result in results if result.agent_id != winner_agent_id), None)
    if loser is None or not loser.solved:
        return f"{winner.display_name} won; the other agent did not solve the game."

    margin = loser.attempt_count - winner.attempt_count
    return f"{winner.display_name} won by {margin} attempt{'s' if margin != 1 else ''}."


def run_competition(
    *,
    config: GameConfig,
    setter: SetterAgent,
    guessers: list[GuesserAgent],
    rng: random.Random,
    played_at: datetime,
) -> GameResult:
    secret_number = setter.choose_number(config.minimum, config.maximum, rng)
    competitors = [
        play_session(secret_number=secret_number, config=config, guesser=guesser)
        for guesser in guessers
    ]
    winner_agent_id = choose_winner(competitors)

    return GameResult(
        run_id=played_at.strftime("%Y-%m-%d"),
        played_at=played_at.isoformat(),
        config=config,
        setter_personality=setter.personality,
        secret_number=secret_number,
        competitors=competitors,
        winner_agent_id=winner_agent_id,
        summary=summarize_winner(competitors, winner_agent_id),
    )

