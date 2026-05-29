# Inline SVG architecture diagrams — reusable patterns

When the report needs an architecture/deployment diagram, embed it inline
as `<svg>` inside a `<div class="card">` rather than calling a separate
diagram skill. Keeps the report self-contained. Reusable conventions below
come from the NEO RAG → Agent Gateway sequence of plans.

## Standard `<defs>` block (copy verbatim)

```html
<svg viewBox="0 0 960 480" style="width:100%;height:auto;min-width:880px"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1f2a52" stroke-width="0.5"/>
    </pattern>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#7aa2ff"/>
    </marker>
    <marker id="arrTeal" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#5fd1a3"/>
    </marker>
    <marker id="arrRed" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#ff5d6c"/>
    </marker>
  </defs>
  <rect width="960" height="480" fill="#0d1430"/>
  <rect width="960" height="480" fill="url(#grid)"/>
  <!-- content here -->
</svg>
```

Three colored markers cover the common semantic roles. If you need a
fourth (e.g. purple for state writes), add `<marker id="arrPurple">` with
fill `#b388ff`.

## Wrap the SVG in a card with horizontal-scroll fallback

```html
<div class="card" style="padding:8px;overflow-x:auto">
  <svg viewBox="0 0 960 480"
       style="width:100%;height:auto;min-width:880px" ...>
    ...
  </svg>
</div>
```

`min-width:880px` prevents the SVG from squishing illegibly on narrow
screens; the parent `overflow-x:auto` makes it scroll instead. Without
both, mobile/PDF renders break.

## Trust boundaries

Trust/network/account boundaries are dashed rectangles with no fill, in
the palette color matching the boundary's role:

- Google Cloud / GCP project: `stroke="#7aa2ff"` (accent blue)
- StackIT / on-prem / external SaaS: `stroke="#ffb454"` (high orange)
- Local laptop / developer machine: `stroke="#b388ff"` (accent purple)
- Customer / external caller side: `stroke="#5fd1a3"` (low teal)

Every boundary gets a small monospace label in the top-left in the same
color:

```html
<rect x="20" y="40" width="280" height="220" rx="10"
      fill="none" stroke="#b388ff" stroke-dasharray="8,4" stroke-width="1.2"/>
<text x="36" y="62" fill="#b388ff"
      font-family="JetBrains Mono,monospace"
      font-size="11" letter-spacing="2">LAPTOP · macOS · /Users/mezgerm</text>
```

Letter-spacing 2 + uppercase reads as "this is infrastructure metadata,
not a component name."

## Component box pattern

```html
<rect x="50" y="90" width="220" height="80" rx="8"
      fill="rgba(179,136,255,0.10)" stroke="#b388ff"/>
<text x="160" y="120" text-anchor="middle"
      fill="#e6ecff" font-size="13" font-weight="600">Component name</text>
<text x="160" y="138" text-anchor="middle"
      fill="#9aa6d4" font-size="11">subtitle / resource path</text>
<text x="160" y="154" text-anchor="middle"
      fill="#9aa6d4" font-size="10.5">extra detail line</text>
```

Three lines of text in a 60-80px tall box is the sweet spot. The fill is
the stroke color at 0.10 alpha — this gives a tinted but readable box
that doesn't compete with text.

Component fill semantics (re-use across diagrams for consistency):

- `rgba(122,162,255,0.10)` blue — API surfaces, read paths, caller endpoints
- `rgba(95,209,163,0.10)` teal — happy-path runtime / external service calls
- `rgba(179,136,255,0.10)` purple — state stores, registries, control plane
- `rgba(255,180,84,0.10)` orange — blob storage, external/3rd-party backends
- `rgba(255,93,108,0.10)` red — gateways, policy enforcement, failure-mode handlers

## Arrow conventions

- Solid + colored = happy path (use `markerEnd` matching the line color)
- Dashed (`stroke-dasharray="5,3"`) = secondary path: lookup, polling, audit
- Dashed-wider (`stroke-dasharray="8,4"`) reserved for trust boundaries

Arrows should have a short label centered above:

```html
<path d="M 270 150 L 368 150" stroke="#5fd1a3" stroke-width="2"
      fill="none" marker-end="url(#arrTeal)"/>
<text x="319" y="142" text-anchor="middle"
      fill="#5fd1a3" font-size="10">HTTPS + Bearer</text>
```

Label color = line color, font-size 10, positioned 8px above the line.

## Bottom-left legend

Required when there's more than one arrow color or boundary style. Drop a
small framed legend at the bottom-left:

```html
<g transform="translate(40,440)">
  <rect x="0" y="-14" width="560" height="34" rx="6"
        fill="rgba(255,255,255,0.03)" stroke="#2a3568"/>
  <line x1="14" y1="0" x2="44" y2="0" stroke="#5fd1a3" stroke-width="2"/>
  <text x="50" y="4" fill="#9aa6d4" font-size="10.5">MCP call (happy path)</text>
  <line x1="178" y1="0" x2="208" y2="0"
        stroke="#b388ff" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="214" y="4" fill="#9aa6d4" font-size="10.5">registry lookup</text>
  <line x1="326" y1="0" x2="356" y2="0"
        stroke="#ff5d6c" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="362" y="4" fill="#9aa6d4" font-size="10.5">verification / audit</text>
  <line x1="466" y1="0" x2="496" y2="0"
        stroke="#7aa2ff" stroke-dasharray="8,4"/>
  <text x="502" y="4" fill="#9aa6d4" font-size="10.5">trust boundary</text>
</g>
```

## Pitfalls

- **Don't reuse the architecture-diagram skill's slate-950 palette.** Its
  default colors clash with the report theme. Always use `#0d1430`
  background + this palette.
- **`<text>` doesn't wrap.** Plan label text to fit on one line or split
  into multiple `<text>` elements with explicit y-offsets.
- **viewBox aspect ratio drives final size.** 960×480 is a good default
  for landscape diagrams with a bottom legend; 960×520 if you have a top
  boundary label row plus a bottom legend (NEO RAG plan v1 used 960×520).
- **Inline SVG inflates the HTML.** A typical architecture diagram adds
  3-5 KB. Fine for a single diagram; if you need 3+ in one report,
  consider whether they should be separate `<details>` blocks.
- **`prefers-color-scheme: light` doesn't restyle inline SVG.** The
  diagram stays dark even in light-mode print. Usually acceptable for
  technical reports (looks like a code block), but flag it if the user
  asked for "professional/printable" output.
