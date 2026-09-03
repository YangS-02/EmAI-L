"""
For now, the ability to store and query image is not a consideration. So cross-modal retrieval is not an issue as well as
cross-lingual retrieval (tho embeddinggemma provides decent multilingual capabilities). But key information retrieval and
dimension compression are important.
"""
from pathlib import Path
import chromadb
import ollama


PROJECT_DIR = Path(__file__).resolve().parent
CHROMA_PATH = PROJECT_DIR / "data" / "chroma"
COLLECTION_NAME = "emails"
EMBEDDING_MODEL = "embeddinggemma"


def get_collection():
    """
    Return the local persistent Chroma email collection.
    """

    client = chromadb.PersistentClient(  # save and load the database from local machine
        path=str(CHROMA_PATH)
    )

    collection = client.get_or_create_collection( # if exists, fetch; if not, create new collection
        name=COLLECTION_NAME,
        embedding_function=None # Use the Oll
    )

    return collection


def build_email_document(email):
    """
    Convert an email record into the text that will be embedded for semantic search.
    """

    content = (
        f"From: {email['sender']}\n"
        f"To: {email['recipient']}\n"
        f"Date: {email['date']}\n\n"
        f"{email['body']}"
    )

    return (
        f"title: {email['subject']} | "
        f"text: {content}"
    )


def index_emails(emails):
    """
    Create embeddings for emails that are not already stored in Chroma.

    Note: so after changing the syncing logic, we should still keep the chunk of code checking existences for safety.

    The architecture here: We use Chroma as a storage room (which also provides the similarity search function) for the
    embeddings converted from texts by the embeddinggamma. Moreover, instead of using ChromaDB's built-in embedding
    mechanism, embeddinggamma hosted by Ollama is used here.
    """

    collection = get_collection()

    # -----------------------------------
    # Find emails already indexed <-- old but keep it as a safeguard (sync_recent_emails already checks already indexed emails)
    # -----------------------------------

    existing_records = collection.get()

    # Set index is efficient so we wouldn't have to worry about the time complexity here
    existing_ids = set(existing_records["ids"])
    new_emails = [
        email
        for email in emails
        if email["id"] not in existing_ids
    ]
    if not new_emails:
        print("All emails are already indexed.")
        return 0
    print(f"{len(new_emails)} emails need embeddings.")

    # Process in small batches.
    batch_size = 20

    indexed_count = 0

    for start in range(
        0,
        len(new_emails),
        batch_size
    ):

        batch = new_emails[
            start:start + batch_size
        ]

        # -----------------------------------
        # Turn emails into documents
        # -----------------------------------

        documents = [
            build_email_document(email)
            for email in batch
        ]

        # -----------------------------------
        # Generate embeddings with Ollama
        # -----------------------------------

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=documents  # Ollama allows batch generation of embeddings.
        )
        """
        The returned response has the following structure:
        {
            "model": "......",
            "embeddings": [
                [......],
                [......]
            ],
            "total_duration": ......,  # integer: Total time spent generating in nanoseconds
            "load_duration": ......,  # integer: Load time in nanoseconds
            "prompt_eval_count": ......, # integer: Number of input tokens processed to generate embeddings
        }
        """
        embeddings = response["embeddings"]

        # -----------------------------------
        # Metadata kept alongside vectors
        # -----------------------------------

        metadata = [
            {
                "email_id": email["id"],
                "thread_id": email["thread_id"] or "",
                "sender": email["sender"] or "",
                "recipient": email["recipient"] or "",
                "subject": email["subject"] or "",
                "date": email["date"] or "",
            }
            for email in batch
        ]

        ids = [
            email["id"]
            for email in batch
        ]

        # -----------------------------------
        # Store in Chroma
        # -----------------------------------

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata
        )

        indexed_count += len(batch)

        print(
            f"Indexed "
            f"{indexed_count}/{len(new_emails)}"
        )

    return indexed_count


def search_emails(
    question,
    n_results=5
):
    """
    Search for emails semantically related to the user's question.

    Return: a list of dictionaries, where each dictionary contains the following keys: id, document, metadata, distance
    """

    query_text = (
        f"task: question answering | query: {question}"
    )


    collection = get_collection()

    if collection.count() == 0:
        return []

    # -----------------------------------
    # Embed the question
    # -----------------------------------

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=query_text
    )

    query_embedding = (
        response["embeddings"][0]
    )

    # -----------------------------------
    # Search Chroma
    # -----------------------------------

    result_count = min(
        n_results,
        collection.count()
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=result_count
    )

    # -----------------------------------
    # Make results easier to use
    # -----------------------------------

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append(
            {
                "id": results["ids"][0][i],
                "document":
                    results["documents"][0][i],
                "metadata":
                    results["metadatas"][0][i],
                "distance":
                    results["distances"][0][i],
            }
        )

    return matches


if __name__ == "__main__":
    pass