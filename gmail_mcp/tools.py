"""
tools.py
~~~~~~~~
MCP tool definitions and handlers.
Knows about MCP and calls gmail_client — contains no raw Gmail API calls.
"""

import json

import mcp.types as types

from gmail_mcp.gmail_client import (
    get_gmail_service,
    fetch_messages,
    create_draft_reply,
    create_new_draft,
)

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    types.Tool(
        name="get_unread_emails",
        description=(
            "Fetches unread emails from the Gmail inbox. "
            "Returns sender, subject, body and IDs needed to reply. "
            "Use this when the user specifically asks for unread emails."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of unread emails to fetch (default 5).",
                    "default": 5,
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
                    "description": "Maximum number of recent emails to fetch (default 5).",
                    "default": 5,
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

# ── Tool handlers ─────────────────────────────────────────────────────────────

async def handle_tool_call(name: str, arguments: dict) -> list[types.TextContent]:
    """Route a tool call to the appropriate handler."""

    if name == "get_unread_emails":
        return await _get_unread_emails(arguments)

    if name == "get_recent_emails":
        return await _get_recent_emails(arguments)

    if name == "create_draft_reply":
        return await _create_draft_reply(arguments)

    if name == "create_new_draft":
        return await _create_new_draft(arguments)

    raise ValueError(f"Unknown tool: {name}")


async def _get_unread_emails(arguments: dict) -> list[types.TextContent]:
    max_results = arguments.get("max_results", 5)
    service = get_gmail_service()
    emails = fetch_messages(service, max_results, label_ids=["INBOX", "UNREAD"])

    if not emails:
        return [types.TextContent(type="text", text="No unread emails found.")]

    return [types.TextContent(type="text", text=json.dumps(emails, indent=2))]


async def _get_recent_emails(arguments: dict) -> list[types.TextContent]:
    max_results = arguments.get("max_results", 5)
    service = get_gmail_service()
    emails = fetch_messages(service, max_results, label_ids=["INBOX"])

    if not emails:
        return [types.TextContent(type="text", text="No emails found.")]

    return [types.TextContent(type="text", text=json.dumps(emails, indent=2))]


async def _create_draft_reply(arguments: dict) -> list[types.TextContent]:
    service = get_gmail_service()
    draft = create_draft_reply(
        service,
        thread_id=arguments["thread_id"],
        message_id=arguments["message_id"],
        to=arguments["to"],
        subject=arguments["subject"],
        body=arguments["body"],
    )

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "Draft created successfully",
                    "draft_id": draft["id"],
                    "thread_id": arguments["thread_id"],
                },
                indent=2,
            ),
        )
    ]


async def _create_new_draft(arguments: dict) -> list[types.TextContent]:
    service = get_gmail_service()
    draft = create_new_draft(
        service,
        to=arguments["to"],
        subject=arguments["subject"],
        body=arguments["body"],
    )

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "Draft created successfully",
                    "draft_id": draft["id"],
                    "to": arguments["to"],
                    "subject": arguments["subject"],
                },
                indent=2,
            ),
        )
    ]