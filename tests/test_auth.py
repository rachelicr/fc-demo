"""
test_auth.py
~~~~~~~~~~~~
One-time OAuth authentication setup for the Gmail MCP Server.

Run this script once before using the server for the first time, or any
time token.json is deleted or expires. It will open a browser window
asking you to grant Gmail access, then save a token.json file containing
your credentials for future use.

On WSL you will need to manually copy the URL into a Windows browser.
The redirect will complete via localhost:8081.

Usage:
    python -m tests.test_auth

Output:
    token.json  — saved to the project root, used by the server automatically.
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Walk up from tests/ to the project root where credentials.json lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
creds = flow.run_local_server(port=8081, open_browser=False)

with open(TOKEN_FILE, 'w') as token:
    token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)
profile = service.users().getProfile(userId='me').execute()
print(f"Connected as: {profile['emailAddress']}")
print(f"token.json saved to {TOKEN_FILE} — you're ready to run the server.")