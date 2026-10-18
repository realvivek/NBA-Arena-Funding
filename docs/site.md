# The site

A short data story on the home page, the investigation behind it (a short page and the full report) and eight reference pages, built as a static site from the ledgers in
`data/`. Every number on it is computed from the data at build time, every number links to its entry in the
fact-check ledger, and every chart is drawn at build time as SVG, in a wide and a narrow layout.

## How it is built

```
data/*.csv  ->  pipeline/build.py  ->  site/src/generated/*.json, docs/fact-check.md  ->  astro build  ->  site/dist
```

### Pipeline (`pipeline/`, Python 3.11)

| File | Role |
| --- | --- |
| `datapackage.py`, `schemas.yaml` | Write `data/datapackage.json`: a Frictionless schema for every CSV, with required fields, allowed values, patterns and keys for the files the site reads. |
| `registry.py`, `sources.yaml`, `sources_extra.yaml`, `domains.yaml` | The bibliography. One entry per cited URL with an id, title, publisher, origin (government, court, team_or_league or independent), document date and the date its figures were last checked. `registry.py check` fails if any URL in the data has no entry or an entry is no longer cited. `sources_extra.yaml` holds sources cited by id rather than by URL (the CPI series, the Census table, the research and this project's own ledgers). |
| `views.sql` | DuckDB views over the CSVs. |
| `stats.yaml` | Every number the copy uses: a SQL query (or, rarely, a hand-entered value the build confirms against a data file), a unit, a label and sources. |
| `datasets.yaml` | The rows behind every chart and table, with each row's sources. |
| `models.py`, `fmt.py` | Pydantic models for sources, stats and datasets; how numbers are written (`$9.30 billion`, `$9.30B`, `34.2 percent`, `seven`). |
| `build.py` | Validates the tables, checks the sources, runs the stats and datasets, and writes `site/src/generated/` and `docs/fact-check.md`. `--check` fails when the committed outputs are stale. |
| `tests/` | Reconcile the SQL with the ledger scripts' own totals, and test the formats and the citation parser. |

### Site (`site/`, Astro 7, Svelte 5, LayerCake, d3, Fontsource)

| Path | Role |
| --- | --- |
| `src/content/story.yaml`, `pages.yaml`, `figures.yaml` | All copy: the story, the page heads (with their key figures, `tiles`), the investigation page and the reference pages' notes, and every chart's title, subtitle and notes. Numbers are tokens (`{{core_public}}`, `{{core_public:short}}`, `:title`, `:cap`). A story section or a page is a list of blocks: paragraphs, figures, scroll steps for a figure (`scrolly`, with one paragraph per step), key figures (`stats`: a token in large type over a short label), cards (`cards`: a place or a finding, an optional figure and a sentence or two), the funds with stakes in teams (`funds`: a sentence each, with their stakes drawn from the `investors` dataset), a sentence that ends on a number set large (`reveal`), a pull quote, the ranked list of teams (`teams`) and subheads; `more` links a chapter to the reference pages. |
| `src/content.config.ts` | Content collections with schemas; paragraph sources are references to the `sources` collection. |
| `src/lib/copy.ts` | The copy check and the renderer. The build fails on a typed dollar figure, percentage, number word or numeral (other than a year or a date), a number in a block with no source, an unknown token or source, an em or en dash, a tool name, or marketing language. Tokens render as links to the fact-check entry. |
| `src/components/charts/*.svelte` | The charts, rendered on the server, with LayerCake or as plain SVG. Each draws a wide layout (680 units, shown from 640px up) and a narrow one (340 units); chart text is at least 13 units, so it stays at 11px or more at every width. Label widths are estimated from Libre Franklin's advance widths (`src/lib/chart.ts`), within about 10 percent of the rendered text. |
| `src/components/Figure.astro`, `Chart.astro` | The chart frame: title, subtitle, legend, both layouts, a gray source line, and one toggle, "Notes and data", with the notes, the documents and a table of every value. A figure with steps is laid out as a scroll-driven graphic: the chart holds its place while the steps pass beside it (from 64rem) or over it (as cards, on phones). |
| `src/lib/prepare.ts`, `src/components/Blocks.astro`, `Tiles.astro`, `Cards.astro`, `Funds.astro`, `SourceLine.astro` | Render the blocks in reading order, so the numbered source list follows the order a reader meets the sources; in quiet mode (the story and the investigation page) the text carries no citation marks and `SourceLine` names a chapter's or section's sources at its end. |
| `src/components/Teams.astro` | Every team, ranked: a row per team with the public money in its arena and the team's value, which opens to its record (the arena, the public money and the taxes that paid it, the lease, what the owners paid and the team is worth, and what the public gets back), drawn at build time from the same datasets as the charts. A small script adds sort buttons and shows the first ten teams until the reader asks for all of them. |
| `src/pages/` | The story, the investigation (`who-is-behind/`: key figures, the funds, the owners chart and cards, from `pages.yaml`; the full report at `who-is-behind/report/`, rendered from `report/who-is-behind-nba-arena-deals.md`, which the pipeline copies into `src/generated/`) and the reference pages: arenas, taxes, tax breaks, threats, leases, households, sources and fact check. |
| `tests/site.spec.ts` | Playwright: every page loads with no errors and no requests to other sites, works without JavaScript, fits a 360px phone with no sideways scrolling, keeps chart text at 11px or more, has one h1 and no skipped heading levels, and links every number to an existing fact-check entry. The lead graphic is checked at a desktop and a phone width (each step sets its state, including after a jump, and every row carries its name and amount), the investigation page's figures, funds and link to the full report are checked, and the team list is checked with and without JavaScript. |

## Design

The home page is a short data story, about four minutes to read, set the way a newspaper sets one. Its design
follows patterns found in ten New York Times data stories from 2025 and 2026 (among them "What It Would Look Like
to Pay W.N.B.A. Players What They Deserve", "How Trump Is Getting Richer in Office", "What the Iran War Is Costing
You" and "U.S. Debt Is on Pace to Set a Record High"): the chart carries the finding, its title states it and notes
on the chart say it again with an arrow to the mark; one accent color against gray; money drawn as money; a serif
for the narrative with the key numbers in bold, sometimes a sentence that ends on a number set large; and almost no
interface, only a gray source line under each chart.

A kicker, a serif headline that carries the total, a deck and a dateline open it. The lead graphic is the public's
bill for the arenas as a stack of bills, each worth $100 million, filled from the bottom up as the reader scrolls:
building the arenas in blue, then renovations, purchases, yearly payments and tax breaks in orange, each starting a
new row, with its amount printed beside the stack in large serif type and a leader to its bills, and brackets for
the two shares. Bills the reader has not reached show as outlines. Each chapter is a serif heading, short
paragraphs and its charts, and ends with one gray line naming its sources (each publisher once, with every
document in a fold) and plain links to the reference pages. Paragraphs carry no citation marks; the fact-check
page lists every paragraph with its numbers and sources. The investigation page (`/who-is-behind/`) is set the same
way, a source line under each section; the full text is one link away. The reference pages keep a citation toggle
on each paragraph.

Type is Newsreader for headlines and text and Libre Franklin for charts, captions and the interface, both served
from the site. On the story and the investigation page everything shares one left edge in a 46rem column, and
paragraphs stop at 37.5rem; the lead graphic breaks out to 72rem. Every script is optional: without JavaScript the
lead graphic rests in its last state and its steps read as paragraphs, the team list shows every team in order of
public money with every record still opening, and tooltips are not shown.

Charts follow one palette, validated for color-vision deficiency in light and dark mode: blue for public money,
orange for the second series (existing arenas, visitor taxes, threats, team values, money after building), gray for
private money, and a one-hue blue ramp for shares on the map. Notes and a table of every value sit in one toggle
under each chart. Tooltips are added by a small script and are optional; every value is also in the chart's data
table.

## Deploy

Every push to `main` deploys the site. Neither host runs Python: the pipeline's outputs are committed, and
`.github/workflows/checks.yml` rebuilds the ledgers, reruns the pipeline with `--check`, checks every link in the
built site (`site/scripts/check-links.mjs`) and runs every test on each push.

- GitHub Pages: `.github/workflows/pages.yml` builds the site under the repository's Pages path and deploys it to
  https://realvivek.github.io/NBA-Arena-Funding/. The path comes from the Pages settings at build time
  (`BASE_PATH` and `SITE_URL`), and every link inside the site goes through `sitePath` in `src/lib/paths.ts`, so
  the same code serves from a domain's root or from a subpath. The workflow fails if any built link leaves the
  path or leads nowhere.
- Render: `.github/workflows/deploy-render.yml` creates the `nba-arena-funding` static site on the first run, with
  the settings in `render.yaml` (`npm ci && npm run build` in `site/`, publishing `site/dist`, with a content
  security policy that allows nothing from other sites), then deploys and waits for it to go live. It needs the
  `RENDER_API_KEY` repository secret and does nothing without it. `render.yaml` also works as a Blueprint.
