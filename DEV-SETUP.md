# Setup Guide

This guide walks you through everything you need before writing any code — Claude Desktop installed and connected, and Gmail API credentials ready to use.

---

## Part 1: Claude Desktop

### 1.1 Install Claude Desktop

### 1.2 Locate the Claude Desktop config file
Claude Desktop uses a config file to know which MCP servers to connect to. You'll need to edit this later, but find it now so you know where it is.
C:\Users\ralcraft\AppData\Roaming\Claude\claude_desktop_config.json

---

## Part 2: Google Cloud Project & Gmail API

### 2.1 Create a Google Cloud Project
### 2.2 Enable the Gmail API
### 2.3 Configure the OAuth Consent Screen
### 2.4 Create OAuth 2.0 Credentials

https://console.cloud.google.com/auth/overview?project=fc-demo-mcp
> **Keep this file private.** Never commit `credentials.json` to GitHub. You'll add it to `.gitignore`.

---

## Part 3: Python Environment

The MCP server will be written in Python. Get your environment ready now.

### 3.1 Check Python is installed

```bash
python --version
```

You need Python 3.10 or higher. If you don't have it, download it from [https://python.org](https://python.org).

### 3.2 Create a project folder

```bash
mkdir gmail-mcp-server
cd gmail-mcp-server
```

### 3.3 Create a virtual environment

```bash
conda create -n gmail-mcp python=3.11
conda activate gmail-mcp
python -m pip install mcp google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```
which python = /home/ralcraft/miniforge3/envs/gmail-mcp/bin/python
### 3.4 Install dependencies

```bash
pip install mcp google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

| Package | Purpose |
|---|---|
| `mcp` | The MCP SDK for building your server |
| `google-auth` | Google authentication library |
| `google-auth-oauthlib` | OAuth 2.0 flow for desktop apps |
| `google-api-python-client` | Gmail API client |

---

## Part 4: Verify Gmail API Access

Before building the server, confirm your credentials work by running a quick test.

Place your `credentials.json` in the project folder, then create a file called `test_auth.py`:

```bash
python test_auth.py
```
> The first run will create a `token.json` file in your project folder. This stores your access token so you don't have to re-authorise every time. Add both `credentials.json` and `token.json` to your `.gitignore`.

---

## Checklist

- [x] Claude Desktop installed and signed in
- [x] Google Cloud project created
- [x] Gmail API enabled
- [x] OAuth consent screen configured with correct scopes
- [x] Your Gmail added as a test user
- [x] `credentials.json` downloaded
- [x] Python 3.10+ installed
- [x] Conda environment created and activated
- [x] Dependencies installed
- [x] Test auth script runs successfully

---

## Next Step

Edit: C:\Users\ralcraft\AppData\Roaming\Claude\claude_desktop_config.json
Specifically needed to be WSL compliant:


---

Spec: read 10 emails, reply to an email as a draft or draft a new emai;


---

## AI Attribute
ClaudeAI was used in the creation of this as a pair-programming partner, partly due to specification of the project requirements themselves.