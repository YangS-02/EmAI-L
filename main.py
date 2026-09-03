from database import (
    initialize_database,
    get_all_emails,
)

from rag import answer_email_question

from vector_store import index_emails

from gmail_client import authenticate_gmail
from email_sync import sync_recent_emails


def main():

    # ----------------------------------
    # Initialize database
    # ----------------------------------

    initialize_database()

    # ----------------------------------
    # Connect to Gmail
    # ----------------------------------

    gmail = authenticate_gmail()
    print("Connected to Gmail.")

    # ----------------------------------
    # Sync recent new emails
    # ----------------------------------

    downloaded = sync_recent_emails(
        gmail,
        max_messages=500
    )

    if downloaded:
        print(
            f"Synced {downloaded} new emails."
        )
    else:
        print(
            "No new emails found."
        )

    # ----------------------------------
    # Safety check:
    # make sure SQLite emails are indexed
    # ----------------------------------

    emails = get_all_emails()

    print(
        f"Loaded {len(emails)} emails."
    )

    indexed = index_emails(emails)

    if indexed:
        print(
            f"Indexed {indexed} missing emails."
        )

    # ----------------------------------
    # Interactive Q&A
    # ----------------------------------

    print()
    print("EmAI-L Email Assistant")
    print("Type 'exit' to quit.")

    while True:

        question = input(
            "\nYou: "
        ).strip()

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit",
            "q"
        }:
            break

        result = answer_email_question(
            question,
            n_results=5
        )

        print("\nEmAI-L:")
        print(result["answer"])

        # ----------------------------------
        # Display retrieved sources
        # ----------------------------------

        sources = result["sources"]

        if sources:

            print("\nSources:")

            for index, source in enumerate(
                sources,
                start=1
            ):

                metadata = source["metadata"]

                print(
                    f"[{index}] "
                    f"{metadata['subject']} | "
                    f"{metadata['sender']} | "
                    f"{metadata['date']}"
                )


if __name__ == "__main__":
    main()