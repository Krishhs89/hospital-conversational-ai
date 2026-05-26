"""
Synthetic hospital data generator.
Simulates real-time data that would come from Epic Caboodle / MS Fabric.
"""
import random
from datetime import datetime, timedelta
from typing import Any

_rng = random.Random(42)


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ──────────────────────────────────────────────
# HOSPITAL FLOW DATA
# ──────────────────────────────────────────────

def get_bed_census() -> dict[str, Any]:
    units = {
        "Emergency Department": {"total": 48, "occupied": 41, "holds": 8},
        "ICU":                  {"total": 24, "occupied": 22, "holds": 2},
        "Medical/Surgical":     {"total": 120, "occupied": 103, "holds": 5},
        "Labor & Delivery":     {"total": 18, "occupied": 11, "holds": 0},
        "Pediatrics":           {"total": 30, "occupied": 19, "holds": 1},
        "Oncology":             {"total": 28, "occupied": 25, "holds": 3},
        "Cardiology":           {"total": 32, "occupied": 29, "holds": 4},
        "Orthopedics":          {"total": 26, "occupied": 20, "holds": 2},
    }
    total_beds = sum(u["total"] for u in units.values())
    total_occ  = sum(u["occupied"] for u in units.values())
    return {
        "as_of": _now(),
        "hospital_occupancy_pct": round(total_occ / total_beds * 100, 1),
        "total_licensed_beds": total_beds,
        "total_occupied": total_occ,
        "total_available": total_beds - total_occ,
        "units": units,
        "alerts": [
            "ICU at 91.7% — approaching diversion threshold",
            "Cardiology 90.6% — boarding 4 ED patients",
        ],
    }


def get_patient_admissions() -> dict[str, Any]:
    return {
        "date": _today(),
        "total_admissions_today": 47,
        "admissions_by_source": {
            "Emergency Department": 28,
            "Direct Admission": 12,
            "Transfer from Outside": 4,
            "Surgical Post-op": 3,
        },
        "avg_admit_to_bed_minutes": 68,
        "target_minutes": 45,
        "top_admission_diagnoses": [
            "Chest Pain / ACS Rule-out",
            "COPD Exacerbation",
            "Hip Fracture",
            "Sepsis",
            "CHF Exacerbation",
        ],
    }


def get_discharge_forecast() -> dict[str, Any]:
    return {
        "date": _today(),
        "predicted_discharges_today": 39,
        "actual_discharges_so_far": 14,
        "remaining_predicted": 25,
        "by_hour": {
            "08:00–10:00": 5,
            "10:00–12:00": 8,
            "12:00–14:00": 7,
            "14:00–16:00": 9,
            "16:00–18:00": 10,
        },
        "barriers_to_discharge": [
            {"barrier": "Awaiting PT/OT evaluation", "count": 7},
            {"barrier": "Awaiting transportation", "count": 5},
            {"barrier": "Pending specialist sign-off", "count": 6},
            {"barrier": "SNF/Rehab placement not found", "count": 4},
        ],
    }


def get_boarding_patients() -> dict[str, Any]:
    return {
        "as_of": _now(),
        "total_boarding": 22,
        "boarding_in_ed": 14,
        "avg_boarding_hours": 4.3,
        "longest_boarding_hours": 11.2,
        "by_destination_unit": {
            "ICU": 3,
            "Cardiology": 4,
            "Medical/Surgical": 9,
            "Oncology": 3,
            "Orthopedics": 3,
        },
        "risk_alert": "14 ED boarders risk >4hr LoS target breach within 90 minutes",
    }


def get_ed_wait_times() -> dict[str, Any]:
    return {
        "as_of": _now(),
        "door_to_triage_min": 4,
        "door_to_provider_min": 31,
        "door_to_admit_min": 187,
        "lwbs_pct": 2.1,
        "patients_in_waiting_room": 12,
        "patients_in_treatment": 41,
        "target_door_to_provider_min": 20,
        "trend": "Door-to-provider trending UP 8 min vs prior Tuesday",
    }


# ──────────────────────────────────────────────
# SURGICAL OPERATIONS DATA
# ──────────────────────────────────────────────

def get_or_utilization() -> dict[str, Any]:
    rooms = {}
    for i in range(1, 11):
        util = round(random.uniform(60, 98), 1)
        rooms[f"OR-{i}"] = {
            "utilization_pct": util,
            "cases_today": random.randint(4, 8),
            "minutes_scheduled": random.randint(400, 550),
            "minutes_used": random.randint(350, 540),
        }
    avg_util = round(sum(r["utilization_pct"] for r in rooms.values()) / len(rooms), 1)
    return {
        "date": _today(),
        "avg_or_utilization_pct": avg_util,
        "target_utilization_pct": 85.0,
        "total_cases_scheduled": 62,
        "total_cases_completed": 38,
        "rooms": rooms,
        "alert": "OR-4 and OR-7 running >15 min behind schedule",
    }


def get_or_schedule() -> dict[str, Any]:
    specialties = ["Orthopedics", "Cardiology", "General Surgery",
                   "Neurosurgery", "OB/GYN", "ENT", "Urology"]
    cases = []
    for i in range(1, 11):
        sp = random.choice(specialties)
        start_h = 7 + (i - 1) * 1
        cases.append({
            "or_room": f"OR-{i % 10 + 1}",
            "specialty": sp,
            "scheduled_start": f"{start_h:02d}:00",
            "estimated_duration_min": random.randint(60, 240),
            "status": random.choice(["Completed", "In Progress", "Scheduled", "Delayed"]),
        })
    return {
        "date": _today(),
        "total_cases": 62,
        "sample_cases": cases,
        "add_on_cases_today": 5,
        "cancelled_cases_today": 3,
    }


def get_case_delays() -> dict[str, Any]:
    return {
        "date": _today(),
        "total_delayed_cases": 9,
        "avg_delay_minutes": 23,
        "delay_reasons": [
            {"reason": "Late surgeon arrival", "cases": 3, "avg_delay_min": 18},
            {"reason": "Equipment / instrument not ready", "cases": 2, "avg_delay_min": 31},
            {"reason": "Patient transport delay", "cases": 2, "avg_delay_min": 15},
            {"reason": "Anesthesia consent incomplete", "cases": 1, "avg_delay_min": 22},
            {"reason": "OR room turnover exceeded 30 min", "cases": 1, "avg_delay_min": 41},
        ],
        "estimated_downstream_impact": "OR-4 and OR-7 may require 1 add-on case cancellation if delays persist",
    }


def get_first_case_on_time() -> dict[str, Any]:
    rooms = {f"OR-{i}": random.choice([True, True, True, False]) for i in range(1, 11)}
    on_time_count = sum(1 for v in rooms.values() if v)
    return {
        "date": _today(),
        "on_time_start_pct": round(on_time_count / len(rooms) * 100, 1),
        "target_pct": 85.0,
        "by_room": rooms,
        "top_late_reason": "Surgeon not in-house at scheduled time (3 of 4 late starts)",
    }


def get_or_cancellations() -> dict[str, Any]:
    return {
        "date": _today(),
        "total_cancellations": 3,
        "cancellation_rate_pct": 4.8,
        "target_rate_pct": 3.0,
        "reasons": [
            {"reason": "Patient medically unfit on day of surgery", "count": 1},
            {"reason": "Surgeon unavailable", "count": 1},
            {"reason": "Equipment/supply unavailable", "count": 1},
        ],
        "mtd_cancellation_rate_pct": 3.9,
    }


# ──────────────────────────────────────────────
# PATIENT EXPERIENCE DATA
# ──────────────────────────────────────────────

def get_satisfaction_scores() -> dict[str, Any]:
    depts = {
        "Emergency Department": {"score": 72.4, "target": 80.0, "trend": "down"},
        "ICU":                  {"score": 88.1, "target": 85.0, "trend": "stable"},
        "Medical/Surgical":     {"score": 79.3, "target": 82.0, "trend": "up"},
        "Labor & Delivery":     {"score": 92.7, "target": 90.0, "trend": "up"},
        "Pediatrics":           {"score": 85.4, "target": 85.0, "trend": "stable"},
        "Oncology":             {"score": 81.2, "target": 82.0, "trend": "down"},
        "Cardiology":           {"score": 76.8, "target": 82.0, "trend": "down"},
        "Imaging":              {"score": 68.3, "target": 78.0, "trend": "down"},
        "Orthopedics":          {"score": 83.6, "target": 82.0, "trend": "up"},
    }
    return {
        "period": "May 2026 (MTD)",
        "hospital_overall_score": 79.8,
        "hospital_target": 82.0,
        "percentile_rank": "42nd",
        "departments": depts,
        "domains": {
            "Communication with Nurses": 82.1,
            "Communication with Doctors": 80.4,
            "Responsiveness of Staff": 71.3,
            "Pain Management": 74.8,
            "Cleanliness": 83.2,
            "Discharge Information": 77.6,
            "Overall Rating": 79.8,
        },
    }


def get_feedback_summary() -> dict[str, Any]:
    return {
        "period": "Last 30 days",
        "total_responses": 1243,
        "top_positive_themes": [
            "Nursing staff compassionate and attentive",
            "Doctors explained treatment clearly",
            "Room cleanliness exceeded expectations",
        ],
        "top_negative_themes": [
            "Long wait times in ED and Imaging",
            "Insufficient pain management responsiveness",
            "Discharge instructions unclear or rushed",
            "Difficulty reaching staff via call button",
        ],
        "verbatim_samples": [
            {
                "dept": "Imaging",
                "sentiment": "negative",
                "comment": "Waited 2.5 hours for my MRI. No one updated me on the delay.",
            },
            {
                "dept": "Labor & Delivery",
                "sentiment": "positive",
                "comment": "The nurses were absolutely incredible. Best experience of my life.",
            },
            {
                "dept": "Cardiology",
                "sentiment": "negative",
                "comment": "Night staff took 25 minutes to respond to my call light.",
            },
        ],
    }


def get_score_trends(department: str = "Imaging") -> dict[str, Any]:
    months = ["Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026"]
    base = {"Imaging": 74, "Cardiology": 80, "Emergency Department": 75}.get(department, 79)
    scores = [round(base + random.uniform(-4, 3), 1) for _ in months]
    scores[-1] = round(base - 5.7, 1)  # latest month notably lower
    return {
        "department": department,
        "months": months,
        "scores": scores,
        "national_benchmark": 78.0,
        "delta_vs_prior_month": round(scores[-1] - scores[-2], 1),
        "delta_vs_prior_year": -4.2,
    }


def get_improvement_recommendations(department: str = "Imaging") -> dict[str, Any]:
    recs = {
        "Imaging": [
            "Implement proactive patient wait-time updates every 30 minutes",
            "Deploy scheduling optimization to reduce appointment-to-scan gaps",
            "Add dedicated patient navigator for complex imaging patients",
            "Staff communication training focused on AIDET framework",
        ],
        "Cardiology": [
            "Improve night-shift call-light response with tiered alert system",
            "Conduct daily safety huddles to address patient concerns",
            "Enhance pain management rounding protocol",
        ],
    }
    return {
        "department": department,
        "recommendations": recs.get(department, ["Review staffing ratios", "Enhance communication protocols"]),
        "estimated_score_impact": "+4–7 percentile points within 90 days",
        "benchmark_reference": "Top-quartile hospitals in this domain share these practices",
    }


# ──────────────────────────────────────────────
# IMAGING DATA
# ──────────────────────────────────────────────

def get_imaging_volume() -> dict[str, Any]:
    return {
        "date": _today(),
        "total_exams_today": 187,
        "by_modality": {
            "CT":          {"scheduled": 64, "completed": 48, "pending": 16},
            "MRI":         {"scheduled": 41, "completed": 28, "pending": 13},
            "X-Ray":       {"scheduled": 52, "completed": 52, "pending": 0},
            "Ultrasound":  {"scheduled": 22, "completed": 18, "pending": 4},
            "Nuclear Med": {"scheduled": 8,  "completed": 5,  "pending": 3},
        },
        "inpatient_vs_outpatient": {"inpatient": 112, "outpatient": 75},
        "stat_orders_pending": 7,
    }


def get_imaging_turnaround() -> dict[str, Any]:
    return {
        "date": _today(),
        "avg_order_to_exam_min":    {
            "CT": 48, "MRI": 127, "X-Ray": 22, "Ultrasound": 61,
        },
        "avg_exam_to_report_min":   {
            "CT": 34, "MRI": 52, "X-Ray": 18, "Ultrasound": 41,
        },
        "stat_order_to_report_min": {
            "CT": 28, "MRI": 45, "X-Ray": 15, "Ultrasound": 35,
        },
        "targets": {
            "routine_order_to_report_min": 60,
            "stat_order_to_report_min": 30,
        },
        "alerts": [
            "MRI order-to-exam TAT at 127 min — 67 min above target",
            "2 STAT CT reports pending > 30 min",
        ],
    }


def get_equipment_status() -> dict[str, Any]:
    return {
        "as_of": _now(),
        "equipment": {
            "CT Scanner 1":      {"status": "Operational", "utilization_pct": 88},
            "CT Scanner 2":      {"status": "Operational", "utilization_pct": 71},
            "MRI 3T (Suite A)":  {"status": "Operational", "utilization_pct": 94},
            "MRI 1.5T (Suite B)":{"status": "Down — scheduled maintenance", "utilization_pct": 0},
            "Ultrasound Bay 1":  {"status": "Operational", "utilization_pct": 65},
            "Ultrasound Bay 2":  {"status": "Operational", "utilization_pct": 58},
            "Nuclear Med Cam 1": {"status": "Operational", "utilization_pct": 72},
        },
        "alert": "MRI 1.5T Suite B down — 13 appointments rescheduled; MRI 3T at near-capacity (94%)",
    }


def get_imaging_satisfaction() -> dict[str, Any]:
    return {
        "period": "May 2026 (MTD)",
        "overall_score": 68.3,
        "target": 78.0,
        "national_benchmark": 76.2,
        "gap_to_target": -9.7,
        "lowest_domains": [
            {"domain": "Wait Time Communication", "score": 58.1},
            {"domain": "Staff Courtesy",           "score": 62.4},
            {"domain": "Exam Explanation",         "score": 65.7},
        ],
        "root_cause_summary": (
            "MRI Suite B downtime (since May 14) has increased MRI wait times by ~2.1 hrs, "
            "driving 68% of negative Imaging comments this month."
        ),
    }


# ──────────────────────────────────────────────
# EXECUTIVE DIGEST
# ──────────────────────────────────────────────

def get_executive_digest() -> dict[str, Any]:
    return {
        "generated_at": _now(),
        "hospital_snapshot": {
            "occupancy_pct": 85.4,
            "admits_today": 47,
            "predicted_discharges": 39,
            "boarding_patients": 22,
        },
        "or_snapshot": {
            "avg_utilization_pct": 81.2,
            "cases_on_schedule": "62% on time",
            "delayed_cases": 9,
            "cancellations": 3,
        },
        "patient_experience_snapshot": {
            "hospital_overall": 79.8,
            "lowest_dept": "Imaging (68.3)",
            "improving_depts": ["Medical/Surgical", "Orthopedics", "Labor & Delivery"],
        },
        "predictive_alerts": [
            "⚠️  ICU projected to hit 100% occupancy by 14:00 — recommend activating surge protocol",
            "⚠️  OR mid-morning slowdown predicted: OR-4/OR-7 delays may cascade to 3 PM add-ons",
            "⚠️  Imaging satisfaction trending to 65 if MRI Suite B not restored by week-end",
        ],
        "actions_recommended": [
            "Activate discharge command center for 12 SNF-bound patients",
            "Review OR-4 and OR-7 surgeon scheduling compliance",
            "Escalate MRI Suite B repair timeline with Facilities",
        ],
    }
