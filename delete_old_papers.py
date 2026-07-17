import datetime
import json
import os

today = datetime.datetime.today()
history_file = "paper_history.json"

if os.path.exists(history_file):
    with open(history_file, "r") as file:
        history_json = json.load(file)

papers_deleted = 0

for paper in history_json["papers"]:
    fetched_date = paper["date_fetched"]
    fetched_date = datetime.datetime.strptime(fetched_date, "%Y-%m-%d %H:%M:%S")
    time_passed = today - fetched_date

    if time_passed > 30:
        history_json["papers"].remove(paper)
        papers_deleted +=1

    


if papers_deleted > 0:
    with open(history_file, "w") as file:
        json.dump(history_json, file, indent=4)