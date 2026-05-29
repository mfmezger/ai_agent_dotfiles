# Persistent light/dark theme toggle — reusable snippets

A click-to-switch theme button that defaults to the OS appearance, lets the user
override, and **remembers the choice across reloads** (localStorage). Pure-CSS
checkbox hacks can't persist between page loads — this needs ~12 lines of JS, and
that persistence is the whole point. Shipped in `templates/report.html` (the default theme);
drop the same pieces into any variant (including the indigo default) to add a toggle.

The mechanism: light is the base `:root`; dark tokens live in TWO selectors so both
"OS auto-detect" and "manual force" paths work. Setting `data-theme` on `<html>`
overrides the `@media` auto-detection. Verified in-browser May 2026 — auto-detect,
manual flip, and reload-persistence all confirmed via `browser_console`.

## 1. Dark tokens in BOTH the auto and forced selectors

Light stays in the base `:root`. Put the dark token values in two places — the
`@media` block (guarded so a manual `light` choice wins) and an explicit
`data-theme="dark"` block. Keep the two dark blocks byte-identical.

```css
:root {
  /* LIGHT base — your light palette here */
  --bg:#e8e7e3; /* …all light tokens… */
  --toc-bg:rgba(232,231,227,0.85);   /* sticky-nav backdrop, theme-following */
}
/* OS auto-detect — but NOT if the user manually forced light */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:#1a1a18; /* …all dark tokens… */
    --toc-bg:rgba(26,26,24,0.85);
  }
}
/* Manual force (button / saved choice) — overrides @media */
:root[data-theme="dark"] {
  --bg:#1a1a18; /* …same dark tokens… */
  --toc-bg:rgba(26,26,24,0.85);
}
```

Why both: `:root[data-theme="dark"]` forces dark even on a light-OS machine, and
`:root:not([data-theme="light"])` lets a light-OS user who clicked "dark" keep it
while still defaulting correctly for everyone who never clicks.

## 2. `--toc-bg` token (kill the hardcoded nav backdrop)

The sticky TOC backdrop must follow the theme. Drive it from a token instead of a
hardcoded rgba + a separate `@media` override:

```css
nav.toc{position:sticky;top:0;z-index:10;background:var(--toc-bg);
  border-bottom:1px solid var(--border);padding:10px 0;backdrop-filter:blur(10px)}
```

Define `--toc-bg` in all three token blocks above. Delete any
`@media (prefers-color-scheme: dark){nav.toc{background:…}}` rule — the token
handles it now. (Any other hardcoded surface — code blocks, etc. — gets the same
treatment if it needs to switch.)

## 3. Anti-FOUC inline script in `<head>`

The toggle JS lives at the bottom of `<body>`, so on a dark-OS machine opening a
saved-light report there's a dark→light flash before the script runs. Re-apply the
saved choice before first paint with a tiny inline script high in `<head>`
(right after `<title>`):

```html
<!-- Anti-FOUC: apply saved theme choice before first paint (overrides OS auto-detect). -->
<script>try{var t=localStorage.getItem('report-theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(e){}</script>
```

## 4. The toggle button (reuse existing TOC button style)

Add to the sticky TOC bar, before Expand/Collapse. No new CSS — reuse `.toc-btn`:

```html
<button class="toc-btn" id="btn-theme" title="Toggle light / dark">🌗 Theme</button>
```

## 5. Toggle JS (inside the existing IIFE)

```js
// ===== Theme toggle (light / dark) =====
// Precedence: saved choice → OS preference → light default. data-theme overrides @media.
const root = document.documentElement;
const THEME_KEY = 'report-theme';
function currentTheme() {
  if (root.dataset.theme) return root.dataset.theme;
  return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
function setTheme(t) {
  root.dataset.theme = t;
  try { localStorage.setItem(THEME_KEY, t); } catch (e) {}
}
try {                                  // re-apply saved choice (also done in <head> for FOUC)
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'light' || saved === 'dark') root.dataset.theme = saved;
} catch (e) {}
const themeBtn = document.getElementById('btn-theme');
if (themeBtn) themeBtn.addEventListener('click',
  () => setTheme(currentTheme() === 'dark' ? 'light' : 'dark'));
```

Add a `t` keyboard shortcut in the existing keydown handler, and a help-overlay row:

```js
else if (e.key === 't') setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
```
```html
<dt>t</dt><dd>Toggle light / dark theme</dd>
```

## QA (verified pattern)

`browser_navigate file://…` then drive `browser_console` with `expression` to read
state — don't rely on `browser_click` against a snapshot ref (it can hit a stale ref
and silently no-op; calling `document.getElementById('btn-theme').click()` directly
is reliable):

```js
// initial: no data-theme, resolves from OS
JSON.stringify({dataTheme: document.documentElement.dataset.theme||null,
  osPrefersDark: matchMedia('(prefers-color-scheme: dark)').matches,
  bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()})
// flip + assert persistence
document.getElementById('btn-theme').click();
JSON.stringify({dataTheme: document.documentElement.dataset.theme,
  bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),
  saved: localStorage.getItem('report-theme')})
```

Then set `localStorage.setItem('report-theme','light')`, `browser_navigate` to the
same file again, and confirm `data-theme` comes back as `light` after reload.

Note: once a toggle ships, forcing a mode for vision QA no longer needs the
media-query rewrite trick — just `localStorage.setItem('report-theme', …)` + reload,
or set `<html data-theme="…">`.
