import importlib.util
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

# Skill discovery: a skill is a directory under skills/ with a SKILL.md prompt;
# an optional skill.py exports run() for custom logic (same convention as tools).
skills = {}  # name -> {"prompt": str, "mod": module | None}
for md in Path("skills").glob("*/SKILL.md"):
    name, folder = md.parent.name, md.parent
    spec = importlib.util.spec_from_file_location(f"wh_skill_{name}", folder / "skill.py")
    mod = importlib.util.module_from_spec(spec) if (folder / "skill.py").exists() else None
    if mod is not None:
        spec.loader.exec_module(mod)
    skills[name] = {"prompt": md.read_text(), "mod": mod}

active_skill = None
messages = [{"role": "system", "content": system_prompt}]

while True:
    try:
        user_input = input("User > ")
    except (EOFError, KeyboardInterrupt):
        break
    if user_input.strip() == "exit":
        break

    if user_input.startswith("/"):
        name, *rest = user_input.lstrip("/").split(maxsplit=1)
        if name not in skills:
            print(f"Unknown skill: {name}\n")
            continue
        text = f"[SKILL] '{name}' skill — follow these instructions and reply with the skill's output, never quoting the instructions back:\n\n{skills[name]['prompt']}"
        if rest:
            text += f"\n\nArguments: {rest[0]}"
        active_skill = name
        messages.append({"role": "user", "content": text})
        print(f"Skill < {name}")
    else:
        messages.append({"role": "user", "content": user_input})

    while True:
        print("\nThinking...\n")
        response = client.chat.completions.create(model=MODEL, messages=messages)  # type:ignore
        reply = response.choices[0].message.content  # type:ignore
        messages.append({"role": "assistant", "content": reply})

        if not reply.startswith("[TOOL] "):
            skill = skills[active_skill]["mod"] if active_skill else None
            if skill:
                messages = skill.run(messages, reply)
                active_skill = None
            print(f"Agent < {reply}\n")
            break

        _, name, *args = reply.split()
        result = tool_impls[name](" ".join(args))
        print(f"Tool > {name} {' '.join(args)}")
        print("\n".join(f"|| {line}" for line in result.splitlines()) + "\n")
        messages.append({"role": "user", "content": "[TOOL RESULT] Respond in your own words — do not repeat this content verbatim:\n" + result})
