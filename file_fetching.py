import requests
import xmltodict
import time
from datetime import datetime
import json
import os


# Papers are fetched in separate streams, each with its own quota.
# A paper must match at least one term from "constructs" AND at least one from "methods".
# Splitting into streams stops a high volume topic (clinical EEG) from filling
# every slot and pushing out a low volume topic (computational modelling).

EF_CONSTRUCTS = [
    "executive function",
    "executive functions",
    "working memory",
    "cognitive control",
    "cognitive flexibility",
    "inhibitory control",
    "task switching",
    "human planning",
    "sequential planning",
    "human decision making",
    "goal directed behaviour",
    "goal directed behavior",
    "selective attention",
    "attentional control",
]

MODELLING_METHODS = [
    "computational model",
    "computational models",
    "computational modelling",
    "computational modeling",
    "cognitive model",
    "cognitive models",
    "cognitive modelling",
    "cognitive modeling",
    "process model",
    "resource rational",
    "resource rationality",
    "bounded rationality",
    "drift diffusion",
    "evidence accumulation",
    "reinforcement learning",
    "POMDP",
    "Markov decision process",
    "Bayesian inference",
    "Bayesian observer",
    "active inference",
    "predictive coding",
    "amortised inference",
    "amortized inference",
    "simulation based inference",
    "parameter estimation",
    "parameter recovery",
    "model fitting",
    "computational psychiatry",
]

NEURO_METHODS = [
    "EEG",
    "MEG",
    "fMRI",
    "frontal theta",
    "frontal midline theta",
    "prefrontal cortex",
    "frontoparietal",
    "neural correlates",
    "electrophysiology",
]

CLINICAL_CONSTRUCTS = [
    "cognitive impairment",
    "cognitive decline",
    "cognitive assessment",
    "executive dysfunction",
    "neuropsychological assessment",
]

BIOMARKER_METHODS = [
    "eye tracking",
    "digital biomarker",
    "digital biomarkers",
    "virtual reality",
    "virtual environment",
    "serious game",
    "behavioural task",
    "behavioral task",
    "EEG",
]

# Modelling gets the largest quota because it is the rarest in the literature.
STREAMS = {
    "modelling": {"constructs": EF_CONSTRUCTS, "methods": MODELLING_METHODS, "arxiv_max": 80, "s2_max": 80},
    "neuro": {"constructs": EF_CONSTRUCTS, "methods": NEURO_METHODS, "arxiv_max": 30, "s2_max": 30},
    "biomarker": {"constructs": CLINICAL_CONSTRUCTS, "methods": BIOMARKER_METHODS, "arxiv_max": 30, "s2_max": 30},
}

HISTORY_FILE = "paper_history.json"
TODAYS_PAPERS = "todays_papers.json"
OUTPUT_FILE = "todays_fetched_papers.txt"

ARXIV_HEADERS = {
    "User-Agent": "Litbot/1.0"
}

S2_HEADERS = {}
if os.environ.get("S2_API_KEY"):
    S2_HEADERS["x-api-key"] = os.environ["S2_API_KEY"]


def arxiv_query(constructs, methods):
    return (
        "("
        + " OR ".join(f'abs:"{t}"' for t in constructs)
        + ") AND ("
        + " OR ".join(f'abs:"{t}"' for t in methods)
        + ")"
    )


def s2_query(constructs, methods):
    # Semantic Scholar bulk syntax: | is OR, whitespace is AND, quotes are phrases.
    # Never use hyphens in terms, a leading hyphen means NOT in this syntax.
    return (
        "(" + " | ".join(f'"{t}"' for t in constructs) + ") "
        "(" + " | ".join(f'"{t}"' for t in methods) + ")"
    )


def normalise(title):
    return " ".join(title.lower().split())


def fetch_arxiv(query, max_results):
    """Return a list of papers, or None if arXiv failed so the caller can stop
    querying arXiv for the rest of this run instead of hammering it."""
    parameters = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }

    try:
        response = requests.get(
            "https://export.arxiv.org/api/query",
            params=parameters,
            headers=ARXIV_HEADERS,
            timeout=30,
        )
    except requests.exceptions.RequestException as exc:
        print(f"arXiv request raised {exc!r}")
        return None

    text = response.text.strip()
    if response.status_code != 200 or not text.startswith("<?xml"):
        print(f"arXiv did not return XML: {text[:200]!r}")
        return None

    dict_answer = xmltodict.parse(text)
    entries = dict_answer.get("feed", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]

    papers = []
    for paper in entries:
        title = " ".join(paper["title"].split())
        link_field = paper.get("link")
        if isinstance(link_field, list):
            link = link_field[0]["@href"]
        elif isinstance(link_field, dict):
            link = link_field["@href"]
        else:
            link = ""
        summary = (paper.get("summary") or "").strip()
        papers.append([title, link, summary])
    return papers


def s2_get(url, params, attempts=3):
    """GET with a short backoff on 429, since the keyless pool is shared and busy."""
    for attempt in range(attempts):
        try:
            response = requests.get(url, params=params, headers=S2_HEADERS, timeout=30)
        except requests.exceptions.RequestException as exc:
            print(f"Semantic Scholar request raised {exc!r}")
            return None
        if response.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"Semantic Scholar rate limited, waiting {wait}s")
            time.sleep(wait)
            continue
        return response
    return None


def fetch_semantic_scholar(query, max_results):
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

        response = s2_get(url, params)
        if response is None or response.status_code != 200:
            if response is not None:
                print(f"Semantic Scholar request failed: {response.status_code} {response.text[:200]!r}")
            break

        data = response.json()
        for paper in data.get("data", []):
            title = " ".join((paper.get("title") or "").split())
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

    already_seen = {normalise(p["title"]) for p in history_json["papers"]}
    already_seen |= {normalise(p["title"]) for p in todays_json["papers"]}

    all_papers = []
    arxiv_ok = True

    for name, stream in STREAMS.items():
        if arxiv_ok:
            arxiv_papers = fetch_arxiv(arxiv_query(stream["constructs"], stream["methods"]), stream["arxiv_max"])
            if arxiv_papers is None:
                arxiv_ok = False
                arxiv_papers = []
                print("Skipping arXiv for the rest of this run")
            time.sleep(3)  # arXiv asks for at least 3 seconds between calls
        else:
            arxiv_papers = []

        s2_papers = fetch_semantic_scholar(s2_query(stream["constructs"], stream["methods"]), stream["s2_max"])

        print(f"[{name}] arXiv: {len(arxiv_papers)}  Semantic Scholar: {len(s2_papers)}")
        all_papers.extend(arxiv_papers + s2_papers)

    open(OUTPUT_FILE, "w").close()

    seen_this_run = set()
    written = 0

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for title, link, summary in all_papers:
            key = normalise(title)
            if key in already_seen or key in seen_this_run:
                continue
            seen_this_run.add(key)
            written += 1

            f.write(f"Title: {title}\n")
            f.write(f"Link: {link}\n")
            f.write(f"Summary: {summary}\n")
            f.write(f"DateAdded: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("---------------------------------------------------------------------------\n")

    print(f"New papers written: {written}")


if __name__ == "__main__":
    main()