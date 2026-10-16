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
newmoney={(r['team'],r['year'],r['issuer_series']) for r in csv.DictReader(open(DATA+'/tax_mechanisms/nba_arena_bonds.csv')) if r['new_money']=='True'}
fedpv=defaultdict(float)
for r in csv.DictReader(open(DATA+'/tax_mechanisms/nba_arena_bond_federal_cost.csv')):
    if r['tau']=='0.28' and r['tax_status']!='planned' and (r['team'],r['year'],r['issuer_series']) in newmoney: fedpv[r['team']]+=float(r['pv3_30yr_fed_loss_m'])

hh=json.load(open(DATA+'/inputs/census/acs2024_B11001.json'))
HH={k:(hh['geography'][k]['name'], int(v['B11001']['estimate']['B11001001'])) for k,v in hh['data'].items()}

def r1(x):
    return '' if x is None else round(x,1)

rows=[]; agg=defaultdict(float); aggp=defaultdict(float); bucket26=defaultdict(float); bucket26_priv=defaultdict(float)
PRIVATE_BUILT={'GSW','LAC','BOS','NYK','CHI','LAL','DEN','PHI','TOR','BKN','DET','WAS','UTA','POR'}
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
    acq=t.get('acq'); acqn=acq['amt'] if acq else 0.0; acq26=acqn*f26(acq['year']) if acq else 0.0
    rb=[r for r in t.get('renos',[]) if r['status'] in ('completed','binding')]
    rp=[r for r in t.get('renos',[]) if r['status']=='pending']
    ren_pub_n=sum(sum(r['pub'].values()) for r in rb); ren_tot_n=sum(r['total'] for r in rb)
    ren_pub26=sum(sum(r['pub'].values())*f26(r['cpi_year']) for r in rb); ren_tot26=sum(r['total']*f26(r['cpi_year']) for r in rb)
    pend_n=sum(sum(r['pub'].values()) for r in rp); pend26=sum(sum(r['pub'].values())*f26(r['cpi_year']) for r in rp)
    og=t.get('ongoing',[]); og_n=sum(a for y,a in og); og26=sum(a*f26(y) for y,a in og)
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
    conduit=t.get('conduit')
    le=dict(lease.get(T,{}))
    OVR={'SAS':dict(term_end_year='2032',term_and_nonrelocation='Lease expires 2032 (Bexar County)',outs_penalties_notes='Break fees up to $124M (per Bexar 2015 deal, renovation file)',label='b/c',source=U['bexar15']),
         'WAS':dict(term_end_year='2050',term_and_nonrelocation='Lease-back to DCALP through June 30, 2050 + up to five 4-yr renewals; Wizards/Capitals must play home games there; no-shop to 2045',outs_penalties_notes='Damages not quantified in FIS',label='b',source=U['dc_fis']),
         'OKC':dict(term_end_year='2053',term_and_nonrelocation='Through at least 2053: 25 years from move-in to the new arena (okc.gov 2023; KGOU 2025-06-18; Bond Buyer 2026-04-06); earlier reports said at least 2050',outs_penalties_notes='Early-exit penalties > $1B (KGOU 2025-06-18)',label='b/c',source=U['okc_loi']+' ; https://www.kgou.org/sports/2025-06-18/oklahoma-city-inks-deal-to-keep-thunder-through-2053-nails-down-new-arena-policies')}
    if T in OVR: le.update(OVR[T])
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
        built_privately_majority='Y' if T in PRIVATE_BUILT else 'N',
        construction_cost_nominal_m=r1(cost), construction_cost_currency_note=('C$%.0fM converted at 1999 avg %.4f CAD/USD' % (cad,CAD1999)) if cad else 'USD', construction_cost_label=t['cost_label'], construction_cost_source=t['cost_src'], construction_cost_other_reports=t.get('cost_alt',''),
        public_construction_nominal_m=r1(pubn),
        **{f'pubcon_{b}_m':r1(pub.get(b)) if pub.get(b) else '' for b in BUCKETS},
        public_construction_label=t['pub_label'], public_construction_source=t['pub_src'], public_construction_notes=t['pub_note'],
        private_construction_nominal_m=r1(priv), private_construction_label=t['priv_label'], private_construction_source=t['priv_src'],
        public_acquisition_nominal_m=r1(acqn) if acq else '', public_acquisition_year=acq['year'] if acq else '', public_acquisition_label=acq['label'] if acq else '', public_acquisition_source=(acq['src']+' ; '+acq['note']) if acq else '',
        public_renovation_nominal_m=r1(ren_pub_n), renovation_total_cost_nominal_m=r1(ren_tot_n), public_renovation_pending_nominal_m=r1(pend_n) if pend_n else '',
        renovation_items=reno_txt, renovation_sources=reno_src,
        ongoing_annual_from_net_cost_file=netdesc,
        ongoing_to_date_nominal_m=r1(og_n) if og else '', ongoing_to_date_years=(f"{og[0][0]}-{og[-1][0]} ({len(og)} yrs documented)" if og else ''),
        ongoing_label=t.get('ongoing_label',''), ongoing_source=t.get('ongoing_src',''), ongoing_notes=t.get('ongoing_note',''),
        tax_break_desc=(tbk['desc'] if tbk else ''), tax_break_annual_m=(tbk['annual'] if tbk else ''), tax_break_annual_year=(tbk['annual_year'] if tbk else ''), tax_break_annual_2026_m=(r1(tbk['annual']*f26(tbk['annual_year'])) if tbk else ''),
        tax_break_cumulative_nominal_m=(tbk['cum'] if tbk and tbk.get('cum') else ''), tax_break_future_committed_m=(tbk.get('future','') if tbk else ''), tax_break_notes=(tbk.get('future_note','') if tbk else ''), tax_break_source=((tbk['annual_src']+(' ; '+tbk['cum_src'] if tbk.get('cum_src') else '')) if tbk else ''),
        pilot_or_tax_diversion_financing_m=r1(pilot) if pilot else '', pilot_note=t.get('pilot_note',''),
        conduit_public_financing_repaid_privately_m=r1(conduit) if conduit else '', conduit_2026_m=r1(conduit*fac) if conduit else '', conduit_note=t.get('conduit_note',''),
        tax_exempt_bonds_par_m_from_arena_tax=r1(bd['par_te']) if bd else '', taxable_bonds_par_m=r1(bd['par_tax']) if bd else '', bond_detail=' | '.join(bd['rows']) if bd else '',
        fed_tax_expenditure_pv_m_tau028=r1(fedpv.get(T)) if fedpv.get(T) else '',
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
    detail[T]=dict(core26=core26, spend26=spend26, pub26=pub26, priv26=priv26, acq26=acq26, ren_pub26=ren_pub26, ren_tot26=ren_tot26, og26=og26, pend26=pend26, con26=con_total26, pilot26=pilot26, tb=dict(tb),
                   og_years=[y for y,a in og], pend_items=[(r['desc'], sum(r['pub'].values())*f26(r['cpi_year'])) for r in rp])
    for k,v in dict(core26=core26, spend26=spend26, pub26=pub26, priv26=priv26, acq26=acq26, ren_pub26=ren_pub26, ren_tot26=ren_tot26, og26=og26, pend26=pend26, con26=con_total26, pilot26=pilot26).items():
        agg[k]+=v
        if T in PRIVATE_BUILT: aggp[k]+=v

# notes/gaps per team
GAPS={
'ATL':'Original construction split from Marquette summary (via search index) - Recreation Authority official statements not reachable (EMMA blocked).',
'BOS':'No public money documented; state/MBTA infrastructure around North Station not quantified.',
'BKN':'City $205M figure from IBO 2009 testimony as reported (IBO URL now redirects); MTA land discount unquantified; PILOT bonds counted only in expanded total.',
'CHA':'Public share of 2005 build disputed ($170M taxpayer per Carolina Journal vs city-owned $265M); team contribution ~$23M.',
'CHI':'1989 property-tax break amount not found.',
'CLE':'1994 cost reported $100M-$155M; public $100M from PFM summary; 2017 county share mechanism (hotel/admissions taxes per press) not verified -> mixed.',
'DAL':'Land/infrastructure around Victory Park not quantified.',
'DEN':'Land the city bought from Southern Pacific (1997) - price/transfer terms not found.',
'DET':'Public share excludes DDA land/infrastructure outside bond-funded costs and the ongoing school-tax capture beyond debt service.',
'GSW':'City event-day service costs not counted.',
'HOU':'Rent Supported Debt (Rockets rent) size not found, so net public share overstated; city land $20M from Marquette 2005 (via search).',
'IND':'Ongoing CIB payments documented only 2014-2023 (ACFR ten-year table); 2010-2013 and 2024-26 subsidies not included.',
'LAC':'No public money found; land purchased at $66.25M.',
'LAL':'$58M city financing treated as conduit (AEG guaranty); 1997 deal documents not reached.',
'MEM':'2004 bond repayment mechanisms (tourist taxes, state sales-tax rebate, seat fees) not split; $470M of the $550M renovation pending lease.',
'MIA':'Heat-paid construction per press; county land $38M (press); subsidy assumed $6.4M every year FY2000-26.',
'MIL':'Value of the Bradley Center site conveyed to the team not documented; state GPR to 2035-36 is debt service on counted bonds.',
'MIN':'1995 purchase price from a 2003 legislative committee agenda; only 2024 operating supplements documented.',
'NOP':'1999 construction mechanism from press; ongoing payments partial (audited FY2014, FY2021-23, QJ FY2024-26 only); team revenue entitlements excluded.',
'NYK':'Exemption cumulative ($946.7M) from Reinvent Albany citing IBO July 2023 (nominal, through ~2023) - not converted to 2026$.',
'OKC':'2008 renovation arena share computed pro rata from plan; MAPS 4 money for the new arena reported as $70M, $78M, $89M (okc.gov 2026-10-12) and ~$99M.',
'ORL':'2007 split between TDT bonds and CRA ($100M) from secondary sources; PFM says public $430M.',
'PHI':'No public money found in sources reached (contemporaneous 1994-96 records not reached).',
'PHX':'1992 city $35M mechanism not documented; 2019 $175M includes $25M capital reserve paid over time.',
'POR':'1995 city $34.5M mechanism not documented (reported as garages/infrastructure elsewhere, unverified); $586.6M rebuild pending.',
'SAC':'Value of city parcels/billboard rights given to Kings not documented; final cost $558.2M from Wikipedia (OS estimate $507.1M).',
'SAS':'Public 2002 share computed as cost - Spurs $28.5M; infobox says $186M cost.',
'TOR':'No Canadian public money documented; property-tax status not verified.',
'UTA':'1990 RDA land value and any RDA cash not documented; district $375M in project row.',
'WAS':'1997 public ~$79M from Wikipedia (land, site, Metro); construction total reported $200M-$260M; Monumental share of renovation computed from Council memo ($800M total).',
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

json.dump(dict(as_of=AS_OF, projects=projects, agg=agg, aggp=aggp, bucket26=bucket26, bucket26_priv=bucket26_priv, detail=detail, proj_agg=proj_agg, CPI={k:CPI[k] for k in sorted(CPI) if k>=1960}, CAD1999=CAD1999, HH=HH, fedpv=dict(fedpv)), open(DATA+'/ledger/_calc.json','w'), indent=1, default=float)
print('rows',len(rows),'projects',len(prow))
print('CPI2026 (Jan-Aug avg)',round(C26,3),'n months',len(cpi_m[2026]), '2025 months',len(cpi_m[2025]))
for k,v in agg.items(): print(k, round(v,1))
print('--- private-built group');
for k,v in aggp.items(): print(k, round(v,1))
print('--- buckets 2026$');
for b in BUCKETS: print(b, round(bucket26.get(b,0),1), round(bucket26_priv.get(b,0),1))
print('--- projects', dict(proj_agg))
for T,d in sorted(detail.items(), key=lambda x:-x[1]['core26']): print(T, round(d['core26'],1), round(d['spend26'],1), round(100*d['core26']/d['spend26'],1) if d['spend26'] else None)
