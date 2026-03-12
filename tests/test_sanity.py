"""
tests/test_sanity.py
~~~~~~~~~~~~~~~~~~~~
Lightweight pytest checks that verify the project is correctly structured
and configured. Makes no API calls and creates no drafts.

Tests marked @pytest.mark.local_only require credentials.json and token.json
which are not in the repo — these are skipped in CI automatically.

Run all tests locally:
    python -m pytest tests/test_sanity.py -v

Run only CI-safe tests:
    python -m pytest tests/test_sanity.py -v -m "not local_only"
"""

import os
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# True when running in CI — used to skip tests that need local credentials
IN_CI = os.environ.get("CI") == "true"


# ── File structure ────────────────────────────────────────────────────────────

@pytest.mark.skipif(IN_CI, reason="credentials.json not available in CI")
def test_credentials_file_exists():
    """credentials.json must be present in the project root."""
    assert os.path.exists(os.path.join(BASE_DIR, "credentials.json")), \
        "credentials.json not found — download it from Google Cloud Console"


@pytest.mark.skipif(IN_CI, reason="token.json not available in CI")
def test_token_file_exists():
    """token.json must be present — run python -m tests.test_auth to generate it."""
    assert os.path.exists(os.path.join(BASE_DIR, "token.json")), \
        "token.json not found — run: python -m tests.test_auth"


def test_tone_guidelines_exists():
    """Tone guidelines file must exist for the get_tone_guidelines tool."""
    assert os.path.exists(os.path.join(BASE_DIR, "context", "tone_guidelines.md")), \
        "context/tone_guidelines.md not found"


def test_tone_guidelines_not_empty():
    """Tone guidelines file must have content."""
    path = os.path.join(BASE_DIR, "context", "tone_guidelines.md")
    if os.path.exists(path):
        with open(path) as f:
            content = f.read().strip()
        assert len(content) > 0, "tone_guidelines.md is empty"


# ── Imports ───────────────────────────────────────────────────────────────────

def test_helpers_imports():
    """gmail_mcp.helpers must import without errors."""
    from gmail_mcp.helpers import decode_body, get_header, add_signature
    assert callable(decode_body)
    assert callable(get_header)
    assert callable(add_signature)


def test_gmail_client_imports():
    """gmail_mcp.gmail_client must import without errors."""
    from gmail_mcp.gmail_client import get_gmail_service, fetch_messages
    assert callable(get_gmail_service)
    assert callable(fetch_messages)


def test_tools_imports():
    """gmail_mcp.tools must import without errors."""
    from gmail_mcp.tools import TOOL_DEFINITIONS, handle_tool_call
    assert callable(handle_tool_call)
    assert isinstance(TOOL_DEFINITIONS, list)


# ── Tool definitions ──────────────────────────────────────────────────────────

def test_all_tools_registered():
    """All expected tools must be present in TOOL_DEFINITIONS."""
    from gmail_mcp.tools import TOOL_DEFINITIONS
    registered = {t.name for t in TOOL_DEFINITIONS}
    expected = {
        "get_unread_emails",
        "get_recent_emails",
        "create_draft_reply",
        "create_new_draft",
        "get_tone_guidelines",
    }
    missing = expected - registered
    assert not missing, f"Missing tools: {missing}"


def test_all_tools_have_descriptions():
    """Every tool must have a non-empty description."""
    from gmail_mcp.tools import TOOL_DEFINITIONS
    for tool in TOOL_DEFINITIONS:
        assert tool.description and len(tool.description.strip()) > 0, \
            f"Tool '{tool.name}' has no description"


def test_required_tools_have_required_fields():
    """create_draft_reply must declare its required fields."""
    from gmail_mcp.tools import TOOL_DEFINITIONS
    tool = next(t for t in TOOL_DEFINITIONS if t.name == "create_draft_reply")
    required = tool.inputSchema.get("required", [])
    for field in ["thread_id", "message_id", "to", "subject", "body"]:
        assert field in required, f"create_draft_reply missing required field: {field}"