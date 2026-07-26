import json
import os

with open("todays_papers.json", "r") as file:
    todays_json = json.load(file)

papers = todays_json["papers"] 

history_file = "paper_history.json"

if os.path.exists(history_file):
    with open(history_file, "r") as file:
        history_json = json.load(file)
else:
  
    history_json = {"papers": []}
  
# existing_titles = {paper["title"] for paper in todays_json["papers"]}

# new_papers = [
#     paper for paper in papers
#     if paper["title"] not in existing_titles
# ]

history_json["papers"] = history_json["papers"] + (papers)

with open(history_file, "w") as file:
    json.dump(history_json, file, indent=4)