import sys

import ollama

from qwen_agent.code_executor import run_code

MODEL = "qwen3.5:9b"

MAX_OUTPUT_CHARS = 4000

SYSTEM_PROMPT = (
    "You solve tasks by writing Python code and calling the run_code tool. "
    "Code executes in a persistent namespace: variables you set in one call "
    "are still available in later calls. You have no other way to see "
    "results or communicate progress - print anything you need to see. "
    "When you have the final answer, stop calling run_code and reply with "
    "the answer in plain text."
)


def _describe(name: str, text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return f"{name}:\n{text}"
    return (
        f"{name} was {len(text)} characters, too long to show here - "
        f"it was loaded into the `{name}` variable in your context instead."
    )


RUN_CODE_TOOL = {
    "type": "function",
    "function": {
        "name": "run_code",
        "description": (
            "Execute Python code in a persistent namespace shared across "
            "calls. Returns whatever the code printed to stdout and stderr."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source code to execute.",
                }
            },
            "required": ["code"],
        },
    },
}


def run_agent(task: str, model: str = MODEL) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    while True:
        content = ""
        tool_calls = []
        for chunk in ollama.chat(model=model, messages=messages, tools=[RUN_CODE_TOOL], stream=True):
            piece = chunk.message.content
            if piece:
                content += piece
                print(piece, end="", flush=True)
            if chunk.message.tool_calls:
                tool_calls.extend(chunk.message.tool_calls)

        if not tool_calls:
            print()
            return content

        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {"function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in tool_calls
                ],
            }
        )

        for tc in tool_calls:
            code = tc.function.arguments.get("code", "")
            stdout, stderr = run_code(code)
            print(f"\n--- run_code ---\n{code}\n--- stdout ---\n{stdout}--- stderr ---\n{stderr}")
            tool_content = f"{_describe('_stdout', stdout)}\n{_describe('_stderr', stderr)}"
            messages.append(
                {
                    "role": "tool",
                    "tool_name": tc.function.name,
                    "content": tool_content,
                }
            )


def main() -> None:
    task = " ".join(sys.argv[1:]) or input("Task: ")
    run_agent(task)


if __name__ == "__main__":
    main()
