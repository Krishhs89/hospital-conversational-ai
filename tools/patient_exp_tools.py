"""
Tool definitions + executors for the Patient Experience Agent.
"""
import json
from data.synthetic_data import (
    get_satisfaction_scores,
    get_feedback_summary,
    get_score_trends,
    get_improvement_recommendations,
)

TOOL_DEFS = [
    {
        "name": "get_satisfaction_scores",
        "description": (
            "Returns HCAHPS patient satisfaction scores by department and by domain "
            "(nurse communication, doctor communication, responsiveness, pain, cleanliness, "
            "discharge info). Includes hospital overall score and percentile rank."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_feedback_summary",
        "description": (
            "Returns summarized patient feedback from the last 30 days: "
            "top positive themes, top negative themes, and verbatim comment samples."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_score_trends",
        "description": (
            "Returns 6-month satisfaction score trend for a specific department, "
            "delta vs prior month, delta vs prior year, and national benchmark."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name, e.g. 'Imaging', 'Cardiology', 'Emergency Department'",
                }
            },
            "required": ["department"],
        },
    },
    {
        "name": "get_improvement_recommendations",
        "description": (
            "Returns evidence-based improvement recommendations for a specific department "
            "to improve patient satisfaction scores, with estimated score impact."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name, e.g. 'Imaging', 'Cardiology'",
                }
            },
            "required": ["department"],
        },
    },
]

TOOL_EXECUTORS = {
    "get_satisfaction_scores":       lambda _: json.dumps(get_satisfaction_scores()),
    "get_feedback_summary":          lambda _: json.dumps(get_feedback_summary()),
    "get_score_trends":              lambda inp: json.dumps(get_score_trends(inp.get("department", "Imaging"))),
    "get_improvement_recommendations": lambda inp: json.dumps(
        get_improvement_recommendations(inp.get("department", "Imaging"))
    ),
}
