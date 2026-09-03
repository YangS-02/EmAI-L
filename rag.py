from llm import ask_llm
from vector_store import search_emails


MAX_EMAIL_CHARS = 3000


def build_context(results):
    """
    Convert retrieved emails into context
    that can be given to the LLM.
    """

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):
        metadata = result["metadata"]

        document = result["document"]

        # Avoid sending extremely long emails
        # into the model context.
        if len(document) > MAX_EMAIL_CHARS:
            document = (
                document[:MAX_EMAIL_CHARS]
                + "\n[Email truncated]"
            )

        context = (
            f"[SOURCE {index}]\n"
            f"Email ID: {result['id']}\n"
            f"From: {metadata['sender']}\n"
            f"Date: {metadata['date']}\n"
            f"Subject: {metadata['subject']}\n\n"
            f"{document}"
        )

        context_parts.append(context)

    return "\n\n" + "\n\n".join(context_parts)


def answer_email_question(
    question,
    n_results=5
):
    """
    Retrieve relevant emails and answer
    a question using those emails.
    """

    # ----------------------------------
    # Retrieve relevant emails
    # ----------------------------------

    results = search_emails(
        question,
        n_results=n_results
    )

    if not results:
        return {
            "answer": (
                "I couldn't find any relevant "
                "emails in the local index."
            ),
            "sources": []
        }

    # ----------------------------------
    # Build context
    # ----------------------------------

    context = build_context(results)

    # ----------------------------------
    # Build grounded prompt
    # ----------------------------------

    prompt = f"""
You are answering a question about the user's emails.
Use ONLY the email sources provided below to answer the question.

Rules:
1. Use only information contained in the provided emails.
2. Never invent or infer unsupported facts.
3. If the emails do not contain enough information, simply say that you could not find the answer in the emails.
4. Cite relevant emails using [SOURCE 1], [SOURCE 2], etc.
5. Do not cite sources that do not contribute to the answer.
6. Answer directly and concisely.
7. Do not give unrelated advice, external links, or suggestions.

EMAIL SOURCES:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    answer = ask_llm(prompt)
    # This is like a single shot call to the llm. It doesn't retain conversation memory. Context disappears after llm
    # returns the answer.

    return {
        "answer": answer,
        "sources": results
    }