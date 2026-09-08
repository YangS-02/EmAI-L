import json
from pathlib import Path


RAG_EVAL_DIR = Path(__file__).resolve().parent
JSON_SET_DIR = RAG_EVAL_DIR / "eval_set.json"


"""
The evaluation set is going to be structured as followed:
[
  {
  "id": "sample_001",
  "question": "When is my interview with ******?",
  "reference_contexts": ["actual email content", ......]
  "reference_context_ids": ["email_id", ......],
  "metadata": {
    "unanswerable": false,  <--- true or false
    "source": "human",  <--- human or synthetic
    "question_type": "schedule",  <--- schedule, summary, lookup, ......
    "answer_type": "datetime",  <--- person, location, ......
    "num_relevant_contexts": 1,  <--- number of emails needed to answer the question
    "complexity": "easy"  <--- easy, medium, or hard
    }
  },
......
]

The first orignally created dataset is going to be stored as JSON.

Once the data is loaded into a Ragas Dataset backend, plan to use Ragas for future dataset changes and iterations.
"""
