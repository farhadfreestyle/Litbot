# LitBot
<img src="litbot.png" alt="LitBot logo" width="400">

LitBot is an automated literature screening pipeline. It queries arXiv on a schedule, scores each result for relevance using a large language model, stores the results, and publishes them to two web dashboards, a daily view and a full historical archive.

## How it works

The pipeline runs in four stages, each handled by a separate script.

1. **Fetch.** `file_fetching.py` queries the arXiv API using a configurable search query and writes the raw results to a local file.
2. **Score.** `genai_results_generator.py` sends each fetched paper to an AI model with a scoring prompt, producing a relevance score, an arc classification, and a written justification for each paper, saved to `todays_papers.json`.
3. **Store.** `json_database.py` appends the day's scored results into `paper_history.json`, the cumulative record of every paper LitBot has ever screened.
4. **Clean.** `daily_cleaner.py` clears the day's temporary files at the end of each day so the next run starts fresh.

Two static pages read this data directly in the browser, with no server required once hosted.

- `dashboard.html` reads `todays_papers.json` and shows the most recent run.
- `archive.html` reads `paper_history.json` and shows every paper ever screened, searchable and sortable by date and score.

Automation is handled by three GitHub Actions workflows in `.github/workflows/`.

- `litbot-pipeline.yml` runs the fetch, score, and store steps twice daily.
- `litbot-daily-cleaner.yml` runs the cleanup step once nightly.
- `litbot-cleanup.yml` prunes old entries from the history file once a month.

## Requirements

- Python 3.11 or later
- An OpenAI API key (or equivalent, if the scoring script has been adapted for a different provider)
- A GitHub account, if using the included automation and hosting setup

## Setup

### 1. Clone the repository

```
git clone https://github.com/yourusername/litbot.git
cd litbot
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Configure your API key

Create a `.env` file in the project root, this file is gitignored and must never be committed:

```
OPENAI_API_KEY=your-key-here
```

For automated runs on GitHub Actions, the key must also be added as a repository secret, not read from `.env`, since Actions cannot see local files. In the repository, go to Settings, Secrets and variables, Actions, and add a new repository secret named `OPENAI_API_KEY`.

### 4. Configure the search query

Open `file_fetching.py` and locate the `search_query` parameter used in the arXiv API request. This defines which papers LitBot fetches on each run. Adjust the field prefixes, terms, and boolean structure to match your own research areas. The existing query structure groups synonyms with `OR` and combines concept clusters with `AND`, follow the same pattern when editing it to avoid returning either too few or too many results.

### 5. Configure the AI scoring prompt

Open `genai_results_generator.py` and locate the prompt string passed to the model. This prompt defines the criteria used to score relevance, the hard filter rules for excluding out-of-scope papers, and the JSON structure returned. Update the description of your research focus, the filter conditions, and the scoring rubric to match your own project. The prompt must continue to instruct the model to return valid JSON only, matching the field names expected by the dashboard pages (`title`, `link`, `relevance_score`, `matched_arc`, `filtered`, `elements_present`, `reason`, `date_fetched`), since the dashboards will not render correctly if these fields are renamed or omitted.

## Running locally

Each stage can be run independently for testing:

```
python file_fetching.py
python genai_results_generator.py
python json_database.py
```

To view the dashboards locally, note that opening the HTML files directly by double clicking will not work, since browsers block local file reads triggered from `file://` pages. Serve the folder with a local web server instead:

```
python -m http.server 8000
```

Then open `http://localhost:8000/dashboard.html` and `http://localhost:8000/archive.html` in a browser.

## Automated scheduling

The included GitHub Actions workflows require no local machine to stay running. Once configured, they execute on GitHub's infrastructure on the schedule defined by the `cron` expressions in each workflow file.

Cron schedules in GitHub Actions are specified in UTC. Adjust the cron expressions in `.github/workflows/litbot-pipeline.yml` and `.github/workflows/litbot-daily-cleaner.yml` to match your desired local run times, accounting for the UTC offset of your timezone. Note that a fixed UTC cron expression will shift by one hour relative to local time when daylight saving changes occur, and will need to be updated twice a year if a consistent local time is required.

Scheduled workflows are evaluated by GitHub's own scheduler and are not guaranteed to run at the exact minute specified. Delays of several minutes are normal and expected, particularly following recent changes to the schedule configuration.

## Hosting the dashboards

The dashboard pages can be published with GitHub Pages.

1. In the repository, go to Settings, Pages.
2. Under Build and deployment, set Source to Deploy from a branch.
3. Select the `main` branch and the root folder, then save.

Once published, the dashboards are available at:

```
https://yourusername.github.io/yourrepository/dashboard.html
https://yourusername.github.io/yourrepository/archive.html
```

GitHub Pages requires the repository to be public on the free plan. Private repository hosting requires GitHub Pro or higher.

## Security notes

The `.env` file must never be committed to version control. It is excluded via `.gitignore`, which should not be modified to permit tracking of environment files. If an API key has ever been committed to a repository's history, even briefly or in a private repository, it should be treated as compromised and rotated immediately, since removing the file in a later commit does not remove it from earlier commits still present in the repository's history.

## File reference

| File | Purpose |
|---|---|
| `file_fetching.py` | Queries arXiv and writes raw results |
| `genai_results_generator.py` | Scores papers using an AI model |
| `json_database.py` | Appends scored results to the historical record |
| `daily_cleaner.py` | Clears temporary daily files |
| `delete_old_papers.py` | Prunes old entries from the historical record |
| `todays_papers.json` | Most recent run's scored results |
| `paper_history.json` | Cumulative record of all screened papers |
| `dashboard.html` | Web view of the most recent run |
| `archive.html` | Web view of the full historical record |
| `requirements.txt` | Python dependencies |
| `.github/workflows/` | GitHub Actions automation definitions |
