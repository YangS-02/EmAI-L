# Look into the parsing issue of gmail MIME

import json
from gmail_client import authenticate_gmail, decode_body
from bs4 import BeautifulSoup
import sqlite3
from pathlib import Path



service = authenticate_gmail()
# Get the specific email
# users.messages.get: Gets the specified message.
result = service.users().messages().get(
    userId = "me",
    id = "19f668704f505ed8",
    format = "full"
).execute() # <-- remember to add execute()
# print("="*40, "payload", "="*40)
payload = result["payload"]
# print(json.dumps(payload, indent=2))

# print("="*40, "parts (partId = 0) (text/plain)", "="*40)
part1 = payload["parts"][0]["body"]["data"]
# print(decode_body(part1))
#
# print("="*40, "parts (partId = 1) (text/html)", "="*40)
part2 = payload["parts"][1]["body"]["data"]
# print(decode_body(part2))
"""
The current pipeline: Gmail MIME --> Base64URL encoded body.data --> decode_body() --> decoded MIME
The problem is: there are leftover HTML stuff in the text decoded from text/plain. Not a problem from the decoder
itself. 
The next step is to go through the databbase and see how frequent this problem is. And also see if it has the same
problem when decoding from the text/html.
"""


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["style", "script", "head"]):
        tag.decompose()

    return soup.get_text(
        separator="\n",
        strip=True
    )
# print(html_to_text(decode_body(part2)))
"""
The problem with this is that the structure is not well preserved:
============ From html ============
NOTE
: Members of the Class of 2027 who participated in OCI last year do not have to take any additional action. However, we do encourage you to review the new OCI orientation and our student
OCI website
to refresh your memory of OCI policies and procedures.
IMPORTANT FALL 2026 OCI DATES
Mid-August
: Fall OCI job applications go live for sign-up
============ From plain ============
NOTE: Members of the Class of 2027 who participated in OCI last year do not have to take any additional action. However, we do encourage you to review the new OCI orientation and our student OCI website to refresh your memory of OCI policies and procedures.
IMPORTANT FALL 2026 OCI DATES

Mid-August: Fall OCI job applications go live for sign-up

Question: Is structure to the text important to the quality of the embedding models?
"""


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_DIR / "data" / "emails.db"
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()
cursor.execute(
    """
    SELECT id
    FROM (
            SELECT id, body,
                   (
                       CASE WHEN LOWER(body) LIKE '%background:%'   THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%border-color:%' THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%font-size:%'    THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%padding:%'      THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%margin:%'       THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%table.button%'  THEN 1 ELSE 0 END +
                       CASE WHEN LOWER(body) LIKE '%.wrapper%'      THEN 1 ELSE 0 END +
                       CASE WHEN body LIKE '%{%'                    THEN 1 ELSE 0 END +
                       CASE WHEN body LIKE '%}%'                    THEN 1 ELSE 0 END
                   ) AS hits
            FROM emails
        ) AS sq
    WHERE hits >= 4;
    """
)
result = cursor.fetchall()
print(result)
print(len(result))
connection.close()
corrupt_ids = [emailId[0] for emailId in result]
print(corrupt_ids)
"""
18 out of 500 emails that have these issues. 
"""
