"""
Base agent — wraps the Anthropic client with an agentic tool-use loop.
All specialty agents inherit from this.
"""
import json
import anthropic
from config import ANTHROPIC_MODEL, MAX_TOKENS, get_api_key


class BaseAgent:
    def __init__(
        self,
        name: str,
        system_prompt: str,
        tool_defs: list[dict],
        tool_executors: dict,
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.tool_defs = tool_defs
        self.tool_executors = tool_executors
        self._client = anthropic.Anthropic(api_key=get_api_key())

    def run(self, query: str, history: list[dict]) -> str:
        """
        Agentic tool-use loop.
        First call uses tool_choice="any" to force at least one data retrieval
        before Claude composes its answer. Subsequent calls (after tool results
        are in context) use the default "auto".
        """
        messages = history + [{"role": "user", "content": query}]
        first_call = True

        while True:
            call_kwargs: dict = dict(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tool_defs,
                messages=messages,
            )
            # Force at least one tool call on the very first turn so Claude
            # always grounds its answer in real (synthetic) data.
            if first_call and self.tool_defs:
                call_kwargs["tool_choice"] = {"type": "any"}
                first_call = False

            response = self._client.messages.create(**call_kwargs)

            text_parts = [b.text for b in response.content if b.type == "text"]

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        executor = self.tool_executors.get(block.name)
                        try:
                            result = executor(block.input) if executor else json.dumps({"error": "unknown tool"})
                        except Exception as exc:
                            result = json.dumps({"error": f"tool execution failed: {exc}"})
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                return "\n".join(text_parts) if text_parts else "I was unable to retrieve the requested information."
