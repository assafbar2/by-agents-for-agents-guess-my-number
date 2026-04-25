from __future__ import annotations

import random
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from src.agents.guessers import BinarySearchGuesser, FeedbackRandomGuesser
from src.agents.setter import SetterAgent
from src.game import GameConfig, feedback_for, run_competition


class GameTests(unittest.TestCase):
    def test_feedback_for_secret_number(self) -> None:
        self.assertEqual(feedback_for(42, 12), "too_low")
        self.assertEqual(feedback_for(42, 88), "too_high")
        self.assertEqual(feedback_for(42, 42), "correct")

    def test_competition_uses_same_secret_for_isolated_guessers(self) -> None:
        result = run_competition(
            config=GameConfig(minimum=1, maximum=100),
            setter=SetterAgent(),
            guessers=[
                BinarySearchGuesser(),
                FeedbackRandomGuesser(rng=random.Random(10)),
            ],
            rng=random.Random(20260425),
            played_at=datetime(2026, 4, 25, 10, tzinfo=ZoneInfo("America/Los_Angeles")),
        )

        self.assertGreaterEqual(result.secret_number, 1)
        self.assertLessEqual(result.secret_number, 100)
        self.assertEqual(len(result.competitors), 2)
        self.assertEqual(
            {agent.agent_id for agent in result.competitors},
            {"binary_search", "feedback_random"},
        )
        self.assertTrue(all(agent.solved for agent in result.competitors))

    def test_binary_search_solves_one_to_one_hundred_in_at_most_seven_attempts(self) -> None:
        result = run_competition(
            config=GameConfig(minimum=1, maximum=100),
            setter=SetterAgent(),
            guessers=[BinarySearchGuesser()],
            rng=random.Random(1),
            played_at=datetime(2026, 4, 25, 10, tzinfo=ZoneInfo("America/Los_Angeles")),
        )

        self.assertLessEqual(result.competitors[0].attempt_count, 7)


if __name__ == "__main__":
    unittest.main()
