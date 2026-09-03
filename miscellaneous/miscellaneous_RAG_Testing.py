import ollama
import numpy as np

from vector_store import get_collection
from ollama import embed

if __name__ == "__main__":
    NUM_RESULTS = 5

    questions = [
        "What car does my professor drive?",
        "When is my interview?",
    ]

    response = ollama.embed(
        model="embeddinggemma",
        input=questions
    )
    query = [response["embeddings"][x] for x in range(len(response["embeddings"]))]
    print(np.linalg.norm(response["embeddings"][0])) # embedding vectors are unit-normalized
    print(np.linalg.norm(response["embeddings"][1]))

    collection = get_collection()
    results = collection.query(
        query_embeddings=query,
        n_results=NUM_RESULTS,
        include=["embeddings", "documents"]
    )
    print(results.keys())
    print(collection.configuration)

    for index_questions in range(len(questions)):
        print("=" * 80)
        print("Query: ", questions[index_questions])
        print("=" * 80)
        for index_queries in range(len(results["ids"][0])):
            print('-'*80)
            print(f"Result {1+index_queries}")
            print('-' * 80)
            print(np.linalg.norm(results["embeddings"][index_questions][index_queries]))  # This also confirmed that embedding vectors are unit-normalized
            print(results["documents"][index_questions][index_queries])