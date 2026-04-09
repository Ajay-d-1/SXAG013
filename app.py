"""
ScholAR Pulse — Autonomous Research Intelligence Engine v4.0
Main application entry point. Multi-page navigation router.
"""
import streamlit as st

# Must be the first Streamlit call
st.set_page_config(
    page_title="ScholAR Pulse — Cinematic Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Page Registration ──
overview_page = st.Page("pages/1_overview.py", title="Dashboard", icon="📊", default=True)
graph_page = st.Page("pages/2_knowledge_graph.py", title="Intelligence Map", icon="🕸️")
mindmap_page = st.Page("pages/3_mind_map.py", title="Mind Map", icon="🧠")
cards_page = st.Page("pages/4_intelligence_cards.py", title="Paper Library", icon="📄")
thinking_page = st.Page("pages/5_thinking_flow.py", title="Thinking Flow", icon="💭")
report_page = st.Page("pages/6_report.py", title="Reports", icon="📋")

# ── Navigation ──
pg = st.navigation([
    overview_page,
    graph_page,
    mindmap_page,
    cards_page,
    thinking_page,
    report_page,
])

# ── Initialize Session State ──
defaults = {
    "results": None,
    "papers": [],
    "critiques": [],
    "contradictions": [],
    "sub_questions": [],
    "thinking_events": [],
    "graph_path": "",
    "mindmap_path": "",
    "graph_insights": {},
    "current_topic": "",
    "current_mode": "fast",
    "confidence": 0,
    "depth": 0,
    "analysis_history": [],
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Run Selected Page ──
pg.run()
