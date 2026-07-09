---
title: "Studying for the Claude Certified Architect Exam — Week 2: Tool Design & MCP"
date: 2026-07-19
series: "CCA-F Study Log"
week: 2
domain: "Tool Design & MCP Integration (18%)"
tags: [claude, tools, mcp, tool-design, error-handling, study-log]
---

Week 2 of my [Claude Certified Architect — Foundations](/blog/week1-agentic-architecture) study log. Last week was the agentic loop and multi-agent orchestration. This week is **Tool Design & MCP Integration (18%)** — how you actually *define* the tools an agent uses, why one field matters more than all the rest, and how MCP turns a mess of custom integrations into something reusable.

There's a thread running through the whole domain, and it's the same idea from Week 1:

> **The model is blind. It only knows a tool through the text you write about it.**

Everything below is a consequence of that.

---

## The anatomy of a tool

A tool definition has exactly three parts:

```python
{
    "name": "get_weather",                       # ① what it's called
    "description": "Get the current weather for a city. "
                   "Use when the user asks about weather, temperature, or rain.",  # ② what it does + WHEN to use it
    "input_schema": {                            # ③ what inputs it needs
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Paris'"}
        },
        "required": ["city"]
    }
}
```

- **`name`** — the identifier.
- **`description`** — what the tool does and *when* to use it.
- **`input_schema`** — the parameters, their types, and which are required.

Simple. But the weight is wildly unevenly distributed.

---

## The `description` is the whole ballgame

Picture the model as a **new intern** you've handed a stack of index cards — one per tool. The intern can't see inside any tool; they can only read the cards. Which tool they pick depends entirely on **how clearly each card is written**.

> **To the model, the description *is* the tool.** It doesn't matter how good your tool's internal code is — the model only sees the description.

So a vague description gets you a wrong pick or a missed call:

```python
# ❌ vague — the model doesn't know WHEN to reach for this
"description": "Analyze text"

# ✅ specific — states the trigger condition and the effect
"description": "Run sentiment analysis (positive/negative) on a short text snippet the user pasted. Returns the sentiment label."
```

The key upgrade is writing **when to use it**, not just what it does. (Newer Claude models are conservative about reaching for tools, so a description that spells out the trigger condition measurably improves the should-call rate.)

### The boundary-overlap trap

This is the single most exam-tested idea in the domain. Suppose you have two tools with near-identical descriptions:

```python
{ "name": "analyze_content",  "description": "Analyze content" }
{ "name": "analyze_document", "description": "Analyze document" }
```

The user says "analyze this." Which one? The model can't tell — the cards are indistinguishable, so it picks wrong. The fix is **not** to pile on system-prompt instructions, delete a tool, or merge them. The fix is to **clarify the boundaries in the descriptions**:

```python
{ "name": "analyze_content",
  "description": "Analyze a PLAIN TEXT snippet's sentiment and keywords. For text the user pasted directly." }
{ "name": "analyze_document",
  "description": "Analyze an UPLOADED FILE (PDF/Word): structure and summary. For document files the user uploaded." }
```

Now the boundary is obvious: pasted text → A, uploaded file → B.

> **Exam judgment:** tool picked wrong? First check whether the descriptions overlap — don't reach for "add a stern instruction," "delete the tool," or "merge them." Those are patches; fixing the description fixes the root cause.

Here's a scenario in the exam's style:

> An agent has `send_message` ("Send a message") and `send_email` ("Send a message"). Asked to email someone, it sometimes fires the chat tool instead. Best fix?
>
> **A.** Add a system prompt: "always use send_email for emails"
> **B.** Delete send_message to avoid confusion
> **C.** Rewrite both descriptions so the boundary is clear (send_email → "sends an email to an address"; send_message → "sends an instant chat message")
> **D.** Merge them into one `send` tool

The answer is **C**. A is a fragile patch that leaves two identical cards. B throws away a real capability. D makes the model guess *more*. Clarifying the descriptions is the only root-cause fix.

---

## Built-in tools: don't reinvent the hammer

Some tools are so common that Anthropic ships them pre-made — you declare them, you don't implement them. Think of a toolbox that comes with a standard hammer and screwdriver; you don't forge your own.

They split by **who executes them**:

| Type | Who runs it | Examples |
|---|---|---|
| **Server-side** | Anthropic's infrastructure | `web_search`, code execution |
| **Client-side** | Your program (Anthropic only defines the interface) | `bash`, text editor |

Web search runs entirely on Anthropic's side — you get results back. The text editor is *defined* by Anthropic but **your program does the actual file editing** (the model is blind; it can't touch your files).

For code-exploration work, the exam cares about picking the right search/file tool:

| Tool | Use it to… |
|---|---|
| **Grep** | search by **content** ("where is `login()` called?") |
| **Glob** | search by **filename pattern** ("all `test_*.py` files") |
| **Read / Write / Edit** | read a file / overwrite a whole file / replace a slice |
| **Bash** | run shell commands |

> **The one people mix up:** Grep searches *what's inside* files; Glob searches *what files are named*. "Find everywhere `deprecated_api` is used" → Grep (content). "Find all the test files" → Glob (names).

One documented gotcha: **`Edit` can fail** (it needs the file read first, and the target string must be unique). The correct fallback is **Read then Write** — re-read the file, then rewrite it — not hammering `Edit` again.

---

## MCP: the USB-C for AI tools

Now the big one. **MCP (Model Context Protocol)** solves an integration mess.

Before a standard, every AI app had to hand-write a custom connector to every capability — GitHub, your database, Slack, local notes. That's **M apps × N capabilities = M×N** bespoke connectors, each written independently, none reusable.

MCP is a **universal interface standard** — think **USB-C**. Before USB-C, every device had its own cable. After, one standard port, and anything that speaks it just plugs in.

```
No MCP:  M × N custom connectors (chaos)
MCP:     M + N  — each side implements the standard once

  Claude ──┐                       ┌── GitHub's MCP server
  Tool X ──┼── all speak MCP ───────┼── database's MCP server
  App Y  ──┘                        └── Slack's MCP server
```

Two roles to remember:

- **MCP server** — provides a capability, exposed via the MCP standard (like a USB-C device).
- **MCP client** — the AI app (Claude Code, Claude Desktop) that connects and uses it (like your laptop).

GitHub builds its MCP server **once**, and every MCP-speaking app can use it. **Write once, everyone benefits** — that's the whole value: standardization + reuse.

### Config: where you write it decides who gets it

To use an MCP server, you configure it — and *where* you put that config decides *who* can use it:

| File | Level | Who gets it | Shared via version control? |
|---|---|---|---|
| **`.mcp.json`** | project | everyone on the project | ✅ yes — it lives in the repo |
| **`~/.claude.json`** | user | only you | ❌ no — it's in your home dir |

Project-level is a **shared toolbox bolted to the workshop wall** — it travels with the repo, so teammates get it on clone. User-level is your **personal toolbox from home** — it follows *you* across projects but isn't shared.

> **Exam judgment:** a teammate clones the repo and your MCP server isn't there? You put it in **user-level** (`~/.claude.json`, not shared) instead of **project-level** (`.mcp.json`, shared). To share with the team, it goes project-level.

And because `.mcp.json` is committed, **never hardcode secrets in it** — use environment-variable placeholders like `${API_KEY}`.

---

## Structured error responses: tell the caller what to *do*

When a tool fails, *how* it reports the failure decides whether anything downstream can recover. A bare `"operation failed"` is useless — it gives the model no basis for a next move. It's the difference between a doctor saying "you're sick" and "it's a common cold, rest a few days."

A good structured error has three parts:

```json
{
  "errorCategory": "transient",
  "isRetryable": true,
  "message": "Weather service timed out; please retry shortly."
}
```

The four categories — and whether retrying helps:

| Category | Meaning | Retry? |
|---|---|---|
| **transient** | network blip, timeout, service briefly down | ✅ yes |
| **validation** | bad input format, missing field | ❌ no — fix the input first |
| **business** | e.g. "order is past the 30-day refund window" | ❌ no — it's a rule |
| **permission** | not authorized | ❌ no |

> **The key judgment:** only **transient** errors are worth retrying. Retrying a validation/business/permission error with the same input is wasted effort — the input's still wrong, or the rule still says no. The `isRetryable` boolean makes that decision explicit so nobody has to guess.

One more distinction the exam likes: **a legitimate empty result is not an error.** Searching for "unpaid orders" and finding zero is a valid answer ("0 found"), not a failure. Return it as an error and you'll trigger pointless retries.

---

## The security lesson I learned the embarrassing way

Running my multi-agent demo, I pasted my API key straight into a shell command — in plaintext, into a log. Which is exactly how keys leak.

The fix is the standard credential-hygiene pattern, and it's a real Domain 2/3 point:

- Put the key in a **`.env`** file, never in code or commands.
- Add `.env` to **`.gitignore`** so it's never committed.
- Load it from the environment at runtime (`AsyncAnthropic()` reads `ANTHROPIC_API_KEY` automatically).

The deeper lesson: once a key is exposed anywhere — chat, log, screenshot — hiding it later doesn't help. The only fix is to **revoke and rotate** it. `.env` protects the *next* key; it can't un-expose the one that already leaked. (Yes, I rotated mine.)

---

## Takeaways

- The `description` is the tool, as far as the model is concerned. Write **when** to use it, and keep near-identical tools' boundaries distinct.
- Wrong tool picked → fix the description, not with a stern prompt / deletion / merge.
- Grep = content, Glob = filenames. `Edit` fails → fall back to Read + Write.
- MCP = USB-C: write a server once, every client can use it. `.mcp.json` shares with the team; `~/.claude.json` is just you.
- Errors: `errorCategory` + `isRetryable` + a real message. Only transient is retryable. Empty ≠ error.
- Secrets live in `.env` (git-ignored). Leaked keys get rotated, not hidden.

---

## Further reading (official materials)

The sources I worked through for this week:

- [Anthropic Academy — Introduction to MCP](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [Anthropic Academy — MCP: Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [Docs — Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
- [Docs — Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) (project- vs user-level config)
- [MCP — official specification](https://modelcontextprotocol.io/specification/2025-11-25)

---

## Timeline & what's next

```
Week 1  ✅  Agentic Architecture & Orchestration (27%)
Week 2  ✅  Tool Design & MCP Integration (18%)          ← you are here
Week 3  ⬜  Claude Code Configuration + Prompt Engineering + Context Management
Week 4  ⬜  Review + mock exams
```

Still on my list from the plan: **Agent Skills** and the **Claude Code configuration** domain (CLAUDE.md hierarchy, custom skills, slash commands) — which, fun fact, is exactly the stuff this study project itself is built out of. That's next.
