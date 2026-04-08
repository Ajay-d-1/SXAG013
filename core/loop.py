import uuid
from statistics import mean
from utils.paper_sources import search_all_sources, search_multiple_queries
from agents.planner import PlannerAgent
from agents.skeptic import SkepticAgent
from agents.cartographer import CartographerAgent
from agents.archivist import ArchivistAgent
from config import CONFIDENCE_THRESHOLD, MAX_DEPTH_FAST, MAX_DEPTH_DEEP, FAST_PAPERS_PER_QUERY, DEEP_PAPERS_PER_QUERY


class ResearchLoop:
    def __init__(self, topic: str, mode: str = "fast"):
        self.topic = topic
        self.mode = mode
        self.session_id = str(uuid.uuid4())[:8]
        self.confidence = 0.0
        self.depth = 0
        self.max_depth = MAX_DEPTH_DEEP if mode == "deep" else MAX_DEPTH_FAST
        self.papers_per_query = DEEP_PAPERS_PER_QUERY if mode == "deep" else FAST_PAPERS_PER_QUERY
        self.all_papers = []
        self.all_critiques = []
        self.all_contradictions = []
        self.planner = PlannerAgent()
        self.skeptic = SkepticAgent()
        self.cartographer = CartographerAgent()
        self.archivist = ArchivistAgent()
        self.sub_questions = []

    def _deduplicate(self, new_papers):
        existing_titles = {p["title"].lower().strip() for p in self.all_papers}
        return [p for p in new_papers if p.get("title", "").lower().strip() not in existing_titles]

    def _calculate_confidence(self):
        if not self.all_papers:
            return 0.0
        target = 20 if self.mode == "deep" else 12
        coverage = min(len(self.all_papers) / target, 1.0) * 0.40
        contradiction_ratio = len(self.all_contradictions) / max(len(self.all_papers), 1)
        consistency = max(1 - contradiction_ratio, 0) * 0.35

        scores = []
        for c in self.all_critiques:
            score = c.get("credibility_score", 5)
            if isinstance(score, str):
                try:
                    score = float(score.split("/")[0])
                except (ValueError, IndexError):
                    score = 5.0
            try:
                scores.append(float(score))
            except (ValueError, TypeError):
                scores.append(5.0)

        credibility = (mean(scores) / 10) * 0.25 if scores else 0.125
        return round(coverage + consistency + credibility, 2)

    def run(self, progress_callback=None) -> dict:
        def update(msg):
            if progress_callback:
                progress_callback(msg, self.confidence, self.depth)

        total_steps = self.max_depth + 3  # plan + loop iterations + graph + report

        # Step 1: Plan
        update("🧠 Planner Agent: Decomposing topic into research sub-questions...")
        plan = self.planner.plan(self.topic)
        queries = plan.get("search_queries", [self.topic])
        self.sub_questions = plan.get("sub_questions", [])

        # Step 2: Agentic Loop
        while self.confidence < CONFIDENCE_THRESHOLD and self.depth < self.max_depth:
            query = queries[self.depth] if self.depth < len(queries) else self.topic
            source_label = "OpenAlex + CrossRef"
            update(f"📡 Fetching papers from {source_label}... (Depth {self.depth + 1}/{self.max_depth}, Query: '{query[:50]}')")

            new_papers = self._deduplicate(
                search_all_sources(query, self.papers_per_query)
            )

            if not new_papers:
                update(f"⚠️ No new papers found at depth {self.depth + 1}. Advancing...")
                self.depth += 1
                continue

            update(f"🔍 Skeptic Agent: Analyzing {len(new_papers)} papers for methodology quality...")

            def skeptic_progress(current, total):
                if isinstance(current, str) and current.startswith("contradiction"):
                    update(f"⚔️ Checking paper contradictions ({current})...")
                else:
                    update(f"🔍 Skeptic Agent: Analyzing paper {current}/{total}...")

            critiques, contradictions = self.skeptic.analyze_all(
                new_papers, topic=self.topic, progress_callback=skeptic_progress
            )

            self.all_papers.extend(new_papers)
            self.all_critiques.extend(critiques)
            self.all_contradictions.extend(contradictions)

            self.confidence = self._calculate_confidence()
            pct = int((self.depth + 1) / total_steps * 100)

            if contradictions:
                update(f"🚨 {len(contradictions)} contradiction(s) detected in the literature!")
            else:
                update(f"✅ Depth {self.depth + 1} complete. Confidence: {self.confidence:.0%}")

            if self.confidence < CONFIDENCE_THRESHOLD:
                update(f"🤔 AI decides: Coverage insufficient ({self.confidence:.0%}). Expanding search...")
            else:
                update(f"🎯 AI decides: Sufficient coverage reached ({self.confidence:.0%}). Stopping loop.")

            self.depth += 1

        # Step 3: Build graph
        update("📊 Cartographer: Building knowledge graph...")
        graph_path = self.cartographer.build_graph(
            self.all_papers, self.all_critiques, self.all_contradictions
        )

        # Step 4: Save to SQLite
        self.archivist.save_session(self.session_id, self.topic, self.mode, self.confidence, self.depth)
        self.archivist.save_papers(self.session_id, self.all_papers, self.all_critiques)
        self.archivist.save_contradictions(self.session_id, self.all_contradictions)

        # Step 5: Generate output
        update("✍️ Archivist: Generating report...")
        if self.mode == "fast":
            result = self.archivist.generate_fast_summary(
                self.topic, self.all_papers, self.all_critiques,
                self.all_contradictions, self.confidence
            )
        else:
            result = self.archivist.generate_deep_report(
                self.topic, self.all_papers, self.all_critiques, self.all_contradictions
            )

        result["graph_path"] = graph_path
        result["session_id"] = self.session_id
        update(f"✅ Analysis complete! {len(self.all_papers)} papers analyzed across {self.depth} depth iterations.")
        return result


if __name__ == "__main__":
    loop = ResearchLoop("transformer attention mechanisms", "fast")
    result = loop.run(
        progress_callback=lambda msg, conf, depth: print(f"[Depth {depth}] {msg} | Confidence: {conf:.0%}")
    )
    print("\nFINAL RESULT:")
    import json
    print(json.dumps(result, indent=2))
