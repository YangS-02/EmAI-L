# Project Log
## Sep 3, 2026
- Decided to publish the entire project to GitHub.
- While going through Google's EmbeddingGamma's documentation, noticed the section "[using prompts with EmbeddingGemma](https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers#using_prompts_with_embeddinggemma)". 
The prompts help improve the embedding quality for different tasks and input types. Can't use the argument in that document
since EmbeddingGamma was accessed through Ollama API. Made changes to the way email contents and the queries are passed into the function.
- Now, for RAG quality, start by creating an evaluation set. There are packages that can help with
test data generation like [DeepEval](https://deepeval.com/docs/synthetic-data-generation-introduction#recommended-priority:~:text=second%20look%20at.-,Recommended%20Priority,-The%20best%20evaluation). In their documentation, they prioritize human-created examples over synthetic data.
It makes sense as human-reviewed data tests failure and edge cases. But it is a pain and impossible at scale. The coverage
is a problem as well. Synthetic ones offered by DeepEval or Ragas are good for scale and coverage. But they can also be
problematic in that questions can be general and not reflect the query pattern specific to the program. Here, will 
use a hybrid of self-labeled and synthetic sets.
## Sep 4, 2026
- Start working on the test set. The following are some of the options for RAG testset generation:
  - [Ragas](https://docs.ragas.io/en/stable/concepts/test_data_generation/rag/);
  - [RAGET (legacy)](https://legacy-docs.giskard.ai/en/stable/open_source/testset_generation/testset_generation/index.html#raget-testset-generation);
  - [DeepEval](https://deepeval.com/docs/synthetic-data-generation-introduction#recommended-priority)
- To combine the self-labeled and the synthetic set later, have to somewhat format the way synthetic testset format their data.
## Sep 6, 2026
- need to make a decision on what package to use before moving on to create self-labeled testset. Now, they all offer very
promising functionalities regarding RAG evaluation, but they do seem to have slightly different focuses. I am not going with
Giskard. The page I searched is legacy documentation, and it seems that they have undergone significant changes recently.
[Their newest version requires Python 3.12+](https://docs.giskard.ai/oss/migrate-from-v2#:~:text=Giskard%20v3%20requires%20Python%203.12%20or%20higher.)
, which is another limitation since I am working with Python 3.11.1. Between Ragas and DeepEval, I am leaning towards Ragas as 
they natively support [ids as part of the testset](https://docs.ragas.io/en/stable/references/evaluation_schema/#ragas.dataset_schema.BaseSample.to_string:~:text=SingleTurnSample,-Bases%3A%20BaseSample) and even offer [id-based metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/?h=idbased#example_2:~:text=0.9999999999-,ID%20Based%20Context%20Precision,-IDBasedContextPrecision%20provides).
### Ragas
- `SingleTurnSample` and `MultiTurnSample` inherit from `BaseSample`. A `SingleTurnSample` is essentially one instance/interaction. For the current
stage, `SingleTurnSample` is the focus, as we are not yet conversational.
  - One thing to note is that attributes include both referenced contexts and contexts actually retrieved. And all attributes are optional. So, we can create instances of the class
  from the self-labeled dataset file `eval_rag.json`. And then run RAG on each of the instances and populate fields like `retrieved_context_ids`, before passing these instances in the
  `EvaluationDataset` class for evaluation with the `evaluate()` function.
- `EvaluationDataset` then inherits from `RagasDataset`, and it specifies that it should contain either `SingleTurnSample`'s or `MultiTurnSample`'s.
  - One confusion here is the difference between `EvaluationDataset` and the [Dataset](https://docs.ragas.io/en/stable/concepts/datasets/) described in the Core Concepts section.
  Judging from the fact that the `evaluate()` method accepts both and the descriptions of `Dataset`, `Dataset` is a parallel to `EvaluationDataset` but with more
  flexibility?
## Sep 8, 2026
- As it turned out, they mentioned in the [Migration from v0.3 to v0.4](https://docs.ragas.io/en/stable/howtos/migrations/migrate_from_v03_to_v04/) that `evaluate()` "still works but discourage" as they will
be removed in a future release. And it seems that the natively supported id-based metrics are also getting phased out judging from their updated list of available metrics.
Although I am leaning toward using the old architecture for evaluation since a lot of the stuff makes immediate sense to me, I feel like RAG tuning is 
a continuous process as the project and data evolve over time. And working with the new version now seems like a more reasonable choice.
From what I can understand so far, this new dataset and experiment architecture has a better versioning and iteration
system. Plus, with the new `Dataset` I can still add ids as part of the evaluation dataset and implement id-based metrics myself.
### Self-labeled Evaluation Dataset
- Here is how I am going to structure my data:
  ```
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
  }
  ```
  - These are some of the metadata I can think of and could be useful in [slicing and dicing the dataset](https://docs.ragas.io/en/stable/concepts/datasets/#:~:text=Metadata%20is%20particularly%20useful%20for%20slicing%20and%20dicing%20the%20dataset%2C%20allowing%20you%20to%20analyze%20results%20across%20different%20facets) to
  see how the system could perform on different types of dataset. For example, how well does the RAG retrieve contexts involving dates and times?
  - Here is my current impasse: 
    - I haven't yet implemented chunking in my RAG. And for now, it seems like semantic-based metrics are kind of excessive. 
    The goal is to retrieve the correct/relevant document. But if I were to move on to implement chunking, I would need to evaluate whether 
    the retrieved chunks contain the evidence. Then document-level id-based metrics are not enough.
    - I also think I should implement at least one chunking strategy for comparison. If I do that, I need to structure the self-labeled dataset 
    so it is future-proof and can support evaluation both with and without chunking, as well as chunking-specific tuning if I ever decide to use chunking.
    - And also for tuning LLM-generated answers, I would need additional fields.
  - Current works ok as it is?