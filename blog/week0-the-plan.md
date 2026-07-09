---
title: "Studying for the Claude Certified Architect Exam — Week 0: The Plan"
date: 2026-07-05
series: "CCA-F Study Log"
week: 0
domain: "Overview & study plan"
tags: [claude, certification, study-plan, cca-f, study-log]
---

I'm sitting Anthropic's **Claude Certified Architect — Foundations (CCA-F)** exam, and I'm going to log the whole thing here — one post per week, following a four-week plan. This is Week 0: what the exam actually is, and how I'm going to study for it.

If you're thinking about the same cert, this is the map I'm using.

---

## What the exam is

| | |
|---|---|
| **Format** | 60 multiple-choice questions (4 options each), 120 minutes |
| **Scenarios** | Drawn from a pool of **6 scenarios**; each sitting uses **4** of them |
| **Scoring** | 1000-point scale, **720 to pass**. No negative marking — answer everything. |
| **Result** | Pass / Fail only, valid **12 months** |
| **Delivery** | Online proctored or a test center |
| **Cost** | $125 USD |
| **Who it's for** | Solutions architects with ~6 months of hands-on Claude API / Agent SDK / Claude Code / MCP experience |

The thing to internalize early: **it tests architectural judgment, not coding.** Questions are scenario-based — "an agent is doing X and failing, what's the root cause / best fix?" You never write code. So the goal of studying isn't to memorize syntax; it's to build the intuition that makes the right answer obvious.

---

## The five knowledge domains (and their weights)

| # | Domain | Weight | What it covers |
|---|---|---|---|
| 1 | **Agentic Architecture & Orchestration** | **27%** | agentic loop, `stop_reason`, coordinator-subagent, Task tool, hooks, task decomposition, session state / `fork_session` |
| 2 | **Tool Design & MCP Integration** | 18% | writing tool descriptions, structured error responses, tool allocation across agents, `tool_choice`, `.mcp.json` config, built-in tool selection |
| 3 | **Claude Code Configuration & Workflows** | 20% | CLAUDE.md hierarchy, slash commands, Skills (`context: fork`), path-level rules, plan mode, CI/CD integration |
| 4 | **Prompt Engineering & Structured Output** | 20% | explicit criteria, few-shot, `tool_use` + JSON schema, validation-retry loops, Batch API, multi-instance review |
| 5 | **Context Management & Reliability** | 15% | long-conversation context retention, escalation strategy, multi-agent error propagation, large-codebase exploration, human review & confidence calibration |

> Domains 1, 3, and 4 together are **two-thirds of the exam**. That's where the study time goes first.

---

## The six scenarios

Each exam draws 4 of these 6. Knowing them shapes what "realistic" looks like on the questions:

1. **Customer-support agent** — refunds/billing/account issues; target 80%+ first-contact resolution; the crux is *when NOT to handle autonomously and escalate instead*. (Domains 1, 2, 5)
2. **Code generation with Claude Code** — day-to-day generation/refactor/debug; slash commands, CLAUDE.md, plan-mode trade-offs. (Domains 3, 5)
3. **Multi-agent research system** — a coordinator dispatching search / analysis / synthesis / writing subagents; orchestration and partial-failure handling. (Domains 1, 2, 5)
4. **Developer productivity tool** — using built-in tools (Read/Write/Bash/Grep/Glob) + an MCP server to explore an unfamiliar codebase. (Domains 2, 3, 1)
5. **Claude Code in CI/CD** — automated review / test generation; `-p`, `--output-format json`, `--json-schema`, reducing false positives. (Domains 3, 4)
6. **Structured data extraction** — JSON-schema validation, nullable fields to prevent hallucination, batch strategies over messy documents. (Domains 4, 5)

---

## What's NOT on the exam

The Exam Guide is explicit about what's *out of scope*. Worth knowing so you don't over-study:

- Model fine-tuning / training custom models
- API auth, billing, and account-management details
- Language/framework implementation specifics (beyond what tool & schema config needs)
- MCP server deployment/hosting (infrastructure, networking, containers)
- Claude's internal architecture, training process, or safety methodology (Constitutional AI / RLHF)
- Embedding models & vector-database implementation
- Computer use (browser/desktop automation) and vision/image analysis
- Streaming API implementation details, rate limits, quotas, and pricing math
- OAuth, API-key rotation, and cloud-provider (AWS/GCP/Azure) configuration
- Performance benchmarks, prompt-caching internals, and token-counting algorithms

> Heuristic: the exam is about *architectural judgment*, so anything that's pure infrastructure, low-level implementation, or model internals is out.

---

## The four-week plan

```
Week 1  Agentic architecture + the agent loop        (Domain 1)
Week 2  Tool design & MCP + Claude Code config        (Domains 2, 3)
Week 3  Prompt engineering + context & reliability    (Domains 4, 5)
Week 4  Full review + two mock exams
```

Six study days a week, one day to review, ~1–1.5 hours a day. Each week pairs **concepts** with a **hands-on mini-project** — build the thing, don't just read about it. There are eight small projects across the plan (a minimal agentic loop, a coordinator+subagents demo, an MCP server, a CLAUDE.md hierarchy + custom skill, a CI code-review integration, a structured-extraction pipeline, an escalation/error-propagation design doc, and a human-review workflow design doc).

---

## How I'm actually studying

A few things I'm doing deliberately, because "watch the videos" alone doesn't build judgment:

- **Learn the concept first, then read the source.** Get the mental model down (ideally with a plain analogy and a "why"), *then* read the official docs to confirm and fill in details. Reading cold is slow; reading with a scaffold is fast.
- **Build the mini-projects.** The exam doesn't test code, but building the thing is what turns "I read about parallel subagents" into "I've seen the latency difference myself" — and that's what makes the multiple-choice answer instant.
- **Quiz relentlessly, and track what I miss.** Scenario-style questions after each topic, with a running log of wrong answers so I can re-hit weak spots before the exam.
- **Explain it back in plain language.** If I can't re-tell a concept without jargon, I don't actually understand it yet.

---

## Resources

**Official courses (Anthropic Academy — free):**

- [Claude 101](https://anthropic.skilljar.com/claude-101)
- [Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api)
- [Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills)
- [Introduction to Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [MCP: Advanced Topics](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)

**Exam:**

- [CCA-F exam access request](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request) (via the Claude Partner Network)
- The official **Exam Guide PDF (v0.2)** is the source of truth for domain weights and scenarios — everything above is calibrated against it.

**Practice:**

- [CertSafari — free CCA-F practice bank](https://www.certsafari.com/anthropic/claude-certified-architect) (614 questions, sorted by domain)
- [My study repo](https://github.com/yuannh/cca-f-study-log) — bilingual study guides (English + 中文), hands-on projects, and interactive mock tests

**A note on integrity:** there are plenty of paid "dump" / "braindump" sites promising a guaranteed pass. Skip them — the content is unverifiable, often stale, and using it can violate Anthropic's exam-integrity terms. The free official courses + CertSafari + the Exam Guide already cover the material completely.

---

## What's next

Next post is **Week 1: the agentic loop** — `stop_reason`, stateless conversations, who actually runs your tools, and a hands-on multi-agent research system. That's the biggest domain by weight, so it's where the series really starts. See you there.
