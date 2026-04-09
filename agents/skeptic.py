from groq import Groq
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import GROQ_API_KEY, MODEL_NAME, MODEL_NAME_FAST, MODEL_NAME_REASONING, MAX_CONTRADICTION_PAIRS_FAST, FAST_CRITIQUE_BATCH_SIZE
from utils.prompts import CRITIQUE_PROMPT, CONTRADICTION_PROMPT
from demo_data import get_demo_topic, get_demo_data, DEMO_TOPICS


class SkepticAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    def critique_paper(self, paper: dict, topic: str = "", mode: str = "deep") -> dict:
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

        # Mode-aware model selection and retry timing
        model = MODEL_NAME_FAST if mode == "fast" else MODEL_NAME_REASONING
        retries = 3
        delays = [1, 2, 3] if mode == "fast" else [2, 5, 10]
        for attempt in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    model=model,
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
                # Validate credibility score using weighted formula
                result = self._compute_credibility(result)
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

    def _compute_credibility(self, critique: dict) -> dict:
        """Validate and correct credibility score using weighted formula."""
        try:
            # Sample size quality (30%)
            sample_raw = str(critique.get("sample_size", "not mentioned")).lower()
            if any(k in sample_raw for k in ["not mentioned", "none", "n/a", "unclear"]):
                sample_score = 0
            elif any(k in sample_raw for k in ["1000", "10000", "large", "million", "thousand"]):
                sample_score = 10
            elif any(k in sample_raw for k in ["100", "200", "300", "moderate", "hundred"]):
                sample_score = 5
            else:
                # Try to parse a number
                import re
                nums = re.findall(r'\d+', sample_raw.replace(',', ''))
                if nums:
                    n = int(nums[0])
                    sample_score = 10 if n >= 1000 else 5 if n >= 50 else 2
                else:
                    sample_score = 3

            # Dataset type (25%)
            dataset = str(critique.get("dataset_type", "not mentioned")).lower().strip()
            dataset_score = {"real": 10, "mixed": 6, "synthetic": 3}.get(dataset, 1)

            # Reproducibility (25%)
            repro = critique.get("reproducibility_score", 0)
            if isinstance(repro, str):
                try:
                    repro = int(str(repro).split("/")[0])
                except (ValueError, IndexError):
                    repro = 0
            repro = max(0, min(int(repro), 10))

            # Claim vs evidence alignment (20%)
            boldness = str(critique.get("boldness_vs_evidence", "")).lower().strip()
            boldness_score = {"appropriate": 10, "conservative": 8, "overclaimed": 3}.get(boldness, 5)

            # Compute weighted score
            computed = round(sample_score * 0.30 + dataset_score * 0.25 + repro * 0.25 + boldness_score * 0.20)
            computed = max(0, min(computed, 10))

            # Compare with LLM score
            llm_score = critique.get("credibility_score", 5)
            if isinstance(llm_score, str):
                try:
                    llm_score = int(str(llm_score).split("/")[0])
                except (ValueError, IndexError):
                    llm_score = 5
            llm_score = int(llm_score)

            # If deviation > 3, use computed score
            if abs(llm_score - computed) > 3:
                print(f"[SKEPTIC] Credibility correction: LLM={llm_score}, Computed={computed}, using computed")
                critique["credibility_score"] = computed
            else:
                critique["credibility_score"] = max(0, min(llm_score, 10))

        except Exception as e:
            print(f"[SKEPTIC] Credibility validation error: {e}")
            # Clamp existing score to 0-10
            score = critique.get("credibility_score", 5)
            try:
                score = int(str(score).split("/")[0])
            except (ValueError, IndexError, TypeError):
                score = 5
            critique["credibility_score"] = max(0, min(score, 10))

        return critique

    def analyze_batch(self, papers: list, topic: str = "", mode: str = "deep") -> list:
        """Analyze papers in parallel using ThreadPoolExecutor."""
        model = MODEL_NAME_FAST if mode == "fast" else MODEL_NAME_REASONING
        critiques = [None] * len(papers)

        def _critique_one(idx, paper):
            try:
                return idx, self.critique_paper(paper, topic)
            except Exception as e:
                print(f"[BATCH] Critique failed for paper {idx}: {e}")
                return idx, {
                    "sample_size": "not mentioned",
                    "dataset_type": "not mentioned",
                    "reproducibility_score": 0,
                    "credibility_score": 0,
                    "relevance_score": 0,
                    "influence_type": "application",
                    "boldness_vs_evidence": "overclaimed",
                    "red_flags": ["batch analysis failed"],
                    "main_claims": [],
                    "key_insight": "Analysis could not be completed",
                    "methodology_summary": "Error during batch critique",
                    "title": paper.get("title", ""),
                    "year": paper.get("year", 0)
                }

        max_workers = FAST_CRITIQUE_BATCH_SIZE if mode == "fast" else 3
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(_critique_one, i, p): i for i, p in enumerate(papers)}
                for future in as_completed(futures):
                    try:
                        idx, critique = future.result()
                        critiques[idx] = critique
                    except Exception as e:
                        idx = futures[future]
                        print(f"[BATCH] Future failed for paper {idx}: {e}")
                        critiques[idx] = {
                            "credibility_score": 0,
                            "relevance_score": 0,
                            "red_flags": ["analysis failed"],
                            "main_claims": [],
                            "title": papers[idx].get("title", ""),
                            "year": papers[idx].get("year", 0)
                        }
        except Exception as e:
            print(f"[BATCH] ThreadPoolExecutor error: {e}")
            # Fallback to sequential
            for i, p in enumerate(papers):
                if critiques[i] is None:
                    critiques[i] = self.critique_paper(p, topic)

        return critiques

    def analyze_all(self, papers: list, topic: str = "", progress_callback=None, mode: str = "deep") -> tuple[list, list]:
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
            critiques.append(self.critique_paper(p, topic, mode=mode))

        # If demo contradictions exist, use them
        if demo_contradictions:
            print(f"[DEMO MODE] Using {len(demo_contradictions)} pre-generated contradictions")
            return critiques, demo_contradictions

        # Find contradictions — compare papers with year differences
        pairs = []
        for i in range(len(papers)):
            for j in range(i + 1, len(papers)):
                # Smart filter: only compare papers with credibility >= 5
                cred_i = critiques[i].get("credibility_score", 0) if i < len(critiques) else 0
                cred_j = critiques[j].get("credibility_score", 0) if j < len(critiques) else 0
                if isinstance(cred_i, str):
                    try: cred_i = int(str(cred_i).split("/")[0])
                    except: cred_i = 0
                if isinstance(cred_j, str):
                    try: cred_j = int(str(cred_j).split("/")[0])
                    except: cred_j = 0
                if cred_i < 5 or cred_j < 5:
                    continue

                year_diff = abs(papers[i].get("year", 2024) - papers[j].get("year", 2024))
                if year_diff >= 1:
                    pairs.append((i, j, year_diff))

        # Sort by year difference descending, apply mode-specific caps
        pairs.sort(key=lambda x: x[2], reverse=True)
        max_pairs = MAX_CONTRADICTION_PAIRS_FAST if mode == "fast" else 10
        pairs = pairs[:max_pairs]

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
