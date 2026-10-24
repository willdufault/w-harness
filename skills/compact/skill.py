def run(messages, reply):
    """Called on the final reply while this skill is active; returns the new message list.

    Starts a new session: original system prompt plus a summary of the conversation.
    """
    system_prompt = messages[0]
    return [system_prompt, {"role": "user", "content": f"Summary of the previous session:\n{reply}"}]
