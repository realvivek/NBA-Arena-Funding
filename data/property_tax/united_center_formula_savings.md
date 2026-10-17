# United Center stadium valuation formula: taxes forgone, 2002-2016

`united_center_formula_savings.csv` estimates the property tax the United Center did not pay under the 1989 Illinois stadium valuation formula (Public Act 86-110, now 35 ILCS 200/10-205 to 10-220). The formula valued the arena at 20% of four times its owners' net income after interest, income taxes and capital repairs, with a minimum tax of $1,000,000 a year from the third year after the base year (10-220(d)). It applied for 22 years after the base year.

Columns, all for the Assessor's 75-PIN United Center valuation unit (keypin 17-07-426-007-0000), nominal dollars:

- `board_av`: Board of Review assessed value, summed over the 75 PINs. Cook County Assessor, "Assessor - Assessed Values" (Socrata `uzyt-m557`; titled "Historic Assessed Values" when first used), https://datacatalog.cookcountyil.gov/resource/uzyt-m557.json (b).
- `eq_factor`: final state equalization factor (IDOR, via the Assessor's PTAXSIM database v2024.0.0, table `eq_factor`), https://ccao-data-public-us-east-1.s3.amazonaws.com/ptaxsim/ptaxsim-2024.0.0.db.bz2 (b).
- `rate_pct`: composite tax rate of tax code 77001. PTAXSIM `tax_code` table for 2006-2016 (b); for 2002-2005, Chicago Teachers Union, "Nothing but Net Profit" (2013), Table 3, taken from Clerk data (c; its 2006-2007 rates match PTAXSIM exactly). `rate_label` marks which.
- `bill`: tax billed. PTAXSIM `pin.tax_bill_total` for 2006-2016 (b); `board_av` x `eq_factor` x `rate_pct` for 2002-2005 (a).
- `paid_with_floor`: `bill`, raised to the statutory $1,000,000 minimum where lower (2005-2008) (a).
- `cf_a_tax`: tax at the Assessor's first assessed value after the formula ended, $32,310,359 (tax year 2017 certified), x `eq_factor` x `rate_pct` (a).
- `saving_a`: `cf_a_tax` - `paid_with_floor` (a). Sum 2002-2016: $46.6M. This is the figure used in the ledger's expanded total.
- `cf_b_tax`, `saving_b`: the same with the Assessor's 2021 assessed value, $28,124,917 (about $112.5M market value x 25%) (a). Sum: $36.1M, recorded as the low alternative.

Why this is a floor: 1994-2001 (eight of the formula's 23 years) could not be computed, because Board of Review values before 1999 and Chicago composite rates before 2002 could not be reached (cookcountyclerkil.gov returned 403). Extending the 2002-2010 average saving to those years gives about $77M for the whole term (rough, not used). The Chicago Teachers Union's income-approach estimates for 2002-2007 alone run from $28.2M to $64.2M.

The last formula year is inferred, not documented: the 2017 certified value jumped from a mailed $23.39M to $32.31M in a year with no reassessment, consistent with a 1994 base year plus 22 years (2016) and with press reports that the formula would "expire in 2016". After the formula, bills were $6,979,375 (2017) to $10,146,542 (2024).

`united_center_tax_bills_2017_2024.csv` holds the bills after the formula ended, for the same 75-PIN unit: Clerk assessed value, final equalizer, composite rate and tax billed, all from the Assessor's PTAXSIM database v2024.0.0 (b), https://ccao-data-public-us-east-1.s3.amazonaws.com/ptaxsim/ptaxsim-2024.0.0.db.bz2. The 2024 bill rose after the Board of Review value went from $28.1M to $50.3M.
