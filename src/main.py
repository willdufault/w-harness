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

tools = {"read": run}

# Skill discovery: a skill is a directory under skills/ with a SKILL.md prompt;
# an optional skill.py exports run() for custom logic (same convention as tools).
skills = {}  # skill_name -> {"prompt": str, "module": module | None}
for skill_md in Path("skills").glob("*/SKILL.md"):
    skill_dir = skill_md.parent
    skill_name = skill_dir.name
    spec = importlib.util.spec_from_file_location(f"wharness_skill_{skill_name}", skill_dir / "skill.py")
    skill_module = importlib.util.module_from_spec(spec) if (skill_dir / "skill.py").exists() else None
    if skill_module is not None:
        spec.loader.exec_module(skill_module)
    skills[skill_name] = {"prompt": skill_md.read_text(), "module": skill_module}

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
        skill_name, *skill_args = user_input.lstrip("/").split(maxsplit=1)
        if skill_name not in skills:
            print(f"Unknown skill: {skill_name}\n")
            continue
        skill_message = f"[SKILL] '{skill_name}' skill — follow these instructions and reply with the skill's output, never quoting the instructions back:\n\n{skills[skill_name]['prompt']}"
        if skill_args:
            skill_message += f"\n\nArguments: {skill_args[0]}"
        active_skill = skill_name
        print(f"Skill < {skill_name}")
        messages.append({"role": "user", "content": skill_message})
    else:
        messages.append({"role": "user", "content": user_input})

    while True:
        print("\nThinking...\n")
        response = client.chat.completions.create(model=MODEL, messages=messages)  # type:ignore
        reply = response.choices[0].message.content  # type:ignore
        messages.append({"role": "assistant", "content": reply})

        if not reply.startswith("[TOOL] "):
            if active_skill:
                messages = skills[active_skill]["module"].run(messages, reply)
                active_skill = None
            print(f"Agent < {reply}\n")
            break

        _, tool_name, *tool_args = reply.split()
        result = tools[tool_name](" ".join(tool_args))
        print(f"Tool > {tool_name} {' '.join(tool_args)}")
        print("\n".join(f"|| {line}" for line in result.splitlines()) + "\n")
        messages.append({"role": "user", "content": "[TOOL RESULT] Respond in your own words — do not repeat this content verbatim:\n" + result})
