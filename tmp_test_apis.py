import requests
import xml.etree.ElementTree as ET

def test_arxiv():
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": "all:ai in education", "start": 0, "max_results": 2}
    resp = requests.get(url, params=params)
    root = ET.fromstring(resp.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        abstract = entry.find('atom:summary', ns).text.strip()
        published = entry.find('atom:published', ns).text[:4]
        print(f"ArXiv: {title} ({published})")

def test_crossref():
    url = "https://api.crossref.org/works"
    params = {"query": "ai in education", "select": "title,abstract,issued", "rows": 2}
    resp = requests.get(url, params=params)
    data = resp.json()
    for item in data['message']['items']:
        title = item.get('title', [''])[0]
        year = item.get('issued', {}).get('date-parts', [[0]])[0][0]
        print(f"Crossref: {title} ({year})")

if __name__ == "__main__":
    test_arxiv()
    test_crossref()
