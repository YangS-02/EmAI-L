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
, which is another limitation since I am working with Python 3.11.1. Between RAGAS and DeepEval, I am leaning towards RAGAS as 
they natively support [ids as part of the testset](https://docs.ragas.io/en/stable/references/evaluation_schema/#ragas.dataset_schema.BaseSample.to_string:~:text=SingleTurnSample,-Bases%3A%20BaseSample) and even offer [id-based metrices](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/?h=idbased#example_2:~:text=0.9999999999-,ID%20Based%20Context%20Precision,-IDBasedContextPrecision%20provides).
### RAGAS
- `SingleTurnSample` and `MultiTurnSample` are child of `BaseSample`. A `SingleTurnSample` is essentially one instance/interaction. For the current
stage, `SingleTurnSample` is the focus, as we are not yet conversational.
  - One thing to note is that attributes include both referenced contexts and contexts actually retrieved. And all attributes are optional. So, we can create instances of the class
  from the self-labeled dataset file `eval_rag.json`. And then run RAG on each of the instances and populate fields like `retrieved_context_ids`, before passing these instances in the
  `EvaluationDataset` class for evaluation with the `evaluate()` function.
- `EvaluationDataset` then inherits from `RagasDataset`, and it specifies that it should contain either `SingleTurnSample`'s or `MultiTurnSample`'s.
  - One confusion here is the difference between `EvaluationDataset` and the [Dataset](https://docs.ragas.io/en/stable/concepts/datasets/) described in the Core Concepts section.
  Judging from the fact that the `evaluate()` method accepts both and the descriptions of `Dataset`, `Dataset` is a parallel to `EvaluationDataset` but with more
  flexibility?