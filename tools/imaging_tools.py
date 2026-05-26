"""
Tool definitions + executors for the Imaging Department Agent.
"""
import json
from data.synthetic_data import (
    get_imaging_volume,
    get_imaging_turnaround,
    get_equipment_status,
    get_imaging_satisfaction,
)

TOOL_DEFS = [
    {
        "name": "get_imaging_volume",
        "description": (
            "Returns today's imaging exam volume by modality (CT, MRI, X-Ray, Ultrasound, "
            "Nuclear Med): scheduled, completed, and pending counts."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_imaging_turnaround",
        "description": (
            "Returns order-to-exam and exam-to-report turnaround times by modality, "
            "vs targets, plus STAT order performance and any breach alerts."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_equipment_status",
        "description": (
            "Returns real-time status and utilization of imaging equipment: "
            "CT scanners, MRI suites, ultrasound bays, and nuclear medicine cameras."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_imaging_satisfaction",
        "description": (
            "Returns patient satisfaction scores specifically for the Imaging department, "
            "lowest-scoring domains, gap to target, and root-cause summary."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

TOOL_EXECUTORS = {
    "get_imaging_volume":       lambda _: json.dumps(get_imaging_volume()),
    "get_imaging_turnaround":   lambda _: json.dumps(get_imaging_turnaround()),
    "get_equipment_status":     lambda _: json.dumps(get_equipment_status()),
    "get_imaging_satisfaction": lambda _: json.dumps(get_imaging_satisfaction()),
}
