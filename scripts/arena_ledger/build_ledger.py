import sys
import csv, json, os
from collections import defaultdict, OrderedDict
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA=ROOT+'/data'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_inputs import TEAMS, PROJECTS, U, AS_OF

BUCKETS=['general','sales','tourist','tif','leaserev','land','infra','sin','mixed']
BNAME={'general':'general taxes/GO/appropriations & state grants','sales':'dedicated general sales tax','tourist':'hotel/car-rental/F&B/ticket (visitor) taxes',
       'tif':'tax increment & tax capture (TIF, PSDA, income-tax capture)','leaserev':'lease-revenue bonds (general fund/parking backed)',
       'land':'land contributed or sold below value','infra':'infrastructure/parking/site work','sin':'sin taxes (alcohol/tobacco)','mixed':'public, mechanism split not documented'}

# ---------- CPI-U (CPIAUCNS = BLS CUUR0000SA0, NSA) annual averages ----------
cpi_m=defaultdict(list)
for r in csv.DictReader(open(DATA+'/inputs/cpi/CPIAUCNS.csv')):
    v=r['CPIAUCNS'].strip()
    if v and v!='.': cpi_m[int(r['observation_date'][:4])].append(float(v))
CPI={y:sum(v)/len(v) for y,v in cpi_m.items()}
C26=CPI[2026]
def f26(y):
    if y is None: return 1.0
    y=int(y)
    return 1.0 if y>=2026 else C26/CPI[y]
ex=[float(r['EXCAUS']) for r in csv.DictReader(open(DATA+'/inputs/cpi/EXCAUS.csv')) if r['observation_date'].startswith('1999') and r['EXCAUS'] not in ('','.')]
CAD1999=sum(ex)/len(ex)

# ---------- merges ----------
lease={r['team']:r for r in csv.DictReader(open(DATA+'/authorities/lease_clock.csv'))}
net={}
for r in csv.DictReader(open(DATA+'/authorities/net_public_cost.csv')):
    net.setdefault(r['team'],[]).append(r)
bonds=defaultdict(lambda: dict(par_te=0.0, par_tax=0.0, rows=[]))
for r in csv.DictReader(open(DATA+'/tax_mechanisms/nba_arena_bonds.csv')):
    k=bonds[r['team']]; p=float(r['par_m'])
    if 'TAXABLE' in r['tax_status']: k['par_tax']+=p
    elif r['tax_status']!='planned': k['par_te']+=p
    k['rows'].append(f"{r['year']} {r['issuer_series'][:60]} ${p:g}M {r['tax_status']}")
# federal cost of tax-exempt bonds: only each issue's new money for the arena (fed_cost_par_m), converted from the year
# whose dollars its par is stated in (2014 for the issues taken from Gayer, Drukker and Gold's Table 3)
counted={(r['team'],r['year'],r['issuer_series']):r for r in csv.DictReader(open(DATA+'/tax_mechanisms/nba_arena_bonds.csv')) if r['fed_cost_par_m']}
fedpv=defaultdict(float); fedpv26=defaultdict(float)  # present value at issue, in the dollars of the par and in 2026 dollars
for r in csv.DictReader(open(DATA+'/tax_mechanisms/nba_arena_bond_federal_cost.csv')):
    b=counted.get((r['team'],r['year'],r['issuer_series']))
    if r['tau']=='0.28' and b:
        pv=float(r['pv3_30yr_fed_loss_m'])*float(b['fed_cost_par_m'])/float(b['par_m'])
        fedpv[r['team']]+=pv; fedpv26[r['team']]+=pv*f26(int(b['par_dollars_year']))

hh=json.load(open(DATA+'/inputs/census/acs2024_B11001.json'))
HH={k:(hh['geography'][k]['name'], int(v['B11001']['estimate']['B11001001'])) for k,v in hh['data'].items()}

def r1(x):
    return '' if x is None else round(x,1)
def r6(x):
    return round(x,6)

# normalized rows for the site pipeline: one row per public-money item, and its funding streams
items=[]; ibuckets=[]
def add_item(T, item_id, kind, desc, year, status, in_core, spend_n, pub_n, fac, cost_label, public_label, cost_source, public_source, note='', buckets=None):
    items.append(OrderedDict(team=T, item_id=item_id, kind=kind, desc=desc, year=year, status=status, in_core=in_core,
        spending_nominal_m=r6(spend_n), public_nominal_m=r6(pub_n), cpi_factor=r6(fac), spending_2026_m=r6(spend_n*fac), public_2026_m=r6(pub_n*fac),
        cost_label=cost_label, public_label=public_label, cost_source=cost_source, public_source=public_source, note=note))
    for b,v in (buckets or {}).items():
        ibuckets.append(OrderedDict(item_id=item_id, team=T, bucket=b, public_nominal_m=r6(v), public_2026_m=r6(v*fac)))

rows=[]; agg=defaultdict(float); aggp=defaultdict(float); bucket26=defaultdict(float); bucket26_priv=defaultdict(float)
PRIVATE_BUILT=set()  # arenas whose construction was less than half public money (filled below, by rule)
SPLIT_UNRESOLVED=set()  # arenas whose public-private construction split conflicts across sources: in neither group
detail={}
for t in TEAMS:
    T=t['team']; yr=t['opened']; fac=f26(yr)
    cost=t.get('cost'); cad=t.get('cost_cad')
    if cost is None and cad: cost=cad/CAD1999
    pub=t.get('pub',{}); pubn=sum(pub.values())
    priv=t.get('priv')
    if priv is None and cad: priv=cost  # private arena, CAD converted
    # construction spending base: max(reported cost, public+private) to avoid understating when public sits outside reported cost
    con_total=max(cost or 0, (pubn or 0)+(priv or 0))
    if t.get('split_unresolved'): SPLIT_UNRESOLVED.add(T)
    elif pubn < 0.5*con_total: PRIVATE_BUILT.add(T)
    acq=t.get('acq'); acqn=acq['amt'] if acq else 0.0; acq26=acqn*f26(acq['year']) if acq else 0.0
    rb=[r for r in t.get('renos',[]) if r['status'] in ('completed','binding')]
    rp=[r for r in t.get('renos',[]) if r['status']=='pending']
    ren_pub_n=sum(sum(r['pub'].values()) for r in rb); ren_tot_n=sum(r['total'] for r in rb)
    ren_pub26=sum(sum(r['pub'].values())*f26(r['cpi_year']) for r in rb); ren_tot26=sum(r['total']*f26(r['cpi_year']) for r in rb)
    pend_n=sum(sum(r['pub'].values()) for r in rp); pend26=sum(sum(r['pub'].values())*f26(r['cpi_year']) for r in rp)
    og=list(t.get('ongoing',[]))
    ogx=t.get('ongoing_extra',[])
    for e in ogx: og+=e['series']
    og.sort()
    og_n=sum(a for y,a in og); og26=sum(a*f26(y) for y,a in og); og_years=sorted({y for y,a in og})
    pub26=pubn*fac; priv26=(priv or 0)*fac; cost26=(cost or 0)*fac; con_total26=con_total*fac
    core26=pub26+acq26+ren_pub26+og26
    spend26=con_total26+ren_tot26+og26
    share=core26/spend26 if spend26 else None
    # buckets (capital only: construction + acquisition + completed/binding renovations)
    tb=defaultdict(float)
    for b,v in pub.items(): tb[b]+=v*fac
    if acq: tb[acq['bucket']]+=acq26
    for r in rb:
        for b,v in r['pub'].items(): tb[b]+=v*f26(r['cpi_year'])
    for b,v in tb.items():
        bucket26[b]+=v
        if T in PRIVATE_BUILT: bucket26_priv[b]+=v
    pilot=t.get('pilot'); pilot26=pilot*fac if pilot else 0.0
    tbk=t.get('taxbreak')
    tb_cum=tbk.get('cum') if tbk else None; tb_cum26=None
    if tbk and tbk.get('series_file'):
        ser=[(int(r['tax_year']), float(r[tbk['series_col']])/1e6) for r in csv.DictReader(open(DATA+'/'+tbk['series_file']))]
        tb_cum=sum(a for y,a in ser); tb_cum26=sum(a*f26(y) for y,a in ser); tb_years=f"{ser[0][0]}-{ser[-1][0]}"
    elif tb_cum: tb_cum26=tb_cum*f26(tbk.get('cum_year'))  # one cumulative figure stated in one year's dollars (MSG: IBO, 2023 dollars)
    exp26=tb_cum26 if (tbk and tbk.get('expanded') and tb_cum26) else 0.0
    conduit=t.get('conduit')
    le=dict(lease.get(T,{}))
    if le.get('term_end_year'):
        try: le['term_end_year']=str(int(float(le['term_end_year'])))
        except Exception: pass
    nets=net.get(T,[])
    netdesc=' | '.join(f"{n['year']}: net ${n['net_$M']}M/yr ({n['rank_basis']}; {n['label']}; {n['src']})" for n in nets)
    bd=bonds.get(T)
    reno_txt=' | '.join(f"{r['desc']} [{r['status']}, CPI yr {r['cpi_year']}]: public ${sum(r['pub'].values()):g}M of ${r['total']:g}M nominal = public ${sum(r['pub'].values())*f26(r['cpi_year']):.1f}M of ${r['total']*f26(r['cpi_year']):.1f}M in 2026$ ({'+'.join(f'{k} {v:g}' for k,v in r['pub'].items()) or 'private'}); label {r['label']}; {r['note']}" for r in t.get('renos',[]))
    reno_src=' | '.join(r['src'] for r in t.get('renos',[]))
    row=OrderedDict(
        row_type='current_arena', team=T, arena=t['arena'], city=t['city'], opened=yr, owner=t['owner'], owner_type=t['owner_type'],
        built_privately_majority='Y' if T in PRIVATE_BUILT else ('unresolved' if T in SPLIT_UNRESOLVED else 'N'),
        construction_cost_nominal_m=r1(cost), construction_cost_currency_note=('C$%.0fM converted at 1999 avg %.4f CAD/USD' % (cad,CAD1999)) if cad else 'USD', construction_cost_label=t['cost_label'], construction_cost_source=t['cost_src'], construction_cost_other_reports=t.get('cost_alt',''),
        public_construction_nominal_m=r1(pubn),
        **{f'pubcon_{b}_m':r1(pub.get(b)) if pub.get(b) else '' for b in BUCKETS},
        public_construction_label=t['pub_label'], public_construction_source=t['pub_src'], public_construction_notes=t['pub_note'],
        private_construction_nominal_m=r1(priv), private_construction_label=t['priv_label'], private_construction_source=t['priv_src'],
        public_acquisition_nominal_m=r1(acqn) if acq else '', public_acquisition_year=acq['year'] if acq else '', public_acquisition_label=acq['label'] if acq else '', public_acquisition_source=(acq['src']+' ; '+acq['note']) if acq else '',
        public_renovation_nominal_m=r1(ren_pub_n), renovation_total_cost_nominal_m=r1(ren_tot_n), public_renovation_pending_nominal_m=r1(pend_n) if pend_n else '',
        renovation_items=reno_txt, renovation_sources=reno_src,
        ongoing_annual_from_net_cost_file=netdesc,
        ongoing_to_date_nominal_m=r1(og_n) if og else '', ongoing_to_date_years=(f"{og_years[0]}-{og_years[-1]} ({len(og_years)} yrs documented)" if og else ''),
        ongoing_label=' ; '.join(x for x in [t.get('ongoing_label','')]+[e['label'] for e in ogx] if x),
        ongoing_source=' ; '.join(x for x in [t.get('ongoing_src','')]+[e['src'] for e in ogx] if x),
        ongoing_notes=' | '.join(x for x in [t.get('ongoing_note','')]+[e['component']+': '+e['note'] for e in ogx] if x),
        tax_break_desc=(tbk['desc'] if tbk else ''), tax_break_annual_m=(tbk['annual'] if tbk and tbk.get('annual') else ''), tax_break_annual_year=(tbk['annual_year'] if tbk and tbk.get('annual') else ''), tax_break_annual_2026_m=(r1(tbk['annual']*f26(tbk['annual_year'])) if tbk and tbk.get('annual') else ''),
        tax_break_cumulative_nominal_m=(r1(tb_cum) if tb_cum else ''), tax_break_cumulative_2026_m=(r1(tb_cum26) if tb_cum26 else ''), tax_break_in_expanded_total=('Y' if exp26 else ('memo' if tbk and tbk.get('memo') else ('' if not tbk else 'N'))),
        tax_break_future_committed_m=(tbk.get('future','') if tbk else ''), tax_break_memo_estimate_m=(tbk.get('memo','') if tbk else ''), tax_break_notes=(tbk.get('future_note','') if tbk else ''), tax_break_source=(((tbk['annual_src'] or '')+(' ; '+tbk['cum_src'] if tbk.get('cum_src') else '')) if tbk else ''),
        pilot_or_tax_diversion_financing_m=r1(pilot) if pilot else '', pilot_note=t.get('pilot_note',''),
        conduit_public_financing_repaid_privately_m=r1(conduit) if conduit else '', conduit_2026_m=r1(conduit*fac) if conduit else '', conduit_note=t.get('conduit_note',''),
        tax_exempt_bonds_par_m_from_arena_tax=r1(bd['par_te']) if bd else '', taxable_bonds_par_m=r1(bd['par_tax']) if bd else '', bond_detail=' | '.join(bd['rows']) if bd else '',
        fed_tax_expenditure_pv_m_tau028=r1(fedpv.get(T)) if fedpv.get(T) else '', fed_tax_expenditure_pv_2026_m=r1(fedpv26.get(T)) if fedpv26.get(T) else '',
        property_tax_status=t['ptax'], property_tax_source=t['ptax_src'],
        lease_end=le.get('term_end_year',''), lease_terms=le.get('term_and_nonrelocation',''), exit_penalty=le.get('outs_penalties_notes',''), lease_label=le.get('label',''), lease_source=le.get('source',''),
        cpi_year_construction=yr, cpi_factor_construction=round(fac,4),
        construction_cost_2026_m=r1(cost26), public_construction_2026_m=r1(pub26), private_construction_2026_m=r1(priv26),
        public_acquisition_2026_m=r1(acq26) if acq else '', public_renovation_2026_m=r1(ren_pub26), renovation_total_cost_2026_m=r1(ren_tot26),
        public_renovation_pending_2026_m=r1(pend26) if pend_n else '', ongoing_to_date_2026_m=r1(og26) if og else '',
        PUBLIC_TOTAL_2026_m=r1(core26), total_arena_spending_2026_m=r1(spend26), public_share_pct=round(100*share,1) if share is not None else '',
        **{f'pubcap_{b}_2026_m':r1(tb.get(b)) if tb.get(b) else '' for b in BUCKETS},
        pilot_2026_m=r1(pilot26) if pilot else '',
        notes_and_gaps=''
    )
    rows.append(row)
    add_item(T, f'{T}-construction', 'construction', f"{t['arena']} construction", yr, 'completed', 'Y', con_total, pubn, fac,
             t['cost_label'], t['pub_label'], t['cost_src'], t['pub_src'], t['pub_note'], pub)
    if acq:
        add_item(T, f'{T}-purchase', 'purchase', f"Public purchase of {t['arena']}", acq['year'], 'completed', 'Y', 0.0, acqn, f26(acq['year']),
                 '', acq['label'], '', acq['src'], acq['note'], {acq['bucket']:acqn})
    for j,r in enumerate(t.get('renos',[]),1):
        core='Y' if r['status'] in ('completed','binding') else 'N'
        add_item(T, f'{T}-renovation-{j}', 'renovation', r['desc'], r['cpi_year'], r['status'], core, r['total'], sum(r['pub'].values()), f26(r['cpi_year']),
                 r['label'], r['label'], r['src'], r['src'], r['note'], r['pub'])
    comps=[(t.get('ongoing_component','Ongoing payments'), t.get('ongoing',[]), t.get('ongoing_label',''), t.get('ongoing_src',''), t.get('ongoing_note',''))]
    comps+=[(e['component'], e['series'], e['label'], e['src'], e['note']) for e in ogx]
    for ci,(cname,series,clabel,csrc,cnote) in enumerate(comps,1):
        for y,a in series:
            add_item(T, f'{T}-ongoing-{ci}-{y}', 'ongoing', cname, y, 'paid', 'Y', a, a, f26(y), clabel, clabel, csrc, csrc, cnote)
    detail[T]=dict(core26=core26, spend26=spend26, pub26=pub26, priv26=priv26, acq26=acq26, ren_pub26=ren_pub26, ren_tot26=ren_tot26, og26=og26, pend26=pend26, con26=con_total26, pilot26=pilot26, tb=dict(tb),
                   og_years=og_years, exp26=exp26, tb_desc=(tbk['desc'] if tbk else ''), tb_short=(tbk.get('short',T) if tbk else ''), tb_memo=(tbk.get('memo') if tbk else None), pend_items=[(r['desc'], sum(r['pub'].values())*f26(r['cpi_year'])) for r in rp])
    for k,v in dict(core26=core26, spend26=spend26, pub26=pub26, priv26=priv26, acq26=acq26, ren_pub26=ren_pub26, ren_tot26=ren_tot26, og26=og26, pend26=pend26, con26=con_total26, pilot26=pilot26).items():
        agg[k]+=v
        if T in PRIVATE_BUILT: aggp[k]+=v

# notes/gaps per team
GAPS={
'ATL':'Original construction split from Marquette summary (via search index) - Recreation Authority official statements not reachable (EMMA blocked).',
'BOS':'No public construction money; as-built cost not found (the 1992 BRA estimate is used); the Chapter 121A tax arrangement and the deferred $5.126M MBTA note are not quantified.',
'BKN':"State $100M from press (Gotham Gazette); city $205M from IBO 2009 testimony; MTA rail yard counted at IBO's $10M arena share; PILOT bonds counted only in expanded total.",
'CHA':'City ACFR states a $200M project without itemizing it; the $170M public figure (press) is not split in any primary document; arena reserve contributions before FY2020 not reachable.',
'CHI':'1989 formula valuation counted in the expanded total for tax years 2002-2016 only; 1994-2001 inputs not reachable; last formula year inferred.',
'CLE':"Arena cost is the recorded building line, excluding the complex's shared land, site and capitalized costs; repayment source of the county's 1992 and 1994 arena bonds not documented (mixed); 2017 county share mechanism not verified (mixed).",
'DAL':'Construction cost and $125M public cap from press; 1998A/B arena bonds of $124.4M outstanding in 2002 (City ACFR) are consistent with the cap; land/infrastructure around Victory Park not quantified.',
'DEN':'Cost includes financing costs; construction sales-tax rebates under the 1997 agreement not quantified (its property-tax increment payments are the counted DURA TIF); seat-tax exemption estimated from one unverified press figure (memo only); land the city bought from Southern Pacific not found.',
'DET':'Public share excludes DDA land/infrastructure outside bond-funded costs and the ongoing school-tax capture beyond debt service.',
'GSW':'City event-day service costs not counted.',
'HOU':'Final cost not found ($235M press; $195M floor from primary budgets); the city $20M for site and infrastructure is in the infrastructure bucket (no split); Rent Supported Debt capped at $30.4M but actual size not found, so net public share overstated; 2020 rent abatements ($2.975M) and pre-opening maintenance deposits ($4.5M, payment unconfirmed) not counted.',
'IND':'1997A/B bond par ($230.7M), which the CIB says funded the construction of the Fieldhouse and an attached garage, exceeds the reported $183M cost and no primary public/private split was found, so the arena is counted as neither privately nor publicly built; the $79M public figure is press. Ongoing CIB payments documented 2014-2025 (ACFR ten-year tables) and 2001.',
'LAC':'No public money found; land purchased at $66.25M.',
'LAL':"City's ~$70M advance treated as conduit (developer must offset it under the Gap Funding Agreement); 1997 deal documents not reached.",
'MEM':'Cost and funding split from the City CAFR (FY2005); Sports Authority bond repayment streams not split (mixed); $470M of the $550M renovation pending lease.',
'MIA':'County land $37.6M from the Inspector General; Heat-paid construction per press; county subsidy assumed $6.4M every year FY2000-26; State of Florida payments after June 2014 at the scheduled rate.',
'MIL':'Value of the Bradley Center site conveyed to the team not documented; state GPR to 2035-36 is debt service on counted bonds.',
'MIN':'City subsidy split (TIF bonds vs land and infrastructure) not settled (mixed); only 2024 operating supplements documented.',
'NOP':'1999 construction cost and mechanism from press; ongoing payments audited FY2003-FY2025 plus budgeted Quality Jobs equivalent FY2025-26 (FY2026 audit not issued); QJ FY2023-24, suite payments and home-game entitlements excluded.',
'NYK':'Exemption cumulative: IBO (July 2023) estimates more than $946.7M in 2023 dollars forgone since 1982, converted to 2026 dollars; fiscal years after 2023 not added.',
'OKC':'2002 cost from press; 2008 renovation arena share computed pro rata from plan; operating subsidy documented for FY2023 only; MAPS 4 money for the new arena reported as $70M, $78M, $89M and ~$99M.',
'ORL':"Cost is a plan-of-finance figure (2016), not an audited final cost; the $12M of city cash repaid from Magic use payments is counted as public, so net public cost is overstated; interest earnings partly on the Magic's deposit (mixed).",
'PHI':'No public money found in sources reached (contemporaneous 1994-96 records not reached).',
'PHX':'1992 cost and $35M city share from press; a 1998 arena refunding of $48.74M suggests more city debt; 2019 $175M includes the $25M renewal and replacement account paid over time.',
'POR':'1995 cost and city $34.5M from press, mechanism not documented; $573M rebuild pending; city match of team capital spending during the bridge term not quantified.',
'SAC':"Cost from the construction monitor's last posted report (99.5% complete), not an audited total; value of city parcels and billboard rights not documented.",
'SAS':'Recorded cost probably includes capitalized interest; the 2000 bond program also paid for Coliseum and grounds work.',
'TOR':"Cost from the owner's web page only; no Canadian public money documented; property-tax status not verified.",
'UTA':'1990 RDA land value and any RDA cash not documented; 2017 city reimbursement counted at its $22.7M cap; district $375M in project row.',
'WAS':'Building cost $175M (GAO, developer estimate) to $260M (press); 1997 public money from GAO (District $61.5M + $14M federal and WMATA for the Metro link); Monumental share of renovation computed from Council memo ($800M total).',
}
for r in rows: r['notes_and_gaps']=GAPS.get(r['team'],'')

# ---------- projects ----------
prow=[]; proj_agg=defaultdict(float); projects=[]
for p in PROJECTS:
    pub=dict(p.get('pub',{}))
    for b,v in p.get('pub_extra',{}).items(): pub[b]=pub.get(b,0)+v  # binding public money outside the arena budget (e.g. OKC 2025 GO garage and offices)
    pubn=sum(pub.values()); pp=p.get('pub_pending',{}); ppn=sum(pp.values())
    row=OrderedDict((k,'') for k in rows[0].keys())
    row.update(row_type='project'+(' (memo: included in team row)' if p['in_team_row'] else ''), team=p['team'], arena=p['arena'], city=p['city'], opened=p['opened'], owner=p['owner'], owner_type=p['owner_type'],
        built_privately_majority='',
        construction_cost_nominal_m=r1(p.get('cost')), construction_cost_currency_note='USD (budget, nominal)', construction_cost_label=p['cost_label'], construction_cost_source=p['cost_src'], construction_cost_other_reports=p.get('cost_alt',''),
        public_construction_nominal_m=r1(pubn) if pub else ('0' if not pp else ''),
        public_construction_label=p['pub_label']+(' ; outside-budget '+p['extra_label'] if p.get('pub_extra') else ''), public_construction_source=p['pub_src']+(' ; '+p['extra_src'] if p.get('pub_extra') else ''),
        public_construction_notes=p['pub_note']+(' OUTSIDE THE ARENA BUDGET: '+p['extra_note'] if p.get('pub_extra') else '')+(' PENDING: '+p.get('pending_note','') if pp else ''),
        private_construction_nominal_m=r1(p.get('priv')), private_construction_label=p.get('priv_label',''), private_construction_source=p.get('priv_src',''),
        public_renovation_pending_nominal_m=r1(ppn) if pp else '',
        lease_terms=p.get('lease',''),
        cpi_year_construction='2026 (future/in-progress budget; not deflated)', cpi_factor_construction=1.0,
        construction_cost_2026_m=r1(p.get('cost')), public_construction_2026_m=r1(pubn) if pub else '', private_construction_2026_m=r1(p.get('priv')),
        public_renovation_pending_2026_m=r1(ppn) if pp else '',
        PUBLIC_TOTAL_2026_m=r1(pubn) if pub else '',
        notes_and_gaps='Status: '+p['status'])
    for b in BUCKETS:
        if pub.get(b): row[f'pubcon_{b}_m']=r1(pub[b]); row[f'pubcap_{b}_2026_m']=r1(pub[b])
    prow.append(row)
    if not p['in_team_row']:
        # a project item's spending is its public money, so it carries the public label and source
        plab=p['pub_label']+(' ; '+p['extra_label'] if p.get('pub_extra') else ''); psrc=row['public_construction_source']
        if pubn: add_item(p['team'], f"{p['team']}-project", 'project', p['arena'], 2026, p['status'], 'N', pubn, pubn, 1.0, plab, plab, psrc, psrc, p['pub_note'], pub)
        if ppn: add_item(p['team'], f"{p['team']}-project-pending", 'project', p['arena'], 2026, 'pending', 'N', ppn, ppn, 1.0, p['pub_label'], p['pub_label'], p['pub_src'], p['pub_src'], p.get('pending_note',''), pp)
    projects.append(dict(team=p['team'], arena=p['arena'], status=p['status'], in_team_row=p['in_team_row'], pub=pubn, pend=ppn))
    if not p['in_team_row']:
        proj_agg['binding_or_approved_new']+=pubn
        proj_agg['pending_new']+=ppn
        for b,v in pub.items(): proj_agg['b_'+b]+=v

# ---------- write CSV ----------
os.makedirs(DATA+'/ledger',exist_ok=True)
with open(DATA+'/ledger/arena_ledger.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows+prow: w.writerow(r)

# the normalized rows must add up to the same core totals
core_items=sum(i['public_2026_m'] for i in items if i['in_core']=='Y'); spend_items=sum(i['spending_2026_m'] for i in items if i['in_core']=='Y')
assert abs(core_items-agg['core26'])<0.01 and abs(spend_items-agg['spend26'])<0.01, (core_items, agg['core26'], spend_items, agg['spend26'])
for fn,data in (('ledger_items.csv',items),('ledger_buckets.csv',ibuckets)):
    with open(DATA+'/ledger/'+fn,'w',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(data[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(data)
json.dump(dict(as_of=AS_OF, projects=projects, agg=agg, aggp=aggp, bucket26=bucket26, bucket26_priv=bucket26_priv, detail=detail, proj_agg=proj_agg, CPI={k:CPI[k] for k in sorted(CPI) if k>=1960}, CAD1999=CAD1999, HH=HH, fedpv=dict(fedpv), fedpv26=dict(fedpv26)), open(DATA+'/ledger/_calc.json','w'), indent=1, default=float)
print('rows',len(rows),'projects',len(prow))
print('CPI2026 (Jan-Aug avg)',round(C26,3),'n months',len(cpi_m[2026]), '2025 months',len(cpi_m[2025]))
for k,v in agg.items(): print(k, round(v,1))
print('--- private-built group');
for k,v in aggp.items(): print(k, round(v,1))
print('--- buckets 2026$');
for b in BUCKETS: print(b, round(bucket26.get(b,0),1), round(bucket26_priv.get(b,0),1))
print('--- projects', dict(proj_agg))
for T,d in sorted(detail.items(), key=lambda x:-x[1]['core26']): print(T, round(d['core26'],1), round(d['spend26'],1), round(100*d['core26']/d['spend26'],1) if d['spend26'] else None)
