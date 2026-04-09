"""
Shared sidebar component for ScholAR Pulse.
Renders research input, mode selection, and recent sessions on every page.
"""
import streamlit as st
from core.loop import ResearchLoop


def render_sidebar():
    """Render the full ScholAR Pulse sidebar."""
    with st.sidebar:
        # ── Branding ──
        st.markdown('''
        <div style="padding:4px 0 20px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#00f2ff,#00dbe7);
              display:flex;align-items:center;justify-content:center;box-shadow:0 0 15px rgba(0,242,255,0.4);font-size:16px;">🔬</div>
            <div>
              <div style="font-family:Space Grotesk,sans-serif;font-size:17px;font-weight:700;color:#00f2ff;letter-spacing:-0.5px;">ScholAR Pulse</div>
              <div style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:0.2em;">Cinematic Intelligence</div>
            </div>
          </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("---")

        # ── Research Input ──
        st.markdown('<div style="font-size:10px;font-family:Manrope,sans-serif;color:#00f2ff;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;">Enter Research Topic</div>', unsafe_allow_html=True)
        topic = st.text_input("Research Topic", placeholder="e.g. CRISPR gene editing", label_visibility="collapsed", key="sidebar_topic")

        col1, col2 = st.columns(2)
        with col1:
            fast = st.button("⚡ Fast Mode", use_container_width=True, key="fast_btn")
        with col2:
            deep = st.button("🧠 Deep Mode", use_container_width=True, key="deep_btn")

        # ── Execute Research ──
        if fast or deep:
            mode = "fast" if fast else "deep"
            if topic:
                _run_research(topic, mode)
            else:
                st.warning("Please enter a research topic.")

        st.markdown("---")

        # ── How It Works ──
        with st.expander("🏗️ The Pulse Architecture"):
            st.markdown("""
            **Four autonomous agents working in synchronization:**

            🧠 **Planner** — Decomposes topic into research sub-questions

            🔍 **Skeptic** — Challenges methodology with adversarial AI

            🗺️ **Cartographer** — Maps semantic relationships between papers

            📚 **Archivist** — Synthesizes findings into structured reports
            """)

        # ── Recent Sessions ──
        if "analysis_history" in st.session_state and st.session_state.analysis_history:
            st.markdown('<div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;margin-top:16px;">Recent Sessions</div>', unsafe_allow_html=True)
            for entry in st.session_state.analysis_history[-5:][::-1]:
                st.markdown(f'''
                <div style="background:rgba(25,27,34,0.5);border-radius:6px;padding:8px 12px;margin:4px 0;
                  border:0.5px solid rgba(0,242,255,0.06);font-size:12px;color:#94a3b8;">
                  <span style="color:#00f2ff;">●</span> {entry.get("topic", "Unknown")[:40]}
                  <span style="font-size:10px;color:#3a494b;float:right;">{entry.get("mode", "fast").upper()}</span>
                </div>
                ''', unsafe_allow_html=True)

    return topic


def _run_research(topic, mode):
    """Execute the research loop and store results in session state."""
    st.session_state.pop("results", None)

    progress_placeholder = st.sidebar.empty()
    status_text = st.sidebar.empty()

    with st.spinner(f"{'⚡' if mode == 'fast' else '🧠'} Running {mode.upper()} analysis..."):
        loop = ResearchLoop(topic, mode)

        def progress_cb(msg, conf, depth):
            status_text.markdown(f'<div style="font-size:11px;color:#94a3b8;padding:4px 0;">{msg}</div>', unsafe_allow_html=True)

        result = loop.run(progress_callback=progress_cb)

    status_text.empty()

    # Store ALL data in session_state
    st.session_state.results = result
    st.session_state.current_topic = topic
    st.session_state.current_mode = mode
    st.session_state.papers = loop.all_papers
    st.session_state.critiques = loop.all_critiques
    st.session_state.contradictions = loop.all_contradictions
    st.session_state.sub_questions = loop.sub_questions
    st.session_state.thinking_events = loop.thinking_feed.get_events()
    st.session_state.confidence = loop.confidence
    st.session_state.depth = loop.depth

    # Build mindmap
    mindmap_path = loop.cartographer.build_mindmap(
        topic, loop.sub_questions, loop.all_papers, loop.all_critiques
    )
    st.session_state.mindmap_path = mindmap_path
    st.session_state.graph_path = result.get("graph_path", "")

    # Graph insights
    st.session_state.graph_insights = loop.cartographer.generate_graph_insights(
        loop.all_papers, loop.all_critiques, loop.all_contradictions
    )

    # History
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    st.session_state.analysis_history.append({"topic": topic, "mode": mode, "session_id": result.get("session_id", "")})

    st.rerun()
