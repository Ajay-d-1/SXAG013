import streamlit as st
import json
import os
from core.loop import ResearchLoop
from agents.archivist import ArchivistAgent
from agents.cartographer import CartographerAgent

st.set_page_config(page_title="ScholAR Pulse", page_icon="🔬", layout="wide")

# ─────────────────────── PREMIUM CSS ───────────────────────
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
.stApp { background: #0b0f19; }
div[data-testid="stSidebar"] { background: linear-gradient(180deg, #06080d 0%, #0d1117 100%); border-right: 1px solid rgba(255,255,255,0.04); }
header[data-testid="stHeader"] { background: transparent !important; }

/* Hero Section */
.hero-badge {
    display: inline-block; background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2));
    border: 1px solid rgba(139,92,246,0.3); border-radius: 20px; padding: 4px 14px;
    font-size: 0.8rem; color: #a78bfa; margin-bottom: 8px;
}
.hero-title {
    font-size: 2.8rem; font-weight: 700; margin: 0;
    background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}
.hero-sub { color: #64748b; font-size: 1.05rem; margin-top: 4px; }

/* Metric Cards */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin: 16px 0; }
.metric-card {
    background: rgba(30, 35, 45, 0.5); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 18px;
    text-align: center; transition: all 0.25s;
}
.metric-card:hover { border-color: rgba(99,102,241,0.4); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.metric-value { font-size: 1.7rem; font-weight: 700; color: #f8fafc; }
.metric-label { font-size: 0.8rem; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

/* Flashcard Grid */
.fc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; margin: 12px 0; }
.fc-card {
    background: rgba(30, 35, 45, 0.55); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 16px;
    padding: 22px; transition: all 0.3s; position: relative; overflow: hidden;
}
.fc-card:hover { border-color: rgba(56, 189, 248, 0.4); transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,0.35); }
.fc-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: 16px 16px 0 0;
}
.fc-card.cred-high::before { background: linear-gradient(90deg, #10b981, #34d399); }
.fc-card.cred-med::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.fc-card.cred-low::before { background: linear-gradient(90deg, #ef4444, #f87171); }
.fc-title { font-weight: 600; font-size: 1rem; color: #f1f5f9; margin-bottom: 6px; line-height: 1.3; }
.fc-meta { font-size: 0.82rem; color: #64748b; margin-bottom: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
.fc-badge {
    display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem;
    font-weight: 500;
}
.badge-green { background: rgba(16,185,129,0.15); color: #34d399; }
.badge-yellow { background: rgba(245,158,11,0.15); color: #fbbf24; }
.badge-red { background: rgba(239,68,68,0.15); color: #f87171; }
.badge-blue { background: rgba(56,189,248,0.15); color: #38bdf8; }
.badge-purple { background: rgba(139,92,246,0.15); color: #a78bfa; }
.fc-insight { font-style: italic; color: #94a3b8; font-size: 0.88rem; margin: 10px 0; border-left: 3px solid #6366f1; padding-left: 10px; }
.fc-section { margin-top: 10px; font-size: 0.88rem; color: #cbd5e1; }
.fc-section b { color: #94a3b8; }
.fc-flag { color: #f87171; font-size: 0.82rem; margin-top: 4px; }

/* Report Sections */
.report-section {
    background: rgba(30,35,45,0.4); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 22px; margin: 12px 0;
}
.report-section h3 { color: #e2e8f0; margin-bottom: 8px; }

/* Contradiction Card */
.contradiction-card {
    background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.2);
    border-radius: 14px; padding: 20px; margin: 12px 0;
}

/* Source Badges */
.source-badge {
    display: inline-block; padding: 1px 6px; border-radius: 4px;
    font-size: 0.7rem; font-weight: 500;
}
</style>
''', unsafe_allow_html=True)


# ─────────────────────── SIDEBAR ───────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0;">
        <div style="font-size:2.4rem;">🔬</div>
        <div style="font-size:1.4rem; font-weight:700; color:#f8fafc; margin-top:4px;">ScholAR Pulse</div>
        <div style="font-size:0.85rem; color:#64748b;">Autonomous Research Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.expander("🏗️ How it works", expanded=False):
        st.markdown("""
        **1. 🧠 Planner** — Decomposes topic into 5 research sub-questions

        **2. 📡 Multi-Source Fetch** — Papers from OpenAlex, CrossRef & Semantic Scholar

        **3. 🔍 Skeptic** — AI critiques methodology, scores credibility & relevance

        **4. ⚔️ Contradiction Engine** — Detects conflicting claims across papers

        **5. 📊 Cartographer** — Builds interactive knowledge graph & mind map

        **6. ✍️ Archivist** — Generates publication-grade research reports
        """)

    st.divider()
    st.markdown("##### 📂 Recent Sessions")
    try:
        archivist = ArchivistAgent()
        cursor = archivist.conn.execute("SELECT topic, confidence, depth, mode, created_at FROM sessions ORDER BY created_at DESC LIMIT 5")
        sessions = cursor.fetchall()
        if sessions:
            for s in sessions:
                mode_icon = "⚡" if s[3] == "fast" else "🔬"
                st.caption(f"{mode_icon} **{s[0]}** — {s[1]:.0%} conf. | depth {s[2]}")
        else:
            st.caption("No sessions yet. Run your first analysis!")
    except Exception:
        st.caption("No history available.")

    st.divider()
    st.markdown("""
    <div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2); border-radius:10px; padding:12px; font-size:0.85rem; color:#a78bfa;">
        💡 <b>Tip:</b> Deep Mode runs 4 depth iterations and generates a publication-grade literature review. Fast Mode gives a quick intelligence briefing.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────── SESSION STATE ───────────────────────
defaults = {
    "results": None, "mode": None, "graph_path": None, "mindmap_path": None,
    "is_running": False, "papers": [], "critiques": [], "contradictions": [],
    "planner_output": {}, "report": None, "topic_input": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─────────────────────── HERO / INPUT ───────────────────────
if not st.session_state.results and not st.session_state.is_running:
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
        <div class="hero-badge">✨ Multi-Source AI Research Agent</div>
        <div class="hero-title">ScholAR Pulse</div>
        <div class="hero-sub">Enter any research topic. AI fetches papers from OpenAlex, CrossRef & Semantic Scholar,<br/>critiques methodology, detects contradictions, and generates research intelligence.</div>
    </div>
    """, unsafe_allow_html=True)

topic = st.text_input(
    "🔍 Research Topic",
    placeholder="e.g. transformer attention mechanisms, CRISPR gene editing, renewable energy storage...",
    label_visibility="collapsed" if not st.session_state.results else "visible"
)

if not st.session_state.results and not st.session_state.is_running:
    col_fast, col_deep = st.columns(2)
    with col_fast:
        fast_btn = st.button("⚡ Fast Mode", use_container_width=True, type="primary",
                             help="Quick 2-depth scan, AI-powered briefing")
    with col_deep:
        deep_btn = st.button("🔬 Deep Mode", use_container_width=True,
                             help="4-depth comprehensive scan, publication-grade report")
else:
    col_fast, col_deep = st.columns(2)
    with col_fast:
        fast_btn = st.button("⚡ Fast Mode", use_container_width=True, type="primary")
    with col_deep:
        deep_btn = st.button("🔬 Deep Mode", use_container_width=True)


# ─────────────────────── HANDLE BUTTON CLICKS ───────────────────────
if fast_btn or deep_btn:
    if not topic:
        st.error("Please enter a research topic first.")
    else:
        st.session_state.is_running = True
        st.session_state.mode = "fast" if fast_btn else "deep"
        st.session_state.results = None
        st.session_state.papers = []
        st.session_state.critiques = []
        st.session_state.contradictions = []
        st.session_state.mindmap_path = None
        st.session_state.topic_input = topic
        st.rerun()


# ─────────────────────── PROGRESS DISPLAY ───────────────────────
if st.session_state.is_running:
    run_topic = st.session_state.topic_input or topic
    mode_label = "⚡ Fast Mode" if st.session_state.mode == "fast" else "🔬 Deep Mode"
    st.markdown(f"### {mode_label} — Analyzing: *{run_topic}*")

    status_container = st.empty()
    progress_bar = st.progress(0)

    try:
        loop = ResearchLoop(run_topic, st.session_state.mode)
        messages = []
        step_count = 0

        def callback(msg, confidence, depth):
            global step_count
            messages.append(msg)
            # Estimate progress
            max_depth = loop.max_depth
            total_est = max_depth * 3 + 3
            step = len(messages)
            pct = min(step / total_est, 0.99)
            progress_bar.progress(pct)
            with status_container.container():
                for m in messages[-6:]:
                    if "🚨" in m:
                        st.warning(m)
                    elif "✅" in m or "🎯" in m:
                        st.success(m)
                    elif "⚠️" in m:
                        st.warning(m)
                    else:
                        st.info(m)

        results = loop.run(progress_callback=callback)
        progress_bar.progress(1.0)

        # Store everything
        st.session_state.results = results
        st.session_state.graph_path = results.get("graph_path")
        st.session_state.papers = loop.all_papers
        st.session_state.critiques = loop.all_critiques
        st.session_state.contradictions = loop.all_contradictions
        st.session_state.planner_output = {"sub_questions": loop.sub_questions}
        if st.session_state.mode == "deep":
            st.session_state.report = results

        # Build mind map
        if st.session_state.papers and st.session_state.critiques:
            sqs = loop.sub_questions
            if sqs:
                carto = CartographerAgent()
                st.session_state.mindmap_path = carto.build_mindmap(
                    run_topic, sqs, st.session_state.papers, st.session_state.critiques
                )

        st.session_state.is_running = False
        st.rerun()

    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.session_state.is_running = False


# ─────────────────── HELPER FUNCTIONS ───────────────────
def safe_score(val, default=5):
    if isinstance(val, str):
        try:
            return int(val.split("/")[0])
        except (ValueError, IndexError):
            return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# ─────────────────────── RESULTS DISPLAY ───────────────────────
if st.session_state.results and not st.session_state.is_running:
    results = st.session_state.results
    mode = st.session_state.mode
    papers = st.session_state.papers
    critiques = st.session_state.critiques
    contradictions = st.session_state.contradictions
    run_topic = st.session_state.topic_input or topic

    # ── Metrics Bar ──
    avg_cred = 0
    if critiques:
        scores = [safe_score(c.get("credibility_score", 5)) for c in critiques]
        avg_cred = sum(scores) / len(scores)

    sources = set(p.get("source", "?") for p in papers)
    source_str = " + ".join(sources) if sources else "Multi-source"

    metrics_html = f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{len(papers)}</div>
            <div class="metric-label">📄 Papers Analyzed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(contradictions)}</div>
            <div class="metric-label">⚔️ Contradictions</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{results.get('confidence', 0):.0%}</div>
            <div class="metric-label">🎯 Confidence</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{avg_cred:.1f}</div>
            <div class="metric-label">⭐ Avg Credibility</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)

    # ── Main Tabs ──
    tab_overview, tab_graph, tab_mindmap, tab_cards, tab_report = st.tabs([
        "📋 Overview", "🕸️ Knowledge Graph", "🧠 Mind Map", "🃏 Paper Cards", "📄 Full Report"
    ])

    # ════════════ TAB 1: OVERVIEW ════════════
    with tab_overview:
        # Executive Summary
        exec_summary = results.get("executive_summary", "")
        if exec_summary:
            st.markdown(f"""
            <div class="report-section">
                <h3>📋 Executive Summary</h3>
                <p style="color:#cbd5e1; font-size:0.95rem; line-height:1.6;">{exec_summary}</p>
            </div>
            """, unsafe_allow_html=True)

        # Key Insight
        key_insight = results.get("key_insight", "")
        if key_insight:
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2); border-radius:12px; padding:16px; margin:12px 0;">
                <span style="font-size:1.1rem;">💡</span>
                <span style="color:#e2e8f0; font-size:0.95rem; margin-left:8px;">{key_insight}</span>
            </div>
            """, unsafe_allow_html=True)

        # Top Contradiction
        top_c = results.get("top_contradiction") or (contradictions[0] if contradictions else None)
        if top_c:
            severity = top_c.get("severity", "").upper()
            sev_color = "#ef4444" if severity == "HIGH" else "#f59e0b" if severity == "MEDIUM" else "#64748b"
            st.markdown(f"""
            <div class="contradiction-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:1.1rem; font-weight:600; color:#f87171;">⚡ Top Contradiction</span>
                    <span class="fc-badge" style="background:rgba(239,68,68,0.15); color:{sev_color};">{severity} SEVERITY</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr auto 1fr; gap:12px; align-items:center;">
                    <div style="background:rgba(239,68,68,0.08); border-radius:10px; padding:12px;">
                        <b style="color:#fca5a5; font-size:0.85rem;">{top_c.get('paper_a_title', 'Paper A')[:50]}</b>
                        <p style="color:#cbd5e1; font-size:0.85rem; margin:6px 0 0;">{top_c.get('claim_a', '')}</p>
                    </div>
                    <div style="color:#f87171; font-size:1.4rem; font-weight:700;">⚡</div>
                    <div style="background:rgba(245,158,11,0.08); border-radius:10px; padding:12px;">
                        <b style="color:#fcd34d; font-size:0.85rem;">{top_c.get('paper_b_title', 'Paper B')[:50]}</b>
                        <p style="color:#cbd5e1; font-size:0.85rem; margin:6px 0 0;">{top_c.get('claim_b', '')}</p>
                    </div>
                </div>
                <p style="color:#94a3b8; font-size:0.85rem; margin-top:10px;">
                    <b>Explanation:</b> {top_c.get('explanation', '')}
                </p>
                <p style="color:#6366f1; font-size:0.82rem;">
                    <b>Resolution path:</b> {top_c.get('resolution_path', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Additional contradictions
        if len(contradictions) > 1:
            with st.expander(f"View all {len(contradictions)} contradictions"):
                for i, c in enumerate(contradictions[1:], 2):
                    sev = c.get("severity", "low").upper()
                    st.markdown(f"""
                    **#{i} [{sev}]** {c.get('paper_a_title', '')[:40]} ↔ {c.get('paper_b_title', '')[:40]}

                    {c.get('explanation', '')}

                    *Resolution: {c.get('resolution_path', '')}*

                    ---
                    """)

        # Field momentum / red flags
        momentum = results.get("field_momentum", "")
        if momentum:
            st.info(f"📈 **Field Momentum:** {momentum.capitalize()}")

        flags = results.get("common_red_flags", [])
        if flags:
            st.warning("🚩 **Common Red Flags:** " + " • ".join(flags))

    # ════════════ TAB 2: KNOWLEDGE GRAPH ════════════
    with tab_graph:
        st.markdown("#### 🕸️ Interactive Knowledge Graph")
        st.caption("Node size = credibility • Color = publication year • Red dashed = contradiction • Hover for details")

        graph_path = st.session_state.graph_path
        if graph_path and os.path.exists(graph_path):
            with open(graph_path, "r", encoding="utf-8") as f:
                graph_html = f.read()
            st.components.v1.html(graph_html, height=650, scrolling=False)
        else:
            st.info("Knowledge graph will appear here after analysis.")

    # ════════════ TAB 3: MIND MAP ════════════
    with tab_mindmap:
        st.markdown("#### 🧠 Research Mind Map")
        st.caption("Topic → Sub-questions → Papers (colored by credibility)")

        mm_path = st.session_state.mindmap_path
        if mm_path and os.path.exists(mm_path):
            with open(mm_path, "r", encoding="utf-8") as f:
                mm_html = f.read()
            st.components.v1.html(mm_html, height=650, scrolling=False)
        else:
            st.info("Mind map will appear here after analysis.")

    # ════════════ TAB 4: PAPER CARDS ════════════
    with tab_cards:
        st.markdown("#### 🃏 Paper Analysis Cards")

        if not papers:
            st.info("Run an analysis first.")
        else:
            # Filter
            filter_choice = st.selectbox("Filter by credibility", ["All", "High (7-10)", "Medium (4-6)", "Low (0-3)"], key="fc_filter")

            cards_html = "<div class='fc-grid'>"
            card_count = 0
            for paper, critique in sorted(
                zip(papers, critiques),
                key=lambda x: safe_score(x[1].get("credibility_score", 0)),
                reverse=True
            ):
                cred = safe_score(critique.get("credibility_score", 5))
                rel = safe_score(critique.get("relevance_score", 5))

                # Apply filter
                if filter_choice == "High (7-10)" and cred < 7: continue
                elif filter_choice == "Medium (4-6)" and (cred < 4 or cred > 6): continue
                elif filter_choice == "Low (0-3)" and cred > 3: continue

                title = paper.get("title", "Untitled")
                year = paper.get("year", "?")
                venue = paper.get("venue", "") or ""
                authors = ", ".join(paper.get("authors", [])[:3]) or "Unknown"
                source = paper.get("source", "")
                influence = critique.get("influence_type", "extension")
                insight = critique.get("key_insight", "")
                methodology = critique.get("methodology_summary", "")
                claims = critique.get("main_claims", [])[:3]
                flags = critique.get("red_flags", [])

                cred_class = "cred-high" if cred >= 7 else "cred-med" if cred >= 4 else "cred-low"
                cred_badge = "badge-green" if cred >= 7 else "badge-yellow" if cred >= 4 else "badge-red"

                claims_html = "".join([f"<div style='color:#cbd5e1;'>• {c}</div>" for c in claims])
                flags_html = "".join([f"<div class='fc-flag'>🚩 {fl}</div>" for fl in flags])
                insight_html = f"<div class='fc-insight'>💡 {insight}</div>" if insight else ""

                cards_html += f"""
                <div class="fc-card {cred_class}">
                    <div class="fc-title">{title}</div>
                    <div class="fc-meta">
                        <span class="fc-badge {cred_badge}">★ {cred}/10</span>
                        <span class="fc-badge badge-blue">Rel: {rel}/10</span>
                        <span class="fc-badge badge-purple">{influence}</span>
                        <span style="color:#475569;">{year}</span>
                    </div>
                    <div style="color:#64748b; font-size:0.8rem; margin-bottom:8px;">{authors}</div>
                    {"<div style='color:#475569; font-size:0.78rem; margin-bottom:6px;'>📍 " + venue + "</div>" if venue else ""}
                    {insight_html}
                    <div class="fc-section"><b>Methodology:</b> {methodology}</div>
                    {"<div class='fc-section'><b>Key Claims:</b>" + claims_html + "</div>" if claims else ""}
                    {flags_html}
                </div>
                """
                card_count += 1

            cards_html += "</div>"
            if card_count > 0:
                st.caption(f"Showing {card_count} papers")
                st.markdown(cards_html, unsafe_allow_html=True)
            else:
                st.info("No papers match the selected filter.")

    # ════════════ TAB 5: FULL REPORT ════════════
    with tab_report:
        st.markdown("#### 📄 Research Report")

        if mode == "fast":
            # Fast Mode — AI-powered briefing
            exec_sum = results.get("executive_summary", "")
            methodology_v = results.get("methodology_verdict", "")
            recommended = results.get("recommended_reading", [])
            open_qs = results.get("open_questions", [])

            if exec_sum:
                st.markdown(f"""
                <div class="report-section">
                    <h3>Executive Briefing</h3>
                    <p style="color:#cbd5e1; line-height:1.6;">{exec_sum}</p>
                </div>
                """, unsafe_allow_html=True)

            if methodology_v:
                st.markdown(f"""
                <div class="report-section">
                    <h3>📊 Methodology Verdict</h3>
                    <p style="color:#cbd5e1;">{methodology_v}</p>
                </div>
                """, unsafe_allow_html=True)

            if recommended:
                st.markdown("##### 📚 Recommended Reading")
                for r in recommended:
                    st.markdown(f"- {r}")

            if open_qs:
                st.markdown("##### ❓ Open Questions")
                for q in open_qs:
                    st.markdown(f"- {q}")

            # Paper table
            if papers:
                st.markdown("##### 📋 Paper Summary Table")
                import pandas as pd
                data = []
                for paper, critique in zip(papers, critiques):
                    data.append({
                        "Title": paper.get("title", "")[:50] + "...",
                        "Year": paper.get("year", 0),
                        "Source": paper.get("source", ""),
                        "Credibility": safe_score(critique.get("credibility_score", 0)),
                        "Relevance": safe_score(critique.get("relevance_score", 0)),
                        "Type": critique.get("influence_type", ""),
                        "Flags": len(critique.get("red_flags", []))
                    })
                if data:
                    df = pd.DataFrame(data).sort_values("Credibility", ascending=False)
                    st.dataframe(df, use_container_width=True, hide_index=True)

        else:
            # Deep Mode — Publication-grade report
            report = st.session_state.report or results

            # Sub-tabs
            rtab1, rtab2, rtab3, rtab4, rtab5 = st.tabs([
                "📋 Summary", "📊 Methodology Matrix", "⚔️ Contradictions", "🎯 Research Gaps", "🔮 Frontier"
            ])

            with rtab1:
                exec_sum = report.get("executive_summary", "")
                if exec_sum:
                    st.markdown(f"""
                    <div class="report-section">
                        <h3>Executive Summary</h3>
                        <p style="color:#cbd5e1; line-height:1.7; font-size:0.95rem;">{exec_sum}</p>
                    </div>
                    """, unsafe_allow_html=True)

                snap = report.get("field_snapshot", {})
                if snap:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Field Trend", snap.get("trend", "").capitalize())
                        methods = snap.get("dominant_methods", [])
                        if methods:
                            st.markdown("**Dominant Methods:**")
                            for m in methods:
                                st.markdown(f"- {m}")
                    with col2:
                        key_years = snap.get("key_years", [])
                        if key_years:
                            st.markdown("**Key Years:**")
                            for ky in key_years:
                                st.markdown(f"- {ky}")

                # Paper verdicts
                verdicts = report.get("paper_verdicts", [])
                if verdicts:
                    st.markdown("##### 📝 Paper Verdicts")
                    for v in verdicts:
                        verdict_color = "#10b981" if v.get("verdict") == "strong" else "#f59e0b" if v.get("verdict") == "moderate" else "#ef4444"
                        st.markdown(f"""
                        <div style="background:rgba(30,35,45,0.4); border-radius:10px; padding:12px; margin:6px 0; border-left:3px solid {verdict_color};">
                            <b style="color:#e2e8f0;">{v.get('title', '')[:60]}</b>
                            <span class="fc-badge" style="background:rgba(255,255,255,0.05); color:{verdict_color}; margin-left:8px;">{v.get('verdict', '').upper()}</span>
                            <p style="color:#94a3b8; font-size:0.85rem; margin:4px 0 0;">{v.get('one_liner', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # Download
                archivist_dl = ArchivistAgent()
                download_md = archivist_dl.export_markdown(report, run_topic)
                st.download_button("📥 Download Report (.md)", download_md, f"scholar_pulse_{run_topic[:20]}.md")

            with rtab2:
                matrix = report.get("methodology_matrix", {})
                if matrix:
                    st.success(f"**Strongest Approach:** {matrix.get('strongest_approach', 'N/A')}")
                    st.error(f"**Weakest Approach:** {matrix.get('weakest_approach', 'N/A')}")
                    limits = matrix.get("common_limitations", [])
                    if limits:
                        st.markdown("**Common Limitations:**")
                        for l in limits:
                            st.markdown(f"- {l}")

                # Paper comparison table
                if papers:
                    st.markdown("##### 📊 Full Paper Comparison")
                    import pandas as pd
                    data = []
                    for paper, critique in zip(papers, critiques):
                        data.append({
                            "Title": paper.get("title", "")[:45] + "...",
                            "Year": paper.get("year", 0),
                            "Credibility": safe_score(critique.get("credibility_score", 0)),
                            "Relevance": safe_score(critique.get("relevance_score", 0)),
                            "Type": critique.get("influence_type", ""),
                            "Dataset": critique.get("dataset_type", "unknown"),
                            "Red Flags": len(critique.get("red_flags", []))
                        })
                    if data:
                        df = pd.DataFrame(data).sort_values("Credibility", ascending=False)
                        st.dataframe(df, use_container_width=True, hide_index=True)

            with rtab3:
                c_summary = report.get("contradictions_summary", [])
                if c_summary:
                    for ci, c in enumerate(c_summary, 1):
                        sev = c.get("severity", "low").upper()
                        sev_color = "#ef4444" if sev == "HIGH" else "#f59e0b" if sev == "MEDIUM" else "#64748b"
                        st.markdown(f"""
                        <div class="contradiction-card">
                            <div style="display:flex; justify-content:space-between;">
                                <b style="color:#e2e8f0;">#{ci}. {c.get('paper_a', '')} vs {c.get('paper_b', '')}</b>
                                <span class="fc-badge" style="background:rgba(239,68,68,0.15); color:{sev_color};">{sev}</span>
                            </div>
                            <p style="color:#cbd5e1; margin:8px 0;">{c.get('conflict', '')}</p>
                            <p style="color:#6366f1; font-size:0.85rem;">{c.get('implication', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                elif contradictions:
                    for ci, c in enumerate(contradictions, 1):
                        st.markdown(f"**#{ci}** [{c.get('severity','').upper()}] {c.get('paper_a_title','')} ↔ {c.get('paper_b_title','')}")
                        st.markdown(f"{c.get('explanation', '')}")
                        st.markdown("---")
                else:
                    st.info("No contradictions detected in the analyzed papers.")

            with rtab4:
                gaps = report.get("gaps", [])
                if gaps:
                    for gap in gaps:
                        opp = gap.get("opportunity_score", 0)
                        st.markdown(f"""
                        <div class="report-section">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h3 style="margin:0;">{gap.get('area', 'Gap')}</h3>
                                <span class="fc-badge badge-green" style="font-size:0.9rem;">Opportunity: {opp}/10 ⭐</span>
                            </div>
                            <p style="color:#cbd5e1; margin:8px 0;">{gap.get('description', '')}</p>
                            <p style="color:#64748b; font-size:0.85rem;"><b>Why missing:</b> {gap.get('why_missing', '')}</p>
                            <p style="color:#a78bfa; font-size:0.85rem;"><b>Suggested approach:</b> {gap.get('suggested_approach', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Gap analysis will appear here after deep mode analysis.")

            with rtab5:
                frontiers = report.get("frontier_directions", [])
                if frontiers:
                    for i, f in enumerate(frontiers, 1):
                        diff = f.get("difficulty", "medium")
                        diff_badge = "badge-green" if diff == "low" else "badge-yellow" if diff == "medium" else "badge-red"
                        st.markdown(f"""
                        <div class="report-section">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h3 style="margin:0;">{i}. {f.get('direction', '')}</h3>
                                <div>
                                    <span class="fc-badge badge-blue" style="font-size:0.85rem;">Impact: {f.get('impact_score', 0)}/10</span>
                                    <span class="fc-badge {diff_badge}" style="font-size:0.85rem; margin-left:6px;">{diff.capitalize()}</span>
                                </div>
                            </div>
                            <p style="color:#cbd5e1; margin:8px 0;">{f.get('rationale', '')}</p>
                            <p style="color:#64748b; font-size:0.85rem;">
                                Addresses: {f.get('addresses_gap', '')} &nbsp;•&nbsp;
                                Timeline: {f.get('timeline', 'Unknown')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Frontier analysis will appear here after deep mode analysis.")
