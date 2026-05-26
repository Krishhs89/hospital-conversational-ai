"""
Tool definitions + executors for the Surgical Operations Agent.
"""
import json
from data.synthetic_data import (
    get_or_utilization,
    get_or_schedule,
    get_case_delays,
    get_first_case_on_time,
    get_or_cancellations,
)

TOOL_DEFS = [
    {
        "name": "get_or_utilization",
        "description": (
            "Returns today's OR utilization percentage per room, total cases scheduled vs completed, "
            "and utilization vs target."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_or_schedule",
        "description": (
            "Returns today's full OR schedule: cases by room, specialty, scheduled start time, "
            "duration, and status (completed / in-progress / scheduled / delayed)."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_case_delays",
        "description": (
            "Returns delayed surgical cases today, average delay in minutes, "
            "root causes of delays, and downstream schedule impact."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_first_case_on_time",
        "description": (
            "Returns first-case on-time start percentage by OR room vs target, "
            "and the primary reason for late starts."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_or_cancellations",
        "description": (
            "Returns number and rate of surgical case cancellations today, "
            "cancellation reasons, and month-to-date rate vs target."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

TOOL_EXECUTORS = {
    "get_or_utilization":      lambda _: json.dumps(get_or_utilization()),
    "get_or_schedule":         lambda _: json.dumps(get_or_schedule()),
    "get_case_delays":         lambda _: json.dumps(get_case_delays()),
    "get_first_case_on_time":  lambda _: json.dumps(get_first_case_on_time()),
    "get_or_cancellations":    lambda _: json.dumps(get_or_cancellations()),
}
