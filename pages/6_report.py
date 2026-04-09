"""
Page 6: Full Report — IEEE-format Literature Intelligence Report.
Includes PDF + Markdown download.
"""
import streamlit as st
from datetime import datetime
from ui.css import inject_css
from ui.sidebar import render_sidebar
import streamlit.components.v1 as components
from ui.components import (
    render_page_header, render_glass_card, render_confidence_ring, safe_score, esc
)

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

    results = st.session_state.get("results", {})
    papers = st.session_state.get("papers", [])
    critiques = st.session_state.get("critiques", [])
    contradictions = st.session_state.get("contradictions", [])
    topic = st.session_state.get("current_topic", "")
    mode = st.session_state.get("current_mode", "fast")
    confidence = st.session_state.get("confidence", 0)
    session_id = results.get("session_id", "0000") if results else "0000"

    if not results or not papers:
        st.markdown(render_page_header("Literature Intelligence Report",
            "Run an analysis to generate a publication-grade report", show_badge=False), unsafe_allow_html=True)
        st.markdown('''
        <div style="text-align:center;padding:80px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#128203;</div>
          <div style="font-size:14px;color:#64748b;">No report data yet. Run a research analysis from the sidebar.</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    # REPORT HEADER
    today = datetime.now().strftime("%B %d, %Y")
    avg_cred = results.get("avg_credibility", 0)
    if isinstance(avg_cred, str):
        avg_cred = safe_score(avg_cred)
    intel_score = avg_cred * 10 if avg_cred <= 10 else avg_cred

    st.markdown(f'''
    <div style="backdrop-filter:blur(20px);background:rgba(25,27,34,0.7);border:0.5px solid rgba(0,242,255,0.2);
      border-radius:16px;padding:32px;margin-bottom:24px;position:relative;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
        <span style="font-size:10px;font-family:Courier New,monospace;color:#00f2ff;background:rgba(0,242,255,0.08);
          padding:3px 10px;border-radius:4px;border:0.5px solid rgba(0,242,255,0.2);">REF: SP-{esc(str(session_id))}</span>
        <span style="font-size:11px;color:#64748b;">{today}</span>
      </div>
      <h1 style="font-family:Space Grotesk,sans-serif;font-size:30px;font-weight:700;color:#e2e2eb;margin:0 0 8px;">
        Literature Intelligence Report
      </h1>
      <div style="font-size:14px;color:#94a3b8;margin-bottom:20px;">
        A cinematic multi-modal synthesis of research on <b style="color:#00f2ff;">{esc(topic)}</b>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    # Download Buttons & Intelligence Score
    btn_col, score_col = st.columns([2, 1])
    with btn_col:
        b1, b2 = st.columns(2)
        md_content = _generate_markdown(topic, results, papers, critiques, contradictions, confidence, session_id, today)
        with b1:
            st.download_button("Download Report (.md)", md_content, f"scholar_pulse_report_{session_id}.md", "text/markdown", use_container_width=True)
        with b2:
            try:
                pdf_bytes = _generate_pdf(topic, results, papers, critiques, contradictions, confidence, session_id, today)
                st.download_button("Download PDF", pdf_bytes, f"scholar_pulse_report_{session_id}.pdf", "application/pdf", use_container_width=True)
            except Exception:
                st.button("PDF (install fpdf2)", disabled=True, use_container_width=True)

    with score_col:
        output_glass_card(f'''
          <div style="text-align:center;">
            <div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;">Intelligence Score</div>
            <div style="font-size:32px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#00f2ff;">{intel_score:.1f}<span style="font-size:16px;color:#64748b;">/100</span></div>
            <div style="font-size:10px;color:#64748b;margin-top:4px;">High data density and source reliability</div>
          </div>
        ''', height=120)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # SECTION 1: EXECUTIVE SUMMARY
    summary = esc(results.get("executive_summary", "Analysis complete."))
    output_glass_card(f'''
      <div style="position:relative;margin-bottom:20px;">
        <h2 style="font-family:Space Grotesk,sans-serif;font-size:22px;font-weight:700;color:#e2e2eb;display:flex;align-items:center;gap:10px;margin:0;">
          <span style="width:8px;height:8px;border-radius:50%;background:#00f2ff;box-shadow:0 0 8px #00f2ff;display:inline-block;"></span>
          Executive Summary
        </h2>
      </div>
      <div style="font-size:15px;color:#cbd5e1;line-height:1.8;font-family:Inter,sans-serif;">{summary}</div>
    ''', height=200)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # SECTION 2: FIELD SNAPSHOT
    field_snapshot = results.get("field_snapshot", {})
    momentum = results.get("field_momentum", field_snapshot.get("trend", "stable"))
    key_insight = esc(results.get("key_insight", ""))

    snap_left, snap_right = st.columns([3, 2])

    with snap_left:
        output_glass_card(f'''
          <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Field Snapshot</div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px;">
            <div style="background:rgba(25,27,34,0.5);border-radius:8px;padding:14px;text-align:center;">
              <div style="font-size:10px;color:#64748b;text-transform:uppercase;margin-bottom:4px;">Papers Analyzed</div>
              <div style="font-size:22px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;">{len(papers)}</div>
              <div style="font-size:10px;color:#00f2ff;">{mode.upper()} Mode</div>
            </div>
            <div style="background:rgba(25,27,34,0.5);border-radius:8px;padding:14px;text-align:center;">
              <div style="font-size:10px;color:#64748b;text-transform:uppercase;margin-bottom:4px;">Contradictions</div>
              <div style="font-size:22px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;">{len(contradictions)}</div>
              <div style="font-size:10px;color:#ef4444;">Detected</div>
            </div>
            <div style="background:rgba(25,27,34,0.5);border-radius:8px;padding:14px;text-align:center;">
              <div style="font-size:10px;color:#64748b;text-transform:uppercase;margin-bottom:4px;">Avg Credibility</div>
              <div style="font-size:22px;font-family:Space Grotesk,sans-serif;font-weight:700;color:#e2e2eb;">{avg_cred:.1f}</div>
              <div style="font-size:10px;color:#10b981;">/ 10</div>
            </div>
          </div>
        ''', height=180)

    with snap_right:
        output_glass_card(f'''
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <span style="font-size:16px;">&#128161;</span>
            <span style="font-size:11px;font-family:Manrope,sans-serif;color:#f59e0b;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Key Insights</span>
          </div>
          <div style="font-size:13px;color:#e2e2eb;line-height:1.7;">{key_insight or "No key insight available."}</div>
          <div style="font-size:12px;color:#94a3b8;margin-top:12px;font-style:italic;">Field momentum: <b style="color:#00f2ff;">{esc(momentum.capitalize())}</b></div>
        ''', height=180)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # SECTION 3: CONTRADICTIONS & GAPS
    if contradictions:
        contr_left, gaps_right = st.columns(2)
        with contr_left:
            contr_html = f'<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Contradictions ({len(contradictions)} detected)</div>'
            for c in contradictions[:4]:
                sev = c.get("severity", "low")
                sev_color = "#ef4444" if sev == "high" else "#f59e0b" if sev == "medium" else "#64748b"
                contr_html += f'''
                <div style="background:rgba(239,68,68,0.04);border-radius:8px;padding:14px;margin:8px 0;border-left:2px solid {sev_color};">
                  <div style="font-size:13px;font-family:Space Grotesk,sans-serif;font-weight:600;color:#e2e2eb;margin-bottom:4px;">
                    {esc(c.get("paper_a_title", "")[:40])} vs. {esc(c.get("paper_b_title", "")[:40])}
                  </div>
                  <div style="font-size:11px;color:#94a3b8;">{esc(c.get("explanation", ""))}</div>
                </div>
                '''
            output_glass_card(contr_html, height=300)

        with gaps_right:
            gaps = results.get("gaps", [])
            gaps_html = '<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Research Gaps</div>'
            if gaps:
                for g in gaps[:4]:
                    opp = g.get("opportunity_score", 5)
                    gaps_html += f'''
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(0,242,255,0.05);">
                      <div style="font-size:12px;color:#e2e2eb;">{esc(g.get("area", ""))}</div>
                      <span style="font-size:10px;font-family:Manrope,sans-serif;color:{"#ef4444" if opp >= 8 else "#f59e0b"};text-transform:uppercase;">
                        {"CRITICAL" if opp >= 8 else "MODERATE" if opp >= 5 else "LOW"}
                      </span>
                    </div>
                    '''
            else:
                gaps_html += '<div style="font-size:12px;color:#64748b;">No specific gaps identified.</div>'
            output_glass_card(gaps_html, height=250)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # SECTION 4: PAPER VERDICTS
    paper_verdicts = results.get("paper_verdicts", [])
    if paper_verdicts:
        st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Paper Verdicts</div>', unsafe_allow_html=True)
        for i in range(0, min(len(paper_verdicts), 6), 3):
            cols = st.columns(3)
            for j, pv in enumerate(paper_verdicts[i:i+3]):
                with cols[j]:
                    verdict = pv.get("verdict", "moderate")
                    v_color = "#10b981" if verdict == "strong" else "#f59e0b" if verdict == "moderate" else "#ef4444"
                    output_glass_card(f'''
                      <div style="font-size:10px;color:{v_color};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;font-family:Manrope,sans-serif;">{esc(verdict)}</div>
                      <div style="font-size:13px;color:#e2e2eb;font-weight:600;margin-bottom:6px;">{esc(pv.get("title", "")[:50])}...</div>
                      <div style="font-size:11px;color:#94a3b8;line-height:1.5;">{esc(pv.get("one_liner", ""))}</div>
                    ''', height=120)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # SECTION 5: FUTURE DIRECTIONS & OPEN QUESTIONS
    frontiers = results.get("frontier_directions", [])
    open_qs = results.get("open_questions", [])

    if frontiers or open_qs:
        fut_left, fut_right = st.columns(2)
        with fut_left:
            if frontiers:
                front_html = '<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Future Directions</div>'
                for f in frontiers[:3]:
                    impact = f.get("impact_score", 5)
                    front_html += f'''
                    <div style="margin:10px 0;padding:14px;background:rgba(25,27,34,0.5);border-radius:8px;border-left:2px solid #00f2ff;">
                      <div style="font-size:13px;font-family:Space Grotesk,sans-serif;font-weight:600;color:#e2e2eb;">{esc(f.get("direction", ""))}</div>
                      <div style="font-size:11px;color:#94a3b8;margin-top:4px;">{esc(f.get("rationale", ""))}</div>
                      <div style="font-size:10px;color:#00f2ff;margin-top:6px;">Impact: {impact}/10 | Difficulty: {esc(f.get("difficulty", "medium"))}</div>
                    </div>
                    '''
                output_glass_card(front_html, height=300)
        with fut_right:
            if open_qs:
                oq_html = '<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:16px;">Open Questions</div>'
                for q in open_qs[:5]:
                    oq_html += f'<div style="font-size:12px;color:#94a3b8;padding:8px 0;border-bottom:1px solid rgba(0,242,255,0.04);">&#8226; {esc(q)}</div>'
                output_glass_card(oq_html, height=250)

    # FOOTER
    st.markdown(f'''
    <div style="text-align:center;padding:40px 0 20px;border-top:1px solid rgba(0,242,255,0.05);margin-top:40px;">
      <div style="font-size:10px;color:#3a494b;text-transform:uppercase;letter-spacing:0.15em;">
        Generated by ScholAR Pulse AI - {mode.upper()} Mode - {today}
      </div>
    </div>
    ''', unsafe_allow_html=True)


def _generate_markdown(topic, results, papers, critiques, contradictions, confidence, session_id, date):
    """Generate a full IEEE-format markdown report."""
    md = f"# Literature Intelligence Report: {topic}\n\n"
    md += f"**Report ID:** SP-{session_id} | **Date:** {date} | **Confidence:** {confidence:.0%}\n\n---\n\n"
    md += f"## Abstract\n\n{results.get('executive_summary', 'N/A')}\n\n"
    md += f"## Key Insight\n\n{results.get('key_insight', 'N/A')}\n\n"
    md += f"## Methodology Assessment\n\n{results.get('methodology_verdict', 'N/A')}\n\n"
    md += f"**Field Momentum:** {results.get('field_momentum', 'stable').capitalize()}\n\n"
    md += f"## Paper Analysis ({len(papers)} papers)\n\n"
    md += "| # | Title | Year | Credibility | Relevance | Influence |\n"
    md += "|---|-------|------|-------------|-----------|----------|\n"
    for i, (p, c) in enumerate(zip(papers, critiques), 1):
        cred = safe_score(c.get("credibility_score", 0))
        rel = safe_score(c.get("relevance_score", 0))
        md += f"| {i} | {p.get('title', '')[:60]} | {p.get('year', '?')} | {cred:.0f}/10 | {rel:.0f}/10 | {c.get('influence_type', '?')} |\n"
    md += "\n"
    if contradictions:
        md += f"## Contradictions ({len(contradictions)} detected)\n\n"
        for c in contradictions:
            md += f"### [{c.get('severity', '?').upper()}] {c.get('paper_a_title', '')} vs {c.get('paper_b_title', '')}\n"
            md += f"- **Claim A:** {c.get('claim_a', '')}\n- **Claim B:** {c.get('claim_b', '')}\n"
            md += f"- **Explanation:** {c.get('explanation', '')}\n\n"
    gaps = results.get("gaps", [])
    if gaps:
        md += "## Research Gaps\n\n"
        for g in gaps:
            md += f"### {g.get('area', 'Gap')} (Opportunity: {g.get('opportunity_score', '?')}/10)\n{g.get('description', '')}\n\n"
    frontiers = results.get("frontier_directions", [])
    if frontiers:
        md += "## Future Directions\n\n"
        for f in frontiers:
            md += f"### {f.get('direction', '')} (Impact: {f.get('impact_score', '?')}/10)\n{f.get('rationale', '')}\n\n"
    md += "## References\n\n"
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:3]) or "Unknown"
        md += f"[{i}] {authors}. \"{p.get('title', '')}\". {p.get('venue', '') or 'N/A'}, {p.get('year', '?')}.\n\n"
    md += f"\n---\n*Generated by ScholAR Pulse AI on {date}*\n"
    return md


def _generate_pdf(topic, results, papers, critiques, contradictions, confidence, session_id, date):
    """Generate a PDF report using fpdf2."""
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Literature Intelligence Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, topic, ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Report ID: SP-{session_id} | Date: {date} | Confidence: {confidence:.0%}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, results.get("executive_summary", "N/A"))
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Key Insight", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, results.get("key_insight", "N/A"))
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Analyzed Papers ({len(papers)})", ln=True)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(8, 6, "#", 1); pdf.cell(90, 6, "Title", 1); pdf.cell(15, 6, "Year", 1)
    pdf.cell(20, 6, "Cred.", 1); pdf.cell(20, 6, "Rel.", 1); pdf.cell(30, 6, "Type", 1); pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    for i, (p, c) in enumerate(zip(papers[:20], critiques[:20]), 1):
        pdf.cell(8, 5, str(i), 1)
        pdf.cell(90, 5, p.get("title", "")[:55], 1)
        pdf.cell(15, 5, str(p.get("year", "?")), 1)
        pdf.cell(20, 5, f"{safe_score(c.get('credibility_score', 0)):.0f}/10", 1)
        pdf.cell(20, 5, f"{safe_score(c.get('relevance_score', 0)):.0f}/10", 1)
        pdf.cell(30, 5, c.get("influence_type", "?")[:12], 1); pdf.ln()
    pdf.ln(5)
    if contradictions:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Contradictions ({len(contradictions)})", ln=True)
        for c in contradictions[:5]:
            pdf.set_font("Helvetica", "B", 9)
            pdf.multi_cell(0, 5, f"[{c.get('severity', '?').upper()}] {c.get('paper_a_title', '')[:40]} vs {c.get('paper_b_title', '')[:40]}")
            pdf.set_font("Helvetica", "", 8)
            pdf.multi_cell(0, 4, c.get("explanation", "")); pdf.ln(3)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "References", ln=True)
    pdf.set_font("Helvetica", "", 8)
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:3]) or "Unknown"
        ref = f'[{i}] {authors}. "{p.get("title", "")[:70]}". {p.get("venue", "") or "N/A"}, {p.get("year", "?")}.'
        pdf.multi_cell(0, 4, ref); pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8); pdf.ln(10)
    pdf.cell(0, 5, f"Generated by ScholAR Pulse AI on {date}", ln=True, align="C")
    return pdf.output()


render()
