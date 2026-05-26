"""
Hospital Conversational AI — Streamlit entry point.
Run: streamlit run main.py
"""
import streamlit as st

from config import APP_NAME, APP_SUBTITLE, SESSION_TOKEN_LIMIT, USER_ROLES, AGENT_DESCRIPTIONS
from memory.session_manager import SessionManager
from agents.routing_agent import RoutingAgent
import agents.hospital_flow_agent as flow_mod
import agents.surgical_ops_agent as surgical_mod
import agents.patient_exp_agent as pat_exp_mod
import agents.imaging_agent as imaging_mod
import agents.executive_agent as exec_mod

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── API key guard — fail fast with a clear message ─────────────────────────────
from config import get_api_key
_api_key = get_api_key()
if not _api_key:
    st.error(
        "**ANTHROPIC_API_KEY is not set.**\n\n"
        "On Streamlit Cloud: click **Manage app** (bottom-right) → **Settings** → **Secrets** and add:\n\n"
        "```toml\nANTHROPIC_API_KEY = \"sk-ant-your-key-here\"\n```\n\n"
        "Then click **Save** — the app will reboot automatically."
    )
    st.stop()

# ── Agent registry keyed by routing agent output ───────────────────────────────
AGENT_BUILDERS = {
    "hospital_flow": flow_mod.build,
    "surgical_ops":  surgical_mod.build,
    "patient_exp":   pat_exp_mod.build,
    "imaging":       imaging_mod.build,
    "executive":     exec_mod.build,
}

AGENT_LABELS = {
    "hospital_flow": "🏥 Hospital Flow",
    "surgical_ops":  "🔪 Surgical Ops",
    "patient_exp":   "⭐ Patient Experience",
    "imaging":       "📡 Imaging",
    "executive":     "📋 Executive",
}

# ── Session state bootstrap ────────────────────────────────────────────────────
if "session_mgr" not in st.session_state:
    st.session_state.session_mgr = SessionManager()
if "routing_agent" not in st.session_state:
    st.session_state.routing_agent = RoutingAgent()
if "session" not in st.session_state:
    st.session_state.session = None
if "chat_history" not in st.session_state:       # display-only list of dicts
    st.session_state.chat_history = []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hospital-room.png", width=64)
    st.title(APP_NAME)
    st.caption(APP_SUBTITLE)
    st.divider()

    st.subheader("Your Profile")
    user_name = st.text_input("Name", value="Dr. Krishna", key="user_name_input")
    user_role = st.selectbox("Role", USER_ROLES, key="user_role_input")

    if st.button("Start / Reset Session", type="primary", use_container_width=True):
        mgr = st.session_state.session_mgr
        if st.session_state.session:
            mgr.reset(st.session_state.session.session_id, user_name, user_role)
        else:
            st.session_state.session = mgr.create(user_name, user_role)
        st.session_state.chat_history = []
        st.success(f"Session started for {user_name} ({user_role})")

    st.divider()
    st.subheader("Specialist Agents")
    for key, label in AGENT_LABELS.items():
        st.markdown(f"**{label}**")
        st.caption(AGENT_DESCRIPTIONS[key])

    st.divider()
    st.subheader("Example Questions")
    examples = [
        "Give me my morning briefing",
        "What is the current bed census?",
        "Why did Imaging satisfaction drop?",
        "How are the ORs performing today?",
        "How many patients are boarding in the ED?",
        "What are the top reasons for surgical delays?",
        "Show me 6-month satisfaction trend for Cardiology",
        "Is the MRI equipment operational?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex[:20]}"):
            st.session_state["pending_example"] = ex

    # Session info
    if st.session_state.session:
        s = st.session_state.session
        st.divider()
        st.caption(f"Session: {s.session_id} | ~{s.token_estimate:,} tokens used")
        pct = min(100, int(s.token_estimate / SESSION_TOKEN_LIMIT * 100))
        st.progress(pct, text=f"Token usage: {pct}%")


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown(f"## 🏥 {APP_NAME}")
st.caption(f"*{APP_SUBTITLE}* — powered by Claude claude-sonnet-4-6")

if st.session_state.session is None:
    st.info("👈 Set your name and role in the sidebar, then click **Start / Reset Session** to begin.")
    st.stop()

session = st.session_state.session

# Render existing chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar=msg.get("avatar", "🤖")):
        st.markdown(msg["content"])
        if "agent" in msg and msg["agent"]:
            st.caption(f"— {AGENT_LABELS.get(msg['agent'], msg['agent'])}")

# Handle example button clicks
if "pending_example" in st.session_state:
    pending = st.session_state.pop("pending_example")
    st.session_state["_user_input"] = pending

# Chat input
user_input = st.chat_input("Ask about hospital operations…", key="chat_input")
if "_user_input" in st.session_state:
    user_input = st.session_state.pop("_user_input")

if user_input:
    # Token limit guard
    if not session.within_token_limit(SESSION_TOKEN_LIMIT):
        st.warning(
            "Session token limit reached. Please click **Start / Reset Session** in the sidebar to continue."
        )
        st.stop()

    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input, "avatar": "👤"})
    session.add_user_message(user_input)

    # Route
    with st.spinner("Routing your question…"):
        route = st.session_state.routing_agent.route(user_input)

    if route.get("off_topic"):
        reply = st.session_state.routing_agent.get_off_topic_message(
            route.get("off_topic_reason", "unrelated to hospital operations")
        )
        agent_key = None
    else:
        agent_key = route.get("agent", "executive")
        refined_query = route.get("refined_query", user_input)

        builder = AGENT_BUILDERS[agent_key]
        specialist = builder(user_role)

        with st.spinner(f"Consulting {AGENT_LABELS[agent_key]}…"):
            history = session.get_history(last_n=8)
            # Remove the last user message — we pass refined_query separately
            history = [m for m in history if not (m["role"] == "user" and m["content"] == user_input)]
            reply = specialist.run(refined_query, history)

    # Display assistant reply
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(reply)
        if agent_key:
            st.caption(f"— {AGENT_LABELS.get(agent_key, agent_key)}")

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply,
        "agent": agent_key,
        "avatar": "🤖",
    })
    session.add_assistant_message(reply, agent=agent_key or "guardrail")
    st.rerun()
