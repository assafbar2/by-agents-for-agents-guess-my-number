# By Agents, For Agents: Guess My Number

An offline daily agent competition.

One setter agent chooses a secret number. Two isolated guesser agents try to solve the same number without knowing the other agent exists:

- `BinarySearchGuesser`
- `FeedbackRandomGuesser`, which guesses randomly but narrows its range from setter feedback

The project exists to test GPT-5.5-assisted development, play with small agent interfaces, exercise GitHub Actions scheduling/manual runs, and practice wiring generated work into internal workspaces such as email, Notion, and a published dashboard.

It is intentionally small. The point is not the game itself; the point is the workflow around it.

## Why This Exists

This is a compact test bed for:

- agent role boundaries
- strategy/personality modules
- daily batch execution
- GitHub Actions as a scheduler
- GitHub Pages as a persistent public output
- AgentMail email delivery
- Notion append integration, currently optional and dummy-key friendly
- clear generated artifacts that can be inspected after each run

There is a lot of prep required to "one shot" things well. That has also been the basic promise of Computer Science from day one: spend more time shaping the abstraction, interface, and repeatable process so the actual execution becomes boring.

## Project Layout

```text
src/
  agents/
    setter.py
    base.py
    guessers/
      base.py
      binary_search.py
      feedback_random.py
  outputs/
    agentmail.py
    notion.py
  game.py
  report.py
  run_daily.py
  site.py

data/runs/
  daily JSON and Markdown run records

site/
  static GitHub Pages dashboard
```

## Local Run

```bash
python3 -m src.run_daily --skip-email --skip-notion
```

With a custom range:

```bash
python3 -m src.run_daily --min-number 1 --max-number 1000 --skip-email --skip-notion
```

With a deterministic seed:

```bash
python3 -m src.run_daily --seed 20260425 --skip-email --skip-notion
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## GitHub Actions

The workflow is in:

```text
.github/workflows/daily-game.yml
```

It is configured to run:

- daily at `10:00 AM America/Los_Angeles`
- manually through the GitHub Actions UI via `workflow_dispatch`

GitHub cron runs in UTC, so the workflow is scheduled at both UTC hours that map to 10 AM Pacific across daylight saving changes. A small gate step checks the current `America/Los_Angeles` hour and only runs the game when it is actually 10 AM.

Manual inputs:

- `min_number`
- `max_number`
- `skip_email`
- `skip_notion`

The workflow:

1. checks out the repo
2. sets up Python
3. runs tests
4. runs the competition
5. writes JSON and Markdown results under `data/runs/`
6. updates the static dashboard under `site/`
7. sends email via AgentMail if secrets are present
8. appends to Notion if real Notion secrets are present
9. commits generated result files back to the repo
10. deploys `site/` to GitHub Pages

## GitHub Pages Setup

After pushing the repo to GitHub:

1. Open the repository on GitHub.
2. Go to `Settings` -> `Pages`.
3. Set `Build and deployment` source to `GitHub Actions`.
4. Run `Daily Guess My Number` manually once from the `Actions` tab.

The deployed site will show the latest game and a history table from `site/results.json`.

## Secrets

Required for AgentMail email:

```text
AGENTMAIL_API_KEY
AGENTMAIL_INBOX_ID
REPORT_RECIPIENT_EMAIL
```

Optional for Notion:

```text
NOTION_API_KEY
NOTION_PAGE_ID
```

Notion is deliberately optional for now. If these values are missing, the workflow uses dummy values and the run skips Notion instead of failing.

## AgentMail

The email adapter calls:

```text
POST https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/send
```

It sends both plain text Markdown and HTML versions of the game report.

## Adding More Guessers

Add a new strategy module:

```text
src/agents/guessers/my_new_strategy.py
```

Implement the `GuesserAgent` interface:

```python
class MyNewGuesser(GuesserAgent):
    def reset(self, minimum: int, maximum: int) -> None:
        ...

    def next_guess(self) -> int:
        ...

    def observe_feedback(self, guess: int, feedback: Feedback) -> None:
        ...
```

Then register it in `src/run_daily.py`.
