import sqlite3
import json
import uuid
import os
from statistics import mean
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME
from utils.prompts import LITERATURE_REVIEW_PROMPT, FAST_SUMMARY_PROMPT
from demo_data import get_demo_topic, get_demo_data

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ArchivistAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        db_path = os.path.join(_BASE_DIR, "data", "scholar_pulse.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY, topic TEXT, mode TEXT,
                confidence REAL, depth INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS papers (
                paper_id TEXT PRIMARY KEY, session_id TEXT,
                title TEXT, abstract TEXT, year INTEGER,
                credibility_score INTEGER, red_flags TEXT, main_claims TEXT
            );
            CREATE TABLE IF NOT EXISTS contradictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT,
                paper_a_title TEXT, paper_b_title TEXT,
                claim_a TEXT, claim_b TEXT, severity TEXT, explanation TEXT
            );
        """)
        self.conn.commit()

    def save_session(self, session_id, topic, mode, confidence, depth):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions VALUES (?,?,?,?,?,datetime('now'))",
            (session_id, topic, mode, confidence, depth)
        )
        self.conn.commit()

    def save_papers(self, session_id, papers, critiques):
        for paper, critique in zip(papers, critiques):
            score = critique.get("credibility_score", 0)
            if isinstance(score, str):
                try:
                    score = int(score.split("/")[0])
                except (ValueError, IndexError):
                    score = 0
            self.conn.execute(
                "INSERT OR REPLACE INTO papers VALUES (?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), session_id, paper.get("title", ""),
                 paper.get("abstract", ""), paper.get("year", 0),
                 score,
                 json.dumps(critique.get("red_flags", [])),
                 json.dumps(critique.get("main_claims", [])))
            )
        self.conn.commit()

    def save_contradictions(self, session_id, contradictions):
        for c in contradictions:
            self.conn.execute(
                "INSERT INTO contradictions (session_id,paper_a_title,paper_b_title,claim_a,claim_b,severity,explanation) VALUES (?,?,?,?,?,?,?)",
                (session_id, c.get("paper_a_title", ""), c.get("paper_b_title", ""),
                 c.get("claim_a", ""), c.get("claim_b", ""),
                 c.get("severity", "low"), c.get("explanation", ""))
            )
        self.conn.commit()

    def _safe_score(self, score):
        """Ensure score is a numeric value."""
        if isinstance(score, str):
            try:
                return float(score.split("/")[0])
            except (ValueError, IndexError):
                return 5.0
        try:
            return float(score)
        except (ValueError, TypeError):
            return 5.0

    def generate_fast_summary(self, topic, papers, critiques, contradictions, confidence) -> dict:
        """Generate an AI-powered fast summary using Groq."""
        top_contradiction = contradictions[0] if contradictions else None

        scores = [self._safe_score(c.get("credibility_score", 5)) for c in critiques]
        avg_credibility = mean(scores) if scores else 5.0
        all_red_flags = [flag for c in critiques for flag in c.get("red_flags", [])]

        # Try AI-powered summary
        ai_summary = {}
        try:
            paper_info = []
            for paper, critique in zip(papers[:10], critiques[:10]):
                paper_info.append({
                    "title": paper.get("title", "")[:80],
                    "year": paper.get("year", 0),
                    "credibility": self._safe_score(critique.get("credibility_score", 5)),
                    "claims": critique.get("main_claims", [])[:2],
                    "key_insight": critique.get("key_insight", "")
                })

            user_msg = f"""
Topic: {topic}
Papers: {json.dumps(paper_info)}
Contradictions: {len(contradictions)} found
Average credibility: {avg_credibility:.1f}/10
"""
            completion = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": FAST_SUMMARY_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )
            text = completion.choices[0].message.content.strip()
            text = text.removeprefix("```json").removesuffix("```").strip()
            ai_summary = json.loads(text)
        except Exception as e:
            print(f"Fast summary AI error: {e}")
            ai_summary = {
                "executive_summary": f"Analyzed {len(papers)} papers on '{topic}'. Average credibility: {avg_credibility:.1f}/10. Found {len(contradictions)} contradictions in the literature.",
                "key_insight": f"The field of {topic} shows {'strong' if avg_credibility > 6 else 'moderate'} methodological rigor across {len(papers)} analyzed papers.",
                "methodology_verdict": f"Average credibility score of {avg_credibility:.1f}/10 across all papers.",
                "field_momentum": "stable",
                "recommended_reading": [p.get("title", "") for p in papers[:2]],
                "open_questions": ["Further investigation needed"]
            }

        return {
            "papers_count": len(papers),
            "contradictions_count": len(contradictions),
            "confidence": confidence,
            "avg_credibility": round(avg_credibility, 1),
            "top_contradiction": top_contradiction,
            "common_red_flags": list(set(all_red_flags))[:5],
            **ai_summary
        }

    def generate_deep_report(self, topic, papers, critiques, contradictions) -> dict:
        """Generate a comprehensive deep literature review."""
        paper_summaries = []
        for paper, critique in zip(papers, critiques):
            paper_summaries.append({
                "title": paper.get("title", ""),
                "year": paper.get("year", 0),
                "credibility_score": self._safe_score(critique.get("credibility_score", 0)),
                "relevance_score": self._safe_score(critique.get("relevance_score", 5)),
                "influence_type": critique.get("influence_type", "extension"),
                "methodology_summary": critique.get("methodology_summary", ""),
                "main_claims": critique.get("main_claims", []),
                "red_flags": critique.get("red_flags", []),
                "key_insight": critique.get("key_insight", "")
            })

        # Demo mode interception
        demo_topic = get_demo_topic(topic)
        if demo_topic:
            demo_data = get_demo_data(demo_topic)
            if demo_data and "deep_report" in demo_data:
                return demo_data["deep_report"]

        user_message = f"""
Topic: {topic}
Papers analyzed: {json.dumps(paper_summaries, indent=2)}
Contradictions found: {json.dumps(contradictions, indent=2)}
Generate the complete literature review JSON.
        """
        try:
            completion = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": LITERATURE_REVIEW_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            text = completion.choices[0].message.content.strip()
            text = text.removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            return {"error": "Report generation failed", "raw": str(e)}

    def export_markdown(self, report: dict, topic: str) -> str:
        md = f"# Literature Review: {topic}\n\n"
        if "executive_summary" in report:
            md += f"## Executive Summary\n{report['executive_summary']}\n\n"
        if "field_snapshot" in report:
            snap = report["field_snapshot"]
            md += f"## Field Snapshot\n- Trend: {snap.get('trend', '')}\n"
            md += f"- Dominant Methods: {', '.join(snap.get('dominant_methods', []))}\n\n"
        if "contradictions_summary" in report:
            md += "## Contradictions Detected\n"
            for c in report["contradictions_summary"]:
                md += f"- **[{c.get('severity', '').upper()}]** {c.get('paper_a', '')} vs {c.get('paper_b', '')}: {c.get('conflict', '')}\n"
            md += "\n"
        if "gaps" in report:
            md += "## Research Gaps\n"
            for g in report["gaps"]:
                md += f"### {g.get('area', 'Gap')} (Opportunity: {g.get('opportunity_score', '?')}/10)\n{g.get('description', '')}\n\n"
        if "frontier_directions" in report:
            md += "## Frontier Directions\n"
            for i, f in enumerate(report["frontier_directions"], 1):
                md += f"### {i}. {f.get('direction', '')} (Impact: {f.get('impact_score', '?')}/10)\n{f.get('rationale', '')}\n\n"
        return md


if __name__ == "__main__":
    agent = ArchivistAgent()
    print("Database initialized successfully at data/scholar_pulse.db")
