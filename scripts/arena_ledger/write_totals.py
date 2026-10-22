import sys
import json, csv, os
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA=ROOT+'/data'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_inputs import TEAMS, PROJECTS
TI={t['team']:t for t in TEAMS}
C=json.load(open(DATA+'/ledger/_calc.json'))
agg=C['agg']; aggp=C['aggp']; det=C['detail']; CPI={int(k):v for k,v in C['CPI'].items()}; HH=C['HH']
HH2=json.load(open(DATA+'/inputs/census/acs2024_B11001_states2.json'))
for k,v in HH2['data'].items(): HH[k]=[HH2['geography'][k]['name'], int(v['B11001']['estimate']['B11001001'])]
rows=list(csv.DictReader(open(DATA+'/ledger/arena_ledger.csv')))
cur=[r for r in rows if r['row_type']=='current_arena']
B=['general','sales','tourist','tif','leaserev','land','infra','sin','mixed']
BN={'general':'General taxes / GO bonds / appropriations / state grants / public asset sales','sales':'Dedicated general sales tax','tourist':'Hotel, car-rental, F&B, ticket (visitor) taxes',
    'tif':'Tax increment & tax capture (TIF, CRA, Indiana PSDA, Oregon income-tax capture)','leaserev':'Lease-revenue bonds (general fund / parking backed)','land':'Land contributed or sold below value',
    'infra':'Infrastructure / parking / site work (funding stream not specified)','sin':'Sin taxes (alcohol/tobacco, Cleveland)','mixed':'Public, mechanism split not documented'}
f=lambda x: f"${x/1000:.2f}B" if abs(x)>=1000 else f"${x:.0f}M"
def fac(y): return 1.0 if y>=2026 else CPI[2026]/CPI[y]
def years(ys):
    # compress [2014,2015,2016,2021] -> '2014-16, 2021'
    ys=sorted(ys); runs=[]
    for y in ys:
        if runs and y==runs[-1][1]+1: runs[-1][1]=y
        else: runs.append([y,y])
    return ', '.join(str(a) if a==b else f"{a}-{str(b)[2:]}" for a,b in runs)
def reno_pub(team, desc_has, bucket=None):
    # nominal public money of one renovation item of a team, found by a word in its description
    r=[r for r in TI[team]['renos'] if desc_has in r['desc']]
    assert len(r)==1, (team, desc_has)
    return r[0]['pub'][bucket] if bucket else sum(r[0]['pub'].values())
PJ={(p['team'],p['in_team_row']):p for p in C['projects']}
out=[]
P=out.append
P(f"NBA ARENA LEDGER - COMPUTED TOTALS (built {C['as_of']})")
P('='*78)
P('CPI: BLS CPI-U, U.S. city average, all items, NOT seasonally adjusted (FRED CPIAUCNS = BLS CUUR0000SA0).')
P(f"Annual averages = mean of monthly values. 2026 base = Jan-Aug 2026 average {CPI[2026]:.3f} (September 2026 was published in October and is not included);")
# every year whose CPI converts a counted figure: the items, the Garden's exemption (IBO's 2023 dollars) and the
# United Center's forgone taxes (deflated at their payment years, 2003-2017)
YU=sorted({int(r['year']) for r in csv.DictReader(open(DATA+'/ledger/ledger_items.csv'))} | {2023} | set(range(2003,2018)))
P(f"2025 average uses 11 months ({CPI[2025]:.3f}; Oct 2025 CPI was not published). Years used: " + ', '.join(f"{y}={CPI[y]:.1f}" for y in YU))
P('Conversion: construction money at the opening-year CPI; acquisitions at transaction year; completed renovations at mid-construction year;')
P('ongoing payments at each payment year; money committed for work still under way or in the future is taken at face value (factor 1.0, not deflated).')
P(f"Canadian dollars: Scotiabank Arena C$288M converted at 1999 average {C['CAD1999']:.4f} CAD/USD (FRED EXCAUS) before CPI; the 2023-25 renovation at the 2024 average, 1.3700.")
P('')
P('A. CORE TOTAL - 30 CURRENT NBA ARENAS (spent or legally committed public money, 2026 dollars)')
P('-'*78)
core=agg['core26']; spend=agg['spend26']
P(f"Public construction contributions ............ {f(agg['pub26'])}")
P(f"Public purchases of existing arenas ........... {f(agg['acq26'])}  (Minneapolis 1995, Portland 2024, DC 2024)")
P(f"Public renovation money (completed + binding).. {f(agg['ren_pub26'])}")
ogt=[(k,d['og_years']) for k,d in det.items() if d['og_years']]
P(f"Documented ongoing cash subsidies to date ..... {f(agg['og26'])}  ({'; '.join(f'{k} {years(v)}' for k,v in sorted(ogt))})")
P(f"ALL PUBLIC MONEY (core) ....................... {f(core)}")
P(f"Total arena spending (construction public+private, renovations public+private, ongoing public) = {f(spend)}")
P(f"PUBLIC SHARE OF TOTAL ARENA SPENDING ........... {100*core/spend:.1f}%")
P(f"  construction only: public {f(agg['pub26'])} of {f(agg['con26'])} = {100*agg['pub26']/agg['con26']:.1f}%  (private construction {f(agg['priv26'])})")
P(f"  renovations only: public {f(agg['ren_pub26'])} of {f(agg['ren_tot26'])} = {100*agg['ren_pub26']/agg['ren_tot26']:.1f}%")
pend=[(k,d['pend26']) for k,d in det.items() if d['pend26']]
P(f"Pending public money on current arenas (not in core): {f(agg['pend26'])}  ({'; '.join(f'{k} {f(v)}' for k,v in sorted(pend))}; see the renovation items in arena_ledger.csv)")
P('Method: public share = public money / (max(reported cost, public+private construction) + renovation totals + ongoing public). Public purchases count as')
P('public money but not as new spending (they reimburse private builders). Debt service on counted bonds is NOT added (no double counting).')
P('')
P('B. MECHANISM SPLIT - public CAPITAL money (construction + purchases + completed/binding renovations), 2026$')
P('-'*78)
bt=sum(C['bucket26'].values())
for b in sorted(B,key=lambda b:-C['bucket26'].get(b,0)):
    v=C['bucket26'].get(b,0)
    if v: P(f"  {BN[b]:<92}{f(v):>9}  {100*v/bt:5.1f}%")
P(f"  {'TOTAL capital':<92}{f(bt):>9}")
P(f"  Ongoing operating subsidies (separate from capital): {f(agg['og26'])}")
P('  Rule: each dollar assigned once - by documented funding stream; in-kind land -> land; infrastructure with no stated stream -> infrastructure.')
P('')
P('C. TOP 10 ARENAS BY PUBLIC MONEY (core, 2026$)')
P('-'*78)
top=sorted(cur,key=lambda r:-float(r['PUBLIC_TOTAL_2026_m'] or 0))
for i,r in enumerate(top[:10],1):
    P(f"{i:>2}. {r['team']} {r['arena']:<34} public {f(float(r['PUBLIC_TOTAL_2026_m'])):>8} | share {r['public_share_pct']:>5}% | constr {r['public_construction_2026_m']} + acq {r['public_acquisition_2026_m'] or 0} + reno {r['public_renovation_2026_m']} + ongoing {r['ongoing_to_date_2026_m'] or 0}")
P('')
pb=[r['team'] for r in cur if r['built_privately_majority']=='Y']
P(f"D. ARENAS BUILT MAINLY WITH PRIVATE MONEY (public money under half of construction cost) ({len(pb)}): {', '.join(pb)}")
P('-'*78)
unres=[r['team'] for r in cur if r['built_privately_majority']=='unresolved']
if unres: P(f"Construction split unresolved, counted in neither group: {', '.join(unres)} (see notes_and_gaps in arena_ledger.csv)")
P(f"Construction: private {f(aggp['priv26'])} vs public {f(aggp['pub26'])} ({100*aggp['pub26']/aggp['con26']:.1f}% public); plus public purchases {f(aggp['acq26'])} and public renovation {f(aggp['ren_pub26'])}")
P(f"Core public money {f(aggp['core26'])} of {f(aggp['spend26'])} total spending = {100*aggp['core26']/aggp['spend26']:.1f}%")
later=[t for t in pb if det[t]['acq26']+det[t]['ren_pub26']+det[t]['pend26']>0]
ex=[t for t in pb if t not in later]
s_core=sum(det[t]['core26'] for t in ex); s_sp=sum(det[t]['spend26'] for t in ex)
s_later=sum(det[t]['acq26']+det[t]['ren_pub26']+det[t]['pend26'] for t in later); s_pend=sum(det[t]['pend26'] for t in later)
P(f"Later bought or rebuilt with public money ({len(later)}): "+', '.join(f"{t} {f(det[t]['acq26']+det[t]['ren_pub26']+det[t]['pend26'])}" for t in sorted(later,key=lambda t:-(det[t]['acq26']+det[t]['ren_pub26']+det[t]['pend26'])))+f" = {f(s_later)}, of which {f(s_pend)} pending")
P(f"Excluding those {len(later)}: public {f(s_core)} of {f(s_sp)} = {100*s_core/s_sp:.1f}%")
bp=C['bucket26_priv']; btp=sum(bp.values())
P('Mechanism split of their public capital money (2026$): '+'; '.join(f"{BN[b].split(' (')[0]} {f(bp[b])} ({100*bp[b]/btp:.0f}%)" for b in sorted(bp,key=lambda b:-bp[b]) if bp[b]))
te={'BKN':'PILOT bonds $511M (2009; refunded 2016: $478.7M tax-exempt + $15M taxable)','DET':'MSF 2014A $250M tax-exempt (2014B $200M taxable authorized, $188.5M drawn, Olympia-paid); DDA 2018A refunding $287.4M','UTA':'PID sales-tax bonds 2025A/B/C $900M tax-exempt, up to $525M of it for the arena','WAS':'DC GO-funded $515M (tax status of specific bonds not confirmed)'}
P('Tax-exempt bonds behind privately built arenas: '+'; '.join(f"{k}: {v}" for k,v in te.items())+f". Federal cost of their new money for the arena (tau .28, present value at issue in 2026$; GDG's value for BKN): BKN {f(C['fedpv26'].get('BKN',0))}, DET {f(C['fedpv26'].get('DET',0))}, UTA {f(C['fedpv26'].get('UTA',0))}, WAS {f(C['fedpv26'].get('WAS',0))}.")
P('Other public money and tax breaks at arenas built and owned privately:')
H={
'BKN':'City $205M (IBO 2009 testimony; IBO\'s Sept 2009 brief counts $150M) + State $100M (IBO Sept 2009) capital for land/infrastructure + MTA rail yard $10M (IBO arena share of the $50M bid gap), counted in core; $511M tax-exempt PILOT bonds (property taxes diverted to arena debt; expanded total); full property-tax exemption (would-be $99M/yr 2023 vs $39M PILOT)',
'DET':'$286M DDA tax-increment bonds incl. captured school taxes ($387M 2026$); public ownership -> no property tax; Olympia rent-free',
'WAS':'1997 public money $75.5M (GAO: District $61.5M for land, site and Metro match + $14M federal and WMATA); $50M 2007 TIF notes (arena ticket tax); 2024 $87.5M purchase + $427.5M renovation; property/possessory-interest tax exemption since construction, ~$10M/yr now, continued to June 2050 by the 2024 law ($312.7M FY2025-50 per OCFO)',
'UTA':'RDA-owned land at $1/yr (2026 assessed $68.8M, exempt); city CRA reimbursement for the 2017 renovation up to $22.7M through 2040; $525M of 0.5% city sales-tax bonds into a privately owned arena + $375M for the surrounding district',
'POR':'City $34.5M (1995); building bought for $1 and land under it for $7.13M (2024); $573M pending (state income-tax capture $365M)',
'DEN':'$36.5M TIF + $4.5M city infrastructure (DURA); city land under a 23-year $10-a-year ground lease; construction sales-tax rebates (amount not found); exemption from the 10% seat tax (memo estimate ~$96M, from one press figure)',
'LAL':'City-owned land under 55-yr ground lease (exempt); ~$70M city advance (CAO), counted as public money because credits of city revenue (arena admissions fee, convention center parking) offset most of the developer\'s obligation; ~$58M of bonds and reserves per Seattle 2017',
'NYK':f"Full property-tax exemption since 1982: $42.4M in FY2023 and $43.3M in FY2026 (DOF tax-expenditure reports); more than $946.7M in 2023 dollars for FY1984-FY2023 (IBO, July 2023) plus FY2024-26, {f(det['NYK']['exp26'])} in 2026 dollars - expanded total only",
'CHI':'1989 stadium valuation formula: taxes forgone 2002-2016 about $46.6M nominal (expanded total; 1994-2001 not computed); 2024 assessment cut from $92.1M to $50.3M on appeal',
'GSW':'City transit capital for the arena, $42.5M planned (SFMTA 2015); city event-day services not counted; pays ~$19.5M/yr property tax',
'LAC':'None found; bought public land for $66.25M; pays ~$10.8M/yr property tax',
'BOS':'None found in construction; Chapter 121A designation with negotiated payments ($1.0M rising to $1.5M a year, 1992); pays $2.66M property tax (FY2026)',
'PHI':'City of Philadelphia is owner of record of the arena parcel, almost fully exempt from property tax: about $3.5M a year at the 2025 rate (memo, not counted, as for other publicly owned arenas); no public construction money found',
'TOR':'None documented (owner page: No public funding was used); site bought from Canada Post for C$60M',
}
for k,v in H.items(): P(f"  {k}: {v}")
P('')
P('E. EXPANDED TOTAL (adds tax-break financing that the core excludes)')
P('-'*78)
P(f"Core public money .......................................... {f(core)}")
P(f"+ Barclays PILOT bonds (property tax diverted to arena debt) {f(agg['pilot26'])}")
xb=[(k,d) for k,d in sorted(det.items()) if d.get('exp26')]
for k,d in xb:
    P(f"+ {d['tb_short']:<58} {f(d['exp26'])}" + ('  (IBO cumulative in 2023 dollars, converted)' if k=='NYK' else '  (yearly series, deflated)'))
xs=sum(d['exp26'] for k,d in xb)
exp=core+agg['pilot26']+xs
P(f"= EXPANDED PUBLIC TOTAL .................................... >= {f(exp)}  ({100*exp/(spend+xs):.1f}% of a spending base that adds the tax breaks)")
P('Not added (future): the tax relief in DC\'s 2024 arena law, mainly the continued property/possessory-interest tax exemption for Capital One Arena to June 2050, valued by OCFO at $49.8M FY2025-28 + $262.9M FY2029-50 = $312.7M (OCFO: "not financially necessary").')
for k,d in sorted(det.items()):
    if d.get('tb_memo'): P(f"Memo, not added: {d['tb_short']}: about {f(d['tb_memo'])} nominal, from one unverified press figure (range in arena_ledger.csv tax_break_notes).")
P(f"Memo: federal cost of tax-exempt arena bonds (present value at issue of the federal revenue loss on each issue's new money for the arena, tau=0.28: refundings and taxable issues excluded, Salt Lake City's 2025 PID issue at the arena's $525M of $900M, Indianapolis's 2021A at its ~$254M of new money; GDG's published values for the seven issues in their data, from each issue's redemption schedule, and a level 30-year approximation for the later issues) = {f(sum(C['fedpv26'].values()))} in 2026 dollars, each converted from the year its par is stated in (2014 for the issues from GDG Table 3) - not added (different payer, overlapping with local bonds).")
P('')
P('F. NEW-ARENA / DISTRICT COMMITMENTS NOT IN THE 30-ARENA CORE (face value = 2026$)')
P('-'*78)
NEW=[p for p in C['projects'] if not p['in_team_row']]
bind=[p for p in NEW if p['pub'] and p['status'].startswith('binding')]
vote=[p for p in NEW if p['pub'] and p['status'].startswith('voter-approved')]
pnew=[p for p in NEW if p['pend']]
none=[p for p in NEW if not p['pub'] and not p['pend']]
sb=sum(p['pub'] for p in bind); sv=sum(p['pub'] for p in vote); sp=sum(p['pend'] for p in pnew)
P('Binding: '+'; '.join(f"{p['team']} {p['arena']} {f(p['pub'])}" for p in bind)+f" -> {f(sb)}")
P('Voter-approved, agreements pending: '+'; '.join(f"{p['team']} {p['arena']} {f(p['pub'])}" for p in vote)+f" -> {f(sv)}")
P('Pending/non-binding, new arenas: '+'; '.join(f"{p['team']} {p['arena']} {f(p['pend'])}" for p in pnew)+f" -> {f(sp)}; pending on current arenas (team rows): {f(agg['pend26'])}")
P('No public deal: '+'; '.join(f"{p['team']} {p['arena']}" for p in none))
P('OKC binding total includes $60M of 2025 GO bonds for a garage and team offices outside the $900M arena budget; Bexar County $311M is the voter-approved cap.')
allin=core+sb+sv+sp+agg['pend26']
P(f"Core + binding new = {f(core+sb)}; + all approved/pending = {f(allin)}")
P('')
P('G. COST PER HOUSEHOLD - LARGEST PUBLIC DEALS (2026$; ACS 2024 1-year households, table B11001, Census Reporter API)')
P('-'*78)
hh=lambda g: HH[g][1]
memst=reno_pub('MEM','first phase')+TI['MEM']['state_m']*CPI[2026]/CPI[2004]  # the 2025 grant money is for work under way: face value
D=[
 ('UTA',f"Delta Center, all public money (the 2025 renovation {f(reno_pub('UTA','sales tax'))} and the 2017 reimbursement; the district's {f(PJ[('UTA',False)]['pub'])} from the same tax is not included), 0.5% Salt Lake City sales tax",det['UTA']['core26'],[('16000US4967000',1.0)],'City sales tax; >=30% paid by non-residents (taxflow round), so per-resident-household burden is an upper bound'),
 ('OKC',f"New Thunder arena and related 2025 GO projects ({f(PJ[('OKC',False)]['pub'])}) + Paycom 2002 & 2008 money ({f(det['OKC']['core26'])}), OKC city sales tax and GO bonds",PJ[('OKC',False)]['pub']+det['OKC']['core26'],[('16000US4055000',1.0)],'City sales tax (also paid by commuters/visitors) and GO bonds'),
 ('WAS','Capital One Arena all public money since 1997 (the $12M federal grant and $2M of WMATA money for the Metro link are not DC households\' share)',det['WAS']['core26'],[('04000US11',(det['WAS']['core26']-14.0*CPI[2026]/CPI[1997])/det['WAS']['core26'])],'District of Columbia general fund/GO'),
 ('ORL','Kia Center (2010 build + 2025 renovation)',det['ORL']['core26'],[('05000US12095',1.0)],'Orange County 6% tourist tax - paid mostly by visitors; per-household figure is notional'),
 ('IND','Gainbridge Fieldhouse (1999, CIB capital 2014-34 including the 2020-22 renovation, CIB payments 2001 and 2014-25)',det['IND']['core26'],[('05000US18097',(det['IND']['core26']-reno_pub('IND','2020-22','tif')*CPI[2026]/CPI[2021])/det['IND']['core26']),('04000US18',reno_pub('IND','2020-22','tif')*CPI[2026]/CPI[2021]/det['IND']['core26'])],'Marion County (CIB excise taxes, city) + Indiana (PSDA state-tax capture share)'),
 ('CHA','Spectrum Center (2005, 2014, 2024-25)',det['CHA']['core26'],[('16000US3712000',1.0)],'City of Charlotte hotel/car-rental taxes'),
 ('MEM','FedExForum (2004 build, $80M of the state grant in 2025, subsidies)',det['MEM']['core26'],[('05000US47157',(det['MEM']['core26']-memst)/det['MEM']['core26']),('04000US47',memst/det['MEM']['core26'])],'Shelby County (city+county) + Tennessee ($20M in 2004 for the parking structure + $80M in 2025)'),
 ('HOU','Toyota Center (2003)',det['HOU']['core26'],[('05000US48201',1.0)],'Harris County (HCHSA hotel/car taxes); the expected $95M state grant for the 2026 renovation is pending and not included'),
 ('BKN','Barclays Center direct capital (city $205M, state $100M)',det['BKN']['core26'],[('16000US3651000',205/305),('04000US36',100/305)],'New York City + New York State'),
 ('SAS','Frost Bank Center (2002, 2015) + county $311M for new arena',det['SAS']['core26']+311,[('05000US48029',1.0)],'Bexar County visitor taxes (paid mostly by visitors)'),
 ('DET','Little Caesars Arena DDA TIF',det['DET']['core26'],[('16000US2622000',1.0)],'City of Detroit (TIF also captures county/school taxes; schools backfilled by state)'),
 ('CLE','Rocket Arena (1994, 2017-19, 2019 repairs)',det['CLE']['core26'],[('05000US39035',1.0)],'Cuyahoga County (sin tax, county bonds)'),
 ('POR',f"Moda Center pending rebuild ({f(det['POR']['pend26'])}) + past ({f(det['POR']['core26'])})",det['POR']['pend26']+det['POR']['core26'],[('04000US41',reno_pub('POR','State of Oregon')/(det['POR']['pend26']+det['POR']['core26'])),('05000US41051',reno_pub('POR','Multnomah')/(det['POR']['pend26']+det['POR']['core26'])),('16000US4159000',(reno_pub('POR','City of Portland')+det['POR']['core26'])/(det['POR']['pend26']+det['POR']['core26']))],'Oregon (income-tax capture) + Multnomah County + City of Portland'),
 ('MIL','Fiserv Forum',det['MIL']['core26'],[('05000US55079',(det['MIL']['core26']-TI['MIL']['pub']['general']/2*CPI[2026]/CPI[2018])/det['MIL']['core26']),('04000US55',TI['MIL']['pub']['general']/2*CPI[2026]/CPI[2018]/det['MIL']['core26'])],'Milwaukee County (WCD taxes, county aid cut, city TIF) + Wisconsin (state GPR half of $108.1M)'),
 ('NOP','Smoothie King Center',det['NOP']['core26'],[('04000US22',1.0)],'State of Louisiana (LSED/state)'),
 ('SAC','Golden 1 Center',det['SAC']['core26'],[('16000US0664000',1.0)],'City of Sacramento general fund/parking'),
]
hh_rows=[]
for team,desc,amt,geos,note in D:
    parts=[];
    for g,share in geos:
        nm,n=HH[g]; parts.append(f"{nm} {n:,} hh -> ${amt*share*1e6/n:,.0f}/hh (share {share:.0%})")
        hh_rows.append(dict(team=team, deal=desc, amount_2026_m=round(amt,6), geo_id=g, jurisdiction=nm, households=n, share=round(share,6), per_household_2026=round(amt*share*1e6/n,2), note=note))
    P(f"{team}: {desc}: {f(amt)} | "+' ; '.join(parts)+f" | {note}")
with open(DATA+'/ledger/households.csv','w',newline='') as fh:
    w=csv.DictWriter(fh, fieldnames=list(hh_rows[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(hh_rows)
P('')
P('H. LABELS AND SOURCING')
P('-'*78)
lab={}
for r in cur:
    for k in ['construction_cost_label','public_construction_label']:
        lab.setdefault(k,{}); l=r[k] or 'n/a'; lab[k][l]=lab[k].get(l,0)+1
P('Construction-cost labels: '+str(lab['construction_cost_label'])+' ; public-contribution labels: '+str(lab['public_construction_label']))
P('(a) computed, (b) primary document, (c) press/secondary. Primary documents used include: Wisconsin LFB Informational Paper 18 and WCD audits; Sacramento 2015')
P('lease-revenue bond official statement and construction-monitor reports; Detroit DDA audited statements; Houston 2000 arena letter agreement, 2000 interlocal and 2001 lease;')
P('Indiana CIB ACFRs and MCCRFA audits; Louisiana LLA audits and Senate fiscal decks; DC OCFO fiscal impact statement, Council memo and GAO AIMD-98-223; Bexar County CAFRs')
P('and venue bond official statements; Denver DURA record and the 1997 Arena Agreement; NYC IBO 2009 and 2023; MTA 2009 staff summary; Forest City Enterprises and MSG')
P('SEC filings; Boston Redevelopment Authority 1992 decision; City of Charlotte ACFR and budgets; Gateway EDC audits; Ascent Entertainment SEC filings; City of Memphis CAFRs;')
P('Minnesota Legislative Auditor 2017; Miami-Dade Inspector General IG11-34; Florida OPPAGA 15-01; Orlando/Orange County 2016 interlocal; Phoenix council item 18-3724;')
P('City of Portland ACFRs and term sheet; Salt Lake City ACFR; Oregon SB 1501; Utah PID notices; okc.gov, OCPPA audits and the Oklahoma City Auditor; Miami-Dade budget;')
P('Cook County Assessor data and PTAXSIM. Secondary: Wikipedia, PFM comparables deck for Oregon DAS (June 2026), Bond Buyer, local press.')
P('')
P('I. DISAGREEMENTS RESOLVED (value used <- alternatives)')
P('-'*78)
for r in cur:
    if r['construction_cost_other_reports']: P(f"{r['team']}: cost {r['construction_cost_nominal_m']}M used; other: {r['construction_cost_other_reports']}")
P('CHA: public $170M (Carolina Journal, explicit taxpayer figure) used; the ACFR names occupancy- and rental-car-tax financing, private contributions and sales of city assets without amounts.')
P('CLE: public $120M = county taxable bonds lent to Gateway for arena construction (Gateway FY1999 audit) used; PFM attributed $100M of sin-tax bonds to the arena, but the audit says the 1990 bonds were primarily for the stadium.')
P('ORL: public $418M from the 2016 plan of finance (TDT $270M, land sales $62M, covenant bonds $37M, state and other $30M, interest $19M) used; the $12M of city cash repaid from Magic use payments is counted as the Magic\'s, like other team-repaid financing; PFM counts $430M; earlier split $100M CRA + $330M TDT not supported.')
P('CLE: 2017-19 Transformation public $70M of $196.5M (Gateway FY2024 audit) used; the county\'s bonds were $140M, but the Cavaliers repay one $70M series through added rent (team-repaid, private); press: $185M total.')
P('LAL: the City\'s ~$70M advance (CAO) counted as public, because credits of city revenue (arena admissions fee, convention center parking) offset most of the developer\'s obligation; conduit treatment ($0 public) and Seattle\'s 2017 "$58 million in public financing" are the alternatives.')
P('GSW: public $42.5M of transit capital (SFMTA 2015 plan: General Fund $7.96M + $34.5M from the Mission Bay Transportation Improvement Fund) used; actuals found are smaller ($15.9M of light-rail vehicles, $6.0M appropriated in 2017); Warriors\' $19.4M transit fee private.')
P('IND: capital obligations under the 2014 agreement ($33.5M) and the 2019 agreement ($17.6M of repairs, $120.0M of technology improvements to 2034) from the CIB\'s notes added to the $295M renovation; the 2010 and 2012 amendments\' up to $3.5M not added.')
P('NYK: exemption = IBO\'s FY1984-FY2023 estimate ($946.7M in 2023 dollars) + the Department of Finance\'s FY2024-FY2026 values ($42.2M, $42.9M, $43.3M).')
P('WAS: 1997 public $75.5M (GAO Table 1 plus federal and WMATA Metro money) used; Wikipedia ~$79M; District-only $61.5M.')
P('PHX: 1992 city share $35M (press) used, re-bucketed to tourist taxes per the 2019 council backup; a 1998 arena refunding of $48.74M (CAFR) suggests the city debt was larger.')
P('UTA: 2017 renovation city reimbursement counted at its $22.7M cap (SLC ACFR); the ledger earlier treated the 2017 renovation as fully private.')
P('HOU: public $175M = 2000 Letter Agreement arena budget (primary); press range $125-175M; Rockets rent services a separate rent-supported debt issue (size unknown, not netted). The 2026 renovation\'s expected $95M state grant is pending (no agreement found).')
P('OKC new arena: MAPS 4 money $70M (earlier okc.gov), $78M (OCPPA audited FY2024; okc.gov March 2026; Bond Buyer), ~$99M (Bond Buyer May 2026), $89M (okc.gov Oct 12 2026); public set to $900M arena - $50M Thunder; cost estimate $1.016B (Bond Buyer).')
P('WAS: renovation total $712.5M from Council memo ($800M incl. $87.5M purchase); Monumental now says $1B+.')
P('MIN: purchase $54.6M (Legislative Auditor 2017) vs $54.0M arena line of the 1995 bonds (2003 packet; the $0.6M difference is other acquisition costs) vs ~$54M (SBD 1994); 2017 Taylor $58M (LRL) vs $60M (Wikipedia).')
# other published estimates of public construction money, arena by arena (data/inputs/outside_estimates.csv): the
# arenas where Bradbury's database and the ledger differ by more than a tenth of the larger figure
OB={r['team']:r for r in csv.DictReader(open(DATA+'/inputs/outside_estimates.csv')) if r['estimate']=='bradbury-2026'}
LP={r['team']:float(r['public_construction_2026_m'] or 0) for r in cur}
P(f"Other published estimate, public construction money: J.C. Bradbury's 2026 venue database (Long 2013 for arenas opened through 2010, press after; c; {OB['ATL']['source'].split(' ')[0]}). 2026$, each converted from its opening year; ledger value used <- Bradbury:")
for t in sorted(OB):
    r=OB[t]; y=int(r['opened']); b=float(r['public_nominal_m'] or 0); b26=b*fac(y); l26=LP[t]
    if (b26>0 or l26>0) and abs(l26-b26)>0.1*max(l26,b26):
        P(f"  {t}: {f(l26)} <- {f(b26)} (${b:g}M of ${float(r['total_nominal_m']):g}M in {y}; his source: {r['basis'][:110]})")
P(f"  Totals: ledger {f(sum(LP.values()))}, Bradbury {f(sum(float(r['public_nominal_m'] or 0)*fac(int(r['opened'])) for r in OB.values()))}.")
P('Public shares of construction in other compilations (c; Matheson 2012 / Marquette NSLI 2014, via PolitiFact, https://www.politifact.com/factchecks/2015/may/29/timothy-sheehy/would-paying-half-cost-new-milwaukee-bucks-arena-b/): ATL 29/91%, CHA 100/100%, DAL 50/30%, DEN 22/3%, HOU 82/100%, IND 100/43%, MEM 100/83%, MIA 100/59%, ORL 90/87.5%; the ledger has 29%, 85%, 30%, 20%, 77%, 43%, 100%, 14% and 87% (Miami counts only the county land as construction money and the yearly payments separately).')
P('BOS: $20M public of $241M (Long 2013, via NPR/WAMC, https://www.wamc.org/2013-12-20/the-cost-to-keep-the-home-team-at-home-may-not-be-worth-it, c), probably the Chapter 121A tax arrangement the ledger could not value; ledger $0.')
P('MIN: purchase "$72 million" in 1994 (Mercatus 2018, https://www.mercatus.org/bridge/commentary/target-center-and-minneapolis-celebrate-30-years-stadium-subsidies, c) <- $54.6M used (Legislative Auditor, b).')
P('')
P('J. BUILDING VERSUS REBUILDING SINCE 2014 (2026$)')
P('-'*78)
START=2014
built=[(t['team'],t['opened'],sum(t.get('pub',{}).values())*fac(t['opened'])) for t in TEAMS if t['opened']>=START and t.get('pub')]
rebuilt=[(t['team'],r['cpi_year'],sum(r['pub'].values())*fac(r['cpi_year'])) for t in TEAMS for r in t.get('renos',[]) if r['status'] in ('completed','binding') and r['cpi_year']>=START and r['pub']]
bought=[(t['team'],t['acq']['year'],t['acq']['amt']*fac(t['acq']['year'])) for t in TEAMS if t.get('acq') and t['acq']['year']>=START]
# new arenas under construction with binding public money (outside the 30-arena total, at face value), so that both
# sides count money committed since 2014; districts and pending money are left out on both sides
under=[(p['team'],PJ[(p['team'],False)]['pub']) for p in PROJECTS if p.get('new_arena') and p['status']=='binding']
sb=sum(x[2] for x in built); su=sum(v for k,v in under); sr=sum(x[2] for x in rebuilt)+sum(x[2] for x in bought)
P(f"Public construction money in arenas opened {START}-2026: {f(sb)} ("+', '.join(f"{k} {y} {f(v)}" for k,y,v in built)+")")
P(f"Public money for new arenas under construction, binding (face value): {f(su)} ("+', '.join(f"{k} {f(v)}" for k,v in under)+f"); building since 2014 in all: {f(sb+su)}")
P(f"Public money to renovate or buy existing arenas, {START}-2026 (completed or binding): {f(sr)} = {sr/(sb+su):.2f} times the money to build new arenas ({sr/sb:.2f} times the money in the arenas that opened)")
agg_r={}
for k,y,v in rebuilt+bought: agg_r[k]=agg_r.get(k,0)+v
P('  by arena: '+', '.join(f"{k} {f(v)}" for k,v in sorted(agg_r.items(), key=lambda x:-x[1])))
P(f"Pending on existing arenas (not counted): {f(agg['pend26'])}; new or replacement arenas and districts outside the 30-arena total, binding or voter-approved: {f(sum(p['pub'] for p in C['projects'] if not p['in_team_row']))}")
P('Years: construction at the opening year; renovations at the mid-construction year (future and in-progress work at face value, year 2026); purchases at the transaction year.')
open(DATA+'/ledger/totals.txt','w').write('\n'.join(out)+'\n')
print('\n'.join(out))
