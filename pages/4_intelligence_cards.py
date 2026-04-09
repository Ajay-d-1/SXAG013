"""
Page 4: Intelligence Cards — Paper Analysis Gallery.
Matches Stitch paper_gallery design with sorting, filtering, and detailed cards.
"""
import streamlit as st
from ui.css import inject_css
from ui.sidebar import render_sidebar
from ui.components import render_page_header, render_badge, safe_score, esc


def render():
    inject_css()
    render_sidebar()

    papers = st.session_state.get("papers", [])
    critiques = st.session_state.get("critiques", [])

    st.markdown(render_page_header(
        "Paper Analysis Gallery",
        "Deep intelligence cards for every analyzed paper" if papers else "Run an analysis to generate paper intelligence cards",
        show_badge=False
    ), unsafe_allow_html=True)

    if not papers:
        st.markdown('''
        <div style="text-align:center;padding:80px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#128196;</div>
          <div style="font-size:14px;color:#64748b;">No papers analyzed yet. Run a research analysis from the sidebar.</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Header Label
    st.markdown('''
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
      <div style="width:40px;height:2px;background:#00f2ff;"></div>
      <span style="font-size:11px;font-family:Manrope,sans-serif;color:#00f2ff;text-transform:uppercase;letter-spacing:0.12em;">Research Repository</span>
    </div>
    ''', unsafe_allow_html=True)

    # Controls Row
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
    with ctrl_col1:
        st.markdown(f'<div style="font-size:12px;color:#64748b;padding-top:8px;">Showing {len(papers)} papers</div>', unsafe_allow_html=True)
    with ctrl_col2:
        sort_by = st.selectbox("Sort by", ["Credibility", "Year", "Relevance"], label_visibility="collapsed", key="sort_papers")
    with ctrl_col3:
        filter_by = st.selectbox("Filter", ["All", "High (7+)", "Medium (4-6)", "Low (0-3)"], label_visibility="collapsed", key="filter_papers")

    # Sort & Filter
    paired = list(zip(papers, critiques))
    if sort_by == "Credibility":
        paired.sort(key=lambda x: safe_score(x[1].get("credibility_score", 0)), reverse=True)
    elif sort_by == "Year":
        paired.sort(key=lambda x: x[0].get("year", 0), reverse=True)
    elif sort_by == "Relevance":
        paired.sort(key=lambda x: safe_score(x[1].get("relevance_score", 0)), reverse=True)

    if filter_by == "High (7+)":
        paired = [(p, c) for p, c in paired if safe_score(c.get("credibility_score", 0)) >= 7]
    elif filter_by == "Medium (4-6)":
        paired = [(p, c) for p, c in paired if 4 <= safe_score(c.get("credibility_score", 0)) < 7]
    elif filter_by == "Low (0-3)":
        paired = [(p, c) for p, c in paired if safe_score(c.get("credibility_score", 0)) < 4]

    # Card Grid
    cols_per_row = 3
    for row_start in range(0, len(paired), cols_per_row):
        row_items = paired[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, (paper, critique) in enumerate(row_items):
            with cols[i]:
                _render_paper_card(paper, critique, row_start + i)

    # Footer
    st.markdown(f'''
    <div style="text-align:center;padding:40px 0 20px;">
      <span style="font-size:10px;font-family:Courier New,monospace;color:#3a494b;letter-spacing:0.15em;">
        SYSTEM ENTROPY: 0.00{len(papers) % 100:02d} | LATENT SPACE: OPTIMAL
      </span>
    </div>
    ''', unsafe_allow_html=True)


def _render_paper_card(paper, critique, index):
    """Render a single paper intelligence card matching Stitch paper_gallery design."""
    title = esc(paper.get("title", "Untitled"))
    year = paper.get("year", "?")
    source = esc(paper.get("source", "Unknown"))
    authors = paper.get("authors", [])
    author_str = esc(", ".join(authors[:2])) if authors else "Unknown Author"
    venue = esc(paper.get("venue", "") or "")

    cred = safe_score(critique.get("credibility_score", 0))
    rel = safe_score(critique.get("relevance_score", 5))
    influence = esc(critique.get("influence_type", "extension"))
    methodology = esc(critique.get("methodology_summary", ""))
    key_insight = esc(critique.get("key_insight", ""))
    red_flags = critique.get("red_flags", [])
    main_claims = critique.get("main_claims", [])
    boldness = esc(critique.get("boldness_vs_evidence", ""))
    repro = safe_score(critique.get("reproducibility_score", 0))

    # Colors & badge
    if cred >= 7:
        badge_color, badge_bg, gradient = "#10b981", "rgba(16,185,129,0.15)", "rgba(16,185,129,0.3)"
        cert_label = "HIGH"
    elif cred >= 4:
        badge_color, badge_bg, gradient = "#f59e0b", "rgba(245,158,11,0.15)", "rgba(245,158,11,0.3)"
        cert_label = "MED"
    else:
        badge_color, badge_bg, gradient = "#ef4444", "rgba(239,68,68,0.15)", "rgba(239,68,68,0.3)"
        cert_label = "LOW"
    cert_pct = int(cred * 10)

    # Red flag badges HTML
    flags_html = ""
    if red_flags:
        flags_html += '<div style="font-size:10px;font-family:Manrope,sans-serif;color:#ef4444;text-transform:uppercase;letter-spacing:0.08em;margin-top:12px;margin-bottom:6px;">RED FLAGS DETECTED</div>'
        for flag in red_flags[:3]:
            flags_html += f'<span style="font-size:9px;font-family:Manrope,sans-serif;color:#ef4444;background:rgba(239,68,68,0.12);padding:3px 8px;border-radius:4px;margin-right:4px;margin-bottom:4px;display:inline-block;text-transform:uppercase;letter-spacing:0.05em;">{esc(flag)}</span>'

    # Influence tags
    tags_html = ""
    if influence:
        tags_html += f'<span style="font-size:9px;font-family:Manrope,sans-serif;color:#94a3b8;background:rgba(255,255,255,0.05);padding:3px 8px;border-radius:4px;margin-right:4px;text-transform:uppercase;">{influence}</span>'

    # Paper ID
    paper_id = f"ID:RX-{year}-{index+1:03d}"

    trunc_title = title[:80] + ('...' if len(title) > 80 else '')
    trunc_meth = methodology[:150] + ('...' if len(methodology) > 150 else '')

    st.markdown(f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.1);
      border-radius:12px;overflow:hidden;transition:all 0.3s ease;margin-bottom:4px;position:relative;">
      <div style="height:3px;background:linear-gradient(90deg,{gradient},transparent);"></div>
      <div style="padding:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-size:10px;font-family:Courier New,monospace;color:#3a494b;">{paper_id}</span>
          <span style="font-size:10px;font-family:Manrope,sans-serif;color:{badge_color};background:{badge_bg};
            padding:3px 10px;border-radius:10px;font-weight:600;">{cert_pct}% {cert_label}</span>
        </div>
        <div style="font-family:Space Grotesk,sans-serif;font-size:15px;font-weight:600;color:#e2e2eb;
          line-height:1.3;margin-bottom:8px;">{trunc_title}</div>
        <div style="font-size:11px;color:#00f2ff;margin-bottom:12px;">{year} - {author_str}</div>
        <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Method Summary</div>
        <div style="font-size:12px;color:#94a3b8;line-height:1.5;margin-bottom:8px;">{trunc_meth}</div>
        {flags_html}
        <div style="display:flex;gap:4px;margin-top:14px;flex-wrap:wrap;">
          {tags_html}
        </div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # Expandable detail
    with st.expander(f"Full Analysis - {title[:40]}...", expanded=False):
        det_cols = st.columns(3)
        det_cols[0].metric("Credibility", f"{cred:.0f}/10")
        det_cols[1].metric("Relevance", f"{rel:.0f}/10")
        det_cols[2].metric("Reproducibility", f"{repro:.0f}/10")

        if key_insight:
            st.markdown(f"**Key Insight:** {key_insight}")
        if main_claims:
            st.markdown("**Main Claims:**")
            for claim in main_claims[:3]:
                st.markdown(f"- {esc(claim)}")
        if boldness:
            st.markdown(f"**Evidence vs Claims:** `{boldness}`")
        st.markdown(f"**Source:** {source} | **Venue:** {venue or 'N/A'}")


render()
