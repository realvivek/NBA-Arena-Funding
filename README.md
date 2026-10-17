# Who Paid for the NBA's Arenas

A sourced funding ledger for all 30 current NBA arenas: how each was paid for, which taxes carry the debt, what households in the paying jurisdictions owe per head, and what owners got after threatening to move their teams.

The write-up is in [`report/who-paid-for-nba-arenas.md`](report/who-paid-for-nba-arenas.md). Everything in it traces to a row in `data/`, and every row carries its source URL.

Figures are as of October 16, 2026, in 2026 dollars unless noted.

## Findings

| Measure | Value | Where it comes from |
| --- | --- | --- |
| Public money in the 30 current arenas | $9.30B of $27.18B total spending (34.2%) | `data/ledger/totals.txt`, section A |
| Construction / purchases / renovations / ongoing subsidies | $5.21B / $219M / $3.11B / $759M | same |
| Public money since 2014 to renovate or buy existing arenas vs. public money in arenas opened since 2014 | $2.90B vs. $1.03B (2.8 times) | section J |
| Public total with tax-break financing added | at least $11.06B (39.2%) | section E: Barclays PILOT bonds $738M, MSG exemption $947M, United Center valuation formula $75M (2002-2016) |
| New public commitments outside the 30-arena total | $3.19B binding, approved or pending (OKC, Salt Lake City, San Antonio, Portland, Memphis) | section F |
| Share of public money in the top 10 arenas | 63% | section C |
| Public capital paid mostly by residents / visitors / other | 44.9% / 41.2% / 13.9% of $8.55B | section B |
| Federal cost of tax-exempt arena bonds (present value at issue, 2026 dollars, not added) | $1.91B | section E memo; `data/tax_mechanisms/nba_arena_bond_federal_cost.csv` |
| Documented owner or league relocation threats since 1994 | 20; 13 followed by same-city public money, median 11.2 months later | `data/threats/comparison.txt` |
| Median deal after a threat vs without one | $340M, 64% public vs $239M, 76% public (2025 dollars); Mann-Whitney p = 0.70 and 0.52 | same |

The threat comparison finds no evidence that deals after a threat were larger or more one-sided. The public paid roughly two-thirds to three-quarters of deal costs either way. The samples are small (10 threat deals, 14 without), so this is descriptive, not a causal estimate.

## Layout

```
report/
  who-paid-for-nba-arenas.md     the report
  charts/                        the two charts embedded in the report
data/
  ledger/                        arena_ledger.csv (30 arenas + 10 project rows, 95 columns), totals.txt, _calc.json
  threats/                       threat_ledger.csv (49 episodes), left_behind.csv, comparison.txt
  authorities/                   lease terms and exit penalties, net public cost, Indianapolis CIB payments to the Pacers, verbatim quotes from audits and agendas
  tax_mechanisms/                arena bonds, federal cost of tax-exempt bonds, Louisiana stadium district payments, Indiana PSDA, Section 197 franchise amortization, player income-tax capture
  property_tax/                  United Center assessment history and taxes forgone under its 1989 valuation formula, Intuit Dome parcels, Opportunity Zone sites, illustrative forgone tax on public arenas
  labor_contract/                2023 CBA clauses on arena revenue, naming rights at public arenas, renovation cycles
  dedicated_taxes/               Indianapolis CIB taxes, Salt Lake City arena sales tax and district budget, Wisconsin Center District taxes
  votes_lobbying/                arena votes, host payments, federal lobbying by the NBA, NBPA and owners, MSG related-party items
  inputs/                        CPI-U and CAD/USD series (FRED), household counts (Census ACS 2024, table B11001)
scripts/
  arena_ledger/                  ledger_inputs.py (hand-entered figures with labels and URLs), build_ledger.py, write_totals.py, report_charts.py
  arena_threats/                 build.py (hand-entered threat ledger), compare.py (threat vs no-threat comparison)
notes/
  verification.md                checks against primary records, corrections made and sites that could not be reached
docs/
  site-proposal.md               proposal for the data-story site (not built yet)
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

## Method

- **Scope.** The 30 arenas in use in the 2025-26 season. Ten more rows cover new or rebuilt arenas that are committed or pending.
- **Public money.** Construction contributions, public purchases of existing arenas, completed or binding renovation money, and documented ongoing cash subsidies. Debt service on counted bonds is not added, to avoid double counting. A public purchase counts as public money but not as new spending, because it reimburses a private builder.
- **Total spending.** The larger of the reported construction cost and public plus private construction, plus renovation totals and ongoing public payments.
- **Constant dollars.** BLS CPI-U, not seasonally adjusted (FRED CPIAUCNS), annual averages. The 2026 base is the January-August 2026 average (331.655); September 2026, published in October, is not included. Construction is deflated at the opening year, purchases at the transaction year, renovations at the mid-construction year and ongoing payments at each payment year. Money for work still under way is taken at face value. Canadian dollars convert at the year's average rate (FRED EXCAUS) before deflating.
- **Funding streams.** Each public capital dollar is assigned once, to its documented stream. In-kind land goes to "land". Infrastructure with no stated funding stream goes to "infrastructure".
- **Ongoing payments.** Yearly public cash to the team or the arena's operator for running a public building: operating payments and reimbursements, operating-loss coverage, payments into team-controlled reserves, loan forgiveness and tax pass-throughs. Debt service on counted bonds is excluded.
- **Who pays.** These streams are treated as paid mostly by residents: general taxes, GO bonds and state grants; dedicated sales taxes; tax increment and tax capture; lease-revenue bonds; and sin taxes. Hotel, car-rental, food-and-beverage and ticket taxes are treated as paid mostly by visitors. The split is approximate in both directions: residents pay some visitor taxes, and visitors pay some sales tax.
- **Per household.** Public money divided by ACS 2024 one-year household counts for each paying jurisdiction, weighted by that jurisdiction's share of the funding. These figures are totals, not yearly costs.
- **Threats.** An episode counts when the owner or the league made an explicit or implied threat. That means naming another city, announcing a move, selling to a buyer who intended to move, or the league stating it would move or buy the team. Statements by public officials alone do not count. Classification rules, exclusions and sensitivity runs are in `data/threats/comparison.txt`.
- **Federal bond cost.** The interest-differential method in Gayer, Drukker and Gold (Brookings, 2016), with a 28% marginal rate. It counts new-money issues only, not refundings.
- **Labels.** Every figure in `ledger_inputs.py` is labeled (a) computed, (b) primary document or (c) press/secondary.

## Caveats

- 18 of 30 construction costs still come from press or secondary sources. Twelve come from audits, CAFRs, bond or SEC filings and government decisions (`notes/verification.md` lists them). The `*_label` columns in `arena_ledger.csv` label each component. Where sources disagree, the value used and the alternatives are listed in `totals.txt`, section I.
- Ongoing payments are documented for seven teams: Indianapolis, Miami, New Orleans, Minnesota, Oklahoma City and Charlotte from audits and budgets, and Memphis from press only. Several series have gaps, listed in the ledger's `ongoing_notes`. Other teams' figures are probably understated.
- The core total excludes most property-tax exemptions. Three appear only in the expanded total: Madison Square Garden's exemption, the Barclays Center PILOT bonds and the United Center's 1989 valuation formula (2002-2016 only). Denver's exemption from its seat tax is recorded as a memo, because its only dollar figure is one press report that could not be opened. DC's extended exemption for Capital One Arena is future money and is not added. The DC finance office valued that tax relief at $312.7M through June 2050.
- The threat comparison deflates with approximate CPI-U averages to 2025 dollars, so its dollar figures differ slightly from the ledger's 2026 dollars.
- Pending deals will move these numbers: the Memphis lease, the Portland agreements and the San Antonio city agreement (definitive documents for both due by Dec. 31, 2026).

## Open items

- Replace the remaining 18 secondary construction costs. Most of the missing records are bond official statements on EMMA or older city reports that could not be reached (see `notes/verification.md`).
- Find a city record of Denver's seat-tax receipts before 1999, the United Center's 1994-2001 assessments and tax rates, and the value of TD Garden's 1992 Chapter 121A tax payments.
- Find a primary record of Memphis's yearly subsidy, and fill the gaps in the payment series: Miami FY2011-12, Minneapolis 2019-2025, Charlotte before FY2020, Oklahoma City other than FY2023.
- Search Atlanta, Dallas, Philadelphia, Toronto and the privately owned arenas' recurring public costs, which the October 16 research could not cover.
- Track the pending Memphis, Portland and San Antonio deals into the ledger as they close.
