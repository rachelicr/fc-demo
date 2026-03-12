"""
gmail_client.py
~~~~~~~~~~~~~~~
All Gmail API interaction — authentication, fetching emails, creating drafts.
No MCP knowledge lives here.
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from gmail_mcp.helpers import decode_body, get_header, add_signature

# Read-only by design — only request permissions we actually need.
# gmail.readonly : read emails
# gmail.compose  : create drafts (does not require gmail.modify)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def get_gmail_service():
    """Authenticate and return a Gmail API service client."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8081, open_browser=False)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_messages(service, max_results: int, label_ids: list = None) -> list:
    """Fetch and format a list of messages from Gmail."""
    kwargs = {"userId": "me", "maxResults": max_results}
    if label_ids:
        kwargs["labelIds"] = label_ids

    result = service.users().messages().list(**kwargs).execute()
    messages = result.get("messages", [])

    emails = []
    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="full")
            .execute()
        )

        headers = msg.get("payload", {}).get("headers", [])
        body = decode_body(msg.get("payload", {}))

        if not body.strip():
            body = msg.get("snippet", "(no body available)")

        emails.append({
            "message_id": msg["id"],
            "thread_id": msg["threadId"],
            "from": get_header(headers, "From"),
            "subject": get_header(headers, "Subject"),
            "date": get_header(headers, "Date"),
            "body": body.strip(),
        })

    return emails


def create_draft_reply(service, thread_id: str, message_id: str, to: str, subject: str, body: str) -> dict:
    """Create a correctly threaded draft reply in Gmail."""
    mime_message = MIMEMultipart()
    mime_message["To"] = to
    mime_message["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
    mime_message["In-Reply-To"] = message_id
    mime_message["References"] = message_id
    mime_message.attach(MIMEText(add_signature(body), "plain"))

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

    return (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={
                "message": {
                    "raw": raw,
                    "threadId": thread_id,
                }
            },
        )
        .execute()
    )


def create_new_draft(service, to: str, subject: str, body: str) -> dict:
    """Create a fresh draft email in Gmail to any recipient."""
    mime_message = MIMEMultipart()
    mime_message["To"] = to
    mime_message["Subject"] = subject
    mime_message.attach(MIMEText(add_signature(body), "plain"))

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

    return (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={"message": {"raw": raw}},
        )
        .execute()
    )