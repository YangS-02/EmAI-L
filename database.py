import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_DIR / "data" / "emails.db"


def get_connection():
    """
    Create a connection to the local SQLite database.
    """
    return sqlite3.connect(DATABASE_FILE)


def initialize_database():
    """
    Create the email table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            thread_id TEXT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            date TEXT,
            body TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_emails(emails):
    """
    Save multiple emails in one database transaction.
    """

    if not emails:
        return

    connection = get_connection()
    cursor = connection.cursor()

    rows = [
        (
            email["id"],
            email["thread_id"],
            email["sender"],
            email["recipient"],
            email["subject"],
            email["date"],
            email["body"],
        )
        for email in emails
    ]

    cursor.executemany(
        """
        INSERT INTO emails (
            id,
            thread_id,
            sender,
            recipient,
            subject,
            date,
            body
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(id) DO UPDATE SET
            thread_id = excluded.thread_id,
            sender = excluded.sender,
            recipient = excluded.recipient,
            subject = excluded.subject,
            date = excluded.date,
            body = excluded.body
        """,
        rows
    )

    connection.commit()
    connection.close()


def get_email_count():
    """
    Return the number of emails stored locally.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM emails"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


def get_recent_stored_emails(limit=10):
    """
    Retrieve emails currently stored
    in the local database.
    """

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            thread_id,
            sender,
            recipient,
            subject,
            date,
            body
        FROM emails
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_existing_email_ids():
    """
    Return all Gmail message IDs already stored locally. This is used for sync in email_sync.py
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM emails"
    )

    rows = cursor.fetchall()

    connection.close()

    return {
        row[0]
        for row in rows
    }


def get_all_emails():
    """
    Retrieve all emails stored in SQLite.
    """

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            thread_id,
            sender,
            recipient,
            subject,
            date,
            body
        FROM emails
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]