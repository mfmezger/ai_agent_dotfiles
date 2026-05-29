# Strip-done-items pattern: trimming a report to forward-only after work ships

A report often goes through three phases across a multi-turn conversation:

1. **v1 — Analysis.** Findings, recommendations, options, severity-coded
   cards. The agent presents what's wrong / what to do.
2. **v2 — Decision/status.** User picks options. Cards get "✅ Decided"
   pills. New sections appear ("Implementation status", "Open questions").
   The report grows.
3. **v3 — Forward-only handoff.** Work has been executed. The report's
   audience shifts from "decision-makers reviewing options" to "the next
   agent or human who needs to know what's pending." User asks to "remove
   everything that has been done" or "strip out what's shipped."

Phase 3 is where most reports decay if not handled: stale recommendations
linger, "fix X" cards reference fixes already applied, the hero stats lie
about open questions vs. resolved ones. Result: a future reader can't tell
what's still actionable.

## The strip recipe

When the user signals "remove what's done":

1. **Identify the done sections wholesale.** Look for sections that exist
   only as a record of past work — typically the original findings sections,
   the "what stays" / "what to cut" inventories, the implementation-status
   recap, and any sprint-completed block in the order-of-attack. Don't
   strip card-by-card; rip whole `<section>` blocks. Half-empty sections
   look broken.

2. **Fold forward-looking content out of the done sections BEFORE deleting.**
   Often a "GCP API audit" findings section contains both backward-looking
   ("here's what's wrong with the current code") and forward-looking ("here's
   the correct shape PR 2 should use"). Pull the forward-looking parts into
   a new section (e.g. "PR 2 guidance") so they survive the cull.

3. **Rewrite the hero TL;DR in plain past-tense state.** Not "the branch is
   a walking-skeleton violation" (analysis) and not "Sprint 0 is now landed
   with three open questions" (status recap). Aim for: "v1 ships X. Y lands
   in PR 2. N open questions remain." The TL;DR is now the briefing for
   "what state is this in, what's next."

4. **Hero stats grid → forward-looking metrics only.** Drop "findings", "API
   issues", "speculative cuts". Keep "diff size now", "tests passing",
   "open questions remaining", "pending PRs". The dashboard shifts from
   "review status" to "shipping status."

5. **Order of attack → Roadmap.** The original section is full of done
   sprints. Replace the whole `<section id="order">` body with a slim
   future-PR list. Each item is one paragraph: what + which open questions
   it depends on. No re-litigating Sprint 0.

6. **TOC re-derives from sections that survive.** Easy to forget — stale
   TOC links to deleted sections produce 404-on-click. After stripping,
   `grep -nE '<section id=|href="#'` and reconcile.

7. **Sizing/metrics table is the one historical artifact worth keeping.**
   A before/after diff table is the single piece of "look what changed"
   that belongs in a forward-looking report — it's the proof that the work
   actually happened, useful for the PR description and for future-you
   wondering "was the trim real or just talked about?"

8. **Open questions section is the centerpiece of v3.** If it didn't exist
   before, add it. If it did, this is now the longest section. Order by
   what blocks the next PR.

## Audit the hero after every strip

Same as the plan-pivot pattern: stat counts drift. After cutting 5 sections,
re-read the hero. The stat that said "6 findings" needs to say something
else. If you can't articulate what each hero stat means in 5 words, drop it.

## What NOT to do

- **Don't keep a "Sprint 0 — Done ✅" section as a trophy.** The user asked
  to remove what's done; a section whose entire purpose is to celebrate
  done work IS what's done. The diff-sizing table covers proof-of-work.

- **Don't keep cards labeled "Decided"** if the decision is now embedded in
  the shipped code. Their original purpose was to record the moment of
  decision; once code is live, that moment is in git, not the report.

- **Don't shrink by hiding via `<details>` collapse.** Collapsed-but-present
  is still in the DOM, still in `Ctrl-F` results, still confuses readers
  who expand "everything." Delete, don't hide.

- **Don't lose the citation links to external sources.** When you fold the
  forward-looking content out of the audit cards, carry the `<div class="src">`
  links with it. They're the proof the recommendations are grounded.

- **Don't restructure as `write_file` if you can avoid it.** Use multiple
  targeted `patch` calls per section deleted/replaced. The user edits these
  files between turns; an external edit warning means you should re-read,
  not blow away their changes.

## Numbers that should change on every strip

Audit these mechanically — same list as the pivot pattern, with strip-
specific additions:

- Hero TL;DR (rewrite, don't patch a word at a time)
- Hero stats grid (every number; replace metric names too)
- TOC anchor list (every removed section)
- Status meta-chip ("Status: Sprint 0 done" → "Status: PR 1 ready for review")
- Section count anywhere referenced in body prose
- Reading-time estimate is auto-computed; ignore

## When a strip is the wrong move

If the user is going to keep iterating ("I might revisit Sprint 0 details
next week"), a strip is destructive. Offer the alternative: **fold the
done content into a single collapsed `<details>` block at the bottom of
the report titled "v1 history (archived)".** This preserves the artifact
without polluting the active scanning surface. Don't decide unilaterally;
ask once when there's signal the user might want the history back.

## Pairing with plan-pivot-pattern.md

The pivot pattern handles *changing direction mid-plan*. The strip pattern
handles *removing the past after a phase completes*. They can compose: a
project might pivot at v2 and strip at v4. The pivot pattern is about
making the SHELVED path discoverable (the "Dropped from plan" section);
the strip pattern is about making the EXECUTED past invisible. Different
sections, different rules.
