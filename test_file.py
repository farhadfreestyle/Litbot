import json
history_file = "paper_history.json"

with open(history_file, "r") as file:
        history_json = json.load(file)

print(len(history_json["papers"]))

all_unique_titles = set([paper["title"] for paper in history_json["papers"]])
print("len unique title: ", len(all_unique_titles))

unique_papers = []
titles_added = []
for paper in history_json["papers"]:
        if paper["title"] not in titles_added:
                unique_papers.append(paper)
                titles_added.append(paper["title"])
print(len(unique_papers))

history_json["papers"] = unique_papers

with open(history_file, "w") as file:
    json.dump(history_json, file, indent=4)

print("Len of final history: ", len(history_json["papers"]))
