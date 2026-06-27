# Stakent — Crypto Staking Dashboard (Build Prompt)

Build a pixel-faithful recreation of the "Stakent" staking dashboard described below. This is a **dark-theme, data-dense crypto staking analytics dashboard**. Prioritize matching the layout structure, spacing, and visual hierarchy. Use placeholder/sample data exactly as specified so the result looks like the reference.

---

## 1. Tech Stack

- **React + Vite** (or Next.js App Router if you prefer)
- **Tailwind CSS** for styling
- **lucide-react** for icons
- **recharts** for the line/area charts and timeline sparkline
- No backend — all data is hardcoded sample data
- Single-page dashboard, no routing needed

---

## 2. Design Tokens

### Colors
```
--bg-app:        #0A0A0F   /* app background, near-black with slight cool tint */
--bg-surface:    #121218   /* cards, sidebar panels */
--bg-surface-2:  #16161E   /* nested cards / metric tiles */
--bg-elevated:   #1C1C26   /* hover / active states, dropdown chips */
--border:        #232330   /* hairline borders, 1px, low contrast */
--border-soft:   rgba(255,255,255,0.06)

--text-primary:  #F4F4F6   /* headings, big numbers */
--text-secondary:#9A9AA8   /* labels, subtitles */
--text-muted:    #5C5C6B   /* faded/disabled items */

--accent:        #8B5CF6   /* primary violet — buttons, active nav, highlights */
--accent-soft:   #A78BFA
--accent-glow:   rgba(139,92,246,0.35)

--positive:      #4ADE80   /* green — gains, up arrows */
--negative:      #F87171   /* red — losses, down arrows */

/* Asset brand accents (for token icon chips) */
--eth:    #627EEA
--bnb:    #F0B90B
--matic:  #8247E5
--avax:   #E84142
--sol:    #14F195
```

### Gradient (used on the "Liquid Staking Portfolio" promo card)
```
background: linear-gradient(150deg, #2A1B5E 0%, #4C2A8C 45%, #6D3FB5 100%);
/* with a subtle radial purple glow in the top-right corner and faint diagonal light streaks */
```

### Typography
- Font: a clean geometric/neo-grotesque sans (e.g. **Inter**, **Geist**, or **Satoshi**)
- Big metric numbers: ~40–56px, weight 600–700, tight letter-spacing
- Section titles ("Top Staking Assets"): ~28px, weight 600
- Body/labels: 13–14px
- Micro-labels (e.g. "Reward Rate"): 11–12px, secondary color

### Shape & Spacing
- Card radius: **16px** (rounded-2xl); small chips/buttons: **9999px** (pill) or 10px
- Card padding: 20–24px
- Generous gaps between cards: 16–20px
- 1px borders everywhere, very low contrast (`--border`)
- Subtle shadows only; rely on background contrast rather than heavy shadows

---

## 3. Overall Layout

```
┌───────────────────────────────────────────────────────────────┐
│  (optional fake browser chrome bar — see §9, can be omitted)    │
├──────────────┬────────────────────────────────────────────────┤
│              │  TOP BAR (user, deposit, search, settings, bell)│
│   SIDEBAR    ├────────────────────────────────────────────────┤
│   (~260px)   │  MAIN CONTENT (scrollable)                      │
│              │   • Top Staking Assets row (3 cards + promo)    │
│              │   • Your Active Stakings panel                  │
│              │   • Metrics tab row + 4 metric tiles            │
└──────────────┴────────────────────────────────────────────────┘
```

- Sidebar is fixed-width (~260px), full height, `--bg-surface`.
- Main area has comfortable horizontal padding (~28px) and vertical scroll.
- The whole app sits on `--bg-app`.

---

## 4. Sidebar (left, top → bottom)

1. **Brand**: monogram logo tile (violet) + `Stakent ®` (bold) with subtitle `Top Staking Assets` (muted). A small up/down chevron on the right.

2. **Segmented toggle** (pill container, `--bg-elevated`):
   - `Staking` (active — filled lighter) | `Stablecoin` (inactive)

3. **Primary nav** (icon + label rows, ~44px tall, rounded when active):
   - `Dashboard` — **active** (subtle violet-tinted background + left accent), icon: layout/grid
   - `Assets` — icon: coins
   - `Staking Providers` — icon: server/stack
   - `Staking Calculator` — icon: calculator
   - `Data API` — icon: database, with a small ↗ external-link glyph after the label
   - `Liquid Staking` — with a small **`Beta`** pill badge (violet outline)
   - `Active Staking` — with a count badge **`6`** (violet pill) and an up-chevron (expanded)

4. **Active Staking sub-list** (indented, smaller rows; each = round token icon + two lines):
   - `Asset Ethereum` · `Amount $7,699.00`
   - `Asset Avalanche` · `Amount $1,340.00`
   - `Asset Polygon (Matic)` · `Amount $540.00`
   - `Asset Solana` · `Amount $980.00` — rendered **faded/muted** (`--text-muted`), as if disabled

5. **Bottom promo card** (pinned near bottom, `--bg-surface-2`, rounded):
   - Lightning bolt icon + **`Activate Super`** (bold) + subtitle `Unlock all features on Stakent`

---

## 5. Top Bar (header)

Left → right:
- **User chip**: round avatar, `Ryan Crawford` (bold) with `@Bryan997` and a small **`PRO`** badge; a dropdown chevron.
- **`Deposit`** button (pill, subtle filled, with a small lock 🔒 icon).
- *(spacer)*
- **Search** input (pill, `--bg-surface`, placeholder `Search...`, magnifier icon on the right).
- **`Settings`** button (pill with a small grid/sliders icon).
- **Notification bell** with a small **`2`** count badge.

---

## 6. Section A — "Top Staking Assets"

### Header row
- Title **`Top Staking Assets`** (large).
- Below/beside it: `Recommended coins for 24 hours` + an info ⓘ icon + a **`3 Assets`** pill.
- Right side: three dropdown chips: **`24H ▾`**, **`Proof of Stake ▾`**, **`Desc ▾`**.

### Three asset cards (equal width, in a row)
Each card (`--bg-surface`, rounded-2xl, padding 20px) contains:
- Top: round token icon chip (brand color) + small label `Proof of Stake` (muted) + bold token name. A small ↗ button in the top-right corner.
- Mid: micro-label `Reward Rate`, then a **big percentage** number.
- A pill showing the 24h change with a colored dot + arrow (green up / red down).
- Bottom: a **smooth area/line chart** (sparkline-style, gradient fill fading to transparent) with a labeled point callout (e.g. `+$2,956`). The chart line color matches the trend (violet/blue for up, red for down).

**Card data:**

| Card | Token | Reward Rate | 24h change | Callout | Trend color |
|------|-------|-------------|-----------|---------|-------------|
| 1 | Ethereum (ETH) | **13.62%** | ▲ 6.25% (green) | +$2,956 | violet/blue |
| 2 | BNB Chain | **12.72%** | ▲ 5.67% (green) | +$2,009 | violet/blue |
| 3 | Polygon (Matic) | **6.29%** | ▼ 1.89% (red) | −$0,987 | red |

### Promo card (right of the three, taller / spanning, gradient background §2)
- Top: `Stakent` brand mark + a **`New`** pill (top-right).
- Heading: **`Liquid Staking Portfolio`**.
- Body: `An all-in-one portfolio that helps you make smarter investments into Ethereum Liquid Staking`.
- Two stacked buttons:
  - **`Connect with Wallet`** (solid light/white-ish button with a small wallet icon)
  - **`Enter a Wallet Address`** (subtle/glassy outlined button with a lock icon)

---

## 7. Section B — "Your active stakings" panel

One wide card (`--bg-surface`, rounded-2xl). Internal layout = left detail block + right "Investment Period" block.

### Panel header
- Title **`Your active stakings`** (left).
- Right: a small icon toolbar — line-chart, ⊕ add, ⟳ refresh, ☰ filter.

### Left block
- A pill: `Last Update – 45 minutes ago` + small clock icon.
- Big heading **`Stake Avalanche (AVAX)`** with the red AVAX logo chip; beside it two small link/share icon buttons and a **`View Profile ↗`** button.
- Micro-label `Current Reward Balance, AVAX`.
- **Huge number `31.39686`** (this is the hero metric of the panel).
- Two buttons below: **`Upgrade`** (violet filled) and **`Unstake`** (subtle outlined).

### Right block — "Investment Period" (its own nested card, `--bg-surface-2`)
- Title `Investment Period` + a **`6 Month`** pill (top-right).
- Sub-label `Contribution Period (Month)`.
- A horizontal **range slider / timeline** with vertical tick bars (like an audio waveform), a draggable handle, and a floating **`4 Month`** tooltip above the handle plus a small pause ⏸ marker.

---

## 8. Section C — Metrics tabs + tiles

### Tab/selector row (4 columns, each a labeled dropdown header)
Each shows a **title** + a muted **subtitle**, with a small up/down chevron on the right:
- `Momentum` · `Growth dynamics`
- `General` · `Overview`
- `Risk` · `Risk assessment`
- `Reward` · `Expected profit`

### Four metric tiles (row, `--bg-surface-2`, rounded)
Each tile: a label, a small **`24H`** chip (top-right), and a big value with a colored sub-change.

| Tile | Label | Value | Sub |
|------|-------|-------|-----|
| 1 | Staked Tokens Trend | **−0.82%** | (red tint) |
| 2 | Price | **$41.99** | −1.09% ↓ (red) |
| 3 | Staking Ratio | **60.6%** | — |
| 4 | Reward Rate | mini bar chart | `2.23%` (24H Ago) / `1.46%` (48H Ago) |

> Tile 4 is a small two-bar comparison with a faint sparkline/track rather than a single number.

---

## 9. Optional: Fake browser chrome

The reference is shown inside a macOS-style browser mockup (traffic-light dots, back/forward arrows, an address bar reading `stakent.com`, tab/window icons). **This is presentation chrome, not part of the app** — include it only if you want the screenshot look; otherwise render the dashboard full-bleed.

---

## 10. Build Notes / Acceptance Criteria

- **Dark, low-contrast, premium feel.** Backgrounds are near-black; borders are barely visible; the only saturated color is the violet accent (and red/green for deltas). Don't over-use the accent — it's for the active nav item, primary buttons, badges, and the promo gradient only.
- **Big numbers dominate.** Reward rates, the `31.39686` balance, and metric values should be the largest type on screen.
- **Charts are decorative sparklines**, not full axis charts — no gridlines, smooth curves, gradient fills fading to transparent, optional single annotated point.
- Make it **responsive-ish**: the three asset cards + promo can wrap on narrow widths, but optimize for a wide (~1280px+) desktop layout.
- Use **mock/hardcoded data** matching all values above so it visually matches the reference.
- Components to break out: `Sidebar`, `TopBar`, `AssetCard`, `PromoCard`, `ActiveStakingPanel`, `InvestmentPeriodSlider`, `MetricTabs`, `MetricTile`.

Deliver a working dashboard I can run with `npm install && npm run dev`.
