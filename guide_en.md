# CCA-F Study Guide (English)

A concept review for all five knowledge domains of the **Claude Certified Architect — Foundations** exam. The exam tests **architectural judgment**, so each section leads with the *why*, not just the *what*, and flags the traps the scenario questions like to set.

**One idea underpins everything:** *a language model is blind — it only sees what you feed into its context, and it has no hands (it can't browse, read files, or call APIs; it only emits text).* Most "why" answers fall out of this.

---

## Domain 1 — Agentic Architecture & Orchestration (27%)

The biggest domain. It's about the agent *loop* and multi-agent *orchestration*.

**The agentic loop & `stop_reason`.** Every API response carries a `stop_reason`. You terminate the loop on `stop_reason == "end_turn"` — **never by parsing the text** for words like "done." Text is probabilistic (the model may say "done" mid-reasoning while `stop_reason` is still `tool_use`); `stop_reason` is deterministic. A max-turn cap is a *safety backstop*, not the primary termination condition.
- `end_turn` = finished → stop. `tool_use` = wants a tool → run it, feed the result back, loop. `max_tokens` = you set the cap too low (output truncated). `refusal` = safety refusal (don't retry the same prompt).

**Stateless API.** The Messages API remembers nothing between calls — you resend the entire history every turn. When feeding a tool result back: keep the assistant's `tool_use` block (the `tool_result` pairs to it via `tool_use_id`; drop it → 400), and put the `tool_result` in a `user`-role message. Parallel tool results go in a **single** user message.

**Model decides, harness executes.** The model only *requests* a tool call; **your program** runs it and returns the result. Consequence: if a tool fails, the model has no idea unless the harness reports it. Handle failures by **propagating honestly** (structured) — not by crashing the whole workflow, and never by faking success.

**Coordinator–subagent.** Split a big task into a coordinator that delegates to specialized subagents.
- **Context is not inherited.** Each subagent is a fresh, independent call that sees only what the coordinator writes into its prompt. A subagent "hallucinating" another's results → the fix is the coordinator **explicitly forwarding** the facts, *not* opening peer-to-peer channels.
- **Single hub.** All communication routes through the coordinator (star topology). Direct subagent-to-subagent links are an anti-pattern.
- **Parallel vs serial:** independent tasks → spawn in parallel in one turn; dependent tasks → serial.
- **Decomposition granularity:** too-narrow decomposition leaves whole sub-topics uncovered — a subagent can only cover what it's assigned.

**`fork_session` vs extract-and-inject.** For a focused side-task, extract just the few needed facts ("case facts") into a clean, fresh context — don't fork the entire history. More context isn't better; *more focused* is better (copying everything drowns key facts and burns tokens). Use `fork_session` only when you genuinely need to continue in the same full context.

**Traps:** terminating on text instead of `stop_reason`; opening subagent peer channels; assuming subagents inherit context; "copy the whole history to be safe."

---

## Domain 2 — Tool Design & MCP Integration (18%)

**Anatomy of a tool:** `name`, `description`, `input_schema`. The **`description` is the whole ballgame** — the model is blind, so it knows a tool *only* through its description. Write **when to use it**, not just what it does.

**Boundary overlap (top trap).** Two tools with near-identical descriptions (`analyze_content` vs `analyze_document`; `send_message` vs `send_email` both "Send a message") make the model pick wrong. The fix is to **clarify the boundaries in the descriptions** — not add a stern system prompt, not delete a tool, not merge them.

**Built-in tools.** Server-side (Anthropic runs it: `web_search`, code execution) vs client-side (your program executes: `bash`, text editor). Selection for code work: **Grep** = search by content; **Glob** = search by filename pattern; **Read/Write/Edit** = file ops; **Bash** = commands. `Edit` can fail (needs a prior read; target must be unique) → fall back to **Read + Write**. Don't give one agent 18 tools — scope tools per role.

**`tool_choice`:** `auto` (model decides), `any` (must use some tool), `{type: "tool", name}` (force a specific tool), `none`.

**MCP (Model Context Protocol)** — the "USB-C for AI tools." It standardizes integrations so you go from **M×N** bespoke connectors to **M+N**: an MCP **server** exposes a capability once; any MCP **client** (Claude Code, Claude Desktop) can use it.
- **Config levels:** `.mcp.json` (project-level, committed → shared with the whole team) vs `~/.claude.json` (user-level, personal → **not** shared). Teammate didn't get your server? You put it in user-level. Secrets in `.mcp.json` use `${ENV_VAR}` placeholders — never hardcode.

**Structured error responses.** Return `errorCategory` + `isRetryable` + a human-readable `message`, not a bare "operation failed."
- Categories: **transient** (retryable), **validation** (bad input — not retryable, fix input), **business** (a rule, e.g. past refund window — not retryable, explain), **permission** (not retryable). **Only transient is worth retrying.**
- A **legitimate empty result is not an error** (0 search hits = a valid answer, not a failure).

---

## Domain 3 — Claude Code Configuration & Workflows (20%)

**CLAUDE.md hierarchy.** Instructions load by scope: **user-level** (`~/.claude/CLAUDE.md`, personal, follows you across projects, *not* shared via version control), **project-level** (repo root, shared with the team), **directory-level** (subfolder, loads only when working there). If a teammate didn't get an instruction, it was likely put at user-level instead of project-level. `@import` pulls another file into a CLAUDE.md.

**Path-level rules (`.claude/rules/`).** A rule file with YAML frontmatter `paths:` glob loads **only** when editing matching files — keeps irrelevant context out. (This repo's `.claude/rules/hands-on.md` scopes to `hands-on/**`.)

**Skills vs slash commands.**
- **Skill** (`.claude/skills/<name>/SKILL.md`): can be invoked **proactively** by Claude when the task matches its `description`. Supports `context: fork` (isolated run — like a subagent's separate room, so its work doesn't pollute the main conversation), `allowed-tools` (least-privilege tool restriction), and `argument-hint`. Uses **progressive disclosure** — only the description stays in context; the full `SKILL.md` loads on demand (saves context, avoids clutter).
- **Slash command** (`.claude/commands/`): usually **you** trigger it manually with `/name`.

**Plan mode vs direct execution.** Use plan mode for complex, multi-file, hard-to-reverse work where you want to review the approach first; execute directly for small, single-file, low-risk changes.

**CI/CD integration.** Run headless with `-p` (non-interactive — won't hang waiting for input), emit machine-readable output with `--output-format json` / `--json-schema`, and put review criteria in `CLAUDE.md` so it's not free-form. An **independent review instance** (separate from the one that wrote the code) catches more than self-review. On a second pass, report only new / still-unresolved issues.

---

## Domain 4 — Prompt Engineering & Structured Output (20%)

**Explicit criteria beat vague instructions.** "Flag a comment only when it contradicts the code's actual behavior" >> "check whether comments are accurate." Give categorical, checkable rules, not "be careful."

**Few-shot examples** resolve ambiguity — a few labeled examples of the tricky/edge cases steer behavior better than more prose.

**Structured output via `tool_use` + JSON schema.** Forcing output through a tool/schema guarantees the *structure* — but **not the semantic correctness** of the values. Make possibly-missing fields **nullable/optional** so the model reports "missing" instead of hallucinating a value.

**Validation-retry loop.** On a schema/format failure, attach the *specific* error to the retry request (not "format wrong"). Crucially: **retry helps for format errors, but not for genuinely missing information** — if the document simply doesn't contain the field, retrying won't conjure it (a classic exam point).

**Batch API (Message Batches).** For non-latency-sensitive, high-volume work that tolerates delay (up to ~24h), at ~50% cost. Non-blocking; results come back **unordered** (key by `custom_id`).

**Independent review > self-review.** A model reviewing its own output in the same session misses its own mistakes; a separate review instance is more reliable.

---

## Domain 5 — Context Management & Reliability (15%)

**Preserve key facts in long conversations.** Extract "case facts" (order numbers, confirmed details) and persist them, because progressive summarization can silently drop critical specifics. Beware the **"lost in the middle"** effect — models attend less to the middle of a long context; keep critical info focused, not buried. Use scratchpad files and `/compact` to fight context degradation over long sessions.

**Escalation to a human — use concrete, checkable triggers:** the customer explicitly asks for a human; policy doesn't cover the situation; repeated attempts make no progress. **Do NOT** escalate on emotional tone alone, or on the model's own self-reported confidence score — those are unreliable signals.

**Error propagation in multi-agent systems.** Distinguish "access failed → needs retry" (transient) from a "legitimate empty result" (not an error). The propagation format should carry the failure type, what was attempted, and any partial results — not a bare "failed." Both extremes are anti-patterns: "any exception kills the whole workflow" and "any exception is silently swallowed."

**Human review & confidence calibration.** Aggregate accuracy (e.g. "97% overall") hides systematic errors on a specific document type or field — break accuracy down **by type/field**. Calibrate confidence thresholds against a **labeled validation set**, not a gut number. Use **stratified sampling** — spot-check even high-confidence outputs to catch new failure modes. For conflicting sources, keep a **claim→source** mapping and pass both values downstream, rather than silently merging or picking the "nicer-looking" number.

---

## Exam-day tips

- It's all judgment. When two options both "work," pick the one that fixes the **root cause** (e.g. wrong tool → fix the description, not a patch).
- No negative marking — answer every question.
- Watch for distractor answers that use the *right term for the wrong situation* (e.g. citing `fork_session`, `stop_reason`, or "subagent direct channel" where they don't apply).
- Domains 1 + 3 + 4 are ~two-thirds of the exam — weight your prep there.

## Out of scope (don't over-study)

Fine-tuning; API auth/billing; MCP server deployment/hosting; Claude internals / RLHF; embeddings & vector DBs; computer use & vision; streaming *implementation* details; rate limits / quotas / pricing math; OAuth & cloud-provider config; token-counting algorithms; prompt-caching internals (know it exists).
