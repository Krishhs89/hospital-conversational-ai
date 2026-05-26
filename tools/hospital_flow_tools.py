"""
Tool definitions + executors for the Hospital Flow Agent.
Each TOOL_DEF is passed to the Anthropic API; each function in TOOL_EXECUTORS
is called when Claude requests that tool.
"""
import json
from data.synthetic_data import (
    get_bed_census,
    get_patient_admissions,
    get_discharge_forecast,
    get_boarding_patients,
    get_ed_wait_times,
)

TOOL_DEFS = [
    {
        "name": "get_bed_census",
        "description": (
            "Returns real-time bed census: hospital-wide occupancy percentage, "
            "available beds by unit, and any capacity alerts."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_patient_admissions",
        "description": (
            "Returns today's admission count, admission sources (ED, direct, transfer), "
            "average admit-to-bed time, and top admission diagnoses."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_discharge_forecast",
        "description": (
            "Returns predicted discharges for today, actual discharges so far, "
            "hourly discharge forecast, and top barriers to discharge."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_boarding_patients",
        "description": (
            "Returns number of patients boarding in the ED awaiting an inpatient bed, "
            "average boarding hours, and breakdown by destination unit."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_ed_wait_times",
        "description": (
            "Returns Emergency Department metrics: door-to-triage, door-to-provider, "
            "door-to-admit times, and left-without-being-seen percentage."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

TOOL_EXECUTORS = {
    "get_bed_census":         lambda _: json.dumps(get_bed_census()),
    "get_patient_admissions": lambda _: json.dumps(get_patient_admissions()),
    "get_discharge_forecast": lambda _: json.dumps(get_discharge_forecast()),
    "get_boarding_patients":  lambda _: json.dumps(get_boarding_patients()),
    "get_ed_wait_times":      lambda _: json.dumps(get_ed_wait_times()),
}
