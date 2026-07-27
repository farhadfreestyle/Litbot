import requests
import xmltodict
from datetime import datetime
import json
import os

query = (
    '('
        'abs:"executive function" OR abs:"working memory" OR abs:"cognitive control" '
        'OR abs:"cognitive modelling" OR abs:"cognitive modeling" OR abs:"human cognition" '
        'OR abs:"cognitive decline" OR abs:"cognitive impairment"'
    ') '
    'AND ('
        'abs:"digital biomarker" OR abs:"eye tracking" OR abs:"EEG" OR abs:"behavioural assessment" OR abs:"cognitive assessment" '
        'OR abs:"POMDP" OR abs:"MDP" OR abs:"Markov decision process" OR abs:"Bayesian inference" '
        'OR abs:"amortised inference" OR abs:"amortized inference" OR abs:"computational psychiatry" '
        'OR abs:"active inference" OR abs:"predictive coding"'
    ')'
)

parameters = {
    "search_query": query,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "max_results": 100
}
results = requests.get("http://export.arxiv.org/api/query", params=parameters)

# print(results.text)

dict_answer = xmltodict.parse(results.text)



history_file = "paper_history.json"
todays_papers = "todays_papers.json"


with open(history_file, "r") as file:
        history_json = json.load(file)
    
if not os.path.exists(todays_papers) or os.path.getsize(todays_papers) == 0:
    todays_json = {"papers": []}
else:
    with open(todays_papers, "r") as file:
        todays_json = json.load(file)


previous_titles = {paper["title"] for paper in history_json["papers"]}
todays_titles = {paper["title"] for paper in todays_json["papers"]}

fetched_papers = []

papers = dict_answer["feed"]["entry"]

with open("todays_fetched_papers.txt", "w"):
    pass

for paper in papers:
    paper_data = []
    paper_data.append(paper["title"])
    paper_data.append(paper["link"][0]["@href"])
    
    paper_data.append(paper["summary"])

    with open("todays_fetched_papers.txt", "a+", encoding="utf-8") as f:
      
        if (paper_data[0] not in todays_titles) and (paper_data[0] not in previous_titles):
            
            f.write(f"Title: {paper_data[0]}\n")
            f.write(f"Link: {paper_data[1]}\n")
            f.write(f"Summary: {paper_data[2]}\n")
            f.write(f"DateAdded: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("---------------------------------------------------------------------------\n") 




