# Project Log
## Sep 3, 2026
While going through EmbeddingGamma's documentation, I stumbled upon the section "[using prompts with EmbeddingGemma](https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers#using_prompts_with_embeddinggemma)". 
The prompts help improve the embedding quality for different tasks and input types. But we can't use the argument listed in that document
since I access the EmbeddingGamma through Ollama API. But we make changes to the way we pass the email contents and the queries.