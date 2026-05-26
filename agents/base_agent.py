"""
Base agent — wraps the Anthropic client with an agentic tool-use loop.
All specialty agents inherit from this.
"""
import anthropic
from config import ANTHROPIC_MODEL, MAX_TOKENS, ANTHROPIC_API_KEY


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
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def run(self, query: str, history: list[dict]) -> str:
        """
        Agentic loop: send query → handle tool calls → return final text response.
        history is a list of prior {"role": ..., "content": ...} messages.
        """
        messages = history + [{"role": "user", "content": query}]

        while True:
            response = self._client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tool_defs,
                messages=messages,
            )

            # Collect any text blocks for the final answer
            text_parts = [b.text for b in response.content if b.type == "text"]

            if response.stop_reason == "tool_use":
                # Execute every tool Claude requested
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        executor = self.tool_executors.get(block.name)
                        result = executor(block.input) if executor else '{"error": "unknown tool"}'
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                # Append assistant turn + tool results, then loop
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # stop_reason == "end_turn" — we have the final answer
                return "\n".join(text_parts) if text_parts else "I was unable to retrieve the requested information."
