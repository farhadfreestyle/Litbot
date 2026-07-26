import requests
import xmltodict
from datetime import datetime
import json

query = (
    '('
        'abs:"executive function" OR abs:"working memory" OR abs:"cognitive control" '
        'OR abs:"decision making" OR abs:"decision-making" OR abs:"planning behavior" '
        'OR abs:"planning behaviour" OR abs:"cognitive modelling" OR abs:"cognitive modeling"'
    ') '
    'AND ('
        'abs:"digital biomarker" OR abs:"eye tracking" OR abs:"EEG" OR abs:"behavioural assessment" OR abs:"cognitive assessment" '
        'OR abs:"POMDP" OR abs:"MDP" OR abs:"Markov decision process" OR abs:"Bayesian inference" OR abs:"generative model" '
        'OR abs:"amortised inference" OR abs:"amortized inference" OR abs:"computational psychiatry" '
        'OR abs:"active inference" OR abs:"predictive coding" OR abs:"reinforcement learning" OR abs:"cognitive model"'
    ')'
)

parameters = {
    "search_query": query,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "max_results": 100
}
results = requests.get("http://export.arxiv.org/api/query", params=parameters)
dict_answer = xmltodict.parse(results.text)

history_file = "paper_history.json"

with open(history_file, "r") as file:
        history_json = json.load(file)

previous_titles = {paper["title"] for paper in history_json["papers"]}

fetched_papers = []

papers = dict_answer["feed"]["entry"]
for paper in papers:
    paper_data = []
    paper_data.append(paper["title"])
    paper_data.append(paper["link"][0]["@href"])
    
    paper_data.append(paper["summary"])

    with open("todays_fetched_papers.txt", "a+") as f:
      
        f.seek(0)
        if (paper_data[0] not in f.read()) and (paper_data[0] not in previous_titles):
            f.write(f"Title: {paper_data[0]}\n")
            f.write(f"Link: {paper_data[1]}\n")
            f.write(f"Summary: {paper_data[2]}\n")
            f.write(f"DateAdded: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("---------------------------------------------------------------------------\n") 







