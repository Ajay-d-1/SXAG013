import requests
import time

from demo_data import get_demo_topic, get_demo_data


def search_papers(query: str, limit: int = 15, offset: int = 0) -> list[dict]:
    """Search papers from Semantic Scholar API or return demo data if topic matches."""
    # Check for demo topic first
    demo_topic = get_demo_topic(query)
    if demo_topic:
        print(f"[DEMO MODE] Using pre-loaded papers for: {demo_topic}")
        data = get_demo_data(demo_topic)
        if data:
            return data.get("papers", [])[:limit]
    
    """Search papers from Semantic Scholar API."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "fields": "title,abstract,year,authors,citationCount,externalIds"
    }
    
    retries = 3
    delays = [2, 5, 10]
    papers = []
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 429:
                print(f"Semantic Scholar rate limit hit. Retrying in {delays[attempt]}s...")
                time.sleep(delays[attempt])
                continue
            response.raise_for_status()
            data = response.json()
            papers = data.get("data", [])
            break
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delays[attempt])
            else:
                print(f"Error fetching papers after 3 attempts: {e}")
                return []
        
    # Filter papers with valid abstracts
    filtered = []
    for paper in papers:
        abstract = paper.get("abstract")
        if abstract and len(abstract) >= 50:
            filtered.append(paper)
    
    time.sleep(1)  # Rate limiting
    return filtered


def search_multiple_queries(queries: list[str], papers_per_query: int = 10) -> list[dict]:
    """Search multiple queries and merge results, removing duplicates.
    
    If first query matches a demo topic, returns demo papers immediately
    without making API calls.
    """
    # Check if first query is a demo topic
    if queries:
        demo_topic = get_demo_topic(queries[0])
        if demo_topic:
            data = get_demo_data(demo_topic)
            if data:
                print(f"[DEMO MODE] Returning {len(data.get('papers', []))} papers for: {demo_topic}")
                return data.get("papers", [])
    
    all_papers = []
    seen_titles = set()
    
    for query in queries:
        papers = search_papers(query, limit=papers_per_query)
        for paper in papers:
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_papers.append(paper)
    
    return all_papers


if __name__ == "__main__":
    papers = search_papers("AI rural healthcare", limit=5)
    for p in papers:
        print(f"{p['year']} — {p['title'][:80]}")
