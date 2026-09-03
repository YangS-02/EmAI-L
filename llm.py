from ollama import chat


MODEL_NAME = "qwen3:4b"


def ask_llm(prompt):
    """
    Send a prompt to the local Ollama model.
    """

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a local email assistant. "
                    "Answer clearly and concisely."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.message.content