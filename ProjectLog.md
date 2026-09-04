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
- Start working on the test set. Sources: 
  - [Testset Generation for RAG](https://docs.ragas.io/en/stable/concepts/test_data_generation/rag/);
  - [RAGET Testset Generation](https://legacy-docs.giskard.ai/en/stable/open_source/testset_generation/testset_generation/index.html#raget-testset-generation). 
- These are going to serve as the reference for the type of questions I am going to use. Another thing to note is that to
  combine the self-labeled set and the synthetic set later, have to format the way synthetic testset format their data.
- 