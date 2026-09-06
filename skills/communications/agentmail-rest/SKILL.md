---
name: agentmail-rest
description: "Manage AgentMail inboxes, messages, threads, and sends."
version: 0.1.0
author: Hermes
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, AgentMail, REST, API]
---

# AgentMail REST API

Use the AgentMail REST API to create inboxes, list mail, read threads, and send messages programmatically. This skill covers direct HTTP calls through the `terminal` tool; it does not cover MCP transport or skill-packaged CLIs.

## When to Use

- "check my agent inbox"
- "read my AgentMail messages"
- "send an email from my agent inbox"
- "list AgentMail threads/messages"
- "set up AgentMail access via API key"

## Prerequisites

- `AGENTMAIL_API_KEY` or a bearer token with inbox/read/send scope
- `terminal` with `curl`
- Base URL: `https://api.agentmail.to`
- Inbox identifier in the form `local-part@agentmail.to`

## How to Run

Invoke all endpoints through the `terminal` tool with `curl -s`. Parse JSON from stdout.

## Quick Reference

| Action | Method | Path |
|--------|--------|------|
| List inboxes | GET | `/inboxes` |
| List messages | GET | `/inboxes/{inbox_id}/messages` |
| Get thread | GET | `/inboxes/{inbox_id}/threads/{thread_id}` |
| Send message | POST | `/inboxes/{inbox_id}/messages/send` |
| Get message | GET | `/inboxes/{inbox_id}/messages/{message_id}` |
| Create inbox | POST | `/inboxes` |

Auth header: `Authorization: Bearer $AGENTMAIL_API_KEY`
Content-Type for writes: `application/json`

## Procedure

1. List inboxes:
   - `curl -s https://api.agentmail.to/inboxes -H "Authorization: Bearer $AGENTMAIL_API_KEY"`
   - Parse `inboxes[].inbox_id` and `inboxes[].email`.
2. List messages in an inbox:
   - URL-encode `@` as `%40` in the inbox path.
   - `curl -s "https://api.agentmail.to/inboxes/{url_encoded_inbox_id}/messages" -H "Authorization: Bearer $AGENTMAIL_API_KEY"`
   - Parse `messages[].message_id`, `thread_id`, `subject`, `from`, `preview`.
3. Read a thread to get full message content:
   - Prefer `GET /inboxes/{inbox_id}/threads/{thread_id}` over direct message GET.
   - Direct `GET /inboxes/{inbox_id}/messages/{message_id}` can return `not_found` even when the message exists; the thread endpoint returns the full `messages[]` array with `text`, `html`, and `headers`.
4. Send a message:
   - `curl -s -X POST https://api.agentmail.to/inboxes/{url_encoded_inbox_id}/messages/send -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" -d '{"to":["recipient@example.com"],"subject":"Hello","text":"Body"}'`
5. Identify welcome mail:
   - The first message from `admin@agentmail.to` with subject `Welcome to AgentMail, your inbox is ready` is the standard onboarding mail. Treat it as expected setup noise, not an actual task email.

## Pitfalls

- Always URL-encode the inbox path segment; unencoded `@` causes route mismatch or 404.
- Message GET may return `not_found` while thread GET works; when direct message read fails, fall back to thread read using `thread_id` from the list response.
- Do not echo the bearer token to the user; redact it in summaries.
- Inbox creation and send endpoints may require additional scopes; if a 403 appears, verify the key's permissions in the AgentMail console.

## Verification

```bash
curl -s https://api.agentmail.to/inboxes -H "Authorization: Bearer $AGENTMAIL_API_KEY"
```

Expected result: JSON with `count` and an `inboxes` array containing at least one entry with `inbox_id`, `email`, and `organization_id`.
