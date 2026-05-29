---
description: DEFAULT report/analysis renderer. Load and use this template whenever the user asks to "analyze", "review", "audit", "inspect", "look at", or produce a "report", "analysis", "summary", "writeup", "findings", or "review" of a project, codebase, file, document, dataset, or topic — UNLESS they explicitly ask for plain text, markdown, or a different format. Self-contained light/dark-aware HTML: soft-gray editorial "paper" with serif display headlines and a terracotta accent, severity-coded hairline cards, sticky pill TOC, stats grid, a 🌗 light/dark toggle, and suggested-actions block. (Deep-indigo engineering theme available as report-indigo.html.) Default output path is project_dir/code_review_report.html or topic_report.html for non-project analyses.
---


# html-review-report

Reusable HTML template for rendering code reviews, project analyses, audit reports, and similar structured findings as a polished standalone HTML file.

## When to use

DEFAULT for any report / analysis request. Specifically:

- User says "analyze X", "review X", "audit X", "look at X and tell me what you think", "inspect X", "go over X"
- User says "make me a report on…", "give me a writeup of…", "summarize the findings of…"
- User asks for "improvements", "suggestions", "issues", "problems" in a project / file / document
- User compliments the previous report styling and wants more — reuse this template

Opt-OUT only when the user explicitly says: "plain text", "markdown", "just text", "in the terminal", "don't make a file", "txt", or names a different format (PDF, JSON, etc.).

When in doubt, render the HTML report AND also give a short text summary in chat. Then tell them the absolute path and `open <path>` command.

## Quick recipe

1. Pick the output path. Default: same directory as the analyzed project, named `<project>_review.html` or `code_review_report.html`.
2. Copy `templates/report.html` (full skeleton) and fill in:
   - Hero title, subtitle, meta-row chips (date, path, language, version, LOC)
   - Stats grid (counts per severity)
   - Sticky TOC links (must match section ids)
   - One `<section>` per severity bucket, with one `.card` per finding
   - Quick-wins / "order of attack" block at the end
3. Write with `write_file` (overwrite if exists). Tell the user the absolute path and the `open <path>` command.

## Theme variants

Two skeletons ship with this skill. Pick by the look the user asks for:

- `templates/report.html` — **DEFAULT.** Soft neutral-gray editorial "paper" (light-first, `--bg:#e8e7e3`), **serif display headlines** (Fraunces) over sans body (Inter), flat hairline cards (no drop shadow — separation by fill), single **terracotta accent** (`#c2613f`) used sparingly, dark pill buttons. Dark mode is warm charcoal (`#1a1a18`), NOT indigo. Ships with a **🌗 Theme toggle button** (and `t` shortcut) that flips light/dark and persists to `localStorage` — defaults to OS preference, then remembers the user's manual choice. Use unless the user asks otherwise.
- `templates/report-indigo.html` — **Deep-indigo engineering variant.** Dark-first, Vercel/Linear aesthetic. Gradient hero, drop-shadowed cards, all-sans (Inter). Use when the user wants the indigo/engineering look instead of the calm editorial default.

Both variants share the SAME structure, placeholders, severity classes, and JS engine — every card pattern, interactive feature, and iteration workflow below applies to both. Only the CSS `:root` tokens and font stack differ. To switch an existing report between themes, you can swap just the `<style>` block; the body markup is interchangeable.

The Anthropic variant's signature moves (if hand-tuning): serif `--serif:"Fraunces"` on all `h1–h4`, `--shadow:none`, hairline `--border` with `--panel` fill for cards, terracotta `--accent` doing double duty as brand-warmth + critical-severity, and a soft-gray (de-warmed from Anthropic's cream) `--bg`. Light-mode body grays are darkened (`--muted:#595951`, quality `--med:#8a6d1f`) for WCAG AA on the gray paper — don't lighten them back.

**Theme toggle architecture (anthropic variant).** Light is the base `:root`; dark tokens live in BOTH `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` (OS auto) AND `:root[data-theme="dark"]` (manual force). A `--toc-bg` token carries the sticky-nav backdrop so it follows the theme (don't hardcode the `nav.toc` rgba anymore). The 🌗 button + `t` shortcut flip `document.documentElement.dataset.theme` and persist to `localStorage['report-theme']`; an inline `<head>` script re-applies the saved choice before first paint to avoid a dark→light FOUC flash. To force a mode for QA you can now just set `localStorage.setItem('report-theme','light')` (or `'dark'`) and reload, or set `<html data-theme="…">` — simpler than the media-query rewrite trick below. **Copy-pasteable snippets for all five pieces** (dual dark-token blocks, `--toc-bg`, anti-FOUC head script, button, toggle JS + `t` shortcut) and the in-browser QA recipe are in `references/theme-toggle-snippets.md` — use it to add a toggle to ANY variant, including the indigo default.

### Building a NEW theme variant (recipe)

When the user asks for a fresh look ("make it like <brand>", "a gray version", "warmer"), build it as an **additive variant file** — never overwrite `report.html`. Workflow that worked:

1. **Recon the target's real design** before guessing. `browser_navigate` to the brand's actual site, then `browser_vision` asking for exact background colors, serif-vs-sans, border/shadow treatment, accent usage, card styling. Working from memory of a brand produces a generic approximation; the vision pass catches the signature moves (e.g. Anthropic = warm cream + serif headlines + flat fill-separated cards + single terracotta accent, NOT shadows/indigo/all-sans).
2. **Copy the structure, swap only `:root` tokens + font stack.** Every variant keeps the same markup, placeholders, severity classes, and `<script>` engine. A variant is a `<style>` reskin, nothing more — that's what makes themes interchangeable.
3. **Lock the replace-vs-variant decision with `clarify`** (retire old theme / add alongside / reskin-keep-engine / build-and-decide). Default to additive + "build a smoke-test first" if the user doesn't answer — it's the reversible call and matches their additive-rollout preference.
4. **Smoke-test BOTH modes via the forced-mode trick** (see vision-loop step in the readability workflow). Light and dark have independent contrast bugs.
5. **Expect many small color-iteration turns.** "Bit darker grey?" → "way more gray" → "make a dark one for comparison" is the normal shape. Use surgical `patch` on the `:root` tokens, regenerate the smoke test, re-run `browser_vision`, report the path. When darkening the page `--bg`, also bump the hardcoded `nav.toc` rgba backdrop and `--code-bg`/`--code-border` to stay in the same family, and keep `--panel` bright so cards still float (raising paper darkness alone makes low-severity cards lean entirely on their accent rail).
6. **Document the variant** in this "Theme variants" list AND the Files section the moment it ships, so the next session can pick it by name.

## Card pattern (collapsible)

Every finding is a `.card` with `data-sev` (for filtering) and a `<details>` block. The `<summary>` holds the always-visible badge, title, and **one-line TL;DR**. The `.body` holds the detail (paths, snippets, fix) and is hidden until expanded. Critical cards SHOULD be `<details open>`; lower severities default to collapsed so the page scans fast.

```html
<div class="card crit" data-sev="crit" data-tags="security,perf">
  <details open>  <!-- open by default for crit; omit `open` for high/med/low -->
    <summary>
      <div class="head">
        <span class="badge crit">Critical</span>
        <h3>1. Short title with <code>code refs</code></h3>
        <span class="tag" data-tag="security">security</span>
      </div>
      <p class="tldr-line">One-line takeaway — what's wrong and why it matters.</p>
    </summary>
    <div class="body">
      <div class="files">📄 <span class="path">path/to/file.py:42</span></div>
      <p>Full explanation. Use <code>inline</code> for symbols, <pre>blocks</pre> for snippets.</p>
      <ul><li>Bullet point</li></ul>
      <div class="fix"><strong>Fix:</strong> concrete remediation.</div>
    </div>
  </details>
</div>
```

**`data-sev` is required** — drives the severity filter chips and stats-grid filtering. Must match one of `crit|high|med|low`.

**`data-tags` is optional** but high-value — comma-separated cross-cutting labels (`security`, `perf`, `dx`, `tests`, `docs`). Pair with `<span class="tag" data-tag="…">` chips in the head so a reader can click a tag and see every finding with it across severities.

**`.tldr-line`** is the single most important UX upgrade. Write it as a complete sentence a busy reader can grok without expanding. If you can't summarize the finding in one line, the finding is two findings.

Severity classes (color stripe + badge):
- `crit` red — critical / high-impact
- `high` orange — high-priority / medium-impact
- `med`  yellow — quality / polish
- `low`  green — nice-to-have / security-adjacent

Pick a consistent mapping per report and document it in the legend pill inside the summary section.

## Interactive features (built into the template)

The template ships with these — fill in the content, don't rebuild them:

- **Collapsible cards** (`<details>` + `<summary>`) — TL;DR always visible, body hidden.
- **TL;DR strip** under the hero — `{{TLDR_SENTENCE}}` placeholder, one sentence covering the whole report. The thing exec readers actually read. Always fill it.
- **Reading time** auto-computed from `document.body.innerText` (~220 wpm).
- **Severity filter chips** + clickable stat cards — both toggle the same `data-sev` filter. URL hash (`#sev=crit`) makes filtered views shareable.
- **Tag filter** — click any `.tag[data-tag]` chip on a card to show only findings with that tag. Click again to clear.
- **Live search** — substring match against card text.
- **Active TOC highlight** — IntersectionObserver highlights the section currently in view.
- **Back-to-top button** — appears after 600px scroll.
- **Expand all / Collapse all** buttons in the sticky TOC.
- **Keyboard shortcuts**: `j`/`k` next/prev card (auto-expands as you move), `e`/`c` expand/collapse all, `/` focus search, `1–4` filter by severity, `0` show all, `?` help overlay, `Esc` clear.
- **Print/PDF safe** — `@media print` forces all `<details>` open and hides the filter bar / back-to-top / collapse chevrons, so the Chrome-headless PDF recipe still produces a complete document.

When filling the template: include `data-sev` on every card, write a `.tldr-line` for every card, and write a one-sentence TL;DR for the whole report. The rest is optional polish (tags, custom sections).

## Theme reference

Deep-indigo + pastel accents, Vercel/Linear-style. Auto-adapts via `prefers-color-scheme: light`.

Palette (dark mode):
- bg `#0b1020` → bg2 `#121a33` (very dark blue, not pure black)
- panel `#182142`, panel2 `#1f2a52`, border `#2a3568`
- text `#d4ddf5` (NOT pure white — reduced from #e6ecff to kill dark-mode halation), muted `#9ba6d1`
- accent `#7aa2ff` blue, accent2 `#b388ff` purple
- severity: crit `#ff5d6c`, high `#ffb454`, med `#ffd866`, low `#5fd1a3`, ok `#4ade80`
- code `#0d1430` bg / `#243066` border
- shadow `0 10px 30px rgba(0,0,0,0.35)`

Tricks doing the heavy lifting:
1. Gradient hero — `linear-gradient(135deg, bg2, panel)`
2. Colored 4px `::before` stripe on each card (severity at a glance)
3. Soft shadow lifts cards off the bg
4. Monospace code chips with own bg/border — paths pop
5. Sticky pill TOC at top of viewport
6. Quick-wins block uses a subtle blue→purple gradient

## Typography system (2026 readability upgrade)

The template now ships a CSS-variable-driven type system designed for sustained dark-mode reading. **Do not override these directly** unless you're solving a specific layout problem — they're calibrated against current research (WCAG 2.1, CHI 2023 grade-axis study, Mantlr dark-mode guide).

Tokens (defined in `:root`, light-mode block overrides several):

| Token | Dark | Light | Purpose |
|---|---|---|---|
| `--body-size` | `17px` | `17px` | 2025 baseline for content-heavy UIs (was browser default 16px) |
| `--body-line` | `1.7` | `1.6` | Dark wants more air than light — reduces "heavy" feel |
| `--body-track` | `0.012em` | `0` | Counter halation that makes light text "spread" on dark |
| `--body-weight` | `400` | `430` | Light text on dark renders thinner — light mode wants a touch heavier |
| `--heading-weight` | `600` | `650` | Bold reads heavier on dark; 600 keeps balance |
| `--prose-measure` | `68ch` | `68ch` | 45–75ch legibility window — applied to `.card .body p`, `.subtitle`, `.tldr`, `.section-intro` |

Fluid sizing: `h1` uses `clamp(1.75rem, 1.3rem + 2vw, 2.75rem)` and `section h2` uses `clamp(1.4rem, 1.1rem + 1vw, 1.75rem)` so they scale from 13" laptop to 32" monitor without breakpoints.

Numerics:
- Body uses `font-variant-numeric: lining-nums proportional-nums` (technical reports, not novels — lining figures read more naturally than oldstyle).
- Stat tiles, meta-row, and tables use `tabular-nums lining-nums` so digits column-align.
- Stat tiles are also `text-align: center` so single-digit and multi-digit values share visual rhythm.

Modern wrap: `p { text-wrap: pretty; }` eliminates orphan words and bad rag automatically (WebKit Sept 2025, Baseline). `h1, h2, h3, h4 { text-wrap: balance; }` prevents headings from breaking into a one-word last line.

Focus rings: replaced browser default with `*:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }` — the single biggest "designed vs defaulted" tell (Linear/Stripe/Vercel teardowns).

Fonts: Inter Variable (300–700 weight axis) + JetBrains Mono Variable from Google Fonts via `<link rel="stylesheet">`. **Fallback to system stack** if the network blocks the fetch, so offline PDF rendering still works. If you need a fully self-contained file with no external requests, remove the two `<link>` tags — the system stack (`-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif`) takes over automatically and looks ~85% as good.

TL;DR strip: now `font-size: 1.12rem`, real background tint (12% indigo/violet gradient), 4px left border. It's deliberately the second-most-prominent reading element after h1, because it's the one sentence the exec reader actually reads.

Section rhythm: `section { padding: 64px 0 8px }` (was 40px). Tight WITHIN cards, generous BETWEEN sections — the Stripe/Linear "dense content blocks separated by air" pattern.

When you genuinely need to override a token (e.g. user wants a smaller body size for a print deliverable, or wants a self-contained file), do it at the `:root` level in the report you generate, not by editing the template. Document the override in a code comment so the next iteration doesn't undo it.

## Pitfalls

- Do NOT emit `MEDIA:` tags on CLI — just print the absolute file path and the `open` command.
- Mostly self-contained: all CSS inline in `<style>`. The 2026 typography upgrade adds two `<link>` tags to Google Fonts (Inter Variable + JetBrains Mono Variable). If you need a fully offline / no-external-requests file, delete those two `<link>` tags — the system font stack takes over automatically (small visual downgrade, no functional impact).
- Section ids in the TOC must match `<section id>` exactly.
- When updating an existing report, prefer `write_file` (full overwrite) — the template is short enough that targeted patches usually aren't worth it.
- If the project has its own theme/branding, ask before applying this one — it's opinionated.

## Living-document mode (multi-turn design conversations)

This template works just as well as a **living design doc** that evolves across many turns, not only as a one-shot review:

- First turn: ship the report with all open questions marked.
- Subsequent turns: as decisions get made (e.g. "go with GCS", "skip the sweeper for now"), patch the relevant section with a "✅ Decided" pill and a short rationale. Use `patch` (not `write_file`) for these — surgical edits preserve the rest.
- New sections can be appended for major design pivots (e.g. add a "v1 scope" section once scope locks).
- An inline SVG architecture diagram (themed to the same deep-indigo palette) lands well as a single `.card` containing a self-contained `<svg viewBox=...>`. The same color tokens as the template work great for boundaries (dashed strokes for trust zones) and component fills.
- Open questions stat in the hero should decrement as questions resolve.

When the report becomes the agreed contract, switch from advisory mode to implementation — but keep the report file in the repo, not just in chat history. It's the artifact future-you will look at when the code doesn't match memory.

When the user pivots architecturally mid-conversation ("change of plans, do X instead of Y"), don't `write_file` a fresh report and walk away — restructure with the **plan-pivot pattern**: rewrite the hero stats, redraw the architecture SVG (don't patch element-by-element), renumber phases from 1, add a "Dropped from plan" section that records what each shelved piece would have added and what it would have cost, mark shelved files as `Shelved` in the artifacts table (don't delete from disk), and add a `crit`-severity "Honest limit" card naming the property the simpler approach trades away. Full recipe: `references/plan-pivot-pattern.md`.

When the user signals "remove what's done" / "strip out shipped work" after a phase executes (the report's third life-cycle phase: analysis → status → forward-only handoff), use the **strip-done-items pattern**: rip whole done sections (don't strip card-by-card), fold forward-looking content out of audit cards BEFORE deleting them, rewrite the hero TL;DR to plain forward-state, swap hero stats from review-status to shipping-status metrics, replace "Order of attack" with a slim "Roadmap" of future PRs, and keep the diff-sizing table as the one historical artifact (proof the work happened). Open questions become the centerpiece. Full recipe: `references/strip-done-items-pattern.md`.
## Reconciling plan vs. code when both exist

In long-running design-doc-mode sessions the user often partially implements the plan between turns. When they ask a question like "is X already included?" or "did we do Y?", do NOT answer from the plan alone — `search_files` and `read_file` the relevant module(s) first, then answer in two parts:

- **In the PLAN (the report)**: what the design says.
- **In the CODE (on branch `<name>`)**: what's actually wired up, with file:line references.

Almost always the answer is asymmetric ("in the plan: yes, fully — in the code: only the Protocol seam, the impl is still in-memory"). Hiding that asymmetry leads the user to skip work they actually need to do.

When the asymmetry is non-trivial, add a small **Status callout card** at the top of the relevant section of the report so future re-reads carry the reconciliation:

```html
<div class="card" style="border-left: 3px solid #ffb454;">
  <div class="head"><span class="badge med">Status</span><h3>Branch <code>feat/X</code> vs. this plan</h3></div>
  <p>What's already on the branch: &lt;list&gt;. What's still &lt;in-memory|stubbed|TODO&gt;: &lt;list&gt;. No endpoint / schema / wiring changes needed — the seam is in place.</p>
</div>
```

The orange left-border (`#ffb454`, the `high` severity color) without using the full `.card.high` styling marks the card as informational-status, not a finding. Reuse this pattern any time the plan and the code drift apart.

## Iterating a report across turns

Reports often grow conversationally: the user reads v1, makes a decision, and asks you to fold it in. Pattern that works:

1. **Mark resolved open questions in place** — replace the `<div class="qbox">` body with `<strong>QN. ✅ Decided:</strong> <one-line decision>. See the <a href="#section">section</a>.` Do NOT delete the qbox; keeping the slot preserves numbering and shows the decision history.
2. **Decrement the "Open questions" stat in the hero** when you resolve one. Easy to forget; the report looks stale otherwise.
3. **Add a new dedicated section** for the decided topic (e.g. "GCS bucket design") rather than sprinkling the new content across existing cards. Add a matching TOC pill so the sticky nav reflects it.
4. **Rename section headings when scope changes** — e.g. "Migration plan" → "Rollout plan (additive — sync endpoint stays)" once the user says they're not migrating. The pill subtitle is the right place for the qualifier.
6. **Replace deprecated phase cards with `low`-severity "Optional later" cards** instead of deleting them. Preserves the numbering and shows the team considered and shelved the option.
6. **Cite real file:line references** when the user confirms an existing-codebase fact (e.g. "the project already uses MyAPI for this"). Grep first, then quote `src/path/file.py:LN` in the card — turns the report into a verifiable artifact instead of a vibes doc.

## Design-doc mode (when a report becomes a spec)

A report can evolve from "findings" into "buildable spec" across turns. When the user starts making decisions ("we'll use GCS", "no migration, additive only", "BackgroundTasks for v1"), shift the report into design-doc mode:

- **Add a "v1 plan" / "locked scope" section** with a `pill` like `locked scope` or `decided`. Cards should be different shape than findings — no severity rating, instead:
  - A `high`-severity card with a `.twocol` `.compare good` / `.compare bad` block titled "✅ In v1" / "❌ NOT in v1" — makes scope unambiguous.
  - `high`-severity "Flow" cards numbering the request lifecycle (split sync vs async parts visually).
  - A `med`-severity "Sketch" card with the actual endpoint signature in a `<pre>` block (real Depends, real types, real comments). Forces concreteness.
  - A `med`-severity "Schema" card with Firestore / DB / config layout as a `<pre>` block plus required composite indexes as a `<ul>`.
  - A `med`-severity "Tests" card naming the test strategy (in-memory fakes, emulators, what stays green from existing suite).
  - A `high`-severity "Deployment" card listing k8s / infra changes.
  - A `low`-severity "Done means" / "Acceptance criteria" card with a numbered list of verifiable outcomes (not vague — "pod restart → job appears as failed_lost within ≤12 min").
  - A `crit`-severity card for any non-obvious failure mode the design must catch (e.g. "sweeper must catch TWO stuck states, not one"). These are the future-incident-prevention cards.

## Embedding architecture diagrams inline

When the user asks for "an architecture image / diagram" inside a report, do NOT call the `architecture-diagram` skill and produce a separate file — embed inline SVG in a new `<section>` so the report stays self-contained.

Use the report's palette, not architecture-diagram's slate-950 default:

- Background: `#0d1430` (matches the report's `--code-bg`), with a 40px grid in `#1f2a52`.
- Component fills: `rgba(<accent>, 0.08–0.12)` with stroke = the accent hex.
- Reuse the severity colors as semantic markers in the diagram:
  - `#7aa2ff` blue — API surfaces, read paths
  - `#5fd1a3` teal — happy-path submits, LLM/external calls
  - `#b388ff` purple — state store (Firestore, DB)
  - `#ffb454` orange — blob storage (GCS, S3)
  - `#ff5d6c` red — failure / sweeper / shutdown hooks
- Solid arrows = happy path, dashed = scheduling / polling / cleanup.
- Wrap the `<svg>` in a `<div class="card" style="padding: 8px; overflow-x: auto;">` so it gets the same border/shadow as findings cards.
- Set `viewBox` + `style="width:100%; height:auto; min-width:880px;"` so it scales with container but doesn't squish illegibly on narrow viewports.
- Include a small bottom-left legend inside the SVG (small rect + 3-4 colored line samples) — readers won't always remember the color semantics.
- Boundary boxes (e.g. "STACKIT · KUBERNETES", "GOOGLE CLOUD") as `stroke-dasharray="8,4"` rectangles with no fill — makes trust/network boundaries obvious.
- Use the `architecture-diagram` skill ONLY as a structural reference (markers, double-rect masking, layout spacing) — never copy its color palette into the report.

See `references/inline-svg-architecture-diagrams.md` for the full reusable snippet library: standard `<defs>` block (grid pattern + three colored arrow markers), component-box pattern with semantic fill colors, trust-boundary conventions (purple = laptop, blue = GCP, orange = StackIT/external, teal = customer), arrow conventions, bottom-left legend template, and pitfalls (viewBox sizing, `<text>` no-wrap, light-mode SVG behavior).

## Executive-brief mode (when a report needs to shrink for management)

Some reports start as deep findings and get trimmed down across turns until the user wants a **one-page exec brief**. Recognise the trigger phrases:

- "make it management viable", "for the exec team", "1-page", "just the headlines"
- A trimming sequence: "remove section X", "remove Y", "remove recommended actions"
- "just a sentence what changed" / "TL;DR only"

When this happens, **don't keep patching cards one at a time** — restructure to the exec layout:

1. **Single-sentence Executive Summary** at the top. One paragraph covering every kept item, with the names bolded. No "what it means for us" card unless the user asked for a recommendation — they often explicitly remove these.
2. **Numbers section** as a `<table>` inside one `.card`, not as prose. Comparison tables (old vs new, before/after, us vs competitor) read instantly for a busy reader. Use `tabular-nums`, right-aligned numeric columns, and color the delta cells (`.up` green for improvements, `.down` red for regressions). Add a `<div class="fix">` below the table with the one-line "Read:" interpretation.
3. **Cards section** with one card per remaining item, ~2-3 sentences each. Use the `.head` badge to label the *role* of the card (Watch, Builder, Distribution, Naming, Relevant for us) rather than severity — for exec briefs this is more scannable than crit/high/med/low.
4. **No "Recommended actions" / quickwins block** unless asked. Management briefs are decision support, not task lists; the user often deletes this section explicitly. If they want actions, they'll ask.
5. **Drop the hero header and TOC** if the user removes the lead sections — the page is short enough that a sticky TOC is noise.

Table card pattern (works well for benchmark / pricing / before-after comparisons):

```html
<div class="card">
  <table>
    <thead>
      <tr><th>Metric</th><th style="text-align:right">Old</th><th style="text-align:right">New</th><th style="text-align:right">Δ</th></tr>
    </thead>
    <tbody>
      <tr><td>Score</td><td class="num">46</td><td class="num">55</td><td class="num up">+9</td></tr>
      <tr><td>Cost</td><td class="num">$282</td><td class="num">$1,552</td><td class="num down">5.5×</td></tr>
    </tbody>
  </table>
  <div class="fix"><strong>Read:</strong> one-line takeaway here.</div>
</div>
```

Add this CSS once to support the table style:

```css
table{width:100%;border-collapse:collapse;margin-top:8px;font-size:0.9rem}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-weight:600;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em;background:var(--panel2)}
tr:last-child td{border-bottom:none}
td.num{font-variant-numeric:tabular-nums;text-align:right;font-family:"JetBrains Mono","SF Mono",Menlo,monospace}
td.up{color:var(--low)} td.down{color:var(--crit)}
```

## Pitfalls (additional)

- When updating an existing report across turns, prefer targeted `patch` calls over `write_file` rewrites. The template is verbose, the user often only changes one decision at a time (e.g. "we picked GCS", "we won't migrate, just add"), and patching keeps the diff reviewable. Full overwrite is only worth it for a structural overhaul.
- If the project has its own theme/branding, ask before applying this one — it's opinionated.
- **The user often edits the HTML directly between turns.** Treat the report as a shared artifact, not your private buffer. Before any patch on a report you've already shipped, re-read the relevant region — the user may have rewritten a phrase or fixed your typo, and your patch will silently revert it. If the file-write tool warns about "modified since you last read", STOP and re-read before writing. If you do overwrite an external edit, call it out plainly in your reply so the user can re-apply if they want.
- When the user asks to remove a section by quoting a sentence verbatim, locate the surrounding `<section>` or `<div class="card">` and delete the whole block, not just the sentence — half-empty cards look broken. If you're unsure whether they meant the sentence only or the whole card, ask once.
- After several rounds of trimming, re-read the executive summary / TOC / hero stats — they often reference sections that no longer exist. Offer to fix the dangling references rather than leaving them stale.

## Companion deliverables (PDF, Markdown)

Once a report stabilizes, the user often asks for it in additional formats for distribution. Two recipes that work on macOS:

**HTML → PDF** (headless Chrome, no header/footer, preserves the report's CSS):

```bash
HTML="/abs/path/to/report.html"
PDF="${HTML%.html}.pdf"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PDF" "file://$HTML"
```

Notes:
- Chrome's print mode uses the page's **light-mode** CSS via `@media (prefers-color-scheme: light)`, so PDFs come out white-background even when the browser preview is dark. That's usually what you want for a printable management deliverable — call it out so the user isn't surprised.
- Output ends up ~400–600KB for typical reports. The "N bytes written" line on stderr is the success signal.
- `--no-pdf-header-footer` is important; the default adds a URL footer and timestamp header that look unprofessional on a deliverable.

**HTML → Markdown** (hand-written, not converted): Don't run a tool. Re-author the report as Markdown so prose flows naturally, the table renders correctly in GitHub/Obsidian, and severity badges become `*(Watch)*`-style italics next to the heading. A converter produces ugly nested `<div>` soup. Keep the same structure: front-matter line with sources → executive summary → numbers table → cards as `### Heading *(Badge)*` + paragraph.

When the user iterates on the HTML after PDF/MD were generated, **regenerate both** — they go out of sync fast. Best practice: write all three to the same directory with the same basename and different extensions (`report.html`, `report.pdf`, `report.md`).
- **Don't invent proper nouns.** When the user mentions an unfamiliar product/codename ("add that Vertex AI was renamed", "add Google's OpenClaw"), ask via `clarify` for the actual name before writing it into the report. Reports are durable artifacts — hallucinated names embarrass the user when shared. Multiple-choice clarify ("did you mean X or Y?") is fast and respects their time.
- **Markup-during-patch pitfall**: when patching a card head, it's easy to accidentally leave a stray `</h3>` inside a `<span>` (e.g. `<span class="badge crit">Relevant for us</h3></span><h3>Title</h3>`). Always re-read the patched line, or do a follow-up patch to fix the typo. The lint pass skips HTML so the broken tag won't be flagged automatically.
- **Trimming-removes-numbering-coherence**: when the user asks to remove cards in the middle of a numbered list (e.g. "remove 9, 10, 11"), the remaining cards keep their old numbers (12, 13, 14…). Either renumber down in the same pass, or proactively ask "renumber so the next section starts at 4?" — don't leave it ambiguous across turns.
- **Don't prescribe actions for exec / management audiences unless explicitly asked.** Sentences like "Action: keep X as default; pilot Y selectively" or "Recommendation: …" tend to get deleted on the next turn. For management briefs, default to presenting the data and the named trade-offs (price vs. quality, speed vs. cost) and let the reader draw their own conclusion. The `.fix` block is fine for technical findings ("Fix: add a sweeper") but inappropriate in a strategic/exec context — use a neutral "Read:" or "Note:" block there instead, or just drop it.
- **Iterative trim pattern is common.** Users will often request a maximalist report first, then trim aggressively over several turns ("remove section X", "also remove 9, 10, 11", "remove the header"). Expect this. When asked to trim, use targeted `patch` calls — don't `write_file` the whole thing unless restructuring. Also: when sections are removed, remember to update the TOC, the hero stats (e.g. "N findings"), and the takeaways block to match — stale references are the #1 leftover artifact.
- **Don't elaborate trade-off pickers when the user has an opinion.** During plan iteration, when the user asks for a change ("remove in-memory, store in bucket"), don't pause to offer a 3-option `clarify` picker on a related sub-decision ("where does the result live: A/B/C?") unless you genuinely don't have a default. They'll usually skip the multiple-choice and just type their preference — which means the trade-off framing was wasted. Pick the simplest reasonable default, state the trade-off in one sentence inside the patch ("result stays inline in Firestore; spill to `processed/` only on 1 MiB overflow"), and let them push back if it's wrong. Reserve `clarify` for the genuinely-locked decisions ("which queue", "keep sync endpoint") not for derivative sub-choices.

## Production-readiness audit mode (is-this-prod-ready reports)

When the user asks "how can we make this more production ready", "audit this for prod", "what's missing before we ship", or similar, the report has a distinct shape from a generic code review:

- **Lead with a "What the project already does well" section** (5-10 strength cards, severity = `low`, badge = "Strength"). On a project where the user has clearly put in real engineering work, jumping straight into the criticism reads as a hit piece and they'll discount the findings. The strengths section also forces you to actually look at what's there before listing what's missing — half the time you'll catch yourself about to flag something the codebase already handles. Make these specific (cite `file:line`), not generic praise.
- **Severity mapping for prod-readiness** (document in the legend):
  - `crit` Critical — block production / ship in next sprint (security holes, data-loss risks, will-page-you-at-3am items, lies in operator-facing docs)
  - `high` High — meaningful production impact (cost/perf/reliability risks that don't immediately page but will bite)
  - `med` Quality & correctness — sharp edges, missing structured errors, inconsistent config plumbing, deprecation hygiene
  - `low` Polish & nice-to-have — version drift, README claims, dev-time conveniences
- **Always close with an "Order of attack" block** structured as 3-4 sprints, NOT a flat priority list. Sprint 0 = mechanical fixes a junior can knock out in 1-2 days; sprint 1 = the actual production-incident risks; later sprints = the bigger investments. Group by "what can be deliverable independently" not by raw severity — a sprint of 4 critical items that all touch the same file is worse than a sprint with 2 criticals + 2 highs from different domains.
- **For each finding, name the concrete failure mode** in the TL;DR line ("one slow Vertex call stalls a worker indefinitely", "audit log is lost on every pod restart"), not just the category ("reliability issue", "observability gap"). The TL;DR is what the eng manager reads; it has to be self-contained.
- **Stage 2 of audit** before writing: grep the codebase for what you're about to claim is missing. "No auth" is embarrassing if there's a `Depends(verify_caller)` you didn't notice. Specifically check: auth dependencies on routes, HEALTHCHECK in Dockerfile, USER directive, env-var reads vs Settings class, timeout wrappers around LLM calls, where extracted intermediate values get consumed downstream (a common waste pattern is "we compute X and never read it").
- **Look for the silent-waste pattern**: a stage / field / feature that exists, costs (LLM tokens, latency, code complexity), and isn't read by anything downstream. This is almost always present on agentic pipelines that grew milestone-by-milestone — call it out as `high` severity even though it doesn't "break" anything, because the user is paying for it on every request.
- **Look for the doc-vs-code lie**: operator docs that describe a default or fallback that the code has since removed. These are `crit` because the first new operator will hit them on day one. Grep the OPERATIONS / README for env-var defaults and verify against `config.py` / wherever the actual fallback lives.
- **Honest about additive vs breaking**: per the user's preference, prefer additive fixes ("add alongside, leave old in place") in the Fix blocks. When a fix genuinely is breaking (removing a schema field, changing a default), say so explicitly so the user can weigh the migration cost.

## News / keynote recap mode (external-source reports)

When the report summarizes an external event (keynote, conference, launch day, earnings call, research roundup) rather than analyzing the user's own code/design, the audience filter changes — and it's the most common reason a v1 gets cut down on turn 2.

Rules of thumb when picking what becomes a card:

- **Filter for "does this change a decision the user might actually make?"** A practitioner reading a keynote recap wants to know what to ship on, what to migrate to, what to test, and what to budget for. Things that pass this filter: new models + price/perf, availability dates, API/SDK changes, deprecations, hardware they can buy, breaking-change warnings, MCP/protocol moves that affect what they integrate with.
- **Cut "stage decoration" by default.** Capex numbers, internal datacenter stats, "we are the biggest" flexes, total-customer counts, vanity benchmarks. The user reads the keynote post if they want the marketing. They asked you for a report because they want the actionable subset.
- **Especially cut infra/finance cards when the user is an application developer.** TPU generation splits, total-spend guidance, "1M chips globally" — these are interesting to platform-team readers, near-zero value to someone shipping an app on top. If you're not sure of the audience, lean toward cutting and let them re-add.
- **Pricing is a first-class concern, not a footnote.** Whenever a new model is announced, include a card that compares its price to the user's likely current model — not just to "other vendors". The Google framing of "save $1B vs other frontier models" hides the fact that within Google's own lineup the new model can be substantially more expensive than the previous one. Always answer: "should the user migrate, or stay on the cheaper previous-gen and use the new one selectively?"
- **Add an `Action` line (`<div class="fix"><strong>Action:</strong> …</div>`) to every card where the user could do something.** "Benchmark on your workload", "watch deprecation date", "swap in for video pipelines" — not "this is impressive".
- **Audience filter goes in the hero subtitle**, so re-reads remember the framing: "Highlights for [audience] — [angle]" rather than a generic "everything announced".
- **Default severity mapping for keynote recaps** (different from code-review mapping):
  - `crit` Headline — the 1–3 announcements that reshape the landscape (new flagship model, paradigm shift).
  - `high` Major — concrete products / capabilities the user can ship on or evaluate now.
  - `med` Notable — interesting but secondary; would matter only to some teams.
  - `low` Context — recaps, prior-year teases now confirmed, science/research items, background.
  Document the mapping in the legend pill, same as for code reviews — but use the labels above, not "Critical/High/Quality/Polish".

When the user comes back and asks to cut cards (very common — "remove #3 and #4"), it's a signal you over-included infra/finance/marketing. Patch them out, decrement the count in the hero stats grid, and consider whether the cuts indicate a missing card type (e.g. "they cut my TPU card and asked about pricing → add a pricing-vs-previous-gen card").

### Card numbering after removal

When asked to remove cards, the user has two preferences and you should ask once if it's ambiguous:

1. **Preserve numbering** (replace #3's body with the new content, keep #4 as a new card, leave #5+ as-is) — keeps the conversation diff small but creates gaps if you later remove #4 too.
2. **Renumber down** — cleaner final artifact but every subsequent card title changes.

If the user removes-and-replaces in one breath ("remove 3 and 4 and add X"), do option 1 by default (replace #3 with X, delete #4, leave #5+ alone), and mention renumbering as an offer at the end. Cheap to do later, expensive to undo if you renumber without asking.

## Readability iteration workflow (when user says "make it more readable")

When the user complains about an existing report being hard to read, or asks for a typography / readability / visual quality upgrade to the template, **don't guess and patch blindly**. The workflow that works:

1. **Diagnose against the current template first.** Read the relevant CSS — body font-size, line-height, letter-spacing, container max-width, color tokens. Many "looks ugly" complaints are caused by 3-4 specific defaults that are easy to identify if you list them out.
2. **Parallel web_search across orthogonal axes** rather than one big query. Good axes for typography work: (a) general typography best practices for the current year, (b) dark-mode-specific research, (c) information density vs whitespace, (d) design-audit / dashboard UI patterns. Each axis surfaces different sources. Cap each at 5–6 results.
3. **Build a "findings vs current template" table** mapping each research finding to a specific line/rule in the template that currently violates it. This is the single most useful artifact — turns vague "make it nicer" into a checklist of N concrete changes with sources.
4. **Group findings into 2–4 named bundles** (e.g. "Dark-mode readability", "Type system", "Polish") and use `clarify` with multi-choice. Each bundle is independently shippable. Let the user pick the scope — they often want the biggest-impact bundle only, not the kitchen sink. Reference: `references/readability-research-2026.md` for the actual condensed findings from the May 2026 session.
5. **Apply patches surgically** using `patch` not `write_file` — the template is long and most changes are 5–20 lines. Group related changes into one patch each (palette tokens together, typography rules together, etc.) so the diff stays reviewable.
6. **Verify with the vision loop**: render a smoke-test report at `/tmp/<name>_smoke.html` with all placeholders filled, `browser_navigate file://...`, then `browser_vision` with a numbered list of specific questions ("is body text comfortable?", "do stats align?", "does TL;DR stand out?"). Iterate once based on the critique. Stop at the second pass — diminishing returns kick in fast, and vision will keep finding micro-nits indefinitely.

   **Forcing a specific color mode for QA screenshots.** The headless browser follows ONE OS appearance setting (usually dark), so `browser_vision` only ever sees that mode — even though `@media (prefers-color-scheme: …)` is what real users hit. To QA the *other* mode, generate a throwaway copy with the media query rewritten, then screenshot that:
   - **Force LIGHT** (when the browser defaults dark): neutralize the dark block so it never matches —
     `html.replace("@media (prefers-color-scheme: dark)", "@media (prefers-color-scheme: dark) and (max-width: 1px)")` → write to `/tmp/<name>_smoke_light.html`.
   - **Force DARK** (when the browser defaults light, or to pin dark regardless): make the dark block always apply —
     `html.replace("@media (prefers-color-scheme: dark)", "@media all")` → write to `/tmp/<name>_smoke_dark.html`. This works because the dark `:root` block sits *after* the base `:root` in source order, so `@media all` wins the cascade.
   QA BOTH modes for any theme that ships a light-and-dark palette — light-mode contrast bugs (secondary grays failing WCAG AA on a gray/cream paper) and dark-mode bugs (hairline borders too faint, leaning on accent rails for card separation) are independent and each only shows up in its own mode. Never edit the real template's media queries to force a mode — only the throwaway `/tmp` copy.
7. **Document new tokens in SKILL.md immediately.** When you add CSS variables (`--body-size`, `--prose-measure`, etc.), update the Typography reference section in the same patch sequence. Next session needs to know they exist.

Research synthesis from this session is preserved in `references/readability-research-2026.md` — load it before re-running similar searches; it has the dark-mode halation fix, prose measure rationale, Stripe/Linear craft markers, and the specific tokens that worked.

## Files

- `templates/report.html` — DEFAULT soft-gray editorial skeleton (serif headlines, terracotta accent, 🌗 light/dark toggle) with placeholder content; copy and adapt.
- `templates/report-indigo.html` — deep-indigo engineering variant (dark-first, gradient hero, drop-shadowed cards). Same placeholders/JS as the default; swap when the user wants the indigo/engineering look.
- `references/building-theme-variants.md` — recipe for mirroring an external design system (browse + vision → distill signature moves → additive variant → QA both modes via the force-light trick → fix predictable light-paper contrast failures). Read before any "make it look like X" / new-palette request.
- `references/theme-toggle-snippets.md` — copy-pasteable light/dark toggle (button + `t` shortcut, dual dark-token blocks, `--toc-bg`, anti-FOUC head script, persistence JS) and the `browser_console` QA recipe. Read before adding a manual theme switcher to any variant.
- `references/readability-research-2026.md` — condensed typography/dark-mode research from May 2026, mapped to the template's CSS tokens. Read before re-doing readability work.
- `references/plan-pivot-pattern.md` — mid-conversation architecture pivot recipe.
- `references/strip-done-items-pattern.md` — forward-only handoff after a phase ships.
- `references/inline-svg-architecture-diagrams.md` — palette-matched diagram snippets.
