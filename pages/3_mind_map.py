"""
Page 3: Mind Map — Interactive hierarchical visualization of research decomposition.
"""
import streamlit as st
import os
from ui.css import inject_css
from ui.sidebar import render_sidebar
import streamlit.components.v1 as components
from ui.components import render_page_header, render_glass_card, safe_score, esc

def output_glass_card(html_content, height=None):
    """Output glass card using components.v1.html for reliable rendering."""
    card_html = render_glass_card(html_content)
    if height:
        components.html(card_html, height=height)
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def render():
    inject_css()
    render_sidebar()

    papers = st.session_state.get("papers", [])
    critiques = st.session_state.get("critiques", [])
    sub_questions = st.session_state.get("sub_questions", [])
    mindmap_path = st.session_state.get("mindmap_path", "")
    topic = st.session_state.get("current_topic", "")

    st.markdown(render_page_header(
        "Research Mind Map",
        "Hierarchical decomposition of research questions and evidence flow" if papers else "Run an analysis to generate a mind map",
        show_badge=False
    ), unsafe_allow_html=True)

    if not papers or not mindmap_path:
        st.markdown('''
        <div style="text-align:center;padding:80px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#129504;</div>
          <div style="font-size:14px;color:#64748b;">No data yet. Run a research analysis from the sidebar to generate the mind map.</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Breadcrumb
    st.markdown('''
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;font-size:12px;">
      <span style="color:#00f2ff;cursor:pointer;">Topic</span>
      <span style="color:#3a494b;">&#8250;</span>
      <span style="color:#94a3b8;">Questions</span>
      <span style="color:#3a494b;">&#8250;</span>
      <span style="color:#64748b;">Evidence Flow</span>
    </div>
    ''', unsafe_allow_html=True)

    # Layout: Map + Sidebar
    map_col, info_col = st.columns([3, 1])

    with map_col:
        if os.path.exists(mindmap_path):
            with open(mindmap_path, "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=600, scrolling=False)

            # Bottom toolbar
            st.markdown('''
            <div style="display:flex;align-items:center;gap:20px;background:rgba(25,27,34,0.7);
              border-radius:8px;padding:8px 16px;margin-top:8px;border:0.5px solid rgba(0,242,255,0.08);">
              <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;">MAP ZOOM</div>
              <span style="color:#64748b;cursor:pointer;">&#8722;</span>
              <span style="font-size:12px;color:#e2e2eb;font-family:Space Grotesk,sans-serif;">100%</span>
              <span style="color:#64748b;cursor:pointer;">+</span>
              <div style="height:16px;width:1px;background:rgba(0,242,255,0.1);"></div>
              <span style="font-size:11px;color:#94a3b8;">&#128269; Filter</span>
              <span style="font-size:11px;color:#94a3b8;">&#9670; Layers</span>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.warning("Mind map file not found.")

    with info_col:
        # Node Insights Panel
        st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:16px;font-weight:700;color:#00f2ff;margin-bottom:16px;">Node Insights</div>', unsafe_allow_html=True)

        # Core Objective
        output_glass_card(f'''
          <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">CORE OBJECTIVE</div>
          <div style="font-size:14px;color:#e2e2eb;font-weight:600;">{esc(topic)}</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:6px;">{len(sub_questions)} sub-questions decomposed</div>
        ''', height=100)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Sub-questions list
        if sub_questions:
            sq_html = '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">RESEARCH QUESTIONS</div>'
            for i, sq in enumerate(sub_questions):
                sq_html += f'''
                <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid rgba(0,242,255,0.05);">
                  <div style="min-width:24px;height:24px;border-radius:6px;background:rgba(0,242,255,0.1);
                    display:flex;align-items:center;justify-content:center;font-size:10px;color:#00f2ff;">?</div>
                  <div>
                    <div style="font-size:10px;color:#00f2ff;text-transform:uppercase;margin-bottom:2px;">Sub-Question {i+1:02d}</div>
                    <div style="font-size:12px;color:#e2e2eb;">{esc(sq[:80])}</div>
                  </div>
                </div>
                '''
            output_glass_card(sq_html, height=300)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Predicted Correlations
        if len(papers) >= 2 and critiques:
            corr_html = '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">PREDICTED CORRELATIONS</div>'
            paired = sorted(zip(papers, critiques), key=lambda x: safe_score(x[1].get("credibility_score", 0)), reverse=True)
            for p, c in paired[:3]:
                cred = safe_score(c.get("credibility_score", 0))
                corr_html += f'''
                <div style="margin:10px 0;padding-left:10px;border-left:2px solid #00f2ff;">
                  <div style="font-size:10px;color:#00f2ff;">{cred*10:.0f}% Confidence</div>
                  <div style="font-size:12px;color:#e2e2eb;font-weight:600;">{esc(p.get("title", "")[:40])}...</div>
                  <div style="font-size:10px;color:#64748b;margin-top:2px;">{esc(c.get("influence_type", "extension").capitalize())} research</div>
                </div>
                '''
            output_glass_card(corr_html, height=200)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Full reasoning button
        st.markdown('''
        <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.2);
          border-radius:8px;padding:14px;text-align:center;cursor:pointer;">
          <span style="font-size:10px;font-family:Manrope,sans-serif;color:#00f2ff;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;">
            Open Full Reasoning Chain
          </span>
        </div>
        ''', unsafe_allow_html=True)


render()
