from groq import Groq
import time
import json

from config import GROQ_API_KEY, MODEL_NAME
from utils.prompts import CRITIQUE_PROMPT, CONTRADICTION_PROMPT
from demo_data import get_demo_topic, get_demo_data, DEMO_TOPICS


class SkepticAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def critique_paper(self, paper: dict, topic: str = "") -> dict:
        # Check if paper has pre-generated critique (demo mode)
        prebuilt_critique = paper.get("critique")
        if prebuilt_critique:
            print(f"[DEMO MODE] Using pre-generated critique for: {paper.get('title', '')[:40]}...")
            result = prebuilt_critique.copy()
            result["title"] = paper.get("title", "")
            result["year"] = paper.get("year", 0)
            # Ensure new fields exist
            result.setdefault("relevance_score", 8)
            result.setdefault("influence_type", "extension")
            result.setdefault("key_insight", result.get("methodology_summary", ""))
            return result

        abstract = paper.get("abstract", "")
        if not abstract or len(abstract) < 50:
            return {
                "sample_size": "not mentioned",
                "dataset_type": "not mentioned",
                "reproducibility_score": 1,
                "credibility_score": 1,
                "relevance_score": 1,
                "influence_type": "application",
                "boldness_vs_evidence": "overclaimed",
                "red_flags": ["no abstract"],
                "main_claims": [],
                "key_insight": "Insufficient information to evaluate",
                "methodology_summary": "No abstract available",
                "title": paper.get("title", ""),
                "year": paper.get("year", 0)
            }

        topic_context = f"\nResearch topic being investigated: {topic}" if topic else ""
        user_message = f"Title: {paper.get('title', '')}\nYear: {paper.get('year', '')}\nAbstract: {abstract}{topic_context}"

        retries = 3
        delays = [2, 5, 10]
        for attempt in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": CRITIQUE_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    response_format={"type": "json_object"}
                )
                text = completion.choices[0].message.content.strip()
                text = text.removeprefix("```json").removesuffix("```").strip()
                result = json.loads(text)
                result["title"] = paper.get("title", "")
                result["year"] = paper.get("year", 0)
                # Ensure numeric scores
                for key in ["credibility_score", "relevance_score", "reproducibility_score"]:
                    val = result.get(key, 5)
                    if isinstance(val, str):
                        try:
                            val = int(val.split("/")[0])
                        except (ValueError, IndexError):
                            val = 5
                    result[key] = int(val)
                return result
            except Exception as e:
                print(f"Critique error on attempt {attempt+1}: {e}")
                if attempt < retries - 1:
                    time.sleep(delays[attempt])
                else:
                    return {
                        "sample_size": "not mentioned",
                        "dataset_type": "not mentioned",
                        "reproducibility_score": 1,
                        "credibility_score": 1,
                        "relevance_score": 1,
                        "influence_type": "application",
                        "boldness_vs_evidence": "overclaimed",
                        "red_flags": ["AI analysis failed"],
                        "main_claims": [],
                        "key_insight": "Analysis could not be completed",
                        "methodology_summary": "Error during critique",
                        "title": paper.get("title", ""),
                        "year": paper.get("year", 0)
                    }

    def detect_contradiction(self, paper_a: dict, paper_b: dict, critique_a: dict, critique_b: dict) -> dict:
        user_message = f"""
Paper A title: {paper_a.get('title', '')}
Paper A year: {paper_a.get('year', '')}
Paper A abstract: {paper_a.get('abstract', '')}
Paper A main claims: {critique_a.get('main_claims', [])}

Paper B title: {paper_b.get('title', '')}
Paper B year: {paper_b.get('year', '')}
Paper B abstract: {paper_b.get('abstract', '')}
Paper B main claims: {critique_b.get('main_claims', [])}
"""

        retries = 3
        delays = [2, 5, 10]
        for attempt in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": CONTRADICTION_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    response_format={"type": "json_object"}
                )
                text = completion.choices[0].message.content.strip()
                text = text.removeprefix("```json").removesuffix("```").strip()
                result = json.loads(text)
                result["paper_a_title"] = paper_a.get("title", "")
                result["paper_b_title"] = paper_b.get("title", "")
                return result
            except Exception as e:
                print(f"Contradiction error on attempt {attempt+1}: {e}")
                if attempt < retries - 1:
                    time.sleep(delays[attempt])
                else:
                    return {
                        "contradiction_detected": False,
                        "severity": "none",
                        "type": "none",
                        "relationship": "unrelated",
                        "claim_a": "",
                        "claim_b": "",
                        "explanation": "",
                        "resolution_path": "",
                        "paper_a_title": paper_a.get("title", ""),
                        "paper_b_title": paper_b.get("title", "")
                    }

    def analyze_all(self, papers: list, topic: str = "", progress_callback=None) -> tuple[list, list]:
        critiques = []
        total = len(papers)

        # Check if papers have pre-generated critiques (demo mode)
        demo_contradictions = None
        has_prebuilt_critique = any(p.get("critique") for p in papers)

        if has_prebuilt_critique:
            for topic_key, topic_data in DEMO_TOPICS.items():
                demo_titles = {p["title"] for p in topic_data.get("papers", [])}
                paper_titles = {p.get("title", "") for p in papers}
                if demo_titles & paper_titles:
                    demo_contradictions = topic_data.get("contradictions", [])
                    print(f"[DEMO MODE] Found demo topic: {topic_key}")
                    break

        for i, p in enumerate(papers, 1):
            if progress_callback:
                progress_callback(i, total)
            critiques.append(self.critique_paper(p, topic))

        # If demo contradictions exist, use them
        if demo_contradictions:
            print(f"[DEMO MODE] Using {len(demo_contradictions)} pre-generated contradictions")
            return critiques, demo_contradictions

        # Find contradictions — compare papers with year differences
        pairs = []
        for i in range(len(papers)):
            for j in range(i + 1, len(papers)):
                year_diff = abs(papers[i].get("year", 2024) - papers[j].get("year", 2024))
                if year_diff >= 1:
                    pairs.append((i, j, year_diff))

        # Sort by year difference descending, cap at 10 pairs to avoid rate limits
        pairs.sort(key=lambda x: x[2], reverse=True)
        pairs = pairs[:10]

        contradictions = []
        for idx, (i, j, _) in enumerate(pairs):
            if progress_callback:
                progress_callback(f"contradiction_{idx+1}", len(pairs))
            result = self.detect_contradiction(papers[i], papers[j], critiques[i], critiques[j])
            if result.get("contradiction_detected"):
                contradictions.append(result)

        return critiques, contradictions


if __name__ == "__main__":
    from utils.paper_sources import search_all_sources
    papers = search_all_sources("AI rural healthcare", limit=3)
    agent = SkepticAgent()
    critiques, contradictions = agent.analyze_all(papers, topic="AI rural healthcare")
    print("Critiques:", len(critiques))
    print("Contradictions:", contradictions)
