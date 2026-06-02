---
name: html-reporting
description: Produce single-file, self-contained HTML artifacts instead of Markdown for any output a human will actually read. Use whenever the user asks for a "report", "research summary", "write-up", "spec", "plan", "PR explainer", "code review", "design mockup", "prototype", "dashboard", "deck", or anything that benefits from tables, SVG diagrams, color coding, side-by-side comparisons, sliders, drag-and-drop, or shareable visuals. Also use when the user wants to share something visual with a teammate, when a Markdown plan would exceed ~100 lines, when interactive tweaking would help (sliders, copy-as-JSON, copy-as-prompt buttons), or when the model is about to resort to ASCII-art charts or Unicode color blocks in Markdown. Strongly prefer this skill for any "summarize and present" task — even if the user doesn't explicitly say "HTML".
license: Inspired by Thariq Shihipar (@trq212), "Using Claude Code: The Unreasonable Effectiveness of HTML" (2026).
---

# HTML Reporting

Markdown is the default agent output format, but it caps out fast. Long Markdown rarely gets read; HTML does. This skill is about producing **single-file HTML artifacts** — reports, specs, PR explainers, prototypes, custom editors — that humans actually open, scroll through, and share.

## Why HTML beats Markdown for human-facing output

Markdown's killer feature was always "easy to hand-edit." That feature has lost most of its value: people now edit by prompting the agent to change the file rather than typing into it themselves. What remains is reading and sharing, and Markdown is bad at both once the document gets long.

HTML wins on the dimensions that actually matter for finished artifacts:

- **Information density.** Tables, SVG diagrams, color coding, code with syntax highlighting, side-by-side comparisons, tabs. A 200-line Markdown plan becomes a navigable HTML page with a TOC and collapsible sections.
- **Readability at length.** Past ~100 lines, Markdown becomes a wall. Real typography, spacing, and visual hierarchy make HTML scannable.
- **Sharing.** Drop the file into S3, GitHub Pages, or any static host and send a URL. Browsers render it everywhere, including on phones. Markdown attachments get ignored.
- **Interactivity.** Sliders, knobs, drag-and-drop, live previews, "copy as JSON" buttons — all trivially possible, and they close the loop back to the agent.
- **Diagrams.** When HTML is on the table, the model draws SVG diagrams instead of butchering ASCII art or Unicode color blocks.

The tradeoff: HTML uses roughly 2–4× more tokens and takes proportionally longer to generate. For anything a human will read more than once, that cost is trivially worth it.

## When to reach for this skill

Use HTML when **any** of these are true:

- A human will read this more than they will edit it (specs, reports, plans, reviews, research).
- The output would exceed ~100 lines as Markdown.
- It needs visual structure: tables, diagrams, color coding, comparisons, annotations.
- It needs interactivity: tunable parameters, drag-and-drop, live previews, export buttons.
- It will be shared with teammates or leadership.
- The Markdown version would force ASCII-art or Unicode "color block" hacks.

Stick with Markdown when the artifact is short and meant to be hand-edited (a `CLAUDE.md`, a commit message, a chat reply), or when downstream tooling expects Markdown (GitHub issues, PR descriptions, chat messages).

When you're unsure, ask the user once: *"Want this as a single-file HTML report or as Markdown?"* Then proceed without re-asking.

## Don't over-engineer this

The biggest failure mode is turning HTML output into a ceremony — a `/html` command, a build step, a framework. Don't. The simplest, most effective form is **one `.html` file** with inline `<style>` and `<script>`. No bundlers. No npm. No required network at runtime. The user opens it locally, or uploads it once.

A good HTML artifact is:

1. **Single file.** One `.html` with inline CSS and JS.
2. **Self-contained.** Opens correctly from `file://` with no server. CDN dependencies are allowed only when they earn their keep (e.g., one charting library); never pull in a full framework for a one-shot artifact.
3. **Mobile-responsive.** Sensible `<meta viewport>` and a max-width body. People will open this on their phone.
4. **Printable.** Light background by default. Dark-only styling wastes ink and breaks paste-into-doc workflows.
5. **Linkable.** Real `id` attributes on headings so sections can be deep-linked.

## Default starting point

Three bundled templates cover ~80% of cases. Copy from whichever fits, then adapt:

- **`assets/report.html`** — The flagship template for reports, code reviews, audits, research write-ups, summaries, and structured findings. A polished editorial theme (soft-gray paper, serif headlines, terracotta accent) with a light/dark toggle, collapsible severity-coded cards, a TL;DR strip, a sticky pill TOC, stats grid, filter chips, live search, and keyboard shortcuts. See "The report template" below before customizing.
- **`assets/pr-review.html`** — PR explainers and code reviews. Diff blocks with green/red line backgrounds, severity badges, inline annotations, "what to review first" orientation block.
- **`assets/prototype.html`** — Interactive prototypes and custom editors. Sliders/inputs on the left, live preview on the right, `localStorage` persistence, "Copy as JSON" / "Copy as prompt" export buttons.

All three share a common visual baseline (light/dark color scheme, generous spacing, accessible colors). Read the template you're using before customizing — they encode the conventions described in this skill.

If none of the templates fit (e.g., a draggable triage board, a flag editor with dependency validation), still write a single self-contained file and lift the `<style>` block from the closest template so the visual style stays consistent.

## The report template (`assets/report.html`)

This is the default for any "review / analyze / audit / report" request. It's a single self-contained file — copy it, fill the `{{PLACEHOLDERS}}`, write it, then tell the user the absolute path and the `open <path>` command.

**Visual theme.** Calm editorial look: soft-gray "paper" background, serif display headlines (Fraunces) over a sans body (Inter), flat hairline cards (separation by fill, not drop shadow), and a single terracotta accent used sparingly. Fonts load from Google Fonts with a system-font fallback — delete the two `<link>` tags in the `<head>` for a fully offline file. Light is the default; dark mode is a warm charcoal applied via `prefers-color-scheme` or the manual toggle.

**Light/dark toggle.** A theme button (and the `t` shortcut) flips between light and dark and persists the choice to `localStorage`. It defaults to the OS preference, then remembers the user's manual choice. An inline `<head>` script re-applies the saved choice before first paint to avoid a flash.

**Built-in interactive features** (fill in content, don't rebuild them):

- **Collapsible cards** — each finding is a `<details>` card; the always-visible summary holds a severity badge, title, and one-line TL;DR, with the body hidden until expanded.
- **TL;DR strip** under the hero — one sentence covering the whole report (`{{TLDR_SENTENCE}}`). Always fill it; it's what a busy reader actually reads.
- **Stats grid + severity filter chips** — clickable counts per severity; filtered views are shareable via URL hash (`#sev=crit`).
- **Live search** over card text, **tag filtering**, **active TOC highlight**, **back-to-top**, **expand/collapse all**.
- **Reading time** auto-computed from page text (~220 wpm).
- **Keyboard shortcuts**: `j`/`k` next/prev card, `e`/`c` expand/collapse all, `t` toggle theme, `/` focus search, `1–4` filter by severity, `0` show all, `?` help, `Esc` clear.
- **Print/PDF safe** — `@media print` forces all cards open and hides the filter bar / controls.

**Severity classes** drive the colored card stripe, the badge, and the filter. Use one of `crit | high | med | low`, document the mapping in the legend, and put a `data-sev` on every card. The card markup looks like:

```html
<div class="card crit" data-sev="crit" data-tags="security,perf">
  <details open>  <!-- open by default for crit; omit `open` for lower severities -->
    <summary>
      <div class="head">
        <span class="badge crit">Critical</span>
        <h3>1. Short finding title with <code>code refs</code></h3>
        <span class="tag" data-tag="security">security</span>
      </div>
      <p class="tldr-line">One-line takeaway — what's wrong and why it matters.</p>
    </summary>
    <div class="body">
      <div class="files"><span class="path">path/to/file.py:42</span></div>
      <p>Full explanation. Use <code>inline</code> for symbols.</p>
      <pre>blocks for snippets</pre>
      <div class="fix"><strong>Fix:</strong> concrete remediation.</div>
    </div>
  </details>
</div>
```

The `.tldr-line` is the most important UX element — if you can't summarize a finding in one line, it's probably two findings. For non-review reports (research, summaries) the same structure works: use the cards as sections and pick a sensible severity-to-meaning mapping, or just use plain `<h2>`/`<p>` content inside `<main>`.

**Typography tokens.** The CSS exposes calibrated `:root` variables (`--body-size`, `--body-line`, `--prose-measure`, etc.) tuned for sustained reading and dark-mode legibility. Don't override them directly unless solving a specific layout problem; if you must, do it at the `:root` level of the report you generate (not the template) and leave a comment.

**Building a new theme.** Every theme is just a `<style>` reskin: keep the same markup, placeholders, severity classes, and `<script>`, and swap only the `:root` tokens and font stack. Add new looks as additive variant files (e.g. `report-<name>.html`) rather than overwriting `report.html`, and QA both light and dark modes since their contrast bugs are independent.

## Use-case playbook

### Reports, research, and learning

The flagship use case. Pull from the codebase, git history, issue trackers (via MCP), the open web, and local files, then synthesize all of it into one page someone can actually read.

What a good report includes:

- A 3–5 bullet executive summary at the top.
- A table of contents if there are 4+ sections.
- **SVG diagrams over ASCII.** Always. If you're tempted to draw a flow in monospace, draw it in SVG instead.
- Real citations inline: file paths with line numbers, commit SHAs, URLs. These are the report's receipts; without them the reader has to take everything on faith.
- A "gotchas" or "open questions" section at the bottom — what to be careful about, what's still unclear.

**Prompt pattern:**

> Read `src/rate_limiter.py`, the last 20 commits touching it, and any related design docs. Generate a single-page HTML report explaining how rate limiting works here. Include an SVG diagram of the token-bucket flow, 3–4 annotated code snippets with file:line citations, a comparison table of the strategies we considered, and a "gotchas" section at the bottom. Optimize the layout so someone can understand this in one read.

### Specs, planning, and exploration

For non-trivial features, prefer a small **network of HTML files** over one monolithic Markdown plan:

1. **Brainstorm** — `Generate 4–6 distinct approaches in one HTML file using a responsive grid. Label each with explicit tradeoffs.`
2. **Deep-dive** — pick one: `Expand option N into its own HTML file with wireframes (SVG/HTML), the key code snippets, and risks.`
3. **Implementation plan** — `Write the detailed plan as HTML: data-flow diagrams, file-by-file changes, and the snippets that most need human review.`
4. **Hand off** — start a fresh session, feed it the accumulated HTML files, then write the code.

This works because each artifact is small enough to read and the network as a whole carries the context that a fresh session needs.

### Code review and PR explainers

Markdown is brutal for reviewing diffs. HTML renders them well, and GitHub's diff view is often worse than a custom explainer you can tailor to the specific PR.

Required elements:

- Real syntax-highlighted diffs in `<pre>` blocks with green/red line backgrounds (see `assets/pr-review.html`).
- A severity legend at the top.
- A "what to review first" block — orient the reader so they don't waste attention on the trivial bits.
- Inline annotations next to the diff lines that need explanation.

**Prompt pattern:**

> Review this PR and generate an HTML artifact explaining it. I'm unfamiliar with the backpressure logic, so focus there. Render the real diffs with inline annotations. Color-code findings by severity (info / warn / error). Add SVG diagrams where they clarify control flow.

### Design and prototypes

HTML is the universal design substrate even when the final product ships in Swift, React, or Flutter. Sketch in HTML first, then translate.

Use the prototype template (`assets/prototype.html`) and:

- Build a live preview that updates as inputs change. Vanilla JS, no framework.
- Add a **"Copy params"** or **"Copy as prompt"** button so the user can hand the dialed-in values back to the agent. This closes the loop.
- Include a "Reset to defaults" control.

**Prompt pattern:**

> Prototype the new checkout button: a click triggers a short animation, then it turns purple. Generate an HTML file with sliders for animation duration, easing curve, and final color. Include a "Copy params as JSON" button.

### Custom editing interfaces

When plain-text input can't capture intent, build a **disposable, single-purpose UI**. Examples that work well:

- A drag-and-drop triage board ("Now / Next / Later / Cut") for a list of tickets.
- A feature-flag editor that validates dependencies and warns about invalid combinations.
- A side-by-side prompt template editor with live variable substitution and a token counter.
- A dataset row-by-row approve/reject/label tool.

The non-negotiable element here is **export**: `Copy as JSON`, `Copy as Markdown`, `Copy as prompt`, or `Download .csv`. Without an export action, the artifact is a dead end — the user did the work but can't get the result back to the agent.

Other patterns that pay off:

- Persist state in `localStorage` so a reload doesn't wipe the work.
- Keyboard shortcuts where they save real time (`j`/`k` to navigate rows, `1`/`2`/`3` to assign categories).

## Sharing and viewing

- **Local viewing:** `open file.html` (macOS), `xdg-open file.html` (Linux), `start file.html` (Windows). Offer to do this for the user after writing the file.
- **Sharing:** upload to S3, GitHub Pages, Cloudflare Pages, Vercel, or any static host. The URL is the artifact.
- **PRs:** attach the HTML as a build artifact or link from the PR description.

## Brand and visual consistency

If the project has an existing UI codebase, offer once to scan it for design tokens (colors, typography, spacing, component patterns) and emit a `design-system.html` reference file. Then point at that file when generating later artifacts so the visual style stays on-brand. Don't do this proactively for one-off reports — it's only worth the effort when the user will produce many artifacts for the same project.

## Honest tradeoffs

| Concern | Reality | Mitigation |
|---|---|---|
| Token cost | HTML uses 2–4× more tokens than Markdown | Worth it for anything read by humans; negligible in large context windows |
| Generation time | 2–4× slower than Markdown | Acceptable for outputs read repeatedly; not for ephemeral chat replies |
| Version control | HTML diffs are noisy | Keep artifacts under `reports/` or `docs/html/`; don't try to code-review them line-by-line |
| Default look | Vanilla LLM HTML can feel generic | Use the bundled templates; reference a project design system file if one exists |

## Anti-patterns

- Wrapping a 30-line answer in HTML just because — overkill for short replies.
- Pulling in React, a Tailwind build, or any bundler for a one-shot artifact.
- Splitting one conceptual artifact across many HTML files when one would do.
- Building an interactive editor without an export action — the user has nowhere to send the result.
- Dark-only styling on something likely to be printed or pasted into a doc.
- Re-asking "HTML or Markdown?" every turn after the user already chose.

## Quick checklist before shipping

1. Is HTML actually the right format here? (See "When to reach for this skill.")
2. Single self-contained file, no build step, no required network?
3. Opens cleanly from `file://`?
4. Mobile-friendly and printable?
5. If interactive: is there an export action that closes the loop back to the agent?
6. Did I cite sources / link to code / show real diffs where appropriate?

If all six are yes, write the file. Then offer to open it in the browser.

## Reference

- Thariq Shihipar, *Using Claude Code: The Unreasonable Effectiveness of HTML* — https://x.com/trq212/status/2052809885763747935
- Examples gallery — https://thariqs.github.io/html-effectiveness/
- Bundled templates — `assets/report.html`, `assets/pr-review.html`, `assets/prototype.html`
