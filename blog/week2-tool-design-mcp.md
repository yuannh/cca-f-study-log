---
title: "Studying for the Claude Certified Architect Exam — Week 2: Tool Design, MCP & Claude Code Config"
date: 2026-07-17
series: "CCA-F Study Log"
week: 2
domain: "Tool Design & MCP Integration (18%) + Claude Code Configuration & Workflows (20%)"
tags: [claude, tools, mcp, tool-design, claude-code, claude-md, agent-skills, error-handling, study-log]
---

Week 2 of my [Claude Certified Architect — Foundations](/blog/cca-f-week-1-agentic-loop) study log. Last week was the agentic loop and multi-agent orchestration. This week is a double bill — **Tool Design & MCP Integration (18%)** and **Claude Code Configuration & Workflows (20%)**. Together that's 38% of the exam, and they turn out to be the same subject viewed from two ends: how you *define* what an agent can do, and how you *configure* an agent that's already built.

There's a thread running through both, and it's the same idea from Week 1:

> **The model is blind. It only knows a tool through the text you write about it.**

Almost everything below is a consequence of that — including, as it turns out, the parts that look like they're just about config files.

---

# Part 1 — Tool Design & MCP Integration (18%)

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

# Part 2 — Claude Code Configuration & Workflows (20%)

Second domain of the week. On paper it's a different subject: config files, not tool definitions. In practice I kept hitting ideas I'd just learned — which is the main reason I'm putting both in one post.

## CLAUDE.md: the same lesson as `.mcp.json`

`CLAUDE.md` is the file where you write down what an agent should know about your project — conventions, constraints, how to run the tests. It has **three levels**, and if the `.mcp.json` table above felt familiar, that's not a coincidence:

| Location | Level | Who gets it |
|---|---|---|
| `~/.claude/CLAUDE.md` | **user** | only you, across all your projects |
| `<repo root>/CLAUDE.md` | **project** | everyone who clones the repo |
| `<subdir>/CLAUDE.md` | **directory** | anyone working in that subdirectory |

It's the *exact same shape* as the MCP config split — and it fails the exact same way:

> **Exam judgment:** you wrote conventions in `CLAUDE.md`, but your teammate's agent ignores them. Why? You put them at **user level** (`~/.claude/`, private to you) instead of **project level** (repo root, committed and shared). Same root cause as the MCP server that didn't travel — *where you write it decides who gets it.*

Once I'd seen that twice, it stopped being two facts and became one: **scope is a placement decision, not a syntax decision.**

### Keeping it from turning into a wall of text

Two mechanisms stop `CLAUDE.md` from bloating into something nobody reads and every request pays for:

- **`@import`** — pull another file's contents into `CLAUDE.md` instead of pasting them. Modular, reusable, one source of truth.
- **`.claude/rules/`** — rules that carry a `paths` glob and load **only when a matching file is being edited**.

The second one is the interesting one, because it's a *context* decision, not a tidiness decision. A rule that only matters when touching `*.sql` shouldn't sit in every single request's context. Give it a `paths: ["**/*.sql"]` and it shows up exactly when it's relevant.

Note the granularity ladder: directory-level `CLAUDE.md` loads for a whole subdirectory; a `.claude/rules/` glob loads for a **file pattern**. Finer, and cheaper.

> **The trigger heuristic I settled on:** *editing a kind of file* → `.claude/rules/` with `paths`. *Doing a kind of task* → a skill (next section).

## Agent Skills: the description is the whole ballgame, again

A **skill** is a packaged bundle of expertise the agent loads **on demand**. It lives at `.claude/skills/<name>/SKILL.md`: frontmatter on top, instructions below.

```markdown
---
name: quiz-me
description: Generate exam-style scenario questions to quiz the user, grade them one at a time, and log weak areas
argument-hint: [domain number or scenario name]
allowed-tools: Read, Write, Edit
context: fork
---

<the actual instructions go here>
```

The mechanism to understand is **progressive disclosure**:

- Sitting idle, a skill costs you **only its `description`** — one line in context.
- When a task matches that description, the **full `SKILL.md` loads**.

So you can have thirty skills installed and pay for thirty lines, not thirty manuals. Cheaper *and* more focused — the agent isn't wading through 29 irrelevant playbooks to find the one that matters.

Which brings back the thread from the top of this post. **The `description` is the trigger.** It's the only thing the model sees when deciding whether this skill is relevant — same as a tool description, same blindness, same failure mode. A vague skill description means a skill that never fires. I've now met this idea three times in two domains, so I'm going to assume it's on the exam.

Two frontmatter fields worth knowing:

- **`allowed-tools`** — least privilege. A skill that only reads files has no business holding `Bash`.
- **`context: fork`** — run the skill in an **isolated context** rather than the main conversation. That's the subagent idea from Week 1 wearing different clothes: a clean room, so the side task's noise never lands in the main thread.

> **Skill vs slash command:** a **skill** can be invoked *by the model* when your description matches the situation. A **slash command** is generally something *you* fire manually with `/name`. Model-triggered vs human-triggered — that's the distinction.

Fun fact: this study project is itself built out of this stuff. The `quiz-me` skill above is real — it's what quizzes me at the end of each domain. Studying the material by living inside it turned out to be the cheapest revision trick I found.

## Plan mode: when to think before acting

**Plan mode** makes the agent produce a plan and get your sign-off *before* it touches anything. The exam wants you to know when it's worth it:

| Situation | Do this |
|---|---|
| Large / multi-file / hard to undo (a refactor across 40 files) | **Plan mode** — align first, because being wrong is expensive |
| Small / local / low-risk (fix a typo, add a log line) | **Just do it** — a plan costs more than the mistake would |

The judgment being tested is that **both extremes are anti-patterns.** Planning a one-line fix is ceremony. Letting an agent free-run a 40-file refactor is how you get a mess nobody can review. The variable is **the cost of being wrong**, and that's what you should be pattern-matching on — not the size of the diff.

## CI/CD: the flag that decides whether it hangs

Running Claude Code in a pipeline has one gotcha that will bite you before any of the interesting stuff does:

```bash
claude -p "Review the diff for bugs" --output-format json
```

- **`-p`** — non-interactive (headless). Without it, the agent waits for input that will never come in CI, and **your job hangs until it times out**.
- **`--output-format json`** — machine-parseable output, so the pipeline can actually act on the result instead of regexing prose.

Then the architectural parts:

- **Put the review criteria in `CLAUDE.md`**, not in the shell command. The criteria are a project fact — they belong with the project, versioned and reviewed, not buried in a YAML step.
- **Use a separate instance to review** rather than asking the author-agent to check its own work. Independent review beats self-review, for exactly the reason it does with humans: the context that produced the bug is the context least likely to spot it.
- **On a second pass, report only what's new or unresolved.** Re-reporting everything trains people to ignore the bot, and a review nobody reads is worse than no review — it's a review that provides false assurance.

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

**Tool Design & MCP (18%)**

- The `description` is the tool, as far as the model is concerned. Write **when** to use it, and keep near-identical tools' boundaries distinct.
- Wrong tool picked → fix the description, not with a stern prompt / deletion / merge.
- Grep = content, Glob = filenames. `Edit` fails → fall back to Read + Write.
- MCP = USB-C: write a server once, every client can use it. `.mcp.json` shares with the team; `~/.claude.json` is just you.
- Errors: `errorCategory` + `isRetryable` + a real message. Only transient is retryable. Empty ≠ error.
- Secrets live in `.env` (git-ignored). Leaked keys get rotated, not hidden.

**Claude Code Config & Workflows (20%)**

- `CLAUDE.md` is user / project / directory level. Teammate didn't get your conventions → you wrote them at user level. **Where you write it decides who gets it** — same lesson as `.mcp.json`.
- `@import` for modularity; `.claude/rules/` + a `paths` glob to load a rule only when a matching file is edited. Editing a file type → rules. Doing a task type → skill.
- Skills load by **progressive disclosure**: description always, full `SKILL.md` on demand. The description is the trigger — same blindness as tool descriptions. `allowed-tools` for least privilege, `context: fork` for isolation.
- Skill = model can invoke it. Slash command = you invoke it.
- Plan mode when being wrong is expensive (big, multi-file, hard to undo); just act when it isn't. Both extremes are anti-patterns.
- CI: `-p` or it hangs, `--output-format json` so the pipeline can parse it. Criteria in `CLAUDE.md`, a separate instance reviews, second pass reports only new/unresolved.

**The one idea underneath both:** the model only knows what you wrote down, and *where* you wrote it down decides who — and what — ever sees it.

---

## Further reading (official materials)

The sources I worked through for this week:

*Tool Design & MCP*

- [Anthropic Academy — Introduction to MCP](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [Anthropic Academy — MCP: Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [Docs — Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
- [Docs — Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) (project- vs user-level config)
- [MCP — official specification](https://modelcontextprotocol.io/specification/2025-11-25)

*Claude Code config & workflows*

- [Anthropic Academy — Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)
- [Anthropic Academy — Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills)
- [Docs — Memory / CLAUDE.md](https://code.claude.com/docs/en/memory) (the three-level hierarchy and `@import`)
- [Docs — Common workflows](https://code.claude.com/docs/en/common-workflows)
- [Docs — Headless mode](https://code.claude.com/docs/en/headless) (`-p`, `--output-format json`)
- [Docs — Slash commands](https://code.claude.com/docs/en/slash-commands)

---

## Timeline & what's next

```
Week 1  ✅  Agentic Architecture & Orchestration (27%)
Week 2  ✅  Tool Design & MCP + Claude Code config (18% + 20%)   ← you are here
Week 3  ⬜  Prompt Engineering + Context Management (20% + 15%)
Week 4  ⬜  Review + mock exams
```

That's **65% of the exam** covered — the three biggest domains are behind me.

An honest note on pacing: the writing lags the studying. By the time this went up I'd already worked through **Prompt Engineering** (Week 3's first half) and started on **Context Management** — where the running theme turns out to invert. Weeks 1 and 2 were about *writing things down clearly*. Week 3 is about the opposite discipline: **what to leave out**, and why a context stuffed with everything makes an agent worse rather than better.

That one's already cost me a wrong answer. More on it next week.
