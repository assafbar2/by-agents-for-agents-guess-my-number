from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class SetterAgent:
    personality: str = "random"

    def choose_number(self, minimum: int, maximum: int, rng: random.Random) -> int:
        if minimum > maximum:
            raise ValueError("minimum cannot be greater than maximum")

        if self.personality != "random":
            raise ValueError(f"Unsupported setter personality: {self.personality}")

        return rng.randint(minimum, maximum)

