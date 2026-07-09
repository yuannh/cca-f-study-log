# Lovable prompt — how to publish each weekly post

This is the prompt to paste into Lovable to add a study-log post to your blog.
Reuse it every week: swap in the new week's metadata and paste that week's
Markdown body (from the matching `weekN-*.md` file) where indicated.

---

## Reusable prompt template

> Add a new post to my site (dearartist.xyz), most likely under the **Notes** section,
> as part of a series called **"CCA-F Study Log"** (a weekly log of me studying for the
> Claude Certified Architect — Foundations exam).
>
> Keep it consistent with my site's existing aesthetic: **minimalist, terminal/monospace-influenced,
> content-over-decoration, English.** Don't introduce a heavy corporate-blog template. Requirements:
> - Render the body as **Markdown**, with **syntax-highlighted code blocks** (the posts contain Python), proper **tables**, and blockquotes for callouts.
> - Show the **title**, **publish date**, and **tags** at the top.
> - If my blog has a series or tag index, add this post under the **"CCA-F Study Log"** series so the weekly posts group together and read in order (Week 1, Week 2, …).
> - Add a small "Week N of 4" progress indicator if it fits the design.
>
> **Metadata**
> - Title: `Studying for the Claude Certified Architect Exam — Week 1: How the Agentic Loop Actually Works`
> - Date: `2026-07-12`
> - Series: `CCA-F Study Log` (Week 1 of 4)
> - Tags: `claude`, `agents`, `llm`, `agentic-loop`, `mcp`, `study-log`
>
> **Body (Markdown):**
>
> ```markdown
> <PASTE THE CONTENTS OF blog/week1-agentic-architecture.md HERE — everything
>  below the frontmatter `---` block>
> ```

---

## Tips

- **Paste the body from the `.md` file**, not from chat — the file is the source of truth and keeps its formatting.
- Strip the top **frontmatter** (the `--- ... ---` block) before pasting; that's metadata for me, not for the page. The title/date/tags are already in the prompt above.
- For **Week 2+**, reuse this same prompt: change the Title / Date / Week number / Tags, and paste that week's body. Keep the series name **"CCA-F Study Log"** identical every time so Lovable groups them.
- If Lovable's output looks off (e.g. code blocks not highlighting, tables breaking), tell it exactly what to fix — "the Python code blocks aren't syntax-highlighted" — rather than re-pasting everything.
