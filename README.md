# wharness

A very simple toy LLM harness: a chat loop against OpenRouter.

## Run

```sh
uv run -m src.main
```

Requires `OPENROUTER_API_KEY` in `.env` (or your environment). The system prompt lives in `system_prompt.md`.

Both follow the same folder convention: a directory with a module exporting `run()`, auto-discovered at startup (`<name>/skill.py` or `<name>/tool.py`). Each module's LLM-facing text lives with the folder: a skill's prompt is its `SKILL.md` (injected on `/name`); a tool's description is its `tool.py` module docstring, its parameters taken from `run()`'s signature — the tool list in `system_prompt.md` is generated from these at startup (replacing the `{{TOOLS}}` placeholder).
