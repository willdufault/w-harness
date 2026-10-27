# wharness

A very simple toy LLM harness: a chat loop against OpenRouter.

## Run

```sh
uv run -m src.main
```

Requires `OPENROUTER_API_KEY` in `.env` (or your environment). The system prompt lives in `system_prompt.md`.

Two extension types share the same convention: a module exporting `run()`, auto-discovered at startup. Tools live in `tools/<name>.py`; their description is the module docstring, their parameters taken from `run()`'s signature — the tool list in `system_prompt.md` is generated from these at startup (replacing the `{{TOOLS}}` placeholder). Commands live in `commands/<name>.py`; their instructions are the module docstring, injected into the chat when the user types `/name`.
