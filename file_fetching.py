import requests
import xmltodict
import time
from datetime import datetime
import json
import os


COGNITIVE_TERMS = [
    "executive function",
    "working memory",
    "cognitive function",
    "cognitive control",
    "cognitive modelling",
    "cognitive modeling",
    "cognitive decline",
    "cognitive impairment",
]

METHODS_TERMS = [
    "reinforcement learning",
    "POMDP",
    "MDP",
    "Markov decision process",
    "Bayesian inference",
    "ecologically valid",
    "amortised inference",
    "amortized inference",
    "computational psychiatry",
    "active inference",
    "predictive coding",
    "parameter estimation",
    "parameter identification",
    "model fitting",
    "model validation",
    "virtual environment",
    "virtual reality task",
    "digital biomarker",
    "eye tracking",
    "EEG",
    "behavioural assessment",
    "cognitive assessment",
]

ARXIV_QUERY = (
    "("
    + " OR ".join(f'abs:"{t}"' for t in COGNITIVE_TERMS)
    + ") AND ("
    + " OR ".join(f'abs:"{t}"' for t in METHODS_TERMS)
    + ")"
)

S2_QUERY = (
    "(" + " | ".join(f'"{t}"' for t in COGNITIVE_TERMS) + ") "
    "(" + " | ".join(f'"{t}"' for t in METHODS_TERMS) + ")"
)

HISTORY_FILE = "paper_history.json"
TODAYS_PAPERS = "todays_papers.json"
OUTPUT_FILE = "todays_fetched_papers.txt"



def fetch_arxiv(query, max_results=100):
    parameters = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }
    results = requests.get("http://export.arxiv.org/api/query", params=parameters)
    dict_answer = xmltodict.parse(results.text)

    entries = dict_answer.get("feed", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]

    papers = []
    for paper in entries:
        title = paper["title"].strip()
        link = paper["link"][0]["@href"]
        summary = paper["summary"].strip()
        papers.append([title, link, summary])
    return papers


def fetch_semantic_scholar(query, max_results=100):
    url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    params = {
        "query": query,
        "fields": "title,abstract,url,externalIds",
        "sort": "publicationDate:desc",
    }

    papers = []
    token = None

    while len(papers) < max_results:
        if token:
            params["token"] = token

        response = requests.get(url, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        for paper in data.get("data", []):
            title = (paper.get("title") or "").strip()
            if not title:
                continue
            link = paper.get("url") or ""
            summary = (paper.get("abstract") or "").strip()
            papers.append([title, link, summary])

        token = data.get("token")
        if not token:
            break

        time.sleep(1)  
    return papers[:max_results]


def main():
    with open(HISTORY_FILE, "r") as file:
        history_json = json.load(file)

    if not os.path.exists(TODAYS_PAPERS) or os.path.getsize(TODAYS_PAPERS) == 0:
        todays_json = {"papers": []}
    else:
        with open(TODAYS_PAPERS, "r") as file:
            todays_json = json.load(file)

    previous_titles = {paper["title"] for paper in history_json["papers"]}
    todays_titles = {paper["title"] for paper in todays_json["papers"]}

    arxiv_papers = fetch_arxiv(ARXIV_QUERY)
    print(f"arXiv: {len(arxiv_papers)} candidates")

    s2_papers = fetch_semantic_scholar(S2_QUERY)
    print(f"Semantic Scholar: {len(s2_papers)} candidates")

    all_papers = arxiv_papers + s2_papers

    with open(OUTPUT_FILE, "w"):
        pass

    seen_this_run = set()

    for paper_data in all_papers:
        title = paper_data[0]

        if title in previous_titles or title in todays_titles or title in seen_this_run:
            continue

        seen_this_run.add(title)

        with open(OUTPUT_FILE, "a+", encoding="utf-8") as f:
            f.write(f"Title: {paper_data[0]}\n")
            f.write(f"Link: {paper_data[1]}\n")
            f.write(f"Summary: {paper_data[2]}\n")
            f.write(f"DateAdded: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("---------------------------------------------------------------------------\n")

    print(f"New papers written: {len(seen_this_run)}")


if __name__ == "__main__":
    main()