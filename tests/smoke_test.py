"""
smoke_test.py
~~~~~~~~~~~~~
Sanity check that the Gmail MCP server is wired up correctly.

This is NOT a unit test suite — it makes real calls to the Gmail API
using your stored credentials. Run this after any significant change
to verify the whole stack still works before restarting Claude Desktop.

Usage:
    python smoke_test.py

What it checks:
    1. Credentials and token.json are present
    2. Gmail authentication succeeds
    3. fetch_messages() returns data in the expected shape
    4. create_new_draft() can save a draft to Gmail
    5. All four MCP tool definitions are registered correctly

A PASS on all five checks means Claude Desktop should work.
"""

import sys
import json

# ── Helpers ───────────────────────────────────────────────────────────────────

def passed(msg):
    print(f"  ✓ {msg}")

def failed(msg):
    print(f"  ✗ {msg}")
    sys.exit(1)

def section(msg):
    print(f"\n{msg}")

# ── Checks ────────────────────────────────────────────────────────────────────

section("1. Checking credentials files...")
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(BASE_DIR, "credentials.json")):
    passed("credentials.json found")
else:
    failed("credentials.json not found — run the auth setup first")

if os.path.exists(os.path.join(BASE_DIR, "token.json")):
    passed("token.json found")
else:
    failed("token.json not found — run test_auth.py first")


section("2. Checking Gmail authentication...")
try:
    from gmail_mcp.gmail_client import get_gmail_service
    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    passed(f"Authenticated as {profile['emailAddress']}")
except Exception as e:
    failed(f"Authentication failed: {e}")


section("3. Checking fetch_messages()...")
try:
    from gmail_mcp.gmail_client import fetch_messages
    emails = fetch_messages(service, max_results=1, label_ids=["INBOX"])
    if isinstance(emails, list):
        passed(f"fetch_messages() returned a list ({len(emails)} email(s))")
    else:
        failed(f"fetch_messages() returned unexpected type: {type(emails)}")

    if emails:
        email = emails[0]
        for field in ["message_id", "thread_id", "from", "subject", "date", "body"]:
            if field not in email:
                failed(f"Email missing expected field: '{field}'")
        passed("Email has all expected fields (message_id, thread_id, from, subject, date, body)")
    else:
        passed("Inbox appears empty — shape check skipped")
except Exception as e:
    failed(f"fetch_messages() raised an error: {e}")


section("4. Checking create_new_draft()...")
try:
    from gmail_mcp.gmail_client import create_new_draft
    draft = create_new_draft(
        service,
        to=profile["emailAddress"],  # send to yourself
        subject="[SMOKE TEST] Gmail MCP Server",
        body="This is an automated smoke test draft. Safe to delete.",
    )
    if "id" in draft:
        passed(f"Draft created successfully (draft_id: {draft['id']})")
    else:
        failed(f"create_new_draft() returned unexpected response: {draft}")
except Exception as e:
    failed(f"create_new_draft() raised an error: {e}")


section("5. Checking MCP tool definitions...")
try:
    from gmail_mcp.tools import TOOL_DEFINITIONS
    expected_tools = {"get_unread_emails", "get_recent_emails", "create_draft_reply", "create_new_draft"}
    registered_tools = {t.name for t in TOOL_DEFINITIONS}

    missing = expected_tools - registered_tools
    if missing:
        failed(f"Missing tool definitions: {missing}")
    else:
        passed(f"All {len(expected_tools)} tools registered: {', '.join(sorted(registered_tools))}")
except Exception as e:
    failed(f"Could not load tool definitions: {e}")

section("6. Checking tone guidelines...")
guidelines_path = os.path.join(BASE_DIR, "context", "tone_guidelines.md")
if os.path.exists(guidelines_path):
    passed("tone_guidelines.md found")
else:
    failed("tone_guidelines.md not found in context/")


print("\n✓ All checks passed — server should work correctly with Claude Desktop.\n")