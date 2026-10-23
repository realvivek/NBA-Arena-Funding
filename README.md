# Who Paid for the NBA's Arenas

A sourced funding ledger for all 30 current NBA arenas: how each was paid for, which taxes carry the debt, what households in the paying jurisdictions owe per head, and what owners got after threatening to move their teams.

The write-up is in [`report/who-paid-for-nba-arenas.md`](report/who-paid-for-nba-arenas.md), and the same findings are published as a data story with reference pages, built from this repository (`site/`, see [`docs/site.md`](docs/site.md)). Everything in both traces to a row in `data/`, and every row carries its source URL.

Figures are as of October 22, 2026, in 2026 dollars unless noted.

## Findings

| Measure | Value | Where it comes from |
| --- | --- | --- |
| Public money in the 30 current arenas | $9.59B of $27.46B total spending (34.9%) | `data/ledger/totals.txt`, section A |
| Construction / purchases / renovations / ongoing subsidies | $5.39B / $219M / $3.23B / $753M | same |
| Public money since 2014 to renovate or buy existing arenas vs. to build new ones | $3.02B vs. $1.99B (1.5 times; 1.3 counting Bexar County's voter-approved $311M for a new San Antonio arena): $1.08B in the four arenas with public money that opened since 2014 and $910M in Oklahoma City's arena under construction | section J |
| Public total with tax-break financing added | at least $11.56B (40.3%) | section E: Barclays PILOT bonds $738M, MSG exemption $1.16B (IBO's $946.7M for FY1984-2023 in 2023 dollars, converted, plus the Department of Finance's values for FY2024-2026), United Center valuation formula $73M (2002-2016) |
| Building's share of that total | 53%, counting Barclays Center's PILOT bonds, which paid for its construction; the other 47% came after the arenas opened | stats `construction_share`, `after_opening_share` |
| New public commitments outside the 30-arena total | $3.28B binding, approved or pending (Oklahoma City, Salt Lake City, San Antonio, Portland, Memphis, Houston) | sections A and F |
| Share of public money in the top 10 arenas | 62% | section C |
| Arenas built mainly with private money (public money under half of construction cost; Barclays Center's PILOT bonds count as public) | 20, with Indianapolis unresolved; six were later bought or rebuilt with public money, $2.35B ($573M pending) | section D |
| Public capital paid mostly by residents / visitors (hotel and car-rental taxes) / both (meal and ticket taxes, alone or pooled with hotel taxes) / other | 43.0% / 33.1% / 8.3% / 15.5% of $8.83B | section B |
| The same split before 2014 and since (items dated by the ledger's year rule) | Before 2014: residents 27.2%, visitors 42.2%, both 5.0%, other 25.6% of $4.74B. Since: residents 61.4%, visitors 22.7%, both 12.0%, other 3.9% of $4.10B; without Salt Lake City and Washington, residents 47.8% | stats `residents_share_before_2014` to `residents_share_since_2014_ex` |
| Public capital put or committed since 2014 that voters approved | $148M (3.6%): Oklahoma City's MAPS 4 sales tax (2019) and Bexar County's venue tax (extended 2008); the other 96% was approved by councils, legislatures and appointed boards | stats `voted_since_2014`, `unvoted_since_2014_share`; vote column in `threat_ledger.csv` |
| Share of income the tax behind residents' arena money takes from the poorest fifth of households, as a multiple of the share it takes from the richest 1% (ITEP, *Who Pays?*, 7th edition, statewide) | Utah's sales taxes 15 times (Salt Lake City); Minnesota's 9.0 (Minneapolis); Oklahoma's 7.5 (Oklahoma City); Ohio's alcohol and tobacco taxes 22 (Cleveland); the District of Columbia's taxes as a whole 0.42 (4.8% of income against 11.4%). 63% of residents' capital money came through taxes that take the larger share from the poorest | stats `itep_ut_sales_ratio` to `incid_regressive_share`; `data/who_pays/` |
| Bexar County's Proposition B (Nov. 4, 2025), precincts in fifths of equal households by estimated median household income | 52.1% yes in all; 58% in the fifth with the highest incomes ($110,800 and up), which cast 33% of the votes; 49.3% in the rest of the county; 48% in the lowest fifth, which cast 10% | stats `propb_yes_share` to `propb_top_income`; `data/who_pays/bexar_2025_prop_b_precincts.csv` |
| Public money per household, every arena with counted public money | 24 deals in 31 paying governments; the site's lookup covers 6,863 ZIP code areas; the federal bond cost comes to about $11 per U.S. household | `data/ledger/households.csv`, `data/who_pays/zip_jurisdictions.csv`, stat `fed_per_household` |
| Public money by team value (Forbes, October 2026) | the 10 least valuable teams' arenas $4.77B (49.7%, all 10 took money); the middle 10, $3.41B; the 10 most valuable, $1.41B (5 of 10; $3.38B with tax breaks). Rank correlation -0.60 | stats `value_bottom10_public` to `value_top10_with_breaks` |
| Renovations with public money since 2014 that cost more than their arena did to build (2026 dollars, CPI) | 4: Indianapolis, Phoenix, Salt Lake City, Washington; Salt Lake City's public money alone is 2.3 times the Delta Center's 1991 cost | stats `renovations_over_cost_n`, `uta_renovation_multiple` |
| Miami's documented payments to its arena operator, 1998-2026 | $335M, 4.5 times the county's land for the arena | stats `mia_ongoing`, `mia_ongoing_multiple` |
| Federal cost of tax-exempt arena bonds (present value at issue, 2026 dollars, not added) | $1.41B, $278M of it on five issues whose tax-exempt status is not confirmed | section E memo; `data/tax_mechanisms/nba_arena_bonds.csv`, `nba_arena_bond_federal_cost.csv` |
| Documented owner or league relocation threats since 1994 | 21 (20 without the 76ers' 2024 Camden talks, which rest on anonymous sources); 12 followed by same-city public money, 11 of them within 24 months (median 3.9 months); Portland's money is pending. The four teams that left went to cities with public money waiting (Memphis, New Orleans, Oklahoma City, Brooklyn) | `data/threats/comparison.txt` |
| Median deal after a threat vs without one | $308M, 64% public vs $247M, 78% public (2025 dollars); Mann-Whitney p = 0.95 and 0.46 | same |
| Average NBA team value, October 2026 (mean of Forbes's 30 team values) | $6.13B, 9.7 times the $634M average on the 2014 list (nominal) | `data/teams/team_values.csv`, `value_history.csv` |
| Median team value as a multiple of what its controlling owners paid (26 teams with a comparable price, 2026 dollars) | 6 times | `data/teams/team_values.csv` |
| Arenas of the 16 teams with a controlling owner from finance or a current fund stake | $4.92B, 51% of core public money (they are 53% of the teams); $2.44B (50%) of it counted after the current finance owner or fund arrived, mostly Salt Lake City, Washington, Detroit and Milwaukee | stats `finance_teams_public`, `finance_teams_share`, `finance_teams_after` |
| Public arena deals that give the public a share of a team sale | none of the 22 whose terms could be read (23 reviewed; Memphis's lease was not reached) | `data/teams/public_return.csv` |

The threat comparison finds no evidence that deals after a threat were larger or more one-sided. At the median the public paid 64% of deal costs after a threat and 78% without one. The samples are small (9 threat deals, 13 without), so this is descriptive, not a causal estimate. The waits are uneven: eight approvals came within seven months of a threat, four took more than a year.

## Layout

```
report/
  who-paid-for-nba-arenas.md     the report
  who-is-behind-nba-arena-deals.md  the investigation of who is behind the deals: funds and owners from finance, lobbying, studies, banks, federal money and remedies (summarized on the site at /who-is-behind/, in full at /who-is-behind/report/)
  charts/                        the two charts embedded in the report
data/
  ledger/                        arena_ledger.csv (30 arenas + 10 project rows, 96 columns), ledger_items.csv and ledger_buckets.csv (one row per item and funding stream), households.csv, totals.txt, _calc.json
  threats/                       threat_ledger.csv (50 episodes), left_behind.csv, comparison.txt
  authorities/                   lease terms and exit penalties, net public cost, Indianapolis CIB payments to the Pacers, verbatim quotes from audits and agendas
  tax_mechanisms/                arena bonds, federal cost of tax-exempt bonds, Louisiana stadium district payments, Indiana PSDA, Section 197 franchise amortization, player income-tax capture
  property_tax/                  United Center assessment history and taxes forgone under its 1989 valuation formula, Intuit Dome parcels, Opportunity Zone sites, illustrative forgone tax on public arenas
  labor_contract/                2023 CBA clauses on arena revenue, naming rights at public arenas, renovation cycles
  dedicated_taxes/               Indianapolis CIB taxes, Salt Lake City arena sales tax and district budget, Wisconsin Center District taxes
  votes_lobbying/                arena votes, host payments, federal lobbying by the NBA, NBPA and owners, MSG related-party items
  who_pays/                      ITEP's tax burden by income group, the tax line behind each arena's resident-paid money, Bexar County's 2025 arena vote by precinct with Census estimates, ZIP code areas in each paying government
  teams/                         team_values.csv (owners, prices paid for control, Forbes and Sportico values, deals since), value_history.csv (Forbes's average team value by year), public_return.csv (what each public arena deal returns); every row cites its documents
  inputs/                        CPI-U and CAD/USD series (FRED), household counts (Census ACS 2024, table B11001),
                                 arena locations for the site's map (Wikipedia), quoted research findings with their source
  datapackage.json               table schemas for every CSV (generated by pipeline/datapackage.py)
scripts/
  arena_ledger/                  ledger_inputs.py (hand-entered figures with labels and URLs), build_ledger.py, write_totals.py, report_charts.py
  arena_threats/                 build.py (hand-entered threat ledger), compare.py (threat vs no-threat comparison)
  who_pays/                      itep_extract.py, bexar_precincts.py, zip_jurisdictions.py (helpers that write data/who_pays/ from raw downloads)
notes/
  verification.md                checks against primary records, corrections made and sites that could not be reached
pipeline/                        the site's data build: schemas, source registry, DuckDB stats and datasets, tests
site/                            the data-story site (Astro and Svelte); its data is site/src/generated/, written by pipeline/build.py
docs/
  site.md                        how the site is built, tested and deployed
  site-proposal.md               the approved proposal for the site, with the changes made while building it
  fact-check.md                  every number the site computes, with its label, sources and query (generated)
render.yaml                      Render static-site blueprint (deployed by .github/workflows/deploy-render.yml)
```

Each folder under `data/` that was assembled from several documents has a `sources` file listing them.

## Rebuilding the ledgers

```
uv venv -p 3.11 .venv && uv pip install --python .venv/bin/python "scipy==1.17.*" "matplotlib==3.10.*"
.venv/bin/python scripts/arena_ledger/build_ledger.py     # writes data/ledger/arena_ledger.csv and _calc.json
.venv/bin/python scripts/arena_ledger/write_totals.py     # writes data/ledger/totals.txt
.venv/bin/python scripts/arena_threats/build.py           # writes data/threats/threat_ledger.csv and left_behind.csv
.venv/bin/python scripts/arena_threats/compare.py         # writes data/threats/comparison.txt (needs scipy)
.venv/bin/python scripts/arena_ledger/report_charts.py    # redraws report/charts/*.png (needs matplotlib)
```

Run from any directory; paths resolve from the script location. On Python 3.11 with scipy 1.17 the four data scripts reproduce the committed outputs byte for byte.

The helper scripts (`wiki_extract.py`, `wiki_fin.py`, `wx.py`, `g.py`, `pdftxt.py`, `pdf2txt.py`) pulled figures out of raw downloads: Wikipedia wikitext, audits and official statements. Raw downloads are not redistributed here. To rerun the helpers, put the files under `./raw` or set `RAW_DIR`. `pdftxt.py` needs PyMuPDF and `pdf2txt.py` needs pypdfium2.

The `scripts/who_pays/` helpers write `data/who_pays/` from the raw downloads listed in its `sources.csv`: `itep_extract.py` (needs openpyxl), `bexar_precincts.py` (PyMuPDF, pyshp, shapely and pyproj) and `zip_jurisdictions.py`, which reads `data/ledger/households.csv` and is rerun after `write_totals.py` whenever the paying governments change.

## Method

- **Scope.** The 30 arenas in use in the 2025-26 season. Ten more rows cover new or rebuilt arenas that are committed or pending.
- **Public money.** Construction contributions, public purchases of existing arenas, completed or binding renovation money, and documented ongoing cash subsidies. Debt service on counted bonds is not added, to avoid double counting. A public purchase counts as public money but not as new spending, because it reimburses a private builder.
- **Who repays.** Public financing that the team repays with its own rent or payments counts as private money: Atlanta's 1999 arena bonds, Detroit's 2014B bonds, the Cavaliers' $70M series in the 2017-19 renovation and the $12M of Orlando city cash repaid from Magic use payments. Public money repaid from public revenue counts as public, such as Los Angeles's $70M advance for Crypto.com Arena, repaid from an arena admissions fee and convention-center parking revenue. Houston's rent-supported debt is capped at $30.4M, but its size is not documented, so it is not netted.
- **Building and rebuilding.** Barclays Center's PILOT bonds paid for its construction and are repaid with the property tax the arena would owe. The ledger keeps them in the expanded total with the tax breaks; the site's bill counts them as building money, and so does the test of whether an arena was built mainly with private money (Barclays Center is 65% public counting them, 25% without). The arenas chart draws them inside Barclays Center's construction bar, with its private money net of them. Comparisons since 2014 count both sides the same way, completed or binding money with work under way at face value, so building money includes Oklahoma City's arena under construction.
- **Total spending.** The larger of the reported construction cost and public plus private construction, plus renovation totals and ongoing public payments.
- **Constant dollars.** BLS CPI-U, not seasonally adjusted (FRED CPIAUCNS), annual averages. The 2026 base is the January-August 2026 average (331.655); September 2026, published in October, is not included. Construction is deflated at the opening year, purchases at the transaction year, renovations at the mid-construction year (Toronto's 2023-25 work at 2024, Charlotte's 2024-25 work at 2025) and ongoing payments at each payment year. Property tax forgone is deflated at the year it would have been paid (Cook County bills tax year T in T+1). Money for work still under way is taken at face value. Three small items depart from the rule (about $1M to $8M in all): Salt Lake City's reimbursement of a 2017 renovation, paid through 2040 ($670,906 paid by FY2025), and Phoenix's renewal and replacement deposits from about FY2023 are counted at 2026 face value, and Charlotte's $6.0M of reserve contributions in 2014-2023 is deflated at 2014 with the rest of its 2014 upgrades. Canadian dollars convert at the year's average rate (FRED EXCAUS) before deflating.
- **Funding streams.** Each public capital dollar is assigned once, to its documented stream. In-kind land goes to "land". Infrastructure with no stated funding stream goes to "infrastructure". A stream the records do not name goes to "not split", even where one is likely (Charlotte's 2014 upgrades).
- **Ongoing payments.** Yearly public cash to the team or the arena's operator for running a public building: operating payments and reimbursements, operating costs the public owner pays for the team, operating-loss coverage, payments into team-controlled reserves, loan forgiveness and tax pass-throughs. Debt service on counted bonds is excluded.
- **Who pays.** These streams are treated as paid mostly by residents: general taxes, GO bonds and state grants; dedicated sales taxes; tax increment and tax capture; lease-revenue bonds; and sin taxes. Hotel and car-rental taxes are treated as paid mostly by visitors. Restaurant-meal and ticket taxes, alone or pooled with hotel taxes (Indianapolis's Capital Improvement Board, Milwaukee's Wisconsin Center District, Washington's arena ticket tax), are counted apart as shared by visitors and residents, because the records do not split the pools. The split is approximate in both directions: residents pay some hotel taxes, part of a hotel tax may fall on local owners and workers, and visitors pay some sales tax. No incidence study for these arenas was found.
- **Per household.** Public money divided by ACS 2024 one-year household counts for each paying jurisdiction, weighted by that jurisdiction's share of the funding, for every arena with counted public money (24). These figures are totals, not yearly costs. The site's ZIP lookup lists the paying governments a ZIP code area (Census 2020 ZCTA) lies in, by land area: at least 95% inside counts as inside, 5% to 95% as partly inside.
- **Who pays by income.** For each arena's resident-paid capital money, the matching line of ITEP's *Who Pays?* (7th edition: 2024 tax law at 2023 incomes, senior taxpayers left out) in that state: general sales taxes for dedicated sales taxes, other sales and excise taxes for alcohol and tobacco taxes, property taxes for tax increment, and all state and local taxes for general funds, lease-revenue bonds and Indiana's capture of state taxes (`data/who_pays/itep_tax_lines.csv`). The ratio divides the share of income the line takes from the lowest 20% by the share it takes from the top 1%. It describes how that kind of tax falls across the state, not the arena tax alone, and assumes a city's households pay like the state's.
- **Who voted.** Bexar County's official precinct report for Nov. 4, 2025, whose totals match its official summary, on the 776 precincts of the Texas Legislative Council's 2024 general-election file (the precincts the county used; it has since split 30 more). Each precinct's households and median household income come from the Census block groups it overlaps (ACS 2020-2024), spread by area; the median is approximated by the household-weighted mean of block-group medians. Precincts are ranked by that income and cut into fifths of equal households.
- **Threats.** An episode counts when the owner or the league made an explicit or implied threat. Explicit means naming another city, announcing a move, selling to a buyer who intended to move, or the league stating it would move or buy the team. Implied means talks with another city, "exploring options", invoking or holding a lease out clause, selling to an out-of-town buyer who made no commitment to keep the team, or offering the team with no limit on moving. Statements by public officials alone do not count. Money approved but not final (Portland's 2026 state bonds) is reported as pending, not as money that followed, and loans are left out. Classification rules, exclusions and sensitivity runs are in `data/threats/comparison.txt`.
- **Federal bond cost.** The present value at issue of the federal income tax lost on the bonds' interest, at a 28% marginal rate. For the seven NBA issues in Gayer, Drukker and Gold's data (Brookings, 2016) it is their published value, which follows each issue's redemption schedule (`gdg_pv3_revenue_loss_m` in `nba_arena_bonds.csv`). For later issues it is a level approximation, 30 years of interest on the full par at the issue year's Aaa yield, discounted at 3%; on the seven issues where both can be compared it ran 13.8% above their values, so the later issues are probably overstated. It counts only new money for the arenas: refundings and taxable issues are left out, Salt Lake City's 2025 issue counts the arena's $525M of $900M, and Indianapolis's 2021 issue its new money (about $254M). Bond amounts taken from their Table 3 are in 2014 dollars and are converted from 2014; the others from the year of issue (`fed_cost_par_m` and `par_dollars_year`).
- **Labels.** Every figure in `ledger_inputs.py` is labeled (a) computed, (b) primary document or (c) press/secondary. A few lease and return rows add u, unverified, where a term was reported but no document confirming it was reached.

## Caveats

- 17 of 30 construction costs still come from press or secondary sources. Thirteen come from audits, CAFRs, bond or SEC filings and government decisions (`notes/verification.md` lists them). The `*_label` columns in `arena_ledger.csv` label each component. Where sources disagree, the value used and the alternatives are listed in `totals.txt`, section I.
- Ongoing payments are documented for seven teams: Indianapolis, Miami, New Orleans, Minnesota, Oklahoma City and Charlotte from audits and budgets, and Memphis from press only. Several series have gaps, listed in the ledger's `ongoing_notes`. Other teams' figures are probably understated.
- The core total excludes most property-tax exemptions. Three appear only in the expanded total: Madison Square Garden's exemption, the Barclays Center PILOT bonds and the United Center's 1989 valuation formula (2002-2016 only). Denver's exemption from its seat tax is recorded as a memo, because its only dollar figure is one press report that could not be opened. The exemptions DC's 2024 law continues for Capital One Arena are future money and are not added. The DC finance office valued that tax relief at $312.7M through June 2050.
- Oklahoma City's Dec. 12, 2023 arena vote is not analyzed by precinct: the State Election Board's results site refuses automated access, and its precinct export is meant to be downloaded by hand.
- The precinct income estimates are spread by area, so a precinct that crosses block groups with different incomes is smoothed. With the county's current precinct boundaries instead, the fifths show the same pattern (47.6% yes in the lowest, 57.7% in the highest).
- The threat comparison is in 2025 dollars (CPI-U annual averages from the same FRED file), so its dollar figures differ from the ledger's 2026 dollars.
- Pending deals will move these numbers: the Memphis lease, the Portland agreements (due by Dec. 31, 2026 under Resolution 37750), the San Antonio city agreement (targeted for the end of December 2026; the term sheet sets no deadline) and Houston's expected state grant.

## Open items

- Replace the remaining 17 secondary construction costs. Most of the missing records are bond official statements on EMMA or older city reports that could not be reached (see `notes/verification.md`).
- Settle the four construction splits that every compilation disputes, from 29% to 100% public: Indianapolis, Atlanta, Memphis and New Orleans (also Phoenix's and Charlotte's public shares). Their 1997-2003 bond official statements on EMMA would decide them (`totals.txt`, section I).
- Value the property tax forgone at the 18 publicly owned arenas from assessor records, as was done for Washington, Barclays Center and Madison Square Garden, and check it against Propheter's estimates; value event-day city services for a few arenas; and check the land and early money other compilations report: Salt Lake City's 1991 help (about $19M), Philadelphia's city and state money (about $23M), Chicago's (about $11M) and Long's $20M for TD Garden.
- Find a city record of Denver's seat-tax receipts before 1999, the United Center's 1994-2001 assessments and tax rates, and the value of TD Garden's 1992 Chapter 121A tax payments.
- Find a primary record of Memphis's yearly subsidy, and fill the gaps in the payment series: Miami FY2011-12, Minneapolis 2019-2025, Charlotte before FY2020, Oklahoma City other than FY2023.
- Search Atlanta, Dallas, Philadelphia, Toronto and the privately owned arenas' recurring public costs, which the October 16 research could not cover.
- Track the pending Houston, Memphis, Portland and San Antonio deals into the ledger as they close.
- Analyze Oklahoma City's Dec. 12, 2023 arena vote by precinct once the State Election Board's precinct export is downloaded by hand (`results.okelections.us`, export tab).
- Leads checked on October 22, 2026 (`notes/verification.md`, "Leads checked"): find the Oklahoma Tax Commission's Quality Jobs payments to the Thunder after FY2013 and decide whether state payroll rebates should be counted for both the Thunder and the Pelicans; read the Memphis Sports Authority's funding agreement to see whether MLGW's $50M for FY2029-48 is inside the $550M plan; confirm Shelby County's votes on Private Chapters 67 and 70; get Salt Lake City's 1990 Resolution 112 and RDA minutes for the original Delta Center's public money; find DC's 2024 attorney general letter.
