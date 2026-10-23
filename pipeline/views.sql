-- DuckDB views over the committed data files. Every number on the site is a query against these
-- views (pipeline/stats.yaml, pipeline/datasets.yaml). {root} is replaced with the repository path.
-- build.py adds tables that are not CSVs: cpi, comparison, threat_deals, coords and the *_sources
-- tables that map each row's citations to ids in pipeline/sources.yaml.

-- One row per public-money item: construction, purchase, renovation, yearly payment or new project.
create or replace view items as
select team, item_id, kind, "desc" as description, year, status, in_core = 'Y' as core,
       spending_nominal_m, public_nominal_m, cpi_factor, spending_2026_m, public_2026_m,
       cost_label, public_label, note
from read_csv('{root}/data/ledger/ledger_items.csv', header = true);

-- Public money in each item split by funding stream.
create or replace view buckets as
select item_id, team, bucket, public_nominal_m, public_2026_m
from read_csv('{root}/data/ledger/ledger_buckets.csv', header = true);

-- Funding streams, and who mostly pays each one (README, "Who pays").
create or replace view bucket_groups as
select * from (values
    ('tourist',  'Hotel and car-rental taxes', 'visitors',  1),
    ('meals',    'Restaurant-meal and ticket taxes, alone or pooled with hotel taxes', 'shared', 2),
    ('general',  'General taxes, general-obligation bonds, appropriations, state grants and sales of public assets', 'residents', 3),
    ('sales',    'Dedicated general sales tax', 'residents', 4),
    ('tif',      'Tax increment and other tax capture', 'residents', 5),
    ('leaserev', 'Lease-revenue bonds backed by the general fund or parking', 'residents', 6),
    ('sin',      'Alcohol and tobacco taxes', 'residents', 7),
    ('mixed',    'Public money not split among its funding streams', 'other', 8),
    ('land',     'Land contributed or sold below value', 'other', 9),
    ('infra',    'Infrastructure and site work, funding stream not stated', 'other', 10)
) t(bucket, name, payer, ord);

-- Capital items (everything counted except yearly payments).
create or replace view capital as
select * from items where core and kind <> 'ongoing';

-- The arena ledger: one row per current arena, plus project rows.
create or replace view ledger as
select * from read_csv('{root}/data/ledger/arena_ledger.csv', header = true);

create or replace view arenas as
select * from ledger where row_type = 'current_arena';

create or replace view households as
select * from read_csv('{root}/data/ledger/households.csv', header = true);

create or replace view threats as
select * from read_csv('{root}/data/threats/threat_ledger.csv', header = true);

create or replace view left_behind as
select * from read_csv('{root}/data/threats/left_behind.csv', header = true);

create or replace view leases as
select team, arena, owner, try_cast(term_end_year as integer) as term_end_year, term_and_nonrelocation,
       outs_penalties_notes, summary, label
from read_csv('{root}/data/authorities/lease_clock.csv', header = true, all_varchar = true);

-- Teams: what each controlling owner paid, what the team is worth now, deals since, and what each public arena deal
-- returns to the public. Prices in millions of nominal dollars; values in billions.
create or replace view team_values as
select team, owner, owner_wealth, owner_field, owner_class, control_year, price_year, try_cast(price_m as double) as price_m, price_scope, price_note, price_label,
       try_cast(seller_price_m as double) as seller_price_m, try_cast(seller_year as integer) as seller_year,
       forbes_2025_b, forbes_2026_b, sportico_2026_b, value_label,
       nullif(deal, '') as deal, try_cast(deal_value_b as double) as deal_value_b, nullif(deal_date, '') as deal_date,
       nullif(deal_label, '') as deal_label, note
from read_csv('{root}/data/teams/team_values.csv', header = true, delim = ',', quote = '"', escape = '"', all_varchar = true,
              types = {'control_year': 'INTEGER', 'price_year': 'INTEGER', 'forbes_2025_b': 'DOUBLE', 'forbes_2026_b': 'DOUBLE',
                       'sportico_2026_b': 'DOUBLE'});

create or replace view value_history as
select * from read_csv('{root}/data/teams/value_history.csv', header = true, delim = ',', quote = '"', escape = '"');

create or replace view investors as
select fund, fund_type, team, holder, stake, nullif(entered, '') as entered, try_cast(entry_value_b as double) as entry_value_b,
       status, label, note
from read_csv('{root}/data/teams/investors.csv', header = true, delim = ',', quote = '"', escape = '"', all_varchar = true);

create or replace view public_return as
select team, public_deal = 'Y' as public_deal, sale_share, equity_stake = 'Y' as equity_stake, summary, label, note
from read_csv('{root}/data/teams/public_return.csv', header = true, delim = ',', quote = '"', escape = '"', all_varchar = true);

-- United Center: the 1989 valuation formula years, and the bills after it ended.
create or replace view uc_formula as
select * from read_csv('{root}/data/property_tax/united_center_formula_savings.csv', header = true);

create or replace view uc_bills as
select * from read_csv('{root}/data/property_tax/united_center_tax_bills_2017_2024.csv', header = true);

-- Dedicated tax series.
create or replace view slc_monthly as
select month, slc_ccr_final_distribution_usd as usd
from read_csv('{root}/data/dedicated_taxes/slc_ccr_monthly.csv', header = true, all_varchar = true,
              columns = {'month': 'VARCHAR', 'slc_ccr_final_distribution_usd': 'DOUBLE', 'source': 'VARCHAR'});

create or replace view wcd_annual as
select * from read_csv('{root}/data/dedicated_taxes/wcd_expo_tax_annual.csv', header = true, all_varchar = true);

-- Other published estimates of public money for the same arenas (construction only), for the comparison in the method.
create or replace view outside_estimates as
select * from read_csv('{root}/data/inputs/outside_estimates.csv', header = true);

-- Arena locations for the map (Wikipedia article coordinates).
create or replace view coords as
select team, lat, lon from read_csv('{root}/data/inputs/arena_coordinates.csv', header = true);

-- Federal cost of tax-exempt arena bonds, per issue.
create or replace view fed_bond_cost as
select * from read_csv('{root}/data/tax_mechanisms/nba_arena_bond_federal_cost.csv', header = true);

-- A figure converted to 2026 dollars from a documented one is computed from it: add (a) to its label.
create or replace macro conv_label(lbl, fac) as
    case when fac = 1 or contains(lbl, 'a') then lbl else lbl || '/a' end;

-- Arena bond issues, with whether each raised new money (refundings are excluded from the federal cost).
create or replace view arena_bonds as
select * from read_csv('{root}/data/tax_mechanisms/nba_arena_bonds.csv', header = true, all_varchar = true);

-- Who mostly pays each funding stream, per item.
create or replace view item_payers as
select b.item_id, b.team, b.bucket, g.payer, b.public_2026_m
from buckets b join bucket_groups g using (bucket);

-- Who pays by income: ITEP's Who Pays? (7th edition) state and local taxes as a share of family income for seven
-- income groups in each state, and the ITEP line that matches each resident-paid funding stream of each arena.
create or replace view itep as
select state, line, line_name, grp, grp_order, share_of_income
from read_csv('{root}/data/who_pays/itep_who_pays_7.csv', header = true);

create or replace view itep_lines as
select team, bucket, state, line, note
from read_csv('{root}/data/who_pays/itep_tax_lines.csv', header = true);

-- For each arena's resident-paid capital money by funding stream: the share of income its tax line takes from the
-- poorest fifth of households and from the richest 1% in that state, and the ratio of the two.
create or replace view incidence as
with m as (
    select b.team, b.bucket, sum(b.public_2026_m) as public_2026_m
    from buckets b join capital c using (item_id) join bucket_groups g using (bucket)
    where g.payer = 'residents'
    group by b.team, b.bucket)
select m.team, m.bucket, l.state, l.line, any_value(i.line_name) as line_name, m.public_2026_m,
       max(i.share_of_income) filter (where i.grp_order = 1) as poorest_share,
       max(i.share_of_income) filter (where i.grp_order = 7) as top1_share,
       max(i.share_of_income) filter (where i.grp_order = 1) / max(i.share_of_income) filter (where i.grp_order = 7) as ratio
from m left join itep_lines l using (team, bucket) left join itep i on i.state = l.state and i.line = l.line
group by m.team, m.bucket, l.state, l.line, m.public_2026_m;

-- Bexar County's November 4, 2025 vote on Proposition B, precinct by precinct, with Census estimates.
create or replace view prop_b as
select * from read_csv('{root}/data/who_pays/bexar_2025_prop_b_precincts.csv', header = true, types = {'precinct': 'VARCHAR'});

-- Precincts with votes in five groups holding equal numbers of households, by estimated median income (1 = lowest).
create or replace view prop_b_fifths as
with p as (
    select *, sum(households_est) over (order by median_income_est, precinct rows between unbounded preceding and current row)
                - households_est / 2.0 as mid,
           sum(households_est) over () as total_hh
    from prop_b where yes_votes + no_votes > 0 and median_income_est is not null)
select *, least(5, 1 + floor(5 * mid / total_hh))::integer as fifth from p;

create or replace view bexar_sites as
select * from read_csv('{root}/data/who_pays/bexar_arena_sites.csv', header = true);

-- ZIP code areas (2020) in each paying government of households.csv, with the share of the area's land inside it.
create or replace view zip_geo as
select * from read_csv('{root}/data/who_pays/zip_jurisdictions.csv', header = true, types = {'zip': 'VARCHAR', 'geo_id': 'VARCHAR'});

-- The county outline drawn under the precinct map (simplified from the precincts), and the households in the United
-- States (ACS 2024 1-year) for the federal bond cost per household.
create or replace view bexar_outline as
select geometry.type as geom_type, geometry.coordinates as coords
from read_json_auto('{root}/data/who_pays/bexar_county_outline.json');

create or replace view us_households as
select data['01000US'].B11001.estimate.B11001001 as households, release.id as release
from read_json_auto('{root}/data/inputs/census/acs2024_B11001_more.json');
