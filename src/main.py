import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from tools.read import run

MODEL = "nvidia/nemotron-3.5-lightning:free"
BASE_URL = "https://openrouter.ai/api/v1"

load_dotenv()
client = OpenAI(base_url=BASE_URL, api_key=os.environ["OPENROUTER_API_KEY"])
system_prompt = Path("system_prompt.md").read_text()

tool_impls = {"read": run}

messages = [{"role": "system", "content": system_prompt}]

while True:
    try:
        user_input = input("User > ")
    except (EOFError, KeyboardInterrupt):
        break
    if user_input.strip() == "exit":
        break

    messages.append({"role": "user", "content": user_input})
    while True:
        print("\nThinking...\n")
        response = client.chat.completions.create(model=MODEL, messages=messages)  # type:ignore
        reply = response.choices[0].message.content  # type:ignore
        messages.append({"role": "assistant", "content": reply})

        if not reply.startswith("[TOOL] "):
            print(f"Agent < {reply}\n")
            break

        _, name, *args = reply.split()
        result = tool_impls[name](" ".join(args))
        print(f"Tool > {name} {' '.join(args)}")
        print("\n".join(f"|| {line}" for line in result.splitlines()) + "\n")
        messages.append({"role": "user", "content": "[TOOL RESULT] Respond in your own words — do not repeat this content verbatim:\n" + result})
