"""
Cartographer Agent — Builds interactive knowledge graphs and mind maps.
Uses custom HTML/JS with vis.js for beautiful, immersive visualizations.
"""
import json
import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CartographerAgent:

    def _safe_score(self, val, default=5):
        if isinstance(val, str):
            try:
                return int(val.split("/")[0])
            except (ValueError, IndexError):
                return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def build_graph(self, papers: list, critiques: list, contradictions: list) -> str:
        """Build a D3/vis-style knowledge graph as a self-contained HTML file."""
        assets_dir = os.path.join(_BASE_DIR, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        nodes = []
        edges = []

        for i, (paper, critique) in enumerate(zip(papers, critiques)):
            cred = self._safe_score(critique.get("credibility_score", 5))
            rel = self._safe_score(critique.get("relevance_score", 5))
            year = paper.get("year", 2020) or 2020
            influence = critique.get("influence_type", "extension")
            title = paper.get("title", "Untitled")
            authors = ", ".join(paper.get("authors", [])[:2]) or "Unknown"
            venue = paper.get("venue", "") or ""
            source = paper.get("source", "")
            claims = critique.get("main_claims", [])[:2]
            flags = critique.get("red_flags", [])
            insight = critique.get("key_insight", "")

            # Color by year gradient
            yr = max(min(year, 2025), 2018)
            t = (yr - 2018) / 7
            r = int(108 + t * (255 - 108))
            g = int(92 + t * (107 - 92))
            b = int(231 + t * (53 - 231))
            color = f"rgb({r},{g},{b})"

            # Shape by influence type
            shape_map = {
                "foundational": "diamond",
                "survey": "square",
                "contradiction": "triangle",
                "extension": "dot",
                "application": "dot"
            }
            shape = shape_map.get(influence, "dot")

            # Border by relevance
            border_color = f"rgba(52, 211, 153, {min(rel/10, 1)})" if rel >= 6 else f"rgba(251, 191, 36, {min(rel/10, 1)})"

            tooltip = f"<div style='max-width:320px;font-family:Outfit,sans-serif;'>"
            tooltip += f"<b style='font-size:14px;color:#f8fafc;'>{title}</b><br/>"
            tooltip += f"<span style='color:#94a3b8;font-size:12px;'>{authors} • {venue} • {year}</span><br/>"
            tooltip += f"<hr style='border-color:#334155;margin:6px 0;'/>"
            tooltip += f"<span style='color:#38bdf8;'>Credibility: {cred}/10</span> &nbsp; "
            tooltip += f"<span style='color:#a78bfa;'>Relevance: {rel}/10</span><br/>"
            tooltip += f"<span style='color:#64748b;'>Type: {influence}</span> &nbsp; <span style='color:#64748b;'>Source: {source}</span><br/>"
            if insight:
                tooltip += f"<hr style='border-color:#334155;margin:6px 0;'/>"
                tooltip += f"<span style='color:#e2e8f0;font-style:italic;'>💡 {insight}</span><br/>"
            if claims:
                tooltip += f"<b style='color:#94a3b8;margin-top:4px;display:block;'>Claims:</b>"
                for c in claims:
                    tooltip += f"<span style='color:#cbd5e1;'>• {c}</span><br/>"
            if flags:
                for f in flags:
                    tooltip += f"<span style='color:#f87171;'>🚩 {f}</span><br/>"
            tooltip += "</div>"

            nodes.append({
                "id": i,
                "label": title[:35] + ("..." if len(title) > 35 else ""),
                "size": max(cred * 4, 12),
                "color": {
                    "background": color,
                    "border": border_color,
                    "highlight": {"background": "#38bdf8", "border": "#0ea5e9"}
                },
                "shape": shape,
                "title": tooltip,
                "font": {"color": "#e2e8f0", "size": 11, "face": "Outfit, sans-serif"},
                "borderWidth": 2,
                "shadow": True,
                "year": year
            })

        # Build title index for edge matching
        title_to_id = {}
        for i, paper in enumerate(papers):
            title_to_id[paper.get("title", "")[:40]] = i
            title_to_id[paper.get("title", "")] = i

        # Contradiction edges
        for contradiction in contradictions:
            src_title = contradiction.get("paper_a_title", "")
            tgt_title = contradiction.get("paper_b_title", "")
            src_id = title_to_id.get(src_title[:40]) or title_to_id.get(src_title)
            tgt_id = title_to_id.get(tgt_title[:40]) or title_to_id.get(tgt_title)
            if src_id is not None and tgt_id is not None:
                severity = contradiction.get("severity", "low")
                width = 4 if severity == "high" else 3 if severity == "medium" else 2
                edges.append({
                    "from": src_id,
                    "to": tgt_id,
                    "color": {"color": "#ef4444", "highlight": "#f87171"},
                    "width": width,
                    "dashes": True,
                    "label": f"⚡ {severity.upper()}",
                    "font": {"color": "#f87171", "size": 10, "strokeWidth": 0},
                    "title": contradiction.get("explanation", ""),
                    "smooth": {"type": "curvedCW", "roundness": 0.2}
                })

        # Relationship edges (same year = related, year diff + same question = builds upon)
        for i in range(len(papers)):
            for j in range(i+1, min(i+4, len(papers))):
                if papers[i].get("year", 0) and papers[j].get("year", 0):
                    year_diff = (papers[j].get("year", 0) or 0) - (papers[i].get("year", 0) or 0)
                    if year_diff > 0:
                        edges.append({
                            "from": i, "to": j,
                            "color": {"color": "rgba(99,102,241,0.25)", "highlight": "rgba(99,102,241,0.5)"},
                            "width": 1,
                            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
                            "smooth": {"type": "continuous"}
                        })

        html = self._generate_graph_html(nodes, edges)
        filepath = os.path.join(_BASE_DIR, "assets", "graph.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return filepath

    def _generate_graph_html(self, nodes: list, edges: list) -> str:
        return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; padding:0; background:#0b0f19; overflow:hidden; font-family:'Outfit',sans-serif; }}
  #graph {{ width:100%; height:100vh; }}
  .legend {{
    position:absolute; bottom:12px; left:12px; background:rgba(15,23,42,0.9);
    border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:12px 16px;
    color:#94a3b8; font-size:12px; backdrop-filter:blur(8px);
  }}
  .legend-item {{ display:flex; align-items:center; gap:8px; margin:4px 0; }}
  .legend-dot {{ width:12px; height:12px; border-radius:50%; }}
  .legend-line {{ width:20px; height:3px; border-radius:2px; }}
</style>
</head><body>
<div id="graph"></div>
<div class="legend">
  <b style="color:#e2e8f0;">Legend</b>
  <div class="legend-item"><div class="legend-dot" style="background:#6C5CE7;"></div> Older papers (2018-2020)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#a07cf0;"></div> Mid papers (2021-2022)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#FF6B35;"></div> Recent papers (2023-2025)</div>
  <div class="legend-item"><div class="legend-line" style="background:#ef4444;border-style:dashed;"></div> Contradiction</div>
  <div class="legend-item"><div class="legend-line" style="background:rgba(99,102,241,0.5);"></div> Timeline link</div>
  <div style="margin-top:6px;color:#64748b;font-size:11px;">Node size = credibility • Hover for details</div>
</div>
<script>
var nodes = new vis.DataSet({json.dumps(nodes)});
var edges = new vis.DataSet({json.dumps(edges)});
var container = document.getElementById('graph');
var data = {{ nodes: nodes, edges: edges }};
var options = {{
  physics: {{
    forceAtlas2Based: {{
      gravitationalConstant: -80,
      centralGravity: 0.008,
      springLength: 180,
      springConstant: 0.06,
      damping: 0.4
    }},
    solver: 'forceAtlas2Based',
    stabilization: {{ iterations: 150 }}
  }},
  interaction: {{
    hover: true,
    tooltipDelay: 100,
    zoomView: true,
    dragView: true
  }},
  nodes: {{
    shadow: {{ enabled: true, color: 'rgba(0,0,0,0.4)', size: 8 }}
  }}
}};
var network = new vis.Network(container, data, options);
</script>
</body></html>"""

    def build_mindmap(self, topic, sub_questions, papers, critiques) -> str:
        """Build a hierarchical mind map as HTML."""
        assets_dir = os.path.join(_BASE_DIR, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        nodes = []
        edges = []

        # Root node
        nodes.append({
            "id": "root",
            "label": topic,
            "size": 35,
            "color": {"background": "#3b82f6", "border": "#60a5fa"},
            "shape": "box",
            "font": {"color": "#ffffff", "size": 16, "face": "Outfit, sans-serif", "bold": True},
            "borderWidth": 3,
            "shadow": True,
            "level": 0,
            "margin": 14
        })

        # Sub-question nodes
        sq_colors = ["#f59e0b", "#10b981", "#8b5cf6", "#ec4899", "#06b6d4"]
        for i, sq in enumerate(sub_questions):
            sq_id = f"sq_{i}"
            nodes.append({
                "id": sq_id,
                "label": sq[:50] + ("..." if len(sq) > 50 else ""),
                "size": 22,
                "color": {"background": sq_colors[i % len(sq_colors)], "border": sq_colors[i % len(sq_colors)]},
                "shape": "box",
                "font": {"color": "#ffffff", "size": 13, "face": "Outfit, sans-serif"},
                "borderWidth": 2,
                "shadow": True,
                "level": 1,
                "margin": 10,
                "title": sq
            })
            edges.append({
                "from": "root", "to": sq_id,
                "color": {"color": sq_colors[i % len(sq_colors)], "opacity": 0.6},
                "width": 2
            })

        # Match papers to sub-questions
        sq_keywords = {}
        for i, sq in enumerate(sub_questions):
            words = sq.lower().split()
            sq_keywords[i] = set(w.strip("?.,;:!") for w in words if len(w) > 3)

        for pi, (paper, critique) in enumerate(zip(papers, critiques)):
            title = paper.get("title", "Untitled")
            cred = self._safe_score(critique.get("credibility_score", 5))
            year = paper.get("year", "?")

            # Color based on credibility
            if cred >= 7:
                bg = "#10b981"
            elif cred >= 4:
                bg = "#f59e0b"
            else:
                bg = "#ef4444"

            p_id = f"paper_{pi}"
            nodes.append({
                "id": p_id,
                "label": f"{title[:30]}...\n({year}) ★{cred}",
                "size": max(cred * 2 + 6, 10),
                "color": {"background": bg, "border": bg},
                "shape": "box",
                "font": {"color": "#ffffff", "size": 11, "face": "Outfit, sans-serif", "multi": "html"},
                "borderWidth": 1,
                "shadow": True,
                "level": 2,
                "margin": 8,
                "title": f"{title}\nYear: {year}\nCredibility: {cred}/10"
            })

            # Assign to best-matching sub-question
            paper_text = (title + " " + paper.get("abstract", "")).lower()
            best_sq = 0
            best_score = 0
            for si, kws in sq_keywords.items():
                score = sum(1 for kw in kws if kw in paper_text)
                if score > best_score:
                    best_score = score
                    best_sq = si

            sq_id = f"sq_{best_sq}"
            edges.append({
                "from": sq_id, "to": p_id,
                "color": {"color": "rgba(148,163,184,0.4)"},
                "width": 1
            })

        html = self._generate_mindmap_html(nodes, edges)
        filepath = os.path.join(_BASE_DIR, "assets", "mindmap.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return filepath

    def _generate_mindmap_html(self, nodes: list, edges: list) -> str:
        return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; padding:0; background:#0b0f19; overflow:hidden; font-family:'Outfit',sans-serif; }}
  #mindmap {{ width:100%; height:100vh; }}
  .mm-legend {{
    position:absolute; bottom:12px; right:12px; background:rgba(15,23,42,0.9);
    border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:12px 16px;
    color:#94a3b8; font-size:12px; backdrop-filter:blur(8px);
  }}
  .mm-item {{ display:flex; align-items:center; gap:8px; margin:3px 0; }}
  .mm-dot {{ width:10px; height:10px; border-radius:3px; }}
</style>
</head><body>
<div id="mindmap"></div>
<div class="mm-legend">
  <b style="color:#e2e8f0;">Mind Map</b>
  <div class="mm-item"><div class="mm-dot" style="background:#3b82f6;"></div> Research Topic</div>
  <div class="mm-item"><div class="mm-dot" style="background:#f59e0b;"></div> Sub-questions</div>
  <div class="mm-item"><div class="mm-dot" style="background:#10b981;"></div> High credibility (7-10)</div>
  <div class="mm-item"><div class="mm-dot" style="background:#ef4444;"></div> Low credibility (0-3)</div>
</div>
<script>
var nodes = new vis.DataSet({json.dumps(nodes)});
var edges = new vis.DataSet({json.dumps(edges)});
var container = document.getElementById('mindmap');
var data = {{ nodes: nodes, edges: edges }};
var options = {{
  layout: {{
    hierarchical: {{
      enabled: true,
      direction: 'UD',
      sortMethod: 'directed',
      levelSeparation: 140,
      nodeSpacing: 180,
      treeSpacing: 200
    }}
  }},
  physics: {{
    enabled: true,
    hierarchicalRepulsion: {{
      nodeDistance: 180,
      springLength: 120,
      springConstant: 0.01
    }},
    stabilization: {{ iterations: 100 }}
  }},
  interaction: {{
    hover: true,
    tooltipDelay: 100,
    dragNodes: true,
    zoomView: true
  }},
  edges: {{
    smooth: {{ type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 }}
  }}
}};
var network = new vis.Network(container, data, options);
</script>
</body></html>"""


if __name__ == "__main__":
    agent = CartographerAgent()
    fake_papers = [
        {"title": "CNN for Rural Diagnosis 2022", "year": 2022, "abstract": "Test", "authors": ["A"], "venue": "MICCAI", "source": "OpenAlex"},
        {"title": "ViT Fails Rural Distribution 2024", "year": 2024, "abstract": "Test", "authors": ["B"], "venue": "NeurIPS", "source": "CrossRef"},
    ]
    fake_critiques = [
        {"credibility_score": 4, "relevance_score": 7, "red_flags": ["small sample"], "main_claims": ["test"], "influence_type": "foundational", "key_insight": "test"},
        {"credibility_score": 8, "relevance_score": 9, "red_flags": [], "main_claims": ["test2"], "influence_type": "contradiction", "key_insight": "test2"},
    ]
    fake_contradictions = [{
        "contradiction_detected": True, "severity": "high",
        "claim_a": "CNN achieves 94%", "claim_b": "CNN fails at 67%",
        "explanation": "Direct conflict", "paper_a_title": "CNN for Rural Diagnosis 2022",
        "paper_b_title": "ViT Fails Rural Distribution 2024"
    }]
    path = agent.build_graph(fake_papers, fake_critiques, fake_contradictions)
    print(f"Graph: {path}")
    path2 = agent.build_mindmap("AI Healthcare", ["Q1?", "Q2?"], fake_papers, fake_critiques)
    print(f"Mindmap: {path2}")
