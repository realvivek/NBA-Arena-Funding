# Verification notes

Claims in the report that were checked against primary records, with what each record shows. Last updated October 11, 2026.

## Checked against primary records

| Claim in the report | Record | What it shows |
| --- | --- | --- |
| United Center main parcel cut from $29.3M to $12.6M assessed value in 2024 | Cook County Assessor (Socrata `uzyt-m557`) and Board of Review appeals (`7pny-nedm`), PIN 17182010350000 | 2024 mailed $42,448,434; Assessor certified $29,300,116; Board of Review $12,643,201. Appellant United Center JV, filed by Steven B. Pearlman & Associates. Appeals were filed every year 2016-2025, and only 2024 produced a decrease. The whole complex went from $125.0M to $92.05M to $50.32M. |
| $2.56M of player income tax paid to the Pelicans in FY2023 | Louisiana Legislative Auditor, LSED audits | Nonresident players' tax paid to the Pelicans: $2,347,124 (FY2014), $2,115,732 (FY2022), $2,562,287 (FY2023). The Saints received $3,583,406 in FY2023. |
| $17.68M of Pelicans "lease entitlements" budgeted for FY2027 | Louisiana Senate fiscal presentation, LSED FY2027 | Pelicans lease entitlements, including the player-tax allocation: $11,772,860 (FY2024), $15,343,250 (FY2025), $16,926,925 (FY2026) and $17,683,634 recommended for FY2027. Series in `data/tax_mechanisms/lsed_budget_team_payments.csv`. |
| CBA keeps construction money, relocation inducements and some player-tax payments out of shared revenue | 2023 NBA CBA, Article VII §1(a)(1) | Clause (xvi): player income or privilege tax payments count as BRI except for teams already receiving them in 2015-16, such as Memphis and New Orleans. Clause (viii): 50% of arena naming revenue counts. Clause (i): gate receipts are net of government surcharges, including arena financing charges. Full list in `data/labor_contract/cba_arena_clauses.csv`. |
| $12.71M to the Pacers in 2023, plus $2M of loans forgiven; up to $750M if the team leaves | Indianapolis CIB ACFRs (State Board of Accounts reports 83950A and B61741) | Fieldhouse operating expenses and reimbursements: $13,960,468 (2021), $13,783,251 (2022), $12,709,638 (2023). Pacers note forgiveness: $2,000,000 in 2022 and in 2023. The FY2023 ACFR (MD&A p.43, Note 9) says the agreement requires the Pacers to pay the CIB up to $750 million, mainly if they fail to play their required home games. The 2014-2023 series is in `data/authorities/indianapolis_cib_pacers_2014_2023.csv`. |
| $30.0M paid into the Little Caesars Arena bond fund in FY2024 | Detroit DDA financial statements, FY2024 | Transfer to the stadium fund of $30,026,206 (FY2023: $30,924,733). The notes say the bonds were issued "to incentivize the Detroit Pistons to relocate". |
| Cleveland's public owner owes major repairs | Gateway Economic Development Corp. FY2022 audit | Gateway does not expect to repay its Cuyahoga County notes; about $66.6M of interest has accrued. |
| Houston's public owner must keep the arena "first-class" | Toyota Center lease §8.6; HCHSA special meeting agenda, April 8, 2026 | The lease requires a first-class, state-of-the-art facility. The 2026 agenda lists "approval of certain projects at the Toyota Center". |
| Three of five Salt Lake City district trustees are SEG executives; two of them moved and seconded the SEG reimbursement agreement | Downtown Revitalization PID minutes, June 17, 2025 (utah.gov/pmn file 1368579) | Members present: John Larson (SEG), Mike Maughan (SEG), Andrew Smith (SEG), Darrin Casper (Salt Lake City) and Blake Thomas (Salt Lake County). The board considered the Infrastructure Acquisition and Reimbursement Agreement with SEG Real Estate LLC and Smith Entertainment Group, LLC. Larson moved it, Smith seconded, and the vote was unanimous. |
| Salt Lake City's 0.5% arena sales tax raised $57.99M in FY2026 | Utah State Tax Commission sales-tax distributions | FY2026 $57.99M; the 12 months to September 2026 brought in $58.68M. Monthly series in `data/dedicated_taxes/slc_ccr_monthly.csv`. |
| Wisconsin Center District taxes: $49.97M in 2025, 62% from hotel rooms | Wisconsin DOR expo tax distributions | 2025 total $49,967,419.95. Basic plus additional room tax was $30,769,184 (61.6%). |
| DC's tax relief for Capital One Arena: $312.7M, "not financially necessary" | DC OCFO Tax Abatement Financial Analysis, Bill 25-1004, November 26, 2024, Table 1 | Total exemption value is $49,817,695 for FY2025-2028 and $262,896,844 for FY2029-2050, or $312.7M through the lease's base term ending June 30, 2050. OCFO "finds that the abatement is not financially necessary". |
| MSG property-tax exemption of about $42M a year | NYC Independent Budget Office, March 2023 | $42M in FY2023. The cumulative $946.7M since 1982 comes via Reinvent Albany and is used only in the expanded total. |
| MLB's lobbyist was the only one on record on the Section 197 cap | House Clerk lobbying disclosures (bulk XML) | Ernst & Young for the Office of the Commissioner of Baseball: $50,000 in each of Q1 and Q2 2025, on sports franchise amortization under Section 197 (H.R. 1). The Senate LDA site was down for maintenance, so the House files were used. |

## Corrections made during the work

- **DC exemption value.** One draft of the report gave the value as $262.9M, after misreading the OCFO memo's phrase "$262.9 million through the base term of the Lease". Table 1 of the memo shows that figure is the FY2029-2050 column only. The total through June 30, 2050 is $312.7M, the figure the ledger already carried. The report was corrected on October 11, 2026.
- **Ownership counts.** Two counts were corrected in the opening of the arena table. The public paid half or more on 12 of the 18 publicly owned arenas, not 14. And 7 of the 12 private or privately run arenas got public money or a tax break, not 6.
- **Who pays.** The lead first gave residents' share of public capital as 39%. It was corrected to 46%, which matches the chart and section B of `totals.txt`.
- **Threat deal shares.** The wording "about two-thirds either way" was changed to "two-thirds to three-quarters". Deals were 64% public after a threat and 76% public without one.
- **Cook County query.** A first query used a wrong PIN prefix and returned small totals. The main arena PIN 17182010350000 confirmed the 2024 cut.

## Not reachable from the build environment

- EMMA (MSRB): used for Memphis bond principal, via Gayer, Drukker and Gold's Table 2 instead.
- Wayback Machine (connection reset). The Marquette sports facility report cited for Atlanta now returns 404, so its content was taken from the search index.
- lda.senate.gov / lda.gov: used for lobbying filings, via House Clerk bulk files instead.
