# Plan-pivot pattern: "change of plans" without losing the prior work

When a multi-turn design/deployment plan reaches v1, the user often asks a
clarifying question that triggers a real architectural change — e.g. "why
can't we do X locally instead of deploying to Y?" — and then locks in the
simpler path. The temptation is to `write_file` a fresh report from scratch
and walk away. Don't. The prior approach still has value as the future-prod
reference, and the report's job is to record both the chosen path AND the
considered-but-shelved one.

## The pivot recipe

1. **Rewrite the hero** — new TL;DR sentence that names what changed in plain
   words ("drop Agent Engine; run ADK locally and point the toolset at the
   gateway URL"). Update the stat counts (phases dropped from 5 → 3, runtime
   cost $0, etc.). Update the status chip ("Status: scaffolded, GATEWAY_URL
   not set" not "Status: scaffolded, not deployed").

2. **Redraw the architecture diagram, don't patch it.** A pivot usually
   removes whole components (Agent Engine box, staging bucket arrow) and
   adds new boundaries (Laptop boundary). Patching the SVG element-by-
   element produces visual nonsense. Rewrite the `<svg>` block. Keep the
   palette, marker definitions, and legend identical for visual continuity
   between report versions.

3. **Renumber phases from 1, don't preserve old numbers.** Phases are the
   work-to-do checklist, not a historical log. The reader executes them
   top-down; gaps confuse.

4. **Add a "Dropped from plan" section** at the bottom (TOC anchor
   `#dropped`). One `low`-severity card per shelved piece. The card body
   should answer two questions in 2-3 sentences each: "what would that path
   have added" and "what it would have cost." This is the artifact that
   prevents future-you from re-asking "wait, did we consider X?" — yes, and
   here's why we shelved it.

5. **Mark shelved files in the Artifacts table** with a `low` badge labeled
   `Shelved` (not `Deleted` — the files stay on disk so a future agent can
   re-activate them). The Purpose column for each shelved file should say
   "**No longer part of the plan** — kept on disk as reference for [the
   future scenario where you'd want it]."

6. **Keep the original baseline file too** if it still works in isolation.
   In the NEO RAG pivot the original `example_gateway_agent.py` (registry-
   direct, bypasses gateway) was kept and labeled "Unchanged" because it
   serves as the comparison baseline for "does the gateway route actually
   change anything." Don't auto-delete the baseline just because the new
   path supersedes it.

## What NOT to do on a pivot

- Don't delete the shelved files or the old architecture SVG without saving
  them somewhere. The user will sometimes pivot back two turns later
  ("actually let's do the Agent Engine path after all"), and reconstructing
  is expensive.
- Don't bury the pivot in a single "Note: we changed approach" line at the
  top. The pivot IS the story; restructure to tell it.
- Don't keep stale stats in the hero (e.g. "5 phases" when there are now 3).
  Re-read the hero block after every pivot, not just the section you
  changed. Hero drift is the #1 leftover artifact.
- Don't keep a stale "Caveats" section from the old approach. A pivot
  usually retires some caveats (the SDK kwarg risk goes away if you're not
  calling that SDK anymore) and introduces new ones (gateway traversal
  becomes voluntary on a laptop). Rewrite the caveats section in full.

## Honest-limit caveat (critical-severity)

A pivot to a simpler approach almost always trades away some property the
original had. Name it explicitly as a `crit`-severity card titled "Honest
limit" or similar. In the NEO RAG case: "Gateway traversal is voluntary on
a laptop — nothing forces local code to route through the gateway." This
is not a problem-to-fix card, it's a fact-of-life card. Without it, the
reader assumes the simpler path is strictly better than the shelved one;
it isn't, it's a trade.

## Numbers that should change on every pivot

Audit these mechanically — they're easy to miss when restructuring:

- Hero stats grid (every number)
- Reading time (auto-computed, ignore)
- Footer subtitle ("X phases", "Y findings", project name if scope changed)
- TOC anchor list (added/removed sections)
- Status meta-chip in the hero meta-row
