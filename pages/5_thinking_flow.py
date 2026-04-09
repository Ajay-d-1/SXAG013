"""
Page 5: Thinking Flow — Live AI reasoning visualization.
Shows the full trace of all agent decisions, step by step.
"""
import streamlit as st
from ui.css import inject_css
from ui.sidebar import render_sidebar
import streamlit.components.v1 as components
from ui.components import render_page_header, render_glass_card, esc


AGENT_STYLES = {
    "planner":      {"icon": "&#129504;", "color": "#8b5cf6", "label": "PLANNER",      "bg_icon": "P"},
    "skeptic":      {"icon": "&#128269;", "color": "#ef4444", "label": "SKEPTIC",      "bg_icon": "S"},
    "comparator":   {"icon": "&#9878;",   "color": "#f59e0b", "label": "COMPARATOR",   "bg_icon": "C"},
    "cartographer": {"icon": "&#128506;", "color": "#3b82f6", "label": "CARTOGRAPHER", "bg_icon": "M"},
    "archivist":    {"icon": "&#128218;", "color": "#10b981", "label": "ARCHIVIST",    "bg_icon": "A"},
    "loop":         {"icon": "&#128260;", "color": "#00f2ff", "label": "LOOP",         "bg_icon": "L"},
}


def render():
    inject_css()
    render_sidebar()

    events = st.session_state.get("thinking_events", [])
    topic = st.session_state.get("current_topic", "")

    st.markdown(render_page_header(
        "Thinking Flow",
        "Real-time agent reasoning trace" if events else "Run an analysis to see the AI thinking process",
        show_badge=False
    ), unsafe_allow_html=True)

    if not events:
        st.markdown('''
        <div style="text-align:center;padding:80px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#128173;</div>
          <div style="font-size:14px;color:#64748b;">No thinking events recorded yet. Start a research analysis to watch the agents reason in real-time.</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Agent Status Bar
    agents_seen = set()
    for ev in events:
        agents_seen.add(ev.agent)

    all_agents = ["planner", "skeptic", "comparator", "cartographer", "archivist"]
    last_agent = events[-1].agent if events else ""

    bar_html = '<div style="display:flex;justify-content:space-around;align-items:center;background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.2);border-radius:12px;padding:16px 12px;margin-bottom:24px;backdrop-filter:blur(20px);">'
    for agent in all_agents:
        s = AGENT_STYLES.get(agent, AGENT_STYLES["loop"])
        is_active = agent == last_agent
        is_done = agent in agents_seen and not is_active
        opacity = "1" if is_active else "0.7" if is_done else "0.3"
        glow = f"text-shadow: 0 0 12px {s['color']};" if is_active else ""
        check = " [done]" if is_done and not is_active else ""
        bar_html += f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;opacity:{opacity};transition:all 0.4s;">
          <div style="font-size:28px;{glow}">{s["icon"]}</div>
          <div style="font-size:9px;font-family:Manrope,sans-serif;color:{s["color"]};letter-spacing:0.12em;text-transform:uppercase;">{s["label"]}{check}</div>
        </div>
        '''
    bar_html += '</div>'
    components.html(bar_html, height=80)

    # Summary Stats
    st.markdown(f'''
    <div style="display:flex;gap:20px;margin-bottom:20px;">
      <span style="font-size:11px;color:#64748b;">Total Events: <b style="color:#e2e2eb;">{len(events)}</b></span>
      <span style="font-size:11px;color:#64748b;">Agents Active: <b style="color:#00f2ff;">{len(agents_seen)}</b></span>
      <span style="font-size:11px;color:#64748b;">Topic: <b style="color:#dcb8ff;">{esc(topic[:50])}</b></span>
    </div>
    ''', unsafe_allow_html=True)

    # Filter
    filter_col1, filter_col2 = st.columns([3, 1])
    with filter_col2:
        agent_filter = st.selectbox("Filter by Agent", ["All"] + all_agents, key="think_filter", label_visibility="collapsed")

    filtered_events = events
    if agent_filter != "All":
        filtered_events = [e for e in events if e.agent == agent_filter]

    # Timeline Feed - render in batches to avoid Streamlit limits
    for idx, event in enumerate(filtered_events):
        s = AGENT_STYLES.get(event.agent, AGENT_STYLES["loop"])

        progress_html = ""
        if event.progress:
            progress_html = f'<span style="font-size:10px;color:{s["color"]};background:rgba(0,242,255,0.06);padding:2px 8px;border-radius:4px;float:right;">{esc(event.progress)}</span>'

        event_html = f'''
        <div style="display:flex;gap:16px;margin-bottom:14px;align-items:flex-start;">
          <div style="font-size:10px;font-family:Courier New,monospace;color:#3a494b;padding-top:6px;min-width:50px;">{esc(event.timestamp)}</div>
          <div style="width:3px;min-height:40px;background:{s["color"]};border-radius:2px;opacity:0.5;margin-top:4px;"></div>
          <div style="flex:1;background:rgba(30,31,38,0.5);border-radius:8px;padding:14px 18px;position:relative;overflow:hidden;
            border:1px solid rgba(132,148,149,0.08);">
            {progress_html}
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="font-size:14px;">{s["icon"]}</span>
              <span style="font-size:10px;font-family:Manrope,sans-serif;color:{s["color"]};text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">{s["label"]}</span>
            </div>
            <div style="font-size:13px;color:#e2e2eb;font-weight:500;margin-bottom:4px;">{esc(event.title)}</div>
            <div style="font-size:11px;color:#94a3b8;">{esc(event.detail)}</div>
          </div>
        </div>
        '''
        components.html(event_html, height=100)

    # End Marker
    st.markdown('''
    <div style="text-align:center;padding:24px 0;">
      <div style="width:8px;height:8px;border-radius:50%;background:#00f2ff;margin:0 auto 8px;box-shadow:0 0 8px #00f2ff;"></div>
      <div style="font-size:10px;color:#3a494b;font-family:Manrope,sans-serif;text-transform:uppercase;letter-spacing:0.15em;">END OF REASONING TRACE</div>
    </div>
    ''', unsafe_allow_html=True)


render()
