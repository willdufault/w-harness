"""Summarize the conversation so far in a compact handoff: goal, decisions, key facts, files changed, next steps. Output only the summary."""


def run(messages: list, reply: str) -> list:
    """Called on the final reply while this command is active; returns the new message list.

    Starts a new session: original system prompt plus a summary of the conversation.
    """
    system_prompt = messages[0]
    return [
        system_prompt,
        {"role": "user", "content": f"Summary of the previous session:\n{reply}"},
    ]
