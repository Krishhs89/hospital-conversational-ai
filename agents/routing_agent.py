"""
Routing Agent — the top-level orchestrator (Jarvis).
Classifies the user's intent and delegates to the right specialty agent.
Applies guardrails to keep queries on-topic.
"""
import json
import anthropic
from config import ANTHROPIC_MODEL, MAX_TOKENS, ANTHROPIC_API_KEY, AGENT_DESCRIPTIONS

# Guardrail: domains this system handles
ALLOWED_DOMAINS = set(AGENT_DESCRIPTIONS.keys())

ROUTING_TOOL = {
    "name": "route_to_agent",
    "description": (
        "Classify the user's hospital operations question and identify which specialist "
        "agent should handle it. Return the agent key and a cleaned-up version of the query."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "enum": list(ALLOWED_DOMAINS),
                "description": "The specialist agent best suited to answer the question.",
            },
            "refined_query": {
                "type": "string",
                "description": "The user's question, cleaned up and ready for the specialist agent.",
            },
            "off_topic": {
                "type": "boolean",
                "description": "True if the question is unrelated to hospital operations.",
            },
            "off_topic_reason": {
                "type": "string",
                "description": "Brief explanation if off_topic is true.",
            },
        },
        "required": ["agent", "refined_query", "off_topic"],
    },
}

ROUTING_SYSTEM = """You are the Hospital Conversational AI routing agent — think of yourself as Jarvis
for hospital operations. Your job is to:

1. Determine whether the question relates to hospital operations (hospital flow/capacity,
   surgical operations, patient experience, imaging, or executive briefings).
2. If it does, call route_to_agent with the correct agent key and a refined version of the query.
3. If it is completely unrelated to hospital operations, set off_topic=true.

Available specialist agents:
- hospital_flow : bed census, admissions, discharges, boarding, ED wait times
- surgical_ops  : OR utilization, scheduling, delays, first-case on-time, cancellations
- patient_exp   : HCAHPS satisfaction scores, feedback trends, improvement recommendations
- imaging       : imaging volume, turnaround times, equipment status, Imaging dept satisfaction
- executive     : cross-domain morning briefing, predictive alerts, KPI digest

Always call route_to_agent — do not answer the question yourself."""


class RoutingAgent:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def route(self, query: str) -> dict:
        """
        Returns:
          {"agent": str, "refined_query": str, "off_topic": bool, "off_topic_reason": str}
        """
        response = self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=512,
            system=ROUTING_SYSTEM,
            tools=[ROUTING_TOOL],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": query}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "route_to_agent":
                return block.input

        # Fallback — couldn't route
        return {
            "agent": "executive",
            "refined_query": query,
            "off_topic": False,
            "off_topic_reason": "",
        }

    def get_off_topic_message(self, reason: str) -> str:
        return (
            f"I'm your Hospital Operations AI and can only assist with hospital-related topics "
            f"such as bed capacity, surgical operations, patient experience, or imaging. "
            f"Your question appears to be outside that scope ({reason}). "
            f"Please ask about a hospital operations topic and I'll be happy to help!"
        )
