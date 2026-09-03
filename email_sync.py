from database import (
    get_existing_email_ids,
    save_emails,
)
from gmail_client import (
    get_message_ids,
    get_email_by_id,
)
from vector_store import index_emails



def sync_recent_emails(
    gmail,
    max_messages=100
):
    """
    Synchronize recent Gmail messages into the local SQLite database. But this doesn't handle incorperation of new emails
    into the embedding space. But the function index_email in vector_store.py already naturally handles that.
    But immediately indexing after every sync is better and more stable, I guess.
    """

    print(
        f"Checking the {max_messages} "
        f"most recent Gmail messages..."
    )

    # ---------------------------------
    # Get Gmail message IDs
    # ---------------------------------

    gmail_ids = get_message_ids(
        gmail,
        max_results=max_messages
    )

    print(
        f"Gmail returned {len(gmail_ids)} message IDs."
    )

    # ---------------------------------
    # Find what we already have
    # ---------------------------------

    existing_ids = get_existing_email_ids()

    new_ids = [
        message_id
        for message_id in gmail_ids
        if message_id not in existing_ids
        # Would this lookup be expensive?
        # get_existing_email_ids returns a set (hash table), and the lookup is O(1) average. So this shouldn't be a problem.
    ]

    print(
        f"{len(new_ids)} new emails need downloading."
    )

    # ---------------------------------
    # Download new messages
    # ---------------------------------

    new_emails = []

    for index, message_id in enumerate(
        new_ids,
        start=1
    ):

        print(
            f"Downloading {index}/{len(new_ids)}",
            end="\r"
        )

        try:

            email = get_email_by_id(
                gmail,
                message_id
            )

            new_emails.append(email)

        except Exception as error:

            print()
            print(
                f"Could not download {message_id}: "
                f"{error}"
            )

    if new_ids:
        print()

    # ---------------------------------
    # Save everything at once
    # ---------------------------------

    save_emails(new_emails)

    # Immediately index new emails
    index_emails(new_emails)

    return len(new_emails)