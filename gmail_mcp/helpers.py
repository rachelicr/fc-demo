"""
helpers.py
~~~~~~~~~~
Pure utility functions with no Gmail or MCP dependencies.
"""

import base64


def decode_body(payload: dict) -> str:
    """Recursively extract plain text body from a Gmail message payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            result = decode_body(part)
            if result:
                return result

    return ""


def get_header(headers: list, name: str) -> str:
    """Extract a named header value from a list of header dicts."""
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def add_signature(body: str) -> str:
    """Append a standard signature to an email body."""
    signature = "\n\n--\nThis email was drafted with the assistance of Claude AI via a Gmail MCP Server."
    return body + signature