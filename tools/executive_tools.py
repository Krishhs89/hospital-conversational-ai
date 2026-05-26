"""
Tool definitions + executors for the Executive Briefing Agent.
Aggregates cross-domain KPIs into a single morning digest.
"""
import json
from data.synthetic_data import (
    get_executive_digest,
    get_bed_census,
    get_or_utilization,
    get_satisfaction_scores,
    get_boarding_patients,
)

TOOL_DEFS = [
    {
        "name": "get_executive_digest",
        "description": (
            "Returns a full cross-domain morning briefing for hospital executives: "
            "hospital flow snapshot, OR snapshot, patient experience snapshot, "
            "AI-generated predictive alerts, and recommended actions."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_cross_domain_kpis",
        "description": (
            "Returns today's top KPIs across all domains in one view: "
            "bed occupancy, OR utilization, patient satisfaction, and boarding count."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


def _get_cross_domain_kpis(_: dict) -> str:
    census = get_bed_census()
    or_data = get_or_utilization()
    sat = get_satisfaction_scores()
    boarding = get_boarding_patients()
    return json.dumps({
        "hospital_occupancy_pct": census["hospital_occupancy_pct"],
        "available_beds": census["total_available"],
        "or_avg_utilization_pct": or_data["avg_or_utilization_pct"],
        "patient_satisfaction_overall": sat["hospital_overall_score"],
        "boarding_patients": boarding["total_boarding"],
        "alerts": census["alerts"] + or_data.get("alert", "").split(";"),
    })


TOOL_EXECUTORS = {
    "get_executive_digest":    lambda _: json.dumps(get_executive_digest()),
    "get_cross_domain_kpis":   _get_cross_domain_kpis,
}
