"""
Multi-source academic paper fetching engine.
Sources: OpenAlex (primary), CrossRef (secondary), Semantic Scholar (fallback).
All free APIs with generous limits.
"""

import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from demo_data import get_demo_topic, get_demo_data

OPENALEX_EMAIL = "scholarpulse@research.ai"
HEADERS_CROSSREF = {
    "User-Agent": f"ScholARPulse/1.0 (mailto:{OPENALEX_EMAIL})"
}


def _normalize_openalex(work: dict) -> dict:
    """Normalize an OpenAlex work into our standard schema."""
    title = work.get("title", "") or ""
    abstract_index = work.get("abstract_inverted_index")
    abstract = ""
    if abstract_index:
        # Reconstruct abstract from inverted index
        word_positions = []
        for word, positions in abstract_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join([w for _, w in word_positions])

    authors = []
    for authorship in work.get("authorships", [])[:5]:
        author = authorship.get("author", {})
        name = author.get("display_name", "")
        if name:
            authors.append(name)

    year = work.get("publication_year", 0) or 0
    venue = ""
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    venue = source.get("display_name", "") or ""

    cited_by = work.get("cited_by_count", 0) or 0
    doi = work.get("doi", "") or ""
    url = doi if doi else work.get("id", "")

    return {
        "title": title,
        "abstract": abstract,
        "year": year,
        "authors": authors,
        "venue": venue,
        "url": url,
        "citation_count": cited_by,
        "source": "OpenAlex"
    }


def _normalize_crossref(item: dict) -> dict:
    """Normalize a CrossRef work into our standard schema."""
    title_list = item.get("title", [""])
    title = title_list[0] if title_list else ""
    abstract = item.get("abstract", "") or ""
    # CrossRef sometimes returns HTML in abstracts
    abstract = re.sub(r"<[^>]+>", "", abstract).strip()

    authors = []
    for author in item.get("author", [])[:5]:
        given = author.get("given", "")
        family = author.get("family", "")
        if given and family:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)

    year = 0
    published = item.get("published-print") or item.get("published-online") or item.get("created")
    if published and "date-parts" in published:
        parts = published["date-parts"]
        if parts and parts[0]:
            year = parts[0][0] or 0

    venue = ""
    container = item.get("container-title", [])
    if container:
        venue = container[0]

    doi = item.get("DOI", "")
    url = f"https://doi.org/{doi}" if doi else ""
    cited_by = item.get("is-referenced-by-count", 0) or 0

    return {
        "title": title,
        "abstract": abstract,
        "year": year,
        "authors": authors,
        "venue": venue,
        "url": url,
        "citation_count": cited_by,
        "source": "CrossRef"
    }


def search_openalex(query: str, limit: int = 15, timeout: int = 15) -> list[dict]:
    """Search OpenAlex API — free, 100K req/day with email."""
    try:
        url = "https://api.openalex.org/works"
        params = {
            "search": query,
            "per_page": min(limit, 50),
            "mailto": OPENALEX_EMAIL,
            "select": "id,title,abstract_inverted_index,publication_year,authorships,primary_location,cited_by_count,doi"
        }
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        papers = [_normalize_openalex(w) for w in results]
        # Filter papers with abstracts
        return [p for p in papers if p["abstract"] and len(p["abstract"]) >= 50]
    except Exception as e:
        print(f"[OpenAlex] Error: {e}")
        return []


def search_crossref(query: str, limit: int = 15, timeout: int = 15) -> list[dict]:
    """Search CrossRef API — free, polite pool with email header."""
    try:
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": min(limit, 50),
            "select": "DOI,title,abstract,author,published-print,published-online,created,container-title,is-referenced-by-count"
        }
        response = requests.get(url, params=params, headers=HEADERS_CROSSREF, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        items = data.get("message", {}).get("items", [])
        papers = [_normalize_crossref(item) for item in items]
        return [p for p in papers if p["abstract"] and len(p["abstract"]) >= 50 and p["title"]]
    except Exception as e:
        print(f"[CrossRef] Error: {e}")
        return []


def search_semantic_scholar(query: str, limit: int = 15, timeout: int = 15) -> list[dict]:
    """Search Semantic Scholar API — fallback source."""
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": "title,abstract,year,authors,citationCount,venue,externalIds,url"
        }
        response = requests.get(url, params=params, timeout=timeout)
        if response.status_code == 429:
            print("[SemanticScholar] Rate limited, skipping.")
            return []
        response.raise_for_status()
        data = response.json()
        papers = []
        for item in data.get("data", []):
            abstract = item.get("abstract", "") or ""
            if not abstract or len(abstract) < 50:
                continue
            authors = [a.get("name", "") for a in (item.get("authors") or [])[:5]]
            papers.append({
                "title": item.get("title", ""),
                "abstract": abstract,
                "year": item.get("year", 0) or 0,
                "authors": authors,
                "venue": item.get("venue", "") or "",
                "url": item.get("url", "") or "",
                "citation_count": item.get("citationCount", 0) or 0,
                "source": "SemanticScholar"
            })
        return papers
    except Exception as e:
        print(f"[SemanticScholar] Error: {e}")
        return []


def _deduplicate_papers(papers: list[dict]) -> list[dict]:
    """Deduplicate papers by normalized title."""
    seen = set()
    unique = []
    for paper in papers:
        key = paper.get("title", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(paper)
    return unique


def search_all_sources(query: str, limit: int = 15) -> list[dict]:
    """
    Search multiple academic sources in parallel and merge results.
    Returns deduplicated papers sorted by citation count.
    Demo mode interception is handled here.
    """
    # Demo mode check
    demo_topic = get_demo_topic(query)
    if demo_topic:
        data = get_demo_data(demo_topic)
        if data:
            print(f"[DEMO MODE] Returning {len(data.get('papers', []))} papers for: {demo_topic}")
            return data.get("papers", [])

    all_papers = []

    # Parallel fetch from OpenAlex + CrossRef + Semantic Scholar (all 3)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(search_openalex, query, limit): "OpenAlex",
            executor.submit(search_crossref, query, limit): "CrossRef",
            executor.submit(search_semantic_scholar, query, limit): "SemanticScholar",
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                papers = future.result()
                print(f"[{source}] Fetched {len(papers)} papers")
                all_papers.extend(papers)
            except Exception as e:
                print(f"[{source}] Failed: {e}")

    # Deduplicate and sort by citation count
    unique = _deduplicate_papers(all_papers)
    unique.sort(key=lambda p: p.get("citation_count", 0), reverse=True)

    return unique[:limit]


def search_multiple_queries(queries: list[str], papers_per_query: int = 10) -> list[dict]:
    """
    Search multiple queries across all sources and merge results.
    Demo mode interception for the first query.
    """
    # Demo mode check on first query
    if queries:
        demo_topic = get_demo_topic(queries[0])
        if demo_topic:
            data = get_demo_data(demo_topic)
            if data:
                print(f"[DEMO MODE] Returning {len(data.get('papers', []))} papers for: {demo_topic}")
                return data.get("papers", [])

    all_papers = []
    for query in queries:
        papers = search_all_sources(query, papers_per_query)
        all_papers.extend(papers)

    return _deduplicate_papers(all_papers)

def search_all_sources_fast(query: str, limit: int = 8) -> list[dict]:
    """
    Fast mode variant: shorter timeouts (8s), all 3 sources in parallel.
    Favors speed over completeness.
    """
    # Demo mode check
    demo_topic = get_demo_topic(query)
    if demo_topic:
        data = get_demo_data(demo_topic)
        if data:
            print(f"[DEMO MODE FAST] Returning {len(data.get('papers', []))} papers for: {demo_topic}")
            return data.get("papers", [])

    all_papers = []
    fast_timeout = 8

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(search_openalex, query, limit, fast_timeout): "OpenAlex",
            executor.submit(search_crossref, query, limit, fast_timeout): "CrossRef",
            executor.submit(search_semantic_scholar, query, limit, fast_timeout): "SemanticScholar",
        }
        for future in as_completed(futures):
            source = futures[future]
            try:
                papers = future.result()
                print(f"[FAST {source}] Fetched {len(papers)} papers")
                all_papers.extend(papers)
            except Exception as e:
                print(f"[FAST {source}] Failed: {e}")

    unique = _deduplicate_papers(all_papers)
    unique.sort(key=lambda p: p.get("citation_count", 0), reverse=True)
    return unique[:limit]


if __name__ == "__main__":
    print("Testing multi-source paper search...")
    papers = search_all_sources("transformer attention mechanisms", limit=10)
    for p in papers:
        print(f"  [{p['source']}] {p['year']} — {p['title'][:70]}... (cited: {p['citation_count']})")
    print(f"\nTotal: {len(papers)} unique papers")
