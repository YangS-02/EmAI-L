# Investigate into this MIME format
import json
from gmail_client import authenticate_gmail, decode_body


# Connection to Gmail API
service = authenticate_gmail()
# Get the most recent email
# users.messages.list: Lists the messages in the user's mailbox (https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
results = service.users().messages().list(
    userId="me",
    maxResults=1 # Maximum number of messages to return (defaults to 100, maximum 500)
).execute()
print("=============== results ===============")
print(type(results))
print(results)
"""
Return structure:
{
  "messages": [
    {
      object (Message) --> Each message resource contain only an id and a threadId. Addition detail is accessed using get() 👇
    }
  ],
  "nextPageToken": string,
  "resultSizeEstimate": integer
}
"""


# Fetch the full message
message_id = results["messages"][0]["id"]
message = service.users().messages().get(
    # Path parameter
    userId="me",
    id=message_id,  # The ID of the message to retrieve. This ID is usually retrieved using messages.list
    # Query parameter
    format="full"  # The format to return the message in:
    # full: Returns the full email message data with body content parsed in the payload field; the raw field is not used. Format cannot be used when accessing the api using the gmail.metadata scope.
    # minimal: Returns only email message ID and labels; does not return the email headers, body, or payload.
    # raw: Returns the full email message data with body content in the raw field as a base64url encoded string; the payload field is not used. Format cannot be used when accessing the api using the gmail.metadata scope.
    # metadata: Returns only email message ID, labels, and email headers.
).execute()

payload = message["payload"]

print("=============== payload ===============")
print(type(payload))
print(json.dumps(payload, indent=2))
def print_mime_tree(part, indent=0):
    prefix = "  " * indent

    mime_type = part.get("mimeType", "")
    filename = part.get("filename", "")
    body = part.get("body", {})
    data = body.get("data")

    print(f"{prefix}- {mime_type}")

    if filename:
        print(f"{prefix}  filename: {filename}")

    if data and mime_type in ["text/plain", "text/html"]:
        decoded = decode_body(data)

        print(f"{prefix}  content preview:")
        print(f"{prefix}  {decoded[:200]!r}")

    for child in part.get("parts", []):
        print_mime_tree(child, indent + 1)
print_mime_tree(payload)
