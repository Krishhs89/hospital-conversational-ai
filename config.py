import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    """Lazy loader — called at request time, not import time, so st.secrets is always ready."""
    # 1. Streamlit Cloud secrets (production)
    try:
        import streamlit as st
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    # 2. Local .env / environment variable (development)
    return os.getenv("ANTHROPIC_API_KEY", "")

# Kept for backward-compat; agents should prefer get_api_key() for lazy loading
ANTHROPIC_API_KEY = get_api_key()
ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
SESSION_TOKEN_LIMIT = 20000

APP_NAME = "Hospital Conversational AI"
APP_SUBTITLE = "Your Jarvis for Hospital Operations"
VERSION = "1.0.0"

AGENT_DESCRIPTIONS = {
    "hospital_flow": "Hospital Flow & Capacity Management — bed census, admissions, discharges, ED wait times, boarding",
    "surgical_ops":  "Surgical Operations — OR utilization, scheduling, case delays, first-case on-time starts",
    "patient_exp":   "Patient Experience — HCAHPS satisfaction scores, feedback trends, improvement insights",
    "imaging":       "Imaging Department — volume, turnaround times, equipment status, department satisfaction",
    "executive":     "Executive Morning Briefing — cross-domain KPI digest and predictive alerts",
}

USER_ROLES = ["Executive", "Line Manager", "Nurse", "Doctor", "Administrator"]

DEPARTMENTS = [
    "Emergency Department", "ICU", "Medical/Surgical", "Labor & Delivery",
    "Pediatrics", "Oncology", "Orthopedics", "Cardiology", "Imaging",
    "Operating Rooms",
]
