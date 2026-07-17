from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()
client = OpenAI()
text_file = open("todays_fetched_papers.txt", "r").read()


input = f"""
You are screening arXiv papers for a PhD researcher working on quantitative modelling of human executive function (planning, working memory, attention) using behavioural and multimodal data, for cognitive assessment and early detection of cognitive impairment in people.

His work has two arcs.

Arc 1, digital biomarker development: behavioural task and eye tracking based classification of cognitive style in human participants, combined with EEG, aimed at distinguishing neurotypical and clinical groups. Frequency domain EEG analysis, frontal midline theta, frontoparietal connectivity, continuous non trial locked signals.

Arc 2, computational modelling: POMDP and MDP generative frameworks of human executive function, amortised Bayesian inference trained on synthetic trajectories and validated on real human behavioural and neural data.

Step 1, hard filter, apply before scoring anything.

A paper fails the filter and must receive a relevance score of 0 if it is about any of the following, regardless of shared vocabulary such as working memory, cognitive, or attention.

Evaluating or benchmarking the cognitive abilities of AI models, LLMs, or generative systems.
Video generation, video diffusion, image generation, or reasoning inside generative video or image models.
KV cache, model memory, context window, or any use of the term memory referring to a machine learning system's internal state rather than a human participant's cognition.
Any paper where the study population is not human participants.

Papers that fail the filter must still appear in the output with score 0 and matched_arc None, do not omit them, so the researcher can see what was excluded and why.

Step 2, score the papers that pass the filter.

Assign a relevance score from 0 to 10 based on how many of the following four elements the paper actually contains in its methodology. Do not credit an element for being mentioned in passing or as a co-recorded signal, only credit it if it is a core part of what the study measures and analyses.

Element A, an interactive behavioural task or game paradigm where human participants make timed or sequential decisions, not a static or purely passive recording condition.
Element B, eye tracking of human participants.
Element C, EEG of human participants, specifically frequency domain or connectivity analysis rather than only band power summary or classification accuracy reported without method detail.
Element D, computational modelling of human cognition using POMDP, MDP, Bayesian inference, or a generative model of decision processes, rather than a purely statistical or deep learning classifier with no cognitive process model behind it.

Score based on element count and centrality, using this rubric as a guide rather than a rigid formula.

Four elements present, or three including Element A or D as central to the method, score 9 to 10.
Two elements present, at least one being A, C, or D, score 6 to 8.
One element present, or two present but only as secondary or passively co-recorded signals, score 3 to 5.
No elements present in a way that meets the above bar, but the paper is about human cognitive assessment or clinical cognitive monitoring generally, score 1 to 2.

A physiological signal recorded passively alongside a task, with no behavioural interaction, eye tracking, or frequency domain EEG analysis, such as ECG or HRV used as a standalone or co-recorded proxy signal, does not on its own satisfy any of the four elements and should not push a paper above 5.

Return valid JSON only, no preamble, no markdown fences, in this exact structure:

{{
  "papers": [
    {{
      "title": "...",
      "link": "...",
      "relevance_score": 0,
      "matched_arc": "Arc 1" or "Arc 2" or "Both" or "None",
      "filtered": true or false,
      "elements_present": ["A", "B", "C", "D"],
      "reason": "one sentence, specific, no filler", 
      "date_fetched":the date you see in the txt file as DateAdded
    }}
  ]
}}

Papers to evaluate:

{text_file}
"""

response = client.responses.create(
    model="gpt-5.6",
    input=input
)

todays_papers = "todays_papers.json"

new_data = json.loads(response.output_text)


if not os.path.exists(todays_papers) or os.path.getsize(todays_papers) == 0:
    data = {"papers": []}
else:
    with open(todays_papers, "r") as file:
        data = json.load(file)
      
data["papers"].extend(new_data["papers"])


with open(todays_papers, "w") as file:
    json.dump(data, file, indent=4)