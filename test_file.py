import json
history_file = "paper_history.json"

with open(history_file, "r") as file:
        history_json = json.load(file)

print(len(history_json["papers"]))
