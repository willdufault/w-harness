import importlib.util
import inspect
import os
import time
from pathlib import Path
from types import ModuleType

import openai
from dotenv import load_dotenv
from openai import OpenAI

MODEL = "nvidia/nemotron-3.5-lightning:free"
BASE_URL = "https://openrouter.ai/api/v1"
MAX_INVOKE_ATTEMPTS = 3
INVOKE_RETRY_DELAY_SECONDS = 10


def load_module(path: Path, name: str) -> ModuleType:
    """Import a Python file as a module (importlib, no package machinery needed)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tools() -> dict:
    """Discover *.py files under tools/; description = module docstring."""
    tools = {}
    for tool_file in Path("tools").glob("*.py"):
        tool_name = tool_file.stem
        tools[tool_name] = load_module(tool_file, f"wharness_tool_{tool_name}")
    return tools


def load_commands() -> dict:
    """Discover *.py files under commands/; prompt = module docstring."""
    commands = {}
    for command_file in Path("commands").glob("*.py"):
        command_name = command_file.stem
        commands[command_name] = {"module": load_module(command_file, f"wharness_command_{command_name}")}
    return commands


def render_system_prompt(tools: dict) -> str:
    """Read system_prompt.md and replace {{TOOLS}} with one line per tool:
    description = module docstring, params = run() signature."""
    tool_list = []
    for tool_name, tool_module in sorted(tools.items()):
        params = ", ".join(
            param.name
            for param in inspect.signature(tool_module.run).parameters.values()
        )
        tool_list.append(
            f"- {tool_name}({params}): {inspect.getdoc(tool_module).splitlines()[0]}"
        )
    return (
        Path("system_prompt.md").read_text().replace("{{TOOLS}}", "\n".join(tool_list))
    )


def main():
    """Run one chat session: set up client, discover tools/commands, chat."""
    load_dotenv()
    client = OpenAI(base_url=BASE_URL, api_key=os.environ["OPENROUTER_API_KEY"])

    tools = load_tools()
    commands = load_commands()
    system_prompt = render_system_prompt(tools)

    active_command = None
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("User > ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.strip() == "exit":
            break

        if user_input.startswith("/"):
            command_name, *command_args = user_input.lstrip("/").split(maxsplit=1)
            if command_name not in commands:
                print(f"Unknown command: {command_name}\n")
                continue
            command_message = f"[COMMAND] '{command_name}' command — follow these instructions and reply with the command's output, never quoting the instructions back:\n\n{inspect.getdoc(commands[command_name]['module'])}"
            if command_args:
                command_message += f"\n\nArguments: {command_args[0]}"
            active_command = command_name
            print(f"Command < {command_name}")
            messages.append({"role": "user", "content": command_message})
        else:
            messages.append({"role": "user", "content": user_input})

        while True:
            print("\nThinking...\n")
            for attempt_number in range(1, MAX_INVOKE_ATTEMPTS + 1):
                try:
                    response = client.responses.create(model=MODEL, input=messages)
                    break
                except (openai.RateLimitError, openai.APIConnectionError) as invoke_error:
                    if attempt_number == MAX_INVOKE_ATTEMPTS:
                        raise
                    print(f"Model invoke failed ({type(invoke_error).__name__}), retrying in {INVOKE_RETRY_DELAY_SECONDS}s (attempt {attempt_number}/{MAX_INVOKE_ATTEMPTS})...")
                    time.sleep(INVOKE_RETRY_DELAY_SECONDS)
            reply = response.output_text
            messages.append({"role": "assistant", "content": reply})

            if not reply.startswith("[TOOL] "):
                if active_command:
                    messages = commands[active_command]["module"].run(messages, reply)
                    active_command = None
                print(f"Agent < {reply}\n")
                break

            _, tool_name, *tool_args = reply.split()
            result = tools[tool_name].run(" ".join(tool_args))
            print(f"Tool > {tool_name} {' '.join(tool_args)}")
            print("\n".join(f"| {line}" for line in result.splitlines()))
            messages.append(
                {
                    "role": "user",
                    "content": "[TOOL RESULT] Use this to answer in your own words — don't repeat it verbatim. All results you need are here; don't call this tool again with the same arguments. Answer now:\n"
                    + result,
                }
            )


if __name__ == "__main__":
    main()
