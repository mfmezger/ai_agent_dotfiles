# Building a new theme variant (mirroring an external design system)

When the user asks "make it look like <Anthropic / Stripe / Linear / vendor X>" or "give it a <color> palette", do NOT freehand-guess the look. Mirror the real thing, then ship it additively. Recipe proven in the May 2026 Anthropic-gray session.

## 1. Ground in the real design BEFORE writing CSS
- `browser_navigate` to the reference site.
- `browser_vision` with a SPECIFIC question asking for: exact background hex (cream? off-white? gray?), serif-vs-sans for display vs body, border/shadow treatment, button shape, accent-color usage, card styling, overall mood. Vague "describe this page" wastes the call — enumerate what you need to replicate.
- The accessibility snapshot gives structure, not aesthetics. You MUST use vision for the look.

## 2. Distill the signature moves
Every design system has ~5 load-bearing traits. For Anthropic they were: warm cream bg, **serif display headlines (Fraunces/Tiempos-like) over sans body** (the #1 tell), flat cards (fill not shadow), hairline borders, single terracotta accent used sparingly, dark pill buttons. Pull the equivalent shortlist for whatever you're mirroring — getting the headline font family right matters more than getting every hex perfect.

## 3. Build ADDITIVELY by default
- New file `templates/report-<name>.html` — copy the default skeleton, swap ONLY the `<style>` block's `:root` tokens + font stack + the heading `font-family`. Body markup, placeholders, severity classes, and the whole JS engine stay identical so it's a drop-in and themes are interchangeable by swapping `<style>`.
- Don't retire the existing default unless the user explicitly says "replace". Confirm replace-vs-variant via `clarify` if it's a real decision; if no answer, default to additive (reversible).
- Express colors as CSS variables, never inline hex in rules — the whole point is one-place retheming.

## 4. Light-FIRST variants flip the dark/light scaffolding
The default template is dark-first (`:root` = dark, `@media (prefers-color-scheme: light)` overrides). An Anthropic-style variant is light-first: put the light "paper" palette in `:root` and a `@media (prefers-color-scheme: dark)` block for the dark fallback. Make the dark fallback match the brand (warm charcoal for Anthropic, NOT the indigo of the default).

## 5. QA BOTH modes — and force the one the browser isn't in
Headless browser usually defaults to dark, so it renders your dark fallback. To screenshot the OTHER mode without OS toggling, neutralize the unwanted media query in a temp copy:
```python
# force LIGHT for screenshot when browser is dark:
light = html.replace("@media (prefers-color-scheme: dark)",
                     "@media (prefers-color-scheme: dark) and (max-width: 1px)")
```
Write `/tmp/<name>_light.html`, navigate, vision. (Mirror the trick to force dark from a light-default browser.) For a light-first variant the LIGHT surface is the primary deliverable — QA it hardest.

## 6. Predictable light-paper failures to pre-empt
Vision will almost always flag these on a light/gray surface; fix before declaring done:
- **Secondary grays too light** — subtitle, section-intro, `.tldr-line`, meta-row, stat labels drift below WCAG AA on gray paper. Darken `--muted` (in this skill: `#6c6c64` → `#595951` passed).
- **Gold/yellow severity washes out** — the quality/`--med` color is always the legibility floor on light bg. Darken it (`#9a7d2e` → `#8a6d1f` passed). Red/terracotta/green hold up fine.
- Once darkened for AA, leave them — don't let a later "make it lighter/airier" request lift them back under the floor.

## 7. Stop at the second vision pass
First pass finds the structural misses (wrong bg tone, washed accent). Fix, regenerate, second pass to confirm. Don't loop a third time — vision finds infinite micro-nits (emoji-vs-serif clash, pill recessiveness) that are taste, not defects. Mention them as optional nudges and ship.

## 8. Document the variant in SKILL.md immediately
Add a "Theme variants" section listing each skeleton + when to pick it, and a Files-list pointer. Note which tokens are the signature moves and which grays are AA-floored (so a future session doesn't undo them).
