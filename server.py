import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

# ── Auth ──────────────────────────────────────────────────────────────────────

# Read-only by design — only request permissions we actually need.
# gmail.readonly  : read emails
# gmail.compose   : create drafts (does not require gmail.modify)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _decode_body(payload: dict) -> str:
    """Recursively extract plain text body from a Gmail message payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            result = _decode_body(part)
            if result:
                return result

    return ""


def _get_header(headers: list, name: str) -> str:
    """Extract a named header value from a list of header dicts."""
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def _add_signature(body: str) -> str:
    """Append a standard signature to an email body."""
    signature = "\n\n--\nThis email was drafted with the assistance of Claude AI via a Gmail MCP Server."
    return body + signature


def _fetch_messages(service, max_results: int, label_ids: list = None, query: str = None) -> list:
    """Shared helper to fetch and format a list of messages."""
    kwargs = {"userId": "me", "maxResults": max_results}
    if label_ids:
        kwargs["labelIds"] = label_ids
    if query:
        kwargs["q"] = query

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
        body = _decode_body(msg.get("payload", {}))

        if not body.strip():
            body = msg.get("snippet", "(no body available)")

        emails.append({
            "message_id": msg["id"],
            "thread_id": msg["threadId"],
            "from": _get_header(headers, "From"),
            "subject": _get_header(headers, "Subject"),
            "date": _get_header(headers, "Date"),
            "body": body.strip(),
        })

    return emails


# ── MCP Server ────────────────────────────────────────────────────────────────

server = Server("gmail-mcp-server")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_unread_emails",
            description=(
                "Fetches unread emails from the Gmail inbox. "
                "Returns sender, subject, body and IDs needed to reply."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of unread emails to fetch (default 20).",
                        "default": 20,
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_recent_emails",
            description=(
                "Fetches the most recent emails from Gmail regardless of read status. "
                "Use this tool — NOT get_unread_emails — when the user asks for 'all emails', "
                "'recent emails', 'latest emails', or anything that does not specifically "
                "mention unread. Also use this for summarising what needs attention."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of recent emails to fetch (default 20).",
                        "default": 20,
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="create_draft_reply",
            description=(
                "Creates a draft reply to an email in Gmail. "
                "The draft is correctly threaded so it appears as a reply, not a new email."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "The Gmail thread ID of the email you are replying to.",
                    },
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID of the specific email you are replying to.",
                    },
                    "to": {
                        "type": "string",
                        "description": "The recipient email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject line (should start with 'Re: ' for replies).",
                    },
                    "body": {
                        "type": "string",
                        "description": "The plain text body of the reply.",
                    },
                },
                "required": ["thread_id", "message_id", "to", "subject", "body"],
            },
        ),
        types.Tool(
            name="create_new_draft",
            description=(
                "Creates a new draft email in Gmail to any recipient. "
                "Use this for composing fresh emails, not replies."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The recipient email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject line of the email.",
                    },
                    "body": {
                        "type": "string",
                        "description": "The plain text body of the email.",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "get_unread_emails":
        return await _handle_get_unread_emails(arguments)

    if name == "get_recent_emails":
        return await _handle_get_recent_emails(arguments)

    if name == "create_draft_reply":
        return await _handle_create_draft_reply(arguments)

    if name == "create_new_draft":
        return await _handle_create_new_draft(arguments)

    raise ValueError(f"Unknown tool: {name}")


# ── Tool handlers ─────────────────────────────────────────────────────────────

async def _handle_get_unread_emails(arguments: dict) -> list[types.TextContent]:
    max_results = arguments.get("max_results", 5)
    service = get_gmail_service()

    emails = _fetch_messages(service, max_results, label_ids=["INBOX", "UNREAD"])

    if not emails:
        return [types.TextContent(type="text", text="No unread emails found.")]

    return [types.TextContent(type="text", text=json.dumps(emails, indent=2))]


async def _handle_get_recent_emails(arguments: dict) -> list[types.TextContent]:
    max_results = arguments.get("max_results", 5)
    service = get_gmail_service()

    emails = _fetch_messages(service, max_results, label_ids=["INBOX"])

    if not emails:
        return [types.TextContent(type="text", text="No emails found.")]

    return [types.TextContent(type="text", text=json.dumps(emails, indent=2))]


async def _handle_create_draft_reply(arguments: dict) -> list[types.TextContent]:
    thread_id = arguments["thread_id"]
    message_id = arguments["message_id"]
    to = arguments["to"]
    subject = arguments["subject"]
    body = arguments["body"]

    service = get_gmail_service()

    mime_message = MIMEMultipart()
    mime_message["To"] = to
    mime_message["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
    mime_message["In-Reply-To"] = message_id
    mime_message["References"] = message_id
    mime_message.attach(MIMEText(_add_signature(body), "plain"))

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

    draft = (
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

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "Draft created successfully",
                    "draft_id": draft["id"],
                    "thread_id": thread_id,
                },
                indent=2,
            ),
        )
    ]


async def _handle_create_new_draft(arguments: dict) -> list[types.TextContent]:
    to = arguments["to"]
    subject = arguments["subject"]
    body = arguments["body"]

    service = get_gmail_service()

    mime_message = MIMEMultipart()
    mime_message["To"] = to
    mime_message["Subject"] = subject
    mime_message.attach(MIMEText(_add_signature(body), "plain"))

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")

    draft = (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={"message": {"raw": raw}},
        )
        .execute()
    )

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "Draft created successfully",
                    "draft_id": draft["id"],
                    "to": to,
                    "subject": subject,
                },
                indent=2,
            ),
        )
    ]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())