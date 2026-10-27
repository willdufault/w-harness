"""Summarize the conversation so far in a compact handoff: goal, decisions, key facts, files changed, next steps. Output only the summary."""


def run(messages: list, reply: str) -> list:
    system_prompt = messages[0]
    return [
        system_prompt,
        {"role": "user", "content": f"Summary of the previous session:\n{reply}"},
    ]
