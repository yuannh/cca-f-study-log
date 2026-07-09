# Claude Certified Architect — Foundations (CCA-F) Study

A public, open study project for Anthropic's **Claude Certified Architect — Foundations (CCA-F)** exam — a 4-week plan, hands-on mini-projects, study guides (English + 中文), and practice tests.

> **中文读者**：本仓库是 CCA-F 认证的公开备考资料，含 4 周计划、动手项目、双语学习指南与模拟测试。中文指南见 [`guide_zh.md`](./guide_zh.md)，中文模拟测试见 [`practical_test_zh.html`](./practical_test_zh.html)。

---

## What is the CCA-F exam?

| | |
|---|---|
| **Format** | 60 multiple-choice questions (4 options), 120 minutes |
| **Scenarios** | Drawn from a pool of 6; each sitting uses 4 |
| **Passing** | 720 / 1000. No negative marking. |
| **Result** | Pass / Fail, valid 12 months |
| **Cost** | $125 USD |

It tests **architectural judgment**, not coding — every question is a production scenario asking for the best design decision or root cause.

### Five knowledge domains

| # | Domain | Weight |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | **27%** |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

---

## Repository structure

```
.
├── guide_en.md              # Study guide — all 5 domains (English)
├── guide_zh.md              # 学习指南 — 五大知识域（中文）
├── practical_test_en.html   # Interactive mock test (English)
├── practical_test_zh.html   # 交互式模拟测试（中文）
├── study-plan.md            # Full day-by-day 4-week plan
├── blog/                    # Weekly study-log blog posts
│   ├── week0-the-plan.md
│   ├── week1-agentic-architecture.md
│   └── week2-tool-design-mcp.md
├── hands-on/                # 8 hands-on mini-projects (briefs + code)
│   └── 02-multi-agent-research/   # coordinator + subagents, runnable
├── CLAUDE.md                # Project config — a live Claude Code example
└── .claude/                 # skills + path-level rules — more live examples
```

The `.claude/` folder and root `CLAUDE.md` double as **worked examples for Domain 3** (Claude Code configuration): a custom skill (`.claude/skills/quiz-me/`), a path-scoped rule (`.claude/rules/hands-on.md`), and a project-level `CLAUDE.md`.

---

## How to use this

1. Read [`guide_en.md`](./guide_en.md) / [`guide_zh.md`](./guide_zh.md) for concept coverage of all five domains.
2. Work the [`hands-on/`](./hands-on/) mini-projects — building the thing is what turns reading into judgment.
3. Take [`practical_test_en.html`](./practical_test_en.html) / [`practical_test_zh.html`](./practical_test_zh.html) — open the file in any browser.
4. Follow the weekly [`blog/`](./blog/) posts for the narrative version.

## Official resources

- [Anthropic Academy](https://anthropic.skilljar.com/) — free official courses (Claude 101, Building with the Claude API, Claude Code in Action, Introduction to MCP, MCP Advanced Topics)
- [CCA-F exam access request](https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request)
- [CertSafari — free practice bank](https://www.certsafari.com/anthropic/claude-certified-architect)

> The official **Exam Guide PDF** is the source of truth for domain weights and scenarios. It is Anthropic's copyrighted material and is intentionally **not** redistributed here — get it from the official portal.

## A note on integrity

Skip paid "dump" / "braindump" sites. The content is unverifiable, often stale, and using it can violate Anthropic's exam-integrity terms. The free official courses + CertSafari + the Exam Guide cover the material completely.

---

*This is an independent study project and is not affiliated with or endorsed by Anthropic.*
