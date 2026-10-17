# Working rules for this repo

This repo is an investigation into how the 30 current NBA arenas were funded: what taxpayers paid, through which taxes, and what owners got after threatening to move. The report is in `report/`, the funding and threat ledgers in `data/`, the scripts that rebuild them in `scripts/`, and checks against primary records in `notes/verification.md`. Read `README.md` and `notes/verification.md` before changing anything.

## Build commands

The scripts reproduce the committed outputs byte for byte on Python 3.11 with scipy 1.17. Use a virtual environment outside the repo, or `.venv/` (ignored):

```
uv venv -p 3.11 .venv && uv pip install --python .venv/bin/python "scipy==1.17.*" "matplotlib==3.10.*"
.venv/bin/python scripts/arena_ledger/build_ledger.py     # data/ledger/arena_ledger.csv, _calc.json
.venv/bin/python scripts/arena_ledger/write_totals.py     # data/ledger/totals.txt
.venv/bin/python scripts/arena_threats/build.py           # data/threats/threat_ledger.csv, left_behind.csv
.venv/bin/python scripts/arena_threats/compare.py         # data/threats/comparison.txt
.venv/bin/python scripts/arena_ledger/report_charts.py    # report/charts/*.png, after the ledger is built
git status --short data/                                  # empty when inputs are unchanged
```

Scripts run from any directory. Hand-entered figures live in `scripts/arena_ledger/ledger_inputs.py` and `scripts/arena_threats/build.py`; edit those, never the generated files in `data/ledger/` and `data/threats/`. After any input change, rebuild all four and commit inputs and outputs together.

The helper scripts (`wiki_extract.py`, `wiki_fin.py`, `wx.py`, `g.py`, `pdftxt.py`, `pdf2txt.py`) read raw downloads from `./raw` or `$RAW_DIR`. `pdftxt.py` needs PyMuPDF and `pdf2txt.py` needs pypdfium2.

### The site

The site (`site/`, Astro and Svelte) reads only what `pipeline/build.py` writes to `site/src/generated/`. After any change to the data, `pipeline/*.yaml` or `notes/verification.md`, rerun the pipeline and commit its outputs with the change; CI fails if they are stale. See `docs/site.md`.

```
uv pip install --python .venv/bin/python -r pipeline/requirements.txt
.venv/bin/python pipeline/build.py              # validate every CSV, check sources, compute stats and datasets
.venv/bin/python pipeline/build.py --check      # fail if site/src/generated/ or docs/fact-check.md is stale
.venv/bin/python pipeline/registry.py seed      # add entries for newly cited URLs to pipeline/sources.yaml, then curate them
.venv/bin/python pipeline/datapackage.py        # after adding a CSV or a column
.venv/bin/python -m pytest pipeline/tests -q
cd site && npm ci && npm run build              # site/dist; fails on any copy that breaks the rules below
npx astro check && npm test                     # types; copy rules on every content file
npx playwright test                             # pages; set CHROMIUM_PATH to use a preinstalled browser
```

Never edit `site/src/generated/` or `docs/fact-check.md` by hand. Copy lives in `site/src/content/` (`story.yaml`, `pages.yaml`, `figures.yaml`). Every number in it is a token, `{{key}}`, for a stat defined in `pipeline/stats.yaml`; years and dates may be typed. Every paragraph cites source ids from `pipeline/sources.yaml` (or `sources_extra.yaml`). Names that contain numerals go in `site/src/content/allow.yaml`.

## Sourcing rules

- Check every figure against the primary document, tables as well as prose. An earlier draft understated DC's arena tax break by $50 million by reading one column of a table (FY2029-2050) as the total. Read the whole table and its headings before taking a number.
- When sources disagree, record both: the value used and every alternative with its source (`construction_cost_other_reports` in the ledger, section I of `totals.txt`).
- Label every figure (a) computed, (b) primary document or (c) press or secondary.
- Every figure carries a source URL. A number without one does not go in.
- Express dollars in 2026 terms with BLS CPI-U, not seasonally adjusted (FRED CPIAUCNS), annual averages, as the ledger does: construction at the opening year, purchases at the transaction year, renovations at the mid-construction year, ongoing payments at each payment year, money for work still under way at face value. Canadian dollars convert at the year's average FRED EXCAUS rate before deflating. The 2026 base is the January-August 2026 average (331.655).
- Some sites can't be reached from the build environment (EMMA, the Wayback Machine, at times lda.senate.gov). Say what couldn't be reached in `notes/verification.md` instead of guessing or filling in from memory.
- Record corrections in `notes/verification.md` under "Corrections made during the work".

## Writing rules

- Technical audience, plain language, no marketing.
- No em dashes in copy. Use commas, colons, parentheses or separate sentences.
- No AI or tool names anywhere in commits, pull requests or files.

## Git rules

- Commit as realvivek (`75518860+realvivek@users.noreply.github.com`). No co-author trailers or session links in commit messages or pull requests.
- Keep raw downloads out of git (`raw/` is ignored). Never commit secrets or `.env` files.
