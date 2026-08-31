from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()
client = OpenAI()
text_file = open("todays_fetched_papers.txt", "r").read()


input = f"""
You are screening arXiv papers for a PhD researcher working on quantitative modelling of human executive function (planning, working memory, attention), for cognitive assessment and early detection of cognitive impairment.

His work spans three areas of interest, in descending but not exclusive priority:

Area 1, computational modelling of executive function: generative or inferential models of human planning, working memory, or attention. POMDP/MDP formulations, Bayesian inference (amortised or otherwise), active inference, reinforcement learning models of decision making, or other process models of cognition. This includes modelling work from the CS/ML community even when not validated on neural or eye tracking data, and even when not framed around clinical populations, as long as the object being modelled is human cognitive/executive function.

Area 2, neuroscience findings on executive function: empirical findings, human or animal, about the neural or behavioural basis of planning, working memory, attention, or cognitive control, that could plausibly inform a computational model of these functions, even if the paper itself does no modelling. EEG findings (frontal midline theta, frontoparietal connectivity), fMRI, or behavioural/neuropsychological findings all count here.

Area 3, digital biomarkers and multimodal assessment: behavioural task or eye tracking based classification of cognitive style or clinical status, combined with EEG, distinguishing neurotypical and clinical groups. This is his applied/current project, not his broader research identity, so treat it as one valuable category among three rather than the only thing worth a high score.

Step 1, hard filter, apply before scoring anything.

A paper fails the filter and must receive a relevance score of 0 if it is about any of the following, regardless of shared vocabulary such as working memory, cognitive, or attention.

Evaluating or benchmarking the cognitive abilities of AI models, LLMs, or generative systems.
Video generation, video diffusion, image generation, or reasoning inside generative video or image models.
KV cache, model memory, context window, or any use of the term memory referring to a machine learning system's internal state rather than a human or animal participant's cognition.
Any paper where the study population is not human or animal (e.g. pure simulation with no grounding in biological cognition), UNLESS it is a computational modelling paper under Area 1 whose object of study is explicitly human cognitive/executive function.

Papers that fail the filter must still appear in the output with score 0 and matched_area None, do not omit them, so the researcher can see what was excluded and why.

Step 2, score the papers that pass the filter, from 0 to 10, based on centrality to Areas 1 to 3 above, not on a fixed element count.

9 to 10: paper's core contribution is a computational/generative model of human executive function (Area 1), or it directly reports EEG/behavioural/neural findings on executive function that are clearly usable in a computational model (Area 2), or it is a close methodological match to Area 3 (task/eye tracking/EEG combined for clinical classification).
6 to 8: paper is substantially about executive function, planning, working memory, or attention in humans, with clear relevance to modelling or assessing it, but is narrower in scope, preliminary, or only partially overlaps with Areas 1 to 3.
3 to 5: paper touches executive function or related cognitive constructs but the connection to modelling or assessment is incidental, tangential, or the core contribution is elsewhere (e.g. a general neuroimaging method paper that happens to include an EF task).
1 to 2: paper is about human cognitive assessment or clinical cognitive monitoring generally, with no meaningful connection to executive function modelling specifically.

Do not require multiple elements (task, eye tracking, EEG, modelling) to co-occur for a high score. A pure modelling paper with no neural or eye tracking data, or a pure neuroscience findings paper with no modelling, can each independently score 9 to 10 if central to Area 1 or Area 2 respectively.

if file is empty, return empty json with papers key and empty list value.
Return valid JSON only, no preamble, no markdown fences, in this exact structure:

{{
  "papers": [
    {{
      "title": "...",
      "link": "...",
      "relevance_score": 0,
      "matched_area": "Area 1" or "Area 2" or "Area 3" or "None",
      "filtered": true or false,
      "reason": "one sentence, specific, no filler",
      "date_fetched": the date you see in the txt file as DateAdded
    }}
  ]
}}

if file was empty then:
{{
  "papers": []
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


if len(new_data["papers"]) > 0:
    data["papers"].extend(new_data["papers"])


with open(todays_papers, "w") as file:
    json.dump(data, file, indent=4)