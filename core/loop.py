import uuid
import time
from statistics import mean
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.paper_sources import search_all_sources, search_multiple_queries, search_all_sources_fast
from agents.planner import PlannerAgent
from agents.skeptic import SkepticAgent
from agents.cartographer import CartographerAgent
from agents.archivist import ArchivistAgent
from core.thinking import ThinkingFeed
from config import CONFIDENCE_THRESHOLD, MAX_DEPTH_FAST, MAX_DEPTH_DEEP, FAST_PAPERS_PER_QUERY, DEEP_PAPERS_PER_QUERY, FAST_MODE_TIMEOUT


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
        self.thinking_feed = ThinkingFeed()
        self._start_time = None
        self.perf_metrics = {"step_times": [], "api_calls": 0, "total_elapsed": 0}

    def _time_remaining(self):
        """Returns seconds remaining before FAST_MODE_TIMEOUT. Only active in fast mode."""
        if self.mode != "fast" or self._start_time is None:
            return float('inf')
        elapsed = time.time() - self._start_time
        return max(FAST_MODE_TIMEOUT - elapsed, 0)

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
        total = round(coverage + consistency + credibility, 2)
        # If avg credibility is very low, cap confidence
        avg_cred = mean(scores) if scores else 5.0
        if avg_cred < 4:
            total = min(total, 0.60)
        return total

    def run(self, progress_callback=None) -> dict:
        self._start_time = time.time()

        def update(msg):
            if progress_callback:
                progress_callback(msg, self.confidence, self.depth)

        total_steps = self.max_depth + 3  # plan + loop iterations + graph + report

        # Step 1: Plan
        step_start = time.time()
        update("🧠 Planner Agent: Decomposing topic into research sub-questions...")
        plan = self.planner.plan(self.topic)
        queries = plan.get("search_queries", [self.topic])
        self.sub_questions = plan.get("sub_questions", [])
        self.perf_metrics["step_times"].append({"step": "planning", "duration": round(time.time() - step_start, 2)})
        self.perf_metrics["api_calls"] += 1

        # Thinking event: Planner
        self.thinking_feed.emit_planner(
            "Topic Decomposed",
            f"Sub-questions: {self.sub_questions}",
            "Step 1/5"
        )

        # Step 2: Agentic Loop
        while self.confidence < CONFIDENCE_THRESHOLD and self.depth < self.max_depth:
            # Timeout check: if nearing limit, gracefully stop and use current data
            if self._time_remaining() < 15:
                update("⏱️ Nearing time limit — generating output with current data...")
                self.thinking_feed.emit("loop", "decision",
                    "⏱️ Timeout approaching — graceful stop",
                    f"Time remaining: {self._time_remaining():.0f}s | Papers: {len(self.all_papers)}"
                )
                break

            query = queries[self.depth] if self.depth < len(queries) else self.topic
            source_label = "OpenAlex + CrossRef + SemanticScholar"
            update(f"📡 Fetching papers from {source_label}... (Depth {self.depth + 1}/{self.max_depth}, Query: '{query[:50]}')")

            fetch_start = time.time()
            # Use fast fetching in fast mode
            if self.mode == "fast":
                new_papers = self._deduplicate(
                    search_all_sources_fast(query, self.papers_per_query)
                )
            else:
                new_papers = self._deduplicate(
                    search_all_sources(query, self.papers_per_query)
                )
            self.perf_metrics["step_times"].append({"step": f"fetch_depth_{self.depth+1}", "duration": round(time.time() - fetch_start, 2)})

            # Thinking event: Fetch
            self.thinking_feed.emit("loop", "fetch",
                f"Fetched {len(new_papers)} papers",
                f"Query: {query[:50]} | Depth: {self.depth + 1}",
                "Step 2/5"
            )

            if not new_papers:
                update(f"⚠️ No new papers found at depth {self.depth + 1}. Advancing...")
                self.depth += 1
                continue

            update(f"🔍 Skeptic Agent: Analyzing {len(new_papers)} papers for methodology quality...")

            def skeptic_progress(current, total):
                if isinstance(current, str) and current.startswith("contradiction"):
                    update(f"⚔️ Checking paper contradictions ({current})...")
                    self.thinking_feed.emit_comparator(
                        f"Comparing paper pair {current}",
                        f"Checking for conflicting claims",
                        f"{current}/{total} pairs"
                    )
                else:
                    update(f"🔍 Skeptic Agent: Analyzing paper {current}/{total}...")
                    # Emit per-paper thinking event
                    if current <= len(new_papers):
                        p = new_papers[current - 1]
                        self.thinking_feed.emit_skeptic(
                            f"Analyzing: {p.get('title', '')[:50]}",
                            f"Year: {p.get('year', '?')} | Source: {p.get('source', '?')}",
                            f"Paper {current}/{total}"
                        )

            analyze_start = time.time()
            critiques, contradictions = self.skeptic.analyze_all(
                new_papers, topic=self.topic, progress_callback=skeptic_progress, mode=self.mode
            )
            self.perf_metrics["step_times"].append({"step": f"analyze_depth_{self.depth+1}", "duration": round(time.time() - analyze_start, 2)})
            self.perf_metrics["api_calls"] += len(new_papers) + len([c for c in contradictions if c.get("contradiction_detected")])

            # Emit per-paper credibility results
            for ci, crit in enumerate(critiques):
                cred = crit.get("credibility_score", 0)
                flags = crit.get("red_flags", [])
                self.thinking_feed.emit_skeptic(
                    f"Result: {crit.get('title', '')[:50]}",
                    f"Credibility: {cred}/10 | Flags: {len(flags)}",
                    f"Paper {ci+1}/{len(critiques)}"
                )

            self.all_papers.extend(new_papers)
            self.all_critiques.extend(critiques)
            self.all_contradictions.extend(contradictions)

            self.confidence = self._calculate_confidence()
            pct = int((self.depth + 1) / total_steps * 100)

            # Thinking event: Contradiction results
            self.thinking_feed.emit_comparator(
                f"{len(contradictions)} contradictions detected",
                f"Compared credible paper pairs at depth {self.depth + 1}",
                "Step 4/5"
            )

            if contradictions:
                update(f"🚨 {len(contradictions)} contradiction(s) detected in the literature!")
            else:
                update(f"✅ Depth {self.depth + 1} complete. Confidence: {self.confidence:.0%}")

            if self.confidence < CONFIDENCE_THRESHOLD:
                # Dynamic depth skip: if Fast Mode and confidence > 0.65 after depth 1,
                # skip remaining depths to save time
                if self.mode == "fast" and self.confidence > 0.65 and self.depth >= 1:
                    update(f"⚡ Fast Mode: Good coverage ({self.confidence:.0%}). Skipping remaining depths...")
                    self.thinking_feed.emit("loop", "decision",
                        "⚡ Dynamic depth skip — sufficient Fast coverage",
                        f"Confidence: {self.confidence:.0%} > 65% threshold at depth {self.depth + 1}"
                    )
                    self.depth += 1
                    break
                update(f"🤔 AI decides: Coverage insufficient ({self.confidence:.0%}). Expanding search...")
                self.thinking_feed.emit("loop", "decision",
                    "🔍 Coverage insufficient — expanding search",
                    f"Confidence: {self.confidence:.0%} → need {CONFIDENCE_THRESHOLD:.0%}"
                )
            else:
                update(f"🎯 AI decides: Sufficient coverage reached ({self.confidence:.0%}). Stopping loop.")
                self.thinking_feed.emit("loop", "decision",
                    "🎯 Sufficient coverage reached — stopping loop",
                    f"Confidence: {self.confidence:.0%} | Depth: {self.depth + 1}"
                )

            self.depth += 1

        # Step 3: Build graph
        update("📊 Cartographer: Building knowledge graph...")
        graph_path = self.cartographer.build_graph(
            self.all_papers, self.all_critiques, self.all_contradictions
        )
        self.thinking_feed.emit_cartographer(
            "Knowledge graph built",
            f"{len(self.all_papers)} nodes | {len(self.all_contradictions)} conflict edges",
            "Step 5/5"
        )

        # Step 4: Save to SQLite
        self.archivist.save_session(self.session_id, self.topic, self.mode, self.confidence, self.depth)
        self.archivist.save_papers(self.session_id, self.all_papers, self.all_critiques)
        self.archivist.save_contradictions(self.session_id, self.all_contradictions)

        # Step 5: Generate output
        update("✍️ Archivist: Generating report...")
        self.thinking_feed.emit_archivist(
            "Generating report",
            f"Mode: {self.mode} | Papers: {len(self.all_papers)}",
            "Finalizing"
        )
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
        elapsed = time.time() - self._start_time
        self.perf_metrics["total_elapsed"] = round(elapsed, 2)
        result["perf_metrics"] = self.perf_metrics
        update(f"✅ Analysis complete! {len(self.all_papers)} papers analyzed across {self.depth} depth iterations. ({elapsed:.1f}s)")
        return result


if __name__ == "__main__":
    loop = ResearchLoop("transformer attention mechanisms", "fast")
    result = loop.run(
        progress_callback=lambda msg, conf, depth: print(f"[Depth {depth}] {msg} | Confidence: {conf:.0%}")
    )
    print("\nFINAL RESULT:")
    import json
    print(json.dumps(result, indent=2))
