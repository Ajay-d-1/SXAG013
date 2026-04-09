"""
Page 1: Overview / Dashboard — The main intelligence briefing page.
Matches Stitch analytics_dashboard design.
"""
import streamlit as st
from ui.css import inject_css
from ui.sidebar import render_sidebar
import streamlit.components.v1 as components
from ui.components import (
    render_metrics_row, render_confidence_ring, render_section_header,
    render_insight_card, render_glass_card, render_page_header, safe_score, esc
)

def output_glass_card(html_content, height=None):
    """Output glass card using components.v1.html for reliable rendering."""
    card_html = render_glass_card(html_content)
    if height:
        components.html(card_html, height=height)
    else:
        st.markdown(card_html, unsafe_allow_html=True)

def output_insight_card(icon, title, text, height=160):
    """Output insight card using components.v1.html."""
    card_html = render_insight_card(icon, title, text)
    components.html(card_html, height=height)


def render():
    inject_css()
    render_sidebar()

    results = st.session_state.get("results")

    if not results:
        # Landing Page
        st.markdown(render_page_header(
            'From Papers to <span style="color:#00f2ff;">Intelligence</span>',
            "Not just search. Automated research thinking that bridges the gap between raw data and breakthrough insights."
        ), unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align:center;padding:60px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#128300;</div>
          <div style="font-size:16px;color:#64748b;max-width:500px;margin:0 auto;">
            Enter a research topic in the sidebar and choose <b style="color:#00f2ff;">Fast Mode</b> or <b style="color:#8a2be2;">Deep Mode</b> to begin your intelligence analysis.
          </div>
        </div>
        ''', unsafe_allow_html=True)

        # Agent Architecture Cards
        st.markdown('''
        <div style="margin-top:40px;">
          <h2 style="font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;color:#e2e2eb;margin-bottom:4px;">The Pulse Architecture</h2>
          <div style="font-size:13px;color:#64748b;margin-bottom:24px;">Four autonomous agents working in synchronization.</div>
        </div>
        ''', unsafe_allow_html=True)
        cols = st.columns(4)
        agents = [
            ("&#129504;", "Planner", "Orchestrates research paths and optimizes the inquiry tree for maximum depth.", "#8b5cf6"),
            ("&#128269;", "Skeptic", "Identifies contradictions and challenges paper methodology with adversarial AI.", "#ef4444"),
            ("&#128506;", "Cartographer", "Maps the semantic relationships between disparate fields to find novel connections.", "#3b82f6"),
            ("&#128218;", "Archivist", "Synthesizes and organizes millions of tokens into structured, cite-ready libraries.", "#10b981"),
        ]
        for col, (icon, name, desc, color) in zip(cols, agents):
            with col:
                st.markdown(f'''
                <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.08);
                  border-radius:12px;padding:24px;min-height:220px;">
                  <div style="font-size:32px;background:rgba(25,27,34,0.9);width:48px;height:48px;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;margin-bottom:16px;">{icon}</div>
                  <div style="font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;font-size:16px;margin-bottom:8px;">{name}</div>
                  <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{desc}</div>
                  <div style="height:3px;background:{color};border-radius:2px;margin-top:16px;width:60%;"></div>
                </div>
                ''', unsafe_allow_html=True)
        return

    # ===== RESULTS DASHBOARD =====
    topic = st.session_state.get("current_topic", "Research")

    # Metrics Row
    render_metrics_row(results)

    # Main Content (Left 2/3 + Right 1/3)
    left_col, right_col = st.columns([2, 1])

    with left_col:
        summary = esc(results.get("executive_summary", "Analysis complete."))
        key_insight = esc(results.get("key_insight", ""))
        methodology = esc(results.get("methodology_verdict", ""))
        momentum = results.get("field_momentum", "stable")

        st.markdown(f'''
        <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.2);
          box-shadow:0 0 10px rgba(0,242,255,0.05);border-radius:16px;padding:28px;position:relative;min-height:300px;">
          <div style="position:absolute;top:16px;right:20px;font-size:10px;font-family:Courier New,monospace;color:#3a494b;">
            REP_ID: SP-{esc(str(results.get("session_id", "0000")))}</div>
          <div style="position:relative;margin-bottom:20px;">
            <h2 style="font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;color:#e2e2eb;display:flex;align-items:center;gap:10px;margin:0;">
              <span style="width:8px;height:8px;border-radius:50%;background:#00f2ff;box-shadow:0 0 8px #00f2ff;display:inline-block;"></span>
              Executive Summary
            </h2>
          </div>
          <div style="font-size:15px;color:#cbd5e1;line-height:1.7;font-family:Inter,sans-serif;">{summary}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;">
            <div style="background:rgba(25,27,34,0.5);padding:16px;border-radius:8px;border-left:2px solid #00f2ff;">
              <div style="font-size:13px;font-family:Space Grotesk,sans-serif;color:#00f2ff;margin-bottom:6px;">Primary Catalyst</div>
              <div style="font-size:12px;color:#94a3b8;">{key_insight}</div>
            </div>
            <div style="background:rgba(25,27,34,0.5);padding:16px;border-radius:8px;border-left:2px solid #dcb8ff;">
              <div style="font-size:13px;font-family:Space Grotesk,sans-serif;color:#dcb8ff;margin-bottom:6px;">Methodology Verdict</div>
              <div style="font-size:12px;color:#94a3b8;">{methodology}</div>
            </div>
          </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

        # Insight Highlights Row
        insight_cols = st.columns(3)
        momentum_text = {"accelerating": "Research activity is rapidly expanding with increasing publication volume.",
                         "stable": "Consistent research output with steady progress across the field.",
                         "slowing": "Publication rates are declining, field may be maturing.",
                         "emerging": "New field with exponentially growing interest and early-stage exploration."}.get(momentum, "Steady field activity.")

        red_flags = results.get("common_red_flags", [])
        flags_text = esc(", ".join(red_flags[:3])) if red_flags else "No critical issues detected."

        cards = [
            ("&#128161;", "Key Insight", esc(key_insight) if key_insight else "Analysis pending."),
            ("&#128202;", "Field Momentum", esc(f"{momentum.capitalize()} - {momentum_text}")),
            ("&#127987;", "Red Flags", flags_text),
        ]
        for col, (icon, title, text) in zip(insight_cols, cards):
            with col:
                output_insight_card(icon, title, text, height=160)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

        # Top Contradiction
        contradictions = st.session_state.get("contradictions", [])
        if contradictions:
            top_c = contradictions[0]
            sev = esc(top_c.get("severity", "medium"))
            pa_title = esc(top_c.get("paper_a_title", "")[:60])
            pb_title = esc(top_c.get("paper_b_title", "")[:60])
            claim_a = esc(top_c.get("claim_a", ""))
            claim_b = esc(top_c.get("claim_b", ""))
            expl = esc(top_c.get("explanation", ""))
            st.markdown(f'''
            <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(255,49,49,0.2);
              box-shadow:0 0 10px rgba(255,49,49,0.05);border-radius:12px;padding:24px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                <span style="font-size:18px;">&#9888;</span>
                <span style="font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;font-size:15px;text-transform:uppercase;letter-spacing:0.05em;">Top Contradiction</span>
                <span style="font-size:10px;font-family:Manrope,sans-serif;color:#ff3131;background:rgba(255,49,49,0.15);padding:2px 8px;border-radius:4px;text-transform:uppercase;margin-left:auto;">{sev}</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                <div style="background:rgba(255,49,49,0.05);border-radius:8px;padding:14px;border-left:2px solid #ef4444;">
                  <div style="font-size:11px;color:#ef4444;font-family:Manrope,sans-serif;margin-bottom:4px;">Paper A</div>
                  <div style="font-size:12px;color:#e2e2eb;font-weight:600;">{pa_title}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">{claim_a}</div>
                </div>
                <div style="background:rgba(255,49,49,0.05);border-radius:8px;padding:14px;border-left:2px solid #f59e0b;">
                  <div style="font-size:11px;color:#f59e0b;font-family:Manrope,sans-serif;margin-bottom:4px;">Paper B</div>
                  <div style="font-size:12px;color:#e2e2eb;font-weight:600;">{pb_title}</div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:4px;">{claim_b}</div>
                </div>
              </div>
              <div style="font-size:12px;color:#94a3b8;margin-top:12px;font-style:italic;">{expl}</div>
            </div>
            ''', unsafe_allow_html=True)

    with right_col:
        # Confidence Ring
        confidence = results.get("confidence", 0)
        if isinstance(confidence, (int, float)):
            conf_pct = confidence * 100 if confidence <= 1 else confidence
        else:
            conf_pct = 50
        output_glass_card(render_confidence_ring(conf_pct), height=220)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Propagation Clusters
        insights = st.session_state.get("graph_insights", {})
        clusters = insights.get("clusters", [])
        if clusters:
            cluster_html = ""
            dot_colors = ["#00f2ff", "#dcb8ff", "#00dbe7", "#f59e0b", "#10b981"]
            for i, cl in enumerate(clusters[:5]):
                c = dot_colors[i % len(dot_colors)]
                cluster_html += f'''
                <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;
                  background:rgba(25,27,34,0.5);border-radius:8px;margin:4px 0;cursor:pointer;transition:all 0.2s;">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:6px;height:6px;border-radius:50%;background:{c};"></div>
                    <span style="font-size:12px;color:#e2e2eb;">{esc(cl.capitalize())}</span>
                  </div>
                  <span style="color:#3a494b;font-size:12px;">&#8594;</span>
                </div>
                '''
            output_glass_card(f'''
              <div style="font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;font-size:14px;margin-bottom:12px;">Propagation Clusters</div>
              {cluster_html}
            ''', height=280)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # Real-time Pulse
        events = st.session_state.get("thinking_events", [])
        if events:
            pulse_html = '<div style="display:flex;align-items:center;gap:6px;margin-bottom:12px;">'
            pulse_html += '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00f2ff;box-shadow:0 0 6px #00f2ff;"></span>'
            pulse_html += '<span style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;">Real-time Pulse</span></div>'
            for ev in events[-4:][::-1]:
                pulse_html += f'''
                <div style="display:flex;gap:12px;margin:8px 0;">
                  <div style="font-size:10px;font-family:Courier New,monospace;color:#3a494b;padding-top:2px;min-width:40px;">{esc(ev.timestamp)}</div>
                  <div style="font-size:12px;color:#cbd5e1;">{esc(ev.title)}</div>
                </div>
                '''
            output_glass_card(pulse_html, height=200)

        # Open Questions
        open_qs = results.get("open_questions", [])
        if open_qs:
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            qs_html = '<div style="font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;font-size:14px;margin-bottom:12px;">Open Questions</div>'
            for q in open_qs[:4]:
                qs_html += f'<div style="font-size:12px;color:#94a3b8;padding:6px 0;border-bottom:1px solid rgba(0,242,255,0.05);">{esc(q)}</div>'
            output_glass_card(qs_html, height=180)


render()
