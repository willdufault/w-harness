import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "nvidia/nemotron-3.5-lightning:free"
BASE_URL = "https://openrouter.ai/api/v1"

load_dotenv()
client = OpenAI(base_url=BASE_URL, api_key=os.environ["OPENROUTER_API_KEY"])
system_prompt = Path("system_prompt.md").read_text()

messages = [{"role": "system", "content": system_prompt}]

while True:
    try:
        user_input = input("User > ")
    except (EOFError, KeyboardInterrupt):
        break
    if user_input.strip() == "exit":
        break

    messages.append({"role": "user", "content": user_input})
    print("\nThinking...\n")
    response = client.chat.completions.create(model=MODEL, messages=messages)  # type:ignore
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})  # type:ignore
    print(f"Agent < {reply}\n")
