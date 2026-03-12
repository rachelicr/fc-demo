# Tests

This project uses two levels of testing, appropriate for a demo-scale MCP server.

## test_auth.py

Located in the project root. This is a one-time setup script rather than a test in
the traditional sense — it runs the full OAuth flow against the real Gmail API and
saves a `token.json` file to disk.

Run this first before anything else, and again any time `token.json` is deleted or
your credentials expire.

```bash
python -m tests.test_auth
```

## smoke_test.py

Located in `tests/`. A sanity check that the whole stack is wired up correctly.
Run this after any significant change to the codebase before restarting Claude Desktop.

It makes real calls to the Gmail API using your stored credentials and checks:

1. `credentials.json` and `token.json` are present
2. Gmail authentication succeeds
3. `fetch_messages()` returns data in the expected shape
4. `create_new_draft()` can save a draft to Gmail
5. All four MCP tool definitions are registered correctly

Run from the project root:

```bash
python -m tests.smoke_test
```

Note: the smoke test will create a real draft in your Gmail inbox as part of
check 4. You can safely delete it afterwards.

## Why no unit tests?

This is a deliberately lightweight project — a thin wrapper around the Gmail API
exposed as MCP tools. The meaningful logic lives in Gmail itself and in Claude's
natural language interpretation, neither of which is sensibly unit tested here.

A full unit test suite with mocks would add complexity without meaningfully
increasing confidence. The smoke test gives a better signal for a project of
this kind: if all five checks pass against real credentials, the server works.

For a production system the right additions would be unit tests for `helpers.py`
(pure functions, easy to test), and integration tests using a dedicated test
Gmail account.