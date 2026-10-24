# wharness

A very simple toy LLM harness: a chat loop against OpenRouter.

## Run

```sh
uv run -m src.main
```

Requires `OPENROUTER_API_KEY` in `.env` (or your environment). The system prompt lives in `system_prompt.md`.

Skills are directories under `skills/` (e.g. `/compact` → `skills/compact/`): each has a `SKILL.md` prompt that is injected when you type `/name`, plus an optional `skill.py` exporting `run()` for custom logic. Tools follow the same convention: directories under `tools/` (e.g. `tools/read/`) with a `tool.py` exporting `run()`. In both cases the module exporting `run()` is auto-discovered at startup.
