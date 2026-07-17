import json

TEMPLATE_PATH = "dashboard_template.html"
DATA_PATH = "todays_papers.json"
OUTPUT_PATH = "dashboard.html"


def build_dashboard(data_path=DATA_PATH, template_path=TEMPLATE_PATH, output_path=OUTPUT_PATH):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    html_out = template.replace("__PAPERS_JSON__", json.dumps(data))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Wrote {output_path} with {len(data.get('papers', []))} papers.")


if __name__ == "__main__":
    build_dashboard()
