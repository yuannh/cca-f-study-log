---
title: "Studying for the Claude Certified Architect Exam — Week 1: How the Agentic Loop Actually Works"
date: 2026-07-12
series: "CCA-F Study Log"
week: 1
domain: "Agentic Architecture & Orchestration (27%)"
tags: [claude, agents, llm, agentic-loop, mcp, study-log]
---

I'm studying for Anthropic's **Claude Certified Architect — Foundations (CCA-F)** exam, and I'm turning the whole journey into a weekly log. The exam is 60 scenario-based multiple-choice questions across five knowledge domains. It doesn't test whether you can write code — it tests whether you can make the right **architectural judgment**. So that's what these posts are about: not memorizing syntax, but building the intuition that makes the right answer obvious.

Week 1 is the biggest domain by weight: **Agentic Architecture & Orchestration (27%)**. Here's everything that finally clicked for me.

---

## The one idea everything else hangs on: the model is blind

Before any of the mechanics make sense, you need one mental model:

> **A language model is blind. It can only "see" what you feed into its context. It has no hands — it can't browse the web, read your files, call your database, or send an email. The only thing it can output is text.**

Keep this in your head. Ninety percent of the "why" answers on this exam fall out of it.

---

## The agentic loop: stop on `stop_reason`, not on text

An "agentic loop" is the cycle where the model calls tools, gets results, and keeps going until it's done. The question is: **how do you know when it's done?**

Every response from the Messages API carries a `stop_reason` field telling you *why* the model stopped:

| `stop_reason` | Meaning | What you do |
|---|---|---|
| `end_turn` | The model finished naturally | Stop the loop, return the answer |
| `tool_use` | The model wants to call a tool | Run it, feed the result back, loop again |
| `max_tokens` | Hit the output cap | Raise `max_tokens` or stream |
| `refusal` | Refused for safety reasons | Don't retry the same prompt |

The classic anti-pattern — and a favorite exam trap — is terminating the loop by **parsing the text**:

```python
# ❌ WRONG — never do this
while True:
    response = call_claude(messages)
    if "done" in response.text or "finished" in response.text:
        break
    run_tools(messages, response)
```

Why is this broken? Two reasons, both from "the model is blind / text is probabilistic":

1. **You can't enumerate the phrasing.** The model might say "all set," "handled," or "完成." Your keyword list will always miss one.
2. **Text ≠ intent.** The model might mention "done" *inside its reasoning* while `stop_reason` is still `tool_use` — it isn't actually finished.

The fix is to bind your control flow to the deterministic protocol signal:

```python
# ✅ RIGHT
while True:
    response = call_claude(messages)
    if response.stop_reason == "end_turn":
        break
    run_tools_and_append_results(messages, response)
```

> **Architectural principle:** control flow binds to deterministic signals (`stop_reason`), never to probabilistic output (generated text). A max-turn limit is a *safety backstop*, not your primary termination condition.

---

## The API is stateless — you resend the whole history every turn

Here's the analogy that made this stick for me:

> Talking to the model is like calling an **assistant with amnesia** — the moment you hang up, they forget everything. So every call, you have to re-tell the entire conversation from the start.

The Messages API is **stateless**: the server remembers nothing between requests. If you don't resend the history, the model is amnesiac. This is why a tool-use round trip looks like this:

```
1. You send:  messages = [user: "Weather in Paris?"]
2. Claude:    stop_reason=tool_use, wants get_weather(city="Paris"), id="toolu_01"
3. You run the tool → "22°C, sunny"
4. You append the assistant's FULL turn (including the tool_use block)
   then append a user turn with the tool_result:
        {"type": "tool_result", "tool_use_id": "toolu_01", "content": "22°C, sunny"}
5. You resend the ENTIRE history
6. Claude:    stop_reason=end_turn, "It's 22°C and sunny in Paris."
```

Three non-obvious rules live in here:

- **Resend everything.** The array grows every turn. (This is *why* context management exists as its own topic later.)
- **Keep the `tool_use` block, not just the result.** The `tool_result` pairs to its request via `tool_use_id`. Drop the `tool_use` block and the API rejects the request with a 400.
- **Tool results go in a `user`-role message.** Multiple parallel tool results go in a *single* user message — splitting them across messages quietly trains the model to stop making parallel calls.

---

## Who actually runs the tool? Your program, not the model

This is the subtlety that trips everyone up. When the model "uses a tool," it does **not** execute anything. It only emits a *request*: "I'd like to call `get_weather` with `city=Paris`." Your program (the **harness**) is what actually runs the query and returns the result.

```
Model:  "I want to call get_weather(city=Paris)"   ← just placing an order
   ↓
Your harness actually calls the weather API → "22°C, sunny"   ← the cook
   ↓
Your harness feeds "22°C, sunny" back as a tool_result   ← serving the dish
```

> **The model orders from a menu; your program cooks and serves.** The model *decides*, the harness *executes*.

A direct consequence — and a great exam question — is error handling. If the weather API fails, **the model has no idea**. Only your harness sees the failure. Whether the model finds out depends entirely on whether your harness reports it back. And the three ways to handle a tool failure map to three judgments:

- ✅ **Propagate honestly** (with structured info) → the model can decide to retry, adapt, or tell the user.
- ❌ **Crash the whole workflow** → one hiccup takes everything down.
- ❌ **Silently fake success** → the model builds on fabricated data. The most dangerous option.

---

## Multi-agent: coordinator + subagents

When one task gets big — say a research job that searches, analyzes, and summarizes — you split it into a **coordinator** that delegates to specialized **subagents**. Three "why" questions matter here.

### Why split at all?
A single agent doing everything accumulates a huge, polluted context (hello, "lost in the middle") and has to juggle multiple personas badly. Splitting gives each subagent a **short context, one job, and — when tasks are independent — the ability to run in parallel**.

### Why don't subagents inherit context?
Here's the mental picture:

> The coordinator is a **team lead**; subagents are **specialists, each working in a separate windowless room**. No windows, no doors between rooms — nobody can see anyone else's work.

Each subagent is a **fresh, independent model call** with its own message history starting from zero. The coordinator's history and the other subagents' findings are simply **not there** — unless the coordinator explicitly writes them into that subagent's prompt. (Remember: the model is blind; it only sees what you feed it.) This is a *feature*: isolation keeps each subagent's context clean and focused.

### Why route everything through the coordinator?
Because the alternative — subagents talking directly to each other — is a mesh that nobody controls:

```
      coordinator                    proper: star topology
      /    |    \                     - controlled information flow
  search analyze summarize            - consistent results
   (no direct links between them)     - failures contained at the hub
```

The coordinator is the **single hub**. All results flow back to it; it decides what to pass onward. Open direct subagent-to-subagent channels and you get an uncontrollable web, half-baked intermediate results leaking around, and failures spreading along every link.

> **Exam trap:** when a subagent "hallucinates" another subagent's results, the fix is *not* to open a peer-to-peer channel — it's to have the coordinator **explicitly forward** the needed facts into the subagent's prompt.

### Parallel vs serial: look at the dependencies
- Independent tasks (search laptop A, search laptop B) → **spawn in parallel** in the same turn.
- Dependent tasks (analysis needs the search results) → **serial**.

The rule of thumb: **does task B need task A's output? Yes → serial. No → parallel.**

---

## The hands-on: a minimal multi-agent research system

To make all of this concrete, I built a tiny "compare two laptops" research system: two **search** subagents run in parallel, then a single **analysis** subagent runs serially on their combined results. It satisfies every acceptance criterion — independent subagents, explicit context passing, a single hub, a deliberate-failure test, and parallel spawn.

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()          # reads ANTHROPIC_API_KEY from env — never hardcode
MODEL = "claude-opus-4-8"


# ── subagent: searcher ──
async def search_subagent(laptop_name, fail=False):
    if fail:                       # deliberate-failure switch (test error handling)
        raise RuntimeError(f"search for {laptop_name} timed out (simulated transient failure)")
    # Each subagent is an independent call with its own fresh messages.
    # It cannot see the coordinator's history or the other searcher's results —
    # unless explicitly written into THIS prompt. That's "context isn't inherited."
    resp = await client.messages.create(
        model=MODEL, max_tokens=1024,
        system="You are a hardware researcher. Output only this laptop's specs, price, and review notes.",
        messages=[{"role": "user", "content": f"Look up this laptop: {laptop_name}"}],
    )
    return next(b.text for b in resp.content if b.type == "text")


# ── subagent: analyst ──
async def analysis_subagent(findings):
    # The analyst can't see the searchers' conversations. The coordinator must
    # EXPLICITLY inject the search results into this prompt (extract-and-inject).
    facts = "\n\n".join(f"[{name}]\n{info}" for name, info in findings.items())
    resp = await client.messages.create(
        model=MODEL, max_tokens=1024,
        system="You are an analyst. Compare these laptops and recommend one. "
               "If any laptop's data is missing, say clearly that you can't fully compare it.",
        messages=[{"role": "user", "content": f"Here is the collected data:\n\n{facts}\n\nCompare and recommend."}],
    )
    return next(b.text for b in resp.content if b.type == "text")


# ── coordinator (the single hub) ──
async def coordinator(laptops, fail_on=None):
    # Phase 1: parallel spawn — both searches fire at once (they're independent).
    tasks = {
        name: asyncio.create_task(search_subagent(name, fail=(name == fail_on)))
        for name in laptops
    }
    findings = {}
    for name, task in tasks.items():
        try:
            findings[name] = await task
        except Exception as e:
            # Don't crash the flow, don't fabricate — record the partial result honestly.
            print(f"[coordinator] searcher failed: {name} — {e}")
            findings[name] = f"(data missing: {e})"
    # Phase 2: serial hand-off — analyze only after searches are collected.
    return await analysis_subagent(findings)


if __name__ == "__main__":
    laptops = ["MacBook Air M3", "Dell XPS 13"]
    print(asyncio.run(coordinator(laptops)))
    # Deliberate failure demo:
    # print(asyncio.run(coordinator(laptops, fail_on="Dell XPS 13")))
```

The best part was the **deliberate-failure run**. When one searcher fails, the coordinator catches it, logs it, and proceeds with partial data — and the analyst *honestly* reports "I can't give a final pick, the Dell data is entirely missing," instead of inventing a comparison for a laptop it never saw. Watching "honest degradation" beat "fabrication" in a real run cemented the whole error-handling lesson better than any amount of reading.

(Two honest simplifications for the demo: the coordinator's task decomposition is hard-coded, and "search" uses the model's own knowledge rather than a real web tool. A fuller version would let the coordinator decide the decomposition dynamically and plug in a real `web_search` tool or MCP search server.)

---

## Bonus: streaming — don't make users stare at a spinner

A long response can take 10–30 seconds to generate. Without streaming, the user stares at a spinner the whole time with zero feedback. **Streaming** sends the text back in pieces as it's generated — the "typewriter" effect you see in every chat UI.

> Non-streaming is waiting for the *entire meal* before anything is served. Streaming brings each dish out as it's ready.

Crucially, it's still **one request** — the response just arrives as a series of events:

```
MessageStart → ContentBlockDelta("Quantum") → ContentBlockDelta("computing") → … → MessageStop
```

The **ContentBlockDelta** events carry the actual text you display; the rest are envelope (start/stop markers).

Two reasons to reach for it:

1. **UX** — users see progress immediately instead of a dead spinner.
2. **Avoid timeouts** — a long non-streaming request can sit idle long enough for the HTTP connection to time out and drop, losing everything. Streaming keeps data flowing, so the connection stays alive. Rule of thumb: **long input, long output, or high `max_tokens` → stream.**

In code, three levels of convenience:

```python
# Raw: every event
stream = client.messages.create(..., stream=True)
for event in stream:
    ...

# Simplified: just the text chunks (usually what you want)
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="")

# Both worlds: stream to the user, then grab the assembled message for storage
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        pass
    final_message = stream.get_final_message()
```

When *not* to stream: batch jobs where nobody's watching, or short outputs (a one-word classification) — the overhead buys you nothing.

---

## Gotchas worth remembering

- **`stop_reason == "max_tokens"` means you set the cap too low** — output got cut off mid-thought. `max_tokens` is a *ceiling*, not a target; the model stops early on `end_turn` when it's actually done.
- **`content[0].text` is fragile.** The response `content` is a *list of blocks*; if thinking is on, block 0 might be a thinking block. Prefer `next(b.text for b in resp.content if b.type == "text")`.
- **Extract-and-inject beats copy-everything.** For a focused side-task, injecting just the few facts it needs into a clean context beats forking the entire history. More context isn't better — *more focused* is better. (This is the one I got wrong on a practice question — copying the full history *feels* safest but drowns the key facts and burns tokens.)

---

## Further reading (official materials)

The sources I worked through for this week:

- [Anthropic Academy — Claude 101](https://anthropic.skilljar.com/claude-101) (fundamentals)
- [Anthropic Academy — Building with the Claude API](https://anthropic.skilljar.com/claude-with-the-anthropic-api) (function calling, tool use, streaming)
- [Docs — How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works)
- [Docs — Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Docs — Subagents (Claude Agent SDK)](https://platform.claude.com/docs/en/agent-sdk/subagents) — context isolation and the Task tool
- [Docs — Agent SDK quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart)

---

## Timeline & what's next

```
Week 1  ✅  Agentic Architecture & Orchestration (27%)   ← you are here
Week 2  ⬜  Tool Design & MCP + Claude Code config (18% + 20%)
Week 3  ⬜  Prompt Engineering + Context Management (20% + 15%)
Week 4  ⬜  Review + mock exams
```

Next week is **tool design and MCP** — how you actually *define* a tool (and why the `description` field is the whole ballgame), plus MCP as the "USB-C for AI tools." See you then.
