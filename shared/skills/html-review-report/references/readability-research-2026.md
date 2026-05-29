# Readability research — May 2026

Condensed findings from a web_search pass across four orthogonal axes (general typography, dark mode, density vs whitespace, design audit). Use this before re-searching the same territory — most of the conclusions are stable for the next 12–18 months.

## 1. Body type defaults that changed since 2022

| Property | Old default | 2025–26 baseline | Source |
|---|---|---|---|
| Body font-size | 14–16px | **16–18px** (17px is the sweet spot for content-heavy dark UI) | Frontend Tools 2025, DeveloperUX, Webmatik |
| Line-height (light) | 1.5 | 1.5–1.6 | All six sources agree |
| Line-height (dark) | 1.5 | **1.65–1.75** — dark wants more air | Mantlr 2026 dark-mode guide |
| Line length | unbounded | **45–75ch** (66 is often cited ideal); use `ch` unit | WCAG 2.1, The Crit, Webmatik |
| Body weight (dark) | 400 | 380–400 (or use variable-font grade axis) | CHI 2023 grade study |
| Body weight (light) | 400 | 420–450 (slightly heavier for crispness) | Mantlr |
| Heading weight (dark) | 700 | **600** — bold reads heavier on dark | Mantlr |

`rem` units (not `px`) on font-size are mandatory — `html { font-size: 16px }` overrides user accessibility settings. The "62.5% trick" (root = 10px) is equally bad for the same reason.

## 2. Dark-mode-specific halation fixes

Light text on dark backgrounds suffers from **halation** — letters visually "spread" and "vibrate", making them appear thinner and heavier at the same time. Pure white on pure black is the worst case. Three fixes that stack:

1. **Drop text contrast away from pure white.** `#e6ecff` → `#d4ddf5` keeps AAA contrast against `#0b1020` but kills the buzz. Mantlr recommends `#e5e5e5 on #171717` as a generic reference.
2. **Add 0.01–0.02em letter-spacing on body** (not headings). Counters the optical spread. Invisible to conscious perception.
3. **Lift line-height ~0.1** above light-mode baseline. 1.7 instead of 1.55–1.6 reduces the "heavy" feel of long dark sessions.

CHI 2023 paper ("How bold can we be?") tested the variable-font **grade** axis: increasing grade in dark mode does NOT improve word-pair reading. The fix is reducing contrast and increasing leading, not making letters heavier. ACM eye-tracking study (2025) showed dark mode has **lower perceived workload (NASA-TLX)** than light despite slightly slower reading — users prefer it for sustained dashboard work.

## 3. Information density vs whitespace (Stripe/Linear pattern)

"Density" ≠ "clutter". Pravin Kumar 2026 and Pixeldarts both converge on:

- Tight whitespace **inside** content blocks (paragraph spacing 0.75em, list-item 0.3em).
- Generous whitespace **between** content blocks (section padding 64px is the right baseline, not 40px).
- Even more generous at section boundaries.

This nested-whitespace pattern is what separates dense-but-readable Stripe/Linear pages from dense-but-cluttered amateur dashboards. The eye gets a "rest" at every boundary.

Linear/Stripe craft markers that compound (Mantlr Stripe/Linear teardown):
- **Tabular numerals** on every number that appears in a table or stat tile (`font-variant-numeric: tabular-nums lining-nums`). Numbers visibly drift without it.
- **Designed focus rings** — every interactive element. `*:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }`. Single biggest "designed vs defaulted" signal.
- **All six microstates** designed per interactive element: default, hover, focus, active, disabled, loading. Missing any = unfinished.
- **Restraint in color** — monochrome neutrals + one brand accent + meaningful severity colors. No rainbow palettes.

## 4. Modern CSS wins (Baseline 2024–25)

| Property | What it does | When to use |
|---|---|---|
| `text-wrap: pretty` | Eliminates orphans, bad rag, poor hyphenation across whole paragraphs (WebKit Sept 2025) | Body `<p>` everywhere |
| `text-wrap: balance` | Prevents headings breaking with a one-word last line | All headings |
| `clamp(min, fluid, max)` on font-size | Fluid type with no media queries | All headings; consider for body on print pages |
| `font-variant-numeric: tabular-nums lining-nums` | Column-aligned digits, technical-style figures | Tables, stat tiles, any numeric column |
| `font-variant-numeric: oldstyle-nums` | Book-style figures with descenders | Long-form editorial only — NOT technical reports |
| Variable fonts (Inter, Roboto Flex) | Single file, all weights, grade axis available | Replace static `400/600/700` font files |

## 5. WCAG 2.1 numeric requirements (when in doubt)

- Body contrast 4.5:1 minimum; 7:1 for AAA. Large text (18pt+ or 14pt+ bold) drops to 3:1 / 4.5:1.
- Line-height ≥ 1.5× font-size (testable spacing override criterion).
- Paragraph spacing ≥ 2× font-size.
- Letter-spacing override ≥ 0.12× font-size.
- Word-spacing override ≥ 0.16× font-size.
- Content must reflow at 320px viewport (no horizontal scroll).
- Text must scale to 200% without loss of content.

## 6. Mapping research → template tokens (May 2026 result)

This is what got applied to `templates/report.html` after the research synthesis:

```
--body-size: 17px              [Frontend Tools, DeveloperUX, Webmatik]
--body-line: 1.7 (dark) / 1.6 (light)  [Mantlr 2026]
--body-track: 0.012em (dark) / 0 (light)  [Mantlr halation fix]
--body-weight: 400 (dark) / 430 (light)  [CHI 2023, Mantlr]
--heading-weight: 600 (dark) / 650 (light)  [Mantlr]
--prose-measure: 68ch          [WCAG, The Crit — middle of 45-75 window]
--text: #d4ddf5 (was #e6ecff)  [Mantlr — kill halation]

h1 font-size: clamp(1.75rem, 1.3rem + 2vw, 2.75rem)  [fluid, no breakpoints]
p { text-wrap: pretty }        [WebKit Sept 2025]
h1-h4 { text-wrap: balance }   [Baseline 2024]
section padding: 64px (was 40px)  [Stripe/Linear density gradient]
*:focus-visible: 2px accent outline  [Linear/Stripe craft marker]
font-variant-numeric on body: lining-nums proportional-nums
font-variant-numeric on stats/meta/tables: tabular-nums lining-nums
Stat tiles: text-align: center, uppercase labels with 0.06em tracking
TL;DR: 1.12rem, 4px border, 12% indigo/violet tint background
Fonts: Inter Variable + JetBrains Mono Variable via Google Fonts, system fallback
```

## 7. What NOT to do (anti-findings that came up)

- **Don't use `oldstyle-nums` on technical reports.** The descender figures (3, 4, 5, 7, 9 dip below baseline) look elegant in novels but read awkwardly with file paths, line numbers, and "found N issues" prose. Lining figures every time for code reviews.
- **Don't invert light mode for dark mode.** Reduce saturation, raise the background off pure black, lower text off pure white, pick accent colors specifically for dark (warmer, less saturated). Mantlr and the CHI study both emphasize this.
- **Don't push contrast too low chasing comfort.** AAA (7:1) is still the floor for body text. The `#d4ddf5 on #0b1020` choice tested at ~12:1 — well above AAA, just below the "buzzing" threshold.
- **Don't add gridlines, borders, or chrome trying to "make it look professional."** Restraint is the premium signal. The severity stripe is the only colored chrome that earns its place.
- **Don't fix nits past iteration 2 of the vision loop.** Vision AI will always find another micro-imperfection. Two passes hits ~7.5/10 craft score; chasing 9/10 in a third pass typically produces overcorrection that the user then asks you to revert.

## 8. Re-search triggers

Reload these sources only when:
- The user reports the template now feels dated (likely 2027+).
- A new CSS property becomes Baseline that materially affects readability (`text-wrap: avoid-short-last-lines` is the next likely one — currently spec only).
- The user moves to a non-screen medium (e.g. e-ink, projector) where the dark-mode optimizations stop applying.

For routine "make it more readable" requests, this file plus the SKILL.md Typography section should be enough — no new web_searches needed.
