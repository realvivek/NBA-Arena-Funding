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
    ('tourist',  'Visitor taxes on hotels, car rentals, food and drink, and tickets', 'visitors',  1),
    ('general',  'General taxes, general-obligation bonds, appropriations, state grants and sales of public assets', 'residents', 2),
    ('sales',    'Dedicated general sales tax', 'residents', 3),
    ('tif',      'Tax increment and other tax capture', 'residents', 4),
    ('leaserev', 'Lease-revenue bonds backed by the general fund or parking', 'residents', 5),
    ('sin',      'Alcohol and tobacco taxes', 'residents', 6),
    ('mixed',    'Public money not split among its funding streams', 'other', 7),
    ('land',     'Land contributed or sold below value', 'other', 8),
    ('infra',    'Infrastructure and site work, funding stream not stated', 'other', 9)
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
