"""
Page 2: Knowledge Graph — Multiple interactive graph visualizations.
Includes: Main Knowledge Graph, Credibility Distribution, Timeline, Source Analysis, Methodology Heatmap.
"""
import streamlit as st
import os
from statistics import mean
from collections import Counter
from ui.css import inject_css
from ui.sidebar import render_sidebar
import streamlit.components.v1 as components
from ui.components import render_page_header, render_glass_card, render_section_header, safe_score, esc

def output_glass_card(html_content, height=None):
    """Output glass card using components.v1.html for reliable rendering."""
    card_html = render_glass_card(html_content)
    if height:
        components.html(card_html, height=height)
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def _build_credibility_chart(critiques):
    """Build a credibility distribution bar chart as HTML/SVG."""
    bucket_keys = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    buckets = {k: 0 for k in bucket_keys}
    for c in critiques:
        score = safe_score(c.get("credibility_score", 5))
        idx = min(int(score) // 2, 4)
        buckets[bucket_keys[idx]] += 1

    max_val = max(buckets.values(), default=1) or 1
    colors = ["#ef4444", "#f59e0b", "#f59e0b", "#10b981", "#00f2ff"]
    bars_html = ""
    for i, (key, count) in enumerate(buckets.items()):
        h = max(int(count / max_val * 160), 4)
        bars_html += f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
          <div style="font-size:10px;color:#e2e2eb;font-family:Manrope,sans-serif;">{count}</div>
          <div style="width:40px;height:{h}px;background:{colors[i]};border-radius:4px 4px 0 0;
            transition:height 0.5s ease;opacity:0.85;"></div>
          <div style="font-size:9px;color:#64748b;font-family:Manrope,sans-serif;">{key}</div>
        </div>
        '''
    return f'''
    <div style="padding:20px;">
      <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Credibility Distribution</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Score distribution across analyzed papers</div>
      <div style="display:flex;align-items:flex-end;justify-content:space-around;height:220px;padding-top:20px;">
        {bars_html}
      </div>
      <div style="text-align:center;font-size:10px;color:#64748b;margin-top:12px;font-family:Manrope,sans-serif;">CREDIBILITY SCORE RANGE</div>
    </div>
    '''


def _build_timeline_chart(papers):
    """Build a publication year timeline chart."""
    year_counts = Counter()
    for p in papers:
        y = p.get("year", 0)
        if y and y > 2000:
            year_counts[y] += 1

    if not year_counts:
        return '<div style="padding:20px;color:#64748b;">No year data available.</div>'

    sorted_years = sorted(year_counts.keys())
    max_count = max(year_counts.values(), default=1)

    bars_html = ""
    for year in sorted_years:
        count = year_counts[year]
        h = max(int(count / max_count * 140), 6)
        bars_html += f'''
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;">
          <div style="font-size:10px;color:#e2e2eb;">{count}</div>
          <div style="width:100%;max-width:50px;height:{h}px;background:linear-gradient(180deg,#00f2ff,#00dbe7);
            border-radius:4px 4px 0 0;opacity:0.8;"></div>
          <div style="font-size:9px;color:#64748b;transform:rotate(-45deg);white-space:nowrap;">{year}</div>
        </div>
        '''
    return f'''
    <div style="padding:20px;">
      <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Publication Timeline</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Papers analyzed by year</div>
      <div style="display:flex;align-items:flex-end;justify-content:space-around;height:220px;padding-top:20px;gap:4px;">
        {bars_html}
      </div>
    </div>
    '''


def _build_source_chart(papers):
    """Build a source distribution chart."""
    source_counts = Counter()
    for p in papers:
        src = p.get("source", "Unknown") or "Unknown"
        source_counts[src] += 1

    total = sum(source_counts.values()) or 1
    colors = {"OpenAlex": "#00f2ff", "CrossRef": "#8a2be2", "SemanticScholar": "#f59e0b",
              "S2": "#f59e0b", "Unknown": "#64748b"}

    items_html = ""
    for src, count in source_counts.most_common(5):
        pct = count / total * 100
        color = colors.get(src, "#64748b")
        items_html += f'''
        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;
          border-bottom:1px solid rgba(0,242,255,0.05);">
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:10px;height:10px;border-radius:50%;background:{color};"></div>
            <span style="font-size:12px;color:#e2e2eb;">{esc(src)}</span>
          </div>
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:80px;height:6px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;">
              <div style="height:100%;width:{pct}%;background:{color};border-radius:3px;"></div>
            </div>
            <span style="font-size:11px;color:#94a3b8;min-width:36px;text-align:right;">{count} ({pct:.0f}%)</span>
          </div>
        </div>
        '''
    return f'''
    <div style="padding:20px;">
      <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Source Distribution</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Where papers were fetched from</div>
      {items_html}
    </div>
    '''


def _build_influence_chart(critiques):
    """Build an influence type distribution chart."""
    type_counts = Counter()
    for c in critiques:
        inf = c.get("influence_type", "extension")
        type_counts[inf] += 1

    colors = {"foundational": "#00f2ff", "extension": "#3b82f6", "application": "#10b981",
              "survey": "#f59e0b", "contradiction": "#ef4444"}

    total = sum(type_counts.values()) or 1
    items_html = ""
    for inf_type, count in type_counts.most_common():
        pct = count / total * 100
        color = colors.get(inf_type, "#64748b")
        items_html += f'''
        <div style="display:flex;align-items:center;gap:12px;padding:8px 12px;
          background:rgba(25,27,34,0.5);border-radius:8px;margin:4px 0;">
          <div style="flex:1;">
            <div style="font-size:12px;color:#e2e2eb;text-transform:capitalize;">{esc(inf_type)}</div>
            <div style="width:100%;height:4px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:4px;">
              <div style="height:100%;width:{pct}%;background:{color};border-radius:2px;"></div>
            </div>
          </div>
          <span style="font-size:11px;color:#94a3b8;">{count}</span>
        </div>
        '''
    return f'''
    <div style="padding:20px;">
      <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Influence Type Analysis</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:16px;">How papers contribute to the field</div>
      {items_html}
    </div>
    '''


def _build_methodology_matrix(critiques):
    """Build a methodology quality radar/matrix view."""
    if not critiques:
        return '<div style="padding:20px;color:#64748b;">No critique data available.</div>'

    repro_scores = []
    boldness_map = {"appropriate": 10, "conservative": 8, "overclaimed": 3}
    boldness_scores = []
    dataset_map = {"real": 10, "mixed": 6, "synthetic": 3, "not mentioned": 1}
    dataset_scores = []

    for c in critiques:
        repro_scores.append(safe_score(c.get("reproducibility_score", 5)))
        boldness_scores.append(boldness_map.get(str(c.get("boldness_vs_evidence", "")).lower(), 5))
        dataset_scores.append(dataset_map.get(str(c.get("dataset_type", "")).lower().strip(), 3))

    metrics = [
        ("Reproducibility", mean(repro_scores) if repro_scores else 5, "#00f2ff"),
        ("Evidence Quality", mean(boldness_scores) if boldness_scores else 5, "#10b981"),
        ("Dataset Rigor", mean(dataset_scores) if dataset_scores else 5, "#8a2be2"),
        ("Avg Credibility", mean([safe_score(c.get("credibility_score", 5)) for c in critiques]), "#f59e0b"),
    ]

    bars_html = ""
    for label, val, color in metrics:
        w = val / 10 * 100
        bars_html += f'''
        <div style="margin:10px 0;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:11px;color:#94a3b8;">{label}</span>
            <span style="font-size:11px;color:{color};font-weight:600;">{val:.1f}/10</span>
          </div>
          <div style="width:100%;height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
            <div style="height:100%;width:{w}%;background:linear-gradient(90deg,{color},{color}88);border-radius:4px;transition:width 0.8s ease;"></div>
          </div>
        </div>
        '''
    return f'''
    <div style="padding:20px;">
      <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Methodology Quality Matrix</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Average scores across all papers</div>
      {bars_html}
    </div>
    '''


def render():
    inject_css()
    render_sidebar()

    papers = st.session_state.get("papers", [])
    critiques = st.session_state.get("critiques", [])
    contradictions = st.session_state.get("contradictions", [])
    graph_path = st.session_state.get("graph_path", "")

    st.markdown(render_page_header(
        "Research Intelligence Map",
        "Live structure of knowledge and conflict" if papers else "Run an analysis to generate knowledge graphs",
        show_badge=False
    ), unsafe_allow_html=True)

    if not papers:
        st.markdown('''
        <div style="text-align:center;padding:80px 0;">
          <div style="font-size:48px;margin-bottom:16px;">&#128376;</div>
          <div style="font-size:14px;color:#64748b;">No data yet. Run a research analysis from the sidebar to generate interactive knowledge graphs.</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    # Subtitle Stats
    st.markdown(f'''
    <div style="display:flex;gap:20px;justify-content:center;margin-bottom:24px;">
      <span style="font-size:11px;color:#64748b;font-family:Manrope,sans-serif;">LIVE STRUCTURE OF KNOWLEDGE AND CONFLICT</span>
      <span style="font-size:11px;color:#00f2ff;">{len(papers)} Nodes</span>
      <span style="font-size:11px;color:#ef4444;">{len(contradictions)} Conflicts</span>
    </div>
    ''', unsafe_allow_html=True)

    # GRAPH SELECTOR TABS
    graph_tabs = st.tabs(["Knowledge Graph", "Credibility", "Timeline", "Sources", "Influence Types", "Methodology"])

    with graph_tabs[0]:
        if graph_path and os.path.exists(graph_path):
            left, right = st.columns([3, 1])
            with left:
                with open(graph_path, "r", encoding="utf-8") as f:
                    html = f.read()
                st.components.v1.html(html, height=600, scrolling=False)
            with right:
                insights = st.session_state.get("graph_insights", {})

                output_glass_card(f'''
                  <div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px;">Graph Statistics</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div style="background:rgba(25,27,34,0.5);border-radius:6px;padding:10px;text-align:center;">
                      <div style="font-size:10px;color:#64748b;text-transform:uppercase;">Nodes</div>
                      <div style="font-size:20px;font-family:Space Grotesk,sans-serif;color:#00f2ff;font-weight:700;">{len(papers)}</div>
                    </div>
                    <div style="background:rgba(25,27,34,0.5);border-radius:6px;padding:10px;text-align:center;">
                      <div style="font-size:10px;color:#64748b;text-transform:uppercase;">Conflicts</div>
                      <div style="font-size:20px;font-family:Space Grotesk,sans-serif;color:#ef4444;font-weight:700;">{len(contradictions)}</div>
                    </div>
                  </div>
                ''', height=120)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                top_papers = insights.get("top_papers", [])
                if top_papers:
                    tp_html = '<div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">Top Papers by Credibility</div>'
                    for tp in top_papers[:4]:
                        cred = tp.get("credibility", 0)
                        c_color = "#10b981" if cred >= 7 else "#f59e0b" if cred >= 4 else "#ef4444"
                        t_title = esc(tp.get("title", "")[:45])
                        tp_html += f'''
                        <div style="padding:8px 0;border-bottom:1px solid rgba(0,242,255,0.05);">
                          <div style="font-size:12px;color:#e2e2eb;">{t_title}...</div>
                          <div style="display:flex;justify-content:space-between;margin-top:4px;">
                            <span style="font-size:10px;color:#64748b;">{tp.get("year", "?")}</span>
                            <span style="font-size:10px;color:{c_color};font-weight:600;">&#9733; {cred}/10</span>
                          </div>
                        </div>
                        '''
                    output_glass_card(tp_html, height=250)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                narrative = insights.get("narrative", "")
                if narrative:
                    output_glass_card(f'''
                      <div style="font-size:10px;font-family:Manrope,sans-serif;color:#64748b;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;">AI Narrative</div>
                      <div style="font-size:12px;color:#94a3b8;line-height:1.6;font-style:italic;">{esc(narrative)}</div>
                    ''', height=120)
        else:
            st.info("Knowledge graph file not found. Run analysis to generate.")

    with graph_tabs[1]:
        output_glass_card(_build_credibility_chart(critiques), height=300)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        sorted_critiques = sorted(zip(papers, critiques), key=lambda x: safe_score(x[1].get("credibility_score", 0)), reverse=True)
        rows_html = ""
        for p, c in sorted_critiques[:10]:
            score = safe_score(c.get("credibility_score", 0))
            color = "#10b981" if score >= 7 else "#f59e0b" if score >= 4 else "#ef4444"
            w = score / 10 * 100
            rows_html += f'''
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid rgba(0,242,255,0.04);">
              <div style="flex:1;font-size:12px;color:#e2e2eb;">{esc(p.get("title", "")[:50])}...</div>
              <div style="width:80px;height:5px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;">
                <div style="height:100%;width:{w}%;background:{color};border-radius:3px;"></div>
              </div>
              <span style="font-size:12px;color:{color};font-weight:600;min-width:30px;text-align:right;">{score:.0f}</span>
            </div>
            '''
        if rows_html:
            output_glass_card(f'''
              <div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#e2e2eb;margin-bottom:6px;">Paper Credibility Ranking</div>
              <div style="font-size:12px;color:#64748b;margin-bottom:16px;">Top papers by credibility score</div>
              {rows_html}
            ''', height=350)

    with graph_tabs[2]:
        output_glass_card(_build_timeline_chart(papers), height=300)

    with graph_tabs[3]:
        output_glass_card(_build_source_chart(papers), height=300)

    with graph_tabs[4]:
        output_glass_card(_build_influence_chart(critiques), height=300)

    with graph_tabs[5]:
        output_glass_card(_build_methodology_matrix(critiques), height=300)


render()
