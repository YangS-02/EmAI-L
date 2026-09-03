# EmAI-L

# Files
- `data/`: serve as the SQLite database and vector database
- `credentials/`: store Google OAuth credentials
- `main.py`: the entry point
- `gmail_client.py`: connect to Gmail and retrieve/parse emails
- `database.py`: create/maintain/connect to the SQLite database and implements additional helper functions
- `vector_store.py`: create/maintain/connect to the Chroma database and implements additional helper functions
- `email_sync`: load/parse new emails (from `gmail_client.py`) and save the email in both SQLite and Chroma database
- `llm.py`: wrapped the ollama chat API
- `rag`: create/load the contexts from retrieved emails using similarity search into the query

# Version History
## V1
### Summary
Version one creates the overall architecture of the agent. It uses the Google OAUTH to load the messages. Two databases
are created: SQLite and Chroma. SQLite serves as the library, while Chroma is the librarian who helps you locate things 
in the sea of books stored in the library. The retrieved relevant contexts are then passed into the 4-billion-parameter
model to summarize the content.
### Future Improvement
**Near Future**: Absurd questions like "What car does my professor drive" return results when it wasn't supposed to. 
Hybrid search? Setting thresholds? Tuning HNSW indices? Chunking?
And further stress tests on the RAG are also needed. So, in the next iteration, 
the focus is **RAG retrieval quality**.

**Distant Future**: The agent now is a one-shot retrieval system with the retrieved context passed to an LLM for a single response.
It is not yet conversational, which is the direction I am going for next.