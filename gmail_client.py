from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import base64
from bs4 import BeautifulSoup

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

PROJECT_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = (
    PROJECT_DIR
    / "credentials"
    / "credentials.json"
)

TOKEN_FILE = (
    PROJECT_DIR
    / "credentials"
    / "token.json"
)


def authenticate_gmail():
    creds = None

    # Reuse previous authentication if it exists.
    if TOKEN_FILE.exists():  # If permission has already granted, use TOKEN.
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Authenticate if necessary.
    if not creds or not creds.valid: # Access TOKEN does not exist or access TOKEN is not valid
        if (
            creds  # it exists
            and creds.expired  # access token expired
            and creds.refresh_token  # refresh token available: a long-lived credential that lets your app get a new
                                    # access token without asking you to log in again.
        ):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(  # This creates a new OAuth authorization flow
                CREDENTIALS_FILE,
                SCOPES  # specifies what permissions the program desires
            )
            creds = flow.run_local_server(port=0)  # actually runs the OAuth login process
        TOKEN_FILE.write_text(
            creds.to_json()
        )

    service = build(  # creates the actual Gmail API client that your Python code will use to interact with Gmail
        "gmail",
        "v1",
        credentials=creds
    )

    return service


def decode_body(data):
    """
    Decode a Gmail Base64URL encoded body.
    """
    if not data:
        return ""
    decoded_bytes = base64.urlsafe_b64decode(
        data + "=" * (-len(data) % 4)
    )
    return decoded_bytes.decode(
        "utf-8",
        errors="replace"
    )


def extract_body(payload):
    """
    Extract readable text from a Gmail message payload.
    Prefer text/plain but fall back to text/html if plain text is unavailable or noisy.

    payload: accessed by the get function.

    NOTE: Need to distinguish difference between quoted replies, signatures, mailing-list footers, and forwarded-message history,
    because it currently extracts all readable body content.
    """

    plain_text_parts = []
    html_parts = []

    def has_formatting_noise(text):
        text = text.lower()
        css_signals = [
            "background:",
            "border-color:",
            "font-size:",
            "padding:",
            "margin:",
            "table.button",
            ".wrapper",
            "{",
            "}",
        ]
        hits = sum(
            signal in text
            for signal in css_signals
        )
        return hits >= 4

    def walk_parts(part):
        mime_type = part.get("mimeType", "") # Look for key "mimeType" in the dict
        body = part.get("body", {})  # Look for the body in the dict
        data = body.get("data")  # Look for the encoded data in the subdict associated with "body" in the dict

        if mime_type == "text/plain" and data:
            plain_text_parts.append(
                decode_body(data)
            )

        elif mime_type == "text/html" and data:
            html_parts.append(
                decode_body(data)
            )

        # Value for the key, "parts," is stored as a list of dictionaries.
        # Here, it iterates through the dictionaries in this list and call walk_parts recursively
        for child_part in part.get("parts", []):
            walk_parts(child_part)


    walk_parts(payload)

    # Prefer normal plain text.
    if plain_text_parts:
        plain_text = "\n".join(
            plain_text_parts
        ).strip()

        if not has_formatting_noise(plain_text):
            return plain_text

    # Fall back to stripping HTML.
    if html_parts:
        html = "\n".join(html_parts)
        soup = BeautifulSoup(
            html,
            "html.parser"
        )
        return soup.get_text(
            separator="\n",
            strip=True
        )

    # If plain text looked noisy but no HTML exists,
    # still return the plain text.
    if plain_text_parts:
        return "\n".join(
            plain_text_parts
        ).strip()

    return ""


def get_header(headers, name):
    """
    Find a specific email header.
    """
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")

    return ""


def get_recent_emails(service, max_results=10):
    """
    Retrieve and parse emails from Gmail.
    """

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )

    messages = response.get(
        "messages",
        []
    )

    emails = []

    for message_info in messages:
        message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_info["id"],
                format="full"
            )
            .execute()
        )

        payload = message.get(
            "payload",
            {}
        )

        headers = payload.get(
            "headers",
            []
        )

        email_data = {
            "id": message.get("id"),
            "thread_id": message.get("threadId"),
            "from": get_header(headers, "From"),
            "to": get_header(headers, "To"),
            "subject": get_header(headers, "Subject"),
            "date": get_header(headers, "Date"),
            "body": extract_body(payload),
        }

        emails.append(email_data)

    return emails


def get_message_ids(service, max_results=100):
    """
    Retrieve Gmail message IDs.

    Handles pagination so we can request
    more than one page of results.
    """

    message_ids = []

    page_token = None

    while len(message_ids) < max_results:

        remaining = max_results - len(message_ids)

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=min(remaining, 500),
                pageToken=page_token
            )
            .execute()
        )

        messages = response.get(
            "messages",
            []
        )

        for message in messages:
            message_ids.append(
                message["id"]
            )

        page_token = response.get(
            "nextPageToken"
        )

        if not page_token:
            break

    return message_ids


def get_email_by_id(service, message_id):
    """
    Download and parse one Gmail message.
    """

    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full"
        )
        .execute()
    )

    payload = message.get(
        "payload",
        {}
    )

    headers = payload.get(
        "headers",
        []
    )

    return {
        "id": message.get("id"),
        "thread_id": message.get("threadId"),
        "sender": get_header(headers, "From"),
        "recipient": get_header(headers, "To"),
        "subject": get_header(headers, "Subject"),
        "date": get_header(headers, "Date"),
        "body": extract_body(payload),
    }