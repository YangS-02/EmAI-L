# Project Log
## Sep 3, 2026
- Decided to publish the entire project to GitHub.
- While going through Google's EmbeddingGamma's documentation, I stumbled upon the section "[using prompts with EmbeddingGemma](https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers#using_prompts_with_embeddinggemma)". 
The prompts help improve the embedding quality for different tasks and input types. But we can't use the argument listed in that document
since I access the EmbeddingGamma through Ollama API. But we can make changes to the way email contents and the queries are passed into the function.
- Now, for RAG quality, start by creating an evaluation set? Hand-labeling is going to be a lot. There are packages that can help with
test data generation. [DeepEval](https://deepeval.com/docs/synthetic-data-generation-introduction#recommended-priority:~:text=second%20look%20at.-,Recommended%20Priority,-The%20best%20evaluation) 
recommends and prioritizes human-created examples and ranks synthetic data as least recommended. Guess I will start with some
hand-labeled sets.