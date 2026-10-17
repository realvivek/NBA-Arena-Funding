# Site proposal: Who Paid for the NBA's Arenas

Status: approved Oct. 17, 2026 and built; see section 8 for what changed while building it. Figures are from the ledger as of Oct. 16, 2026 (branch `update-2026-10`), in 2026 dollars unless noted, and will be read from the data at build time, not typed into the copy.

The site is a long-form data story on the home page followed by reference pages that hold the full record. It keeps the sourcing rules in `CLAUDE.md`: every number in the copy comes from a content or data file whose entries cite sources tagged by origin (government, court, team or league, independent), the build fails on an unsourced number, and a fact-check ledger lists every number with its source. Charts are SVG drawn at build time, each with its own phone layout. It deploys on Render.

## 1. The story

**Working headline:** Taxpayers Are Now Paying to Rebuild the NBA's Arenas

**Deck:** Since 2014, public money to renovate or buy existing NBA arenas has been nearly three times the public money in new ones. Another $1 billion is pending, and 11 leases end by 2036.

The story leads with the strongest finding, which is also the most current: the public money has moved from building arenas to rebuilding them. Since 2014, cities, counties and states have committed $2.90B to renovate or buy existing arenas, against $1.03B in the three arenas that opened in that time (Sacramento, Detroit, Milwaukee) (`totals.txt`, section J). Three arenas built mainly with private money (Salt Lake City, Washington, Portland) now carry $1.73B of later public commitments, $573M of it pending.

Sections, in reading order. Each names the chart that carries it (section 3 lists them all).

1. **The rebuild.** The lead and chart 1. The 2024-26 deals in one paragraph: Salt Lake City's 0.5% sales tax ($525M to a privately owned arena), DC's purchase and renovation ($515M), Orlando ($226M), Houston ($95M from the state), Memphis ($550M, mostly pending), Portland ($573M pending).
2. **The whole bill.** Public money in the 30 current arenas is $9.30B of $27.18B spent on them (34.2%). With property-tax exemptions and taxes diverted to arena debt it is at least $11.06B. Ten arenas hold 62.8% of the public money; the four costliest buildings were built mostly with private money. Chart 2 and chart 3.
3. **Built privately, rebuilt publicly.** Salt Lake City, Washington and Portland, told through their own documents: the 1991, 1997 and 1995 private builds, then the public takeovers. Chart 4.
4. **Who pays.** Residents' taxes (general funds, sales taxes, tax capture, sin taxes, lease-revenue bonds) supplied 44.9% of public capital; visitor taxes on hotels, car rentals and food 41.2%. Chart 5. Per household, the largest commitments run from $9,099 in Salt Lake City (an upper bound, since non-residents pay part of the sales tax) to $4,174 in Oklahoma City and $2,293 in Washington. Chart 6.
5. **Money that never shows up as a check.** Madison Square Garden's exemption since 1982 (about $947M), Barclays Center's PILOT bonds ($738M), the United Center's 1989 valuation formula ($75M for 2002-2016 alone), DC's exemption to 2050 ($312.7M, future) and the federal cost of tax-exempt arena bonds ($1.91B, paid by all U.S. taxpayers). Chart 7, with the United Center's bills against what they would have been, year by year.
6. **Payments that keep coming.** Yearly cash to teams or arena operators: Indianapolis, Miami (county and state), New Orleans, Minneapolis, Oklahoma City. $759M documented for seven teams; probably understated elsewhere. Chart 8.
7. **Threats as deadlines.** Of 20 documented owner or league relocation threats since 1994, 13 were followed by public money in the same city, a median 11.2 months later. Deals after a threat were no larger and no more one-sided than deals without one (median 64% vs 76% public; p = 0.52). Chart 9.
8. **The next round.** Eleven leases end by 2036, starting with Memphis and New Orleans in 2029. Each has a pending or expected ask. Chart 10.
9. **What the research says.** One paragraph: the 2023 review of more than 130 studies finds very limited local economic effects.
10. **How this was made.** Method in plain language (CPI-U, the three labels, what is counted and what is not), what could not be reached, and links to the fact-check ledger and sources.

The page ends with one card per reference page.

## 2. Reference pages

Each page opens with a head that states its finding, a deck, the date of the latest data, and its opening chart; the full record follows; notes on the data close the page.

| Page | Headline (finding) | Holds |
| --- | --- | --- |
| `arenas/` | Orlando's Kia Center Holds the Most Public Money of Any NBA Arena | All 30 arenas and the 10 project rows: a sortable table, then one section per arena (anchor `#orl` and so on) with construction, renovations, purchases, ongoing payments, tax breaks, lease, labels and sources |
| `taxes/` | Visitor Taxes Paid 41% of Public Arena Capital | The seven channels (dedicated sales tax, visitor taxes, tax increment, players' income tax, operating payments, tax-exempt bonds, land and property tax), each with its documented series: Salt Lake City's monthly arena tax, Wisconsin district taxes, Detroit's tax increment, Louisiana's payments to the Pelicans, Indianapolis's payments to the Pacers |
| `tax-breaks/` | Madison Square Garden's Exemption Has Cost New York About $947 Million | Every break, counted or not, with its method: MSG, Barclays PILOT bonds and the rail yard, the United Center formula (full yearly table), DC to 2050, Denver's seat tax (memo), Boston's Chapter 121A payments, the federal bond subsidy |
| `threats/` | 13 of 20 Relocation Threats Were Followed by Public Money | The 49-episode threat ledger, classification rules, the comparison and its sensitivity runs, and the cities that kept paying after a team left |
| `leases/` | Eleven NBA Leases End by 2036 | Lease terms and exit penalties, upgrade ("first-class") clauses, and a dated tracker of the pending deals (Memphis, Portland, San Antonio, Oklahoma City, Dallas, Philadelphia) |
| `households/` | In Salt Lake City, the Arena Deal Comes to $9,099 per Household | Per-household figures for every large deal, the paying jurisdictions and their weights, and the residents-versus-visitors split |
| `sources/` | The count of sources, computed at build ("N Sources, From City Audits to Court Records") | Every source grouped by origin tag with publisher, date and the date last checked |
| `fact-check/` | Every Number on This Site and Where It Comes From | The generated fact-check ledger, the corrections log and the list of sites that could not be reached |

Optional, for your decision: `explore/`, the full ledger queryable in the browser with DuckDB-WASM. It is the most hands-on piece of the new tooling, but it downloads several megabytes, so it would load only on that page and only on request.

## 3. Charts

All charts are drawn at build time as SVG, at a desktop width and a phone width, and each phone version has its own layout rather than a scaled-down copy. Every chart has a title that states its finding, a source line with citation links, notes, and a "Show the data" table.

| # | Chart | Finding it shows | Form, desktop / phone |
| --- | --- | --- | --- |
| 1 | Public money by year, building versus rebuilding (1990-2026, with pending deals outlined) | Since 2014 the money has gone mostly to existing arenas: $2.90B against $1.03B | Stacked columns by year / horizontal bars by five-year period |
| 2 | Every arena, public and private money | 34% public overall; 10 arenas hold 63% of the public money; the four costliest buildings are mostly private | 30 horizontal stacked bars sorted by public money, public share labeled, tax breaks hatched / same, with team abbreviations and a two-line label |
| 3 | Where the public money went | The highest public shares are in mid-size and Sun Belt markets; the largest coastal arenas are mostly private | Map of the U.S. and Toronto (conic equal-area), circles sized by public money and shaded by public share / the map with numbered circles above a ranked list |
| 4 | Built privately, rebuilt publicly | Salt Lake City, Washington and Portland: $1.73B of public commitments after private builds | Three small multiples of cumulative money over time, private then public / stacked vertically |
| 5 | Who pays | Residents 44.9%, visitors 41.2%, the rest in kind or not documented | One bar of public capital divided by funding stream, grouped by who mostly pays / the same bar turned vertical with labels beside it |
| 6 | Per household | Salt Lake City $9,099, Oklahoma City $4,174, Washington $2,293 | Dot plot by paying jurisdiction, upper bounds marked / ranked list with inline bars |
| 7 | What the United Center paid, and what it would have paid | The 1989 formula kept the bill at $0.9M-$4.7M a year when the normal bill was about $4.6M-$6.5M | Two lines, 2002-2024, with the formula's end marked / same, fewer ticks |
| 8 | Payments that keep coming | Indianapolis has paid the Pacers $13M-$18M a year since 2015; Miami's arena manager gets county and state money every year | Small multiples of yearly payments by team / stacked vertically |
| 9 | From threat to public money | 13 of 20 threats were followed by public money, a median 11.2 months later; threat deals were not more one-sided | Dumbbells from the threat date to the approval, plus two dot strips comparing deal size and public share / dumbbells only, with the comparison as a short table |
| 10 | The lease clock | 11 leases end by 2036; exit penalties range from $20M to over $1B | Timeline 2026-2055 with exit penalties and pending deals / vertical timeline |

Reference pages reuse these charts where they overlap and add their own: monthly Salt Lake City arena tax, Wisconsin district taxes by source, the threat ledger timeline, and the United Center's assessed values.

## 4. Data pipeline

```
scripts/ (existing, Python 3.11)        ledger_inputs.py -> build_ledger.py, write_totals.py
                                        threat build.py -> compare.py
                                        writes data/ledger/*, data/threats/*
pipeline/ (new, Python 3.11)
  datapackage.json                      Frictionless table schemas for every CSV in data/: types, required
                                        fields, allowed labels (a, b, c and combinations), a source on every row
  sources.yaml                          the bibliography: id, origin (government | court | team_or_league |
                                        independent), title, publisher, URL, document date, last checked
  models.py                             Pydantic models for Source and Figure (value, unit, dollar basis,
                                        label, source ids, note)
  stats.sql                             DuckDB views over the CSVs that compute every number the story
                                        and the reference pages use
  build.py                              runs the views, validates each result, and writes
                                        site/src/data/stats.json, site/src/data/figures/*.json and
                                        docs/fact-check.md
site/ (new, Astro 7 + Svelte 5)
  content collections                   story and page heads (MDX and YAML), figures, sources, each with a
                                        schema; a figure's sources must exist in the sources collection
  number tokens                         prose writes {{reno_vs_build.existing}}; a remark plugin swaps in the
                                        formatted value and a citation link
  charts                                Svelte components using LayerCake and d3 scales, rendered to SVG at
                                        build, each with a desktop and a phone layout
```

What fails the build:

- `frictionless validate` on any CSV that breaks its schema, including a row without a source URL or label.
- `pipeline/build.py` on a URL in the data with no entry in `sources.yaml`, a source without an origin tag or date, or a figure that fails its Pydantic model.
- The Astro build on an unknown number token, an unknown source id, or any numeral in the prose that did not come from a token (a short allowlist file covers things such as section numbers).
- A style check on em dashes and on the copy rules already in `CLAUDE.md`.

Tests and checks before every push: the Python pipeline's tests, `astro check`, a production build, and Playwright tests for the page without JavaScript, a 360-pixel phone with no sideways scrolling, chart text no smaller than 11 pixels on a phone, heading order, and no requests to other sites. A viewport sweep and screenshots at desktop and phone widths, read by eye.

## 5. Tools

New to this project, chosen to replace the hand-written pieces of the earlier site rather than copy them:

| Tool | Version | Role |
| --- | --- | --- |
| Astro | 7.4 | Static site generator; content collections with schemas and source references |
| Svelte | 5.57 | Chart components, rendered on the server; interactive pieces only where needed |
| LayerCake | 11.0 | Chart layout for Svelte (scales, layers, responsive frames) |
| d3-scale, d3-shape, d3-geo, us-atlas | current | Scales, line and area paths, the map projection |
| DuckDB | 1.5 | SQL over the ledger CSVs for every computed number |
| Pydantic | 2.14 | Validation of sources and figures in the pipeline |
| Frictionless | 5.21 | Table schemas and validation for every CSV in `data/` |
| Playwright | 1.64 | Page tests and the viewport sweep |
| DuckDB-WASM | 1.33 | Only if the optional `explore/` page is approved |

## 6. Deploy

A Render static site from `main`, defined in `render.yaml`. To keep Render's build simple, the Python pipeline's outputs (`stats.json`, the figure data, `docs/fact-check.md`) are committed, and a GitHub Actions job reruns the pipeline and fails if they differ from what is committed. Render then only runs `npm ci && npm run build` in `site/` and publishes `site/dist`. Work stays on a feature branch until approved; only `main` deploys.

## 7. Decisions for you

1. **CPI base.** September 2026 CPI-U is now published. Keep the January-August 2026 base (331.655), which the ledger has used since Oct. 11, or move to January-September, which raises every 2026-dollar figure by about 0.2%.
2. **Denver's seat tax.** Keep it as a memo (about $96M, from one press figure that could not be opened) or count it in the expanded total.
3. **Memphis's yearly subsidy.** Keep the $4.95M-$6.3M a year (press only, possibly overlapping debt service) or drop it until a primary record is found.
4. **The `explore/` page.** Build it or not.
5. **Headline.** "Taxpayers Are Now Paying to Rebuild the NBA's Arenas", or a version you prefer.
6. **Where it lives.** A `site/` folder in this repository (recommended, so the data and the site cannot drift apart) or a separate repository.
7. **Render service name and domain.**

## 8. Changes made while building (Oct. 17, 2026)

Decisions in section 7 were taken as recommended: the January-August 2026 CPI base, Denver's seat tax as a memo, Memphis's yearly subsidy kept and flagged (c), no `explore/` page, the working headline, the site in `site/`, and the Render service name `nba-arena-funding`. Building the pipeline found problems in the ledger that changed parts of the plan; each is logged in `notes/verification.md`.

- **Built privately, rebuilt publicly.** "Built mainly with private money" is now a rule, public money under half of the construction cost, which covers 22 arenas, not the hand list of 14. The section and chart 4 now cover the seven of them later bought or rebuilt with public money ($2.71B, $573M pending), not three.
- **Chart 1** shows completed and binding money only, by year; pending deals and new arenas outside the 30 are in its notes, so the earlier years stay readable.
- **Chart 2** shows the eight costliest arenas were all built mainly with private money (the proposal said four).
- **Chart 6** adds the shares of nested governments (a Portland household pays city, county and state shares).
- **The federal cost of tax-exempt bonds** is $1.91B in 2026 dollars; the $1.32B in the proposal was a sum of issue-year present values.
- **The sources page** headline names team filings rather than court records: no source in the bibliography is a court record.
- **Chart text** is set at 13 units in both layouts so it stays at 11px or more down to a 320px screen; chart titles are text inside each figure rather than headings, which keeps the heading order clean.
