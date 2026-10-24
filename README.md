# wharness

A very simple toy LLM harness: a chat loop against OpenRouter.

## Run

```sh
uv run -m src.main
```

Requires `OPENROUTER_API_KEY` in `.env` (or your environment). The system prompt lives in `system_prompt.md`.

Skills are directories under `skills/` (e.g. `/compact` → `skills/compact/`): each has a `SKILL.md` prompt that is injected when you type `/name`, plus an optional `skill.py` exporting `run()` for custom logic, matching the tool module convention.
