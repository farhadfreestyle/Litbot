import requests
import xmltodict
from datetime import datetime

query = (
    '(abs:"executive function" OR abs:"working memory" OR abs:"cognitive control") '
    'AND ('
        'abs:"digital biomarker" OR abs:"eye tracking" OR abs:"EEG" OR abs:"behavioural assessment" OR abs:"cognitive assessment" '
        'OR abs:"POMDP" OR abs:"Bayesian inference" OR abs:"generative model" OR abs:"amortised inference" OR abs:"amortized inference" OR abs:"computational psychiatry"'
    ')'
)

parameters = {
    "search_query": query,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "max_results": 10
}
results = requests.get("http://export.arxiv.org/api/query", params=parameters)
dict_answer = xmltodict.parse(results.text)


fetched_papers = []

papers = dict_answer["feed"]["entry"]
for paper in papers:
    paper_data = []
    paper_data.append(paper["title"])
    paper_data.append(paper["link"][0]["@href"])
    
    paper_data.append(paper["summary"])

    with open("todays_fetched_papers.txt", "a+") as f:
      
        f.seek(0)
        if paper_data[0] not in f.read():
            f.write(f"Title: {paper_data[0]}\n")
            f.write(f"Link: {paper_data[1]}\n")
            f.write(f"Summary: {paper_data[2]}\n")
            f.write(f"DateAdded: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("---------------------------------------------------------------------------\n") 







