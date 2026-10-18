import sys
import csv, os, statistics as st
from scipy.stats import mannwhitneyu
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT=ROOT+'/data/threats/'
# CPI-U annual averages from the same series the funding ledger uses (FRED CPIAUCNS, not seasonally adjusted);
# dollars here are 2025 dollars, and the site converts them to 2026 dollars with the ledger's factor
_m={}
for r in csv.DictReader(open(ROOT+'/data/inputs/cpi/CPIAUCNS.csv')):
    try: _m.setdefault(int(r['observation_date'][:4]),[]).append(float(r['CPIAUCNS']))
    except ValueError: pass
CPI={y:sum(v)/len(v) for y,v in _m.items()}
def r25(x,y): return x*CPI[2025]/CPI[y]

# deal, ledger id, year, public capital $M, total project $M (None if n/a), group T/N, flags
# Values follow the funding ledger (data/ledger): public capital and the total cost it records for the same deal.
D=[
 ('MIN Target Center purchase','E01',1994,54.6,None,'T','explicit;league opposed'),
 ('MIA AmericanAirlines Arena (land)','E03',1996,37.6,272.5,'T','explicit; + $6.4M/yr county operating (not in capital); total = county land + the $234.9M the county capitalized'),
 ('HOU Toyota Center','E07',2000,195,235,'T','explicit;league-backed'),
 ('ORL Amway Center','E10',2007,418,480,'T','implied;66-month lag'),
 ('NOH arena upgrades','E15',2012,50,50,'T','implied;league-owned team'),
 ('SAC Golden 1 Center','E17',2013,223.1,559.2,'T','explicit;league opposed move'),
 ('MIL Fiserv Forum','E18',2015,250,524.1,'T','explicit;league-backed'),
 ('PHX arena renovation','E19',2019,150,234.9,'T','explicit;disputed'),
 ('WAS Capital One Arena','E21',2024,515,800,'T','explicit'),
 ('SEA KeyArena renovation','E02',1993,74.5,95.5,'N','none'),
 ('DAL American Airlines Center','E05',1998,125,420,'N','unclear'),
 ('SAS SBC Center','E06',1999,159.9,188.4,'N','unclear'),
 ('SAS AT&T Center renovation','E25',2015,85,101.5,'N','none'),
 ('MIN Target Center renovation','E26',2016,74,140,'N','none'),
 ('ATL Philips Arena renovation','E27',2016,142.5,192.5,'N','none'),
 ('CLE Q transformation','E28',2017,70,196.5,'N','none'),
 ('IND Fieldhouse renovation and 2019 agreement capital','E29',2019,432.7,497.7,'N','none'),
 ('CHA Spectrum Center + practice','E30',2022,275,None,'N','none'),
 ('OKC new arena','E23',2023,850,900,'N','official_cited'),
 ('UTA Delta Center (sales tax)','E31',2024,525,None,'N','none'),
 ('ORL Kia Center package','E32',2024,226,226,'N','none'),
 ('SAS new arena (county binding; share uses city term sheet)','E24',2025,311,1300,'N','none;share 860/1300 planned'),
]
# SAS 2025 share: planned public $860M (county $311M + city up to $489M under the term sheet + $60M of Midtown TIRZ debt
# for the site) of ~$1.3B
rows=[]
for name,i,y,pub,tot,g,fl in D:
    share = (860/1300 if i=='E24' else (pub/tot if tot else None))
    rows.append(dict(deal=name,id=i,year=y,public_m=pub,public_m_2025=round(r25(pub,y),1),total_m=tot,share=share,group=g,flags=fl))

def summ(sel,label):
    a=[r['public_m_2025'] for r in sel]; s=[r['share'] for r in sel if r['share'] is not None]
    return '%s: n=%d | public $ (2025$) median %.0f, mean %.0f | public share n=%d median %.0f%%, mean %.0f%%'%(label,len(a),st.median(a),st.mean(a),len(s),100*st.median(s),100*st.mean(s))
def test(T,N,label):
    a=[r['public_m_2025'] for r in T]; b=[r['public_m_2025'] for r in N]
    sa=[r['share'] for r in T if r['share'] is not None]; sb=[r['share'] for r in N if r['share'] is not None]
    p1=mannwhitneyu(a,b,alternative='two-sided').pvalue; p2=mannwhitneyu(sa,sb,alternative='two-sided').pvalue
    return '%s\n  %s\n  %s\n  Mann-Whitney two-sided p: dollars %.2f, share %.2f'%(label,summ(T,'threat'),summ(N,'no threat'),p1,p2)

T=[r for r in rows if r['group']=='T']; N=[r for r in rows if r['group']=='N']
out=[]
out.append('COMPARISON: public money after a documented relocation threat vs. deals without one (NBA home-city arena deals, 1993-2026)')
out.append('Generated from threat_ledger.csv; dollars are nominal public CAPITAL commitments converted to 2025 dollars with approximate CPI-U annual averages.')
out.append('')
out.append('CLASSIFICATION RULE')
out.append('- Threat group (T): the owner or the league made an explicit threat (named another city, filed/announced a move, sold to a buyer intending to move, or the league stated it would move/buy the team) or an implied threat (talks with another city, "exploring options", invoking or holding a lease out clause, sale to an out-of-town buyer with no commitment to keep the team, sale offered with no relocation restriction) during the same arena campaign that produced the approval.')
out.append('- No-threat group (N): no such owner/league statement found. Includes cases where only public officials cited relocation risk (OKC 2023, flagged) and two 1998-99 cases with unclear records (DAL 1998, SAS 1999, flagged).')
out.append('- Excluded: operating-only deals (IND 2010 $33.5M; MEM 2022 $44.8M; both threat cases), the 1997 Sacramento loan, unexecuted term sheets (SAC 2012), pending deals (MEM 2024, POR 2026, HOU 2026), and destination-city money (reported separately below).')
out.append('- Public share = public capital / total project cost where both are known (n/a for MIN 1994 purchase, CHA 2022, UTA 2024).')
out.append('')
out.append('DEALS'); out.append('id | year | deal | group | public $M nominal | 2025$ | share | flags')
for r in sorted(rows,key=lambda r:(r['group'],r['year'])):
    out.append('%s | %d | %s | %s | %.1f | %.0f | %s | %s'%(r['id'],r['year'],r['deal'],r['group'],r['public_m'],r['public_m_2025'],('%.0f%%'%(100*r['share'])) if r['share'] is not None else 'n/a',r['flags']))
out.append('')
out.append('RESULTS')
out.append(test(T,N,'Main comparison'))
T2=[r for r in T if 'disputed' not in r['flags'] and 'weak' not in r['flags']]
out.append(test(T2,N,'S1: drop the disputed threat case (PHX 2019)'))
N3=[r for r in N if r['flags'] not in ('unclear',)]
out.append(test(T,N3,'S2: drop unclear no-threat cases (DAL 1998, SAS 1999)'))
T4=T+[r for r in N if r['flags']=='official_cited']; N4=[r for r in N if r['flags']!='official_cited']
out.append(test(T4,N4,'S3: count official-cited risk (OKC 2023) as a threat'))
T5=[r for r in T if r['year']>=2010]; N5=[r for r in N if r['year']>=2010]
out.append(test(T5,N5,'S4: approvals 2010-2026 only'))
T6=[r for r in T if r['id']!='E10']
out.append(test(T6,N,'S5: 36-month window (drops ORL 2007, 66-month lag)'))
NEW={'E03','E07','E10','E17','E18','E05','E06','E23','E24'}
def strat(kind,ids_ok):
    t=[r for r in T if ids_ok(r['id'])]; n=[r for r in N if ids_ok(r['id'])]
    return '%s\n  %s\n  %s'%(kind,summ(t,'threat'),summ(n,'no threat'))
out.append(strat('S6: stratified - NEW ARENAS only (MIA land, HOU, ORL, SAC, MIL vs DAL, SAS99, OKC, SAS25)',lambda i:i in NEW))
out.append(strat('S7: stratified - RENOVATIONS/UPGRADES only',lambda i:i not in NEW and i!='E01'))
out.append('')
# lag stats from ledger
L=list(csv.DictReader(open(OUT+'threat_ledger.csv')))
th=[x for x in L if x['threat_class'] in ('explicit','implied')]
pending=['E22']  # approved by the legislature, final agreements pending (as in the funding ledger)
lag=[(x['id'],x['team'],float(x['months_threat_to_approval'])) for x in th if x['months_threat_to_approval'] and x['id'] not in ('E08','E09','E13','E16')+tuple(pending)]
lv=sorted(v for _,_,v in lag)
out.append('THREAT OUTCOMES (explicit/implied episodes in threat_ledger.csv: n=%d)'%len(th))
same=['E01','E03','E07','E10','E14','E15','E17','E18','E19','E20','E21','E50']
left=['E08','E09','E13','E36']; nomoney=['E11','E12','E16']
assert sorted(same+left+nomoney+pending)==sorted(x['id'] for x in th), 'every counted threat needs one outcome'
out.append('- Same-city public money approved afterward: %d (%s)'%(len(same),', '.join(same)))
out.append('- Same-city public money approved but not final: %d (%s: Oregon\'s SB 1501 bonds, pending agreements)'%(len(pending),', '.join(pending)))
out.append('- Team left; destination city paid (Memphis $250M, Oklahoma City $121.6M, New York PV ~$492M non-federal; New Orleans package): %d (%s)'%(len(left),', '.join(left)))
out.append('- No new money and team stayed: %d (%s; SAC 2011 was followed by E17 money)'%(len(nomoney),', '.join(nomoney)))
out.append('- Months from first documented threat to first same-city approval (n=%d): median %.1f, min %.1f, max %.1f; %d of %d within 24 months'%(len(lv),st.median(lv),min(lv),max(lv),sum(v<=24 for v in lv),len(lv)))
out.append('  ' + '; '.join('%s %s %.1f'%(i,t.split(' (')[0],v) for i,t,v in sorted(lag,key=lambda z:z[2])))
out.append('- League role: backed or enabled the threat in HOU 2000 (Stern ultimatum), MIL 2015 (buy-back clause), SEA->OKC 2008 and CHA->NOH 2002 (relocations approved); opposed in MIN 1994, SAC 2011 and SAC 2013 - yet home-city money still followed in MIN 1994 and SAC 2014.')
out.append('')
out.append('DESTINATION / LURE MONEY (not in T vs N): Memphis 2001 $250M (100% public); Oklahoma City 2008 $121.6M sales tax; Charlotte 2002 ~$265M for the expansion team after the Hornets left; New York 2006-09 PV $350M city + $142M state/MTA (+$194M federal via tax-exempt bonds); Detroit 2017 $34.5M for the Pistons; Kansas City 2004 ~$212M (no team came); offers not used: Seattle 2012 up to $200M, Anaheim 2011 $75M bonds, Louisville 2001 $200M arena, Virginia 2024 ~$1.47B bonds.')
out.append('')
out.append('CAVEATS')
out.append('- Small samples (%d vs %d); p-values are descriptive only;'%(len(T),len(N))+' none of the differences is statistically distinguishable from chance. Deal sizes are driven by era, arena age and scope (new build vs renovation), so a raw comparison cannot isolate the effect of a threat.')
out.append('- Selection: threats are documented mostly where reporters covered them; "no documented threat" is not proof none was made privately. Several no-threat deals were renovations required by lease clauses (e.g., CHA 2022 obligations, IND 2019).')
out.append('- Capital only: operating subsidies (MIA $6.4M/yr; IND CIB ~$12.5M+/yr; MEM $44.8M) and tax exemptions are excluded; including them would raise totals for some threat cases.')
out.append('- CPI: FRED CPIAUCNS annual averages (2025 uses 11 months; October 2025 was not published), the series the funding ledger uses.')
out.append('')
out.append('EVIDENCE ON PAYOFF (task 4)')
out.append('- Bradbury, J.C., Coates, D. & Humphreys, B.R. (2023). "The impact of professional sports franchises and venues on local economies: A comprehensive survey." Journal of Economic Surveys 37(4): 1389-1431. doi:10.1111/joes.12533 (online 2022-09-07). Abstract: >130 studies over 30+ years "continue to confirm the decades-old consensus of very limited economic impacts of professional sports teams and stadiums. Even with added nonpecuniary social benefits ... welfare improvements from hosting teams tend to fall well short of covering public outlays."')
out.append('- Gayer, T., Drukker, A.J. & Gold, A.K. (2016). "Tax-exempt municipal bonds and the financing of professional sports stadiums." Brookings Economic Studies, Sept 2016: of 45 major-league venues built or significantly renovated since 2000, 36 used tax-exempt bonds ($13.0B principal); present-value federal subsidy $3.2B (about $3.7B including bondholder windfall). Updated: Drukker, Gayer & Gold (2020), National Tax Journal 73(1): 157-196, doi:10.17310/ntj.2020.1.05 - 57 venues, 43 with tax-exempt financing, $3.6B PV subsidy, $4.3B federal revenue loss.')
out.append('- Promised vs delivered (NBA arenas):')
out.append('  1) Barclays Center / Atlantic Yards (Nets): 2014 agreement required 2,250 affordable units by 2025-05-31; about 1,374 built and 876 not started; $2,000/month per missing unit penalties (>$1.75M/month) waived by Empire State Development after the developer threatened to sue (Gothamist, 2025). IBO (2009): arena a net loss to the city of $40M (cash) to $180M (with tax breaks).')
out.append('  2) Little Caesars Arena / District Detroit (Pistons since 2017): Detroit News analysis found more than a dozen of the 50 promised blocks emptier than at the 2014 launch and 24 buildings in the Ilitch footprint still empty; a neighborhood advisory council member cited ~700 promised residential units not built while parking was (HBO Real Sports / Local 4, 2019). Ilitch Holdings called the HBO report inaccurate.')
out.append('  3) American Airlines Center / Victory Park (Mavericks): public $185.3M ($125M arena + >$60M infrastructure); by 2006 the district was "less than half completed, and its taxable value about one-third, when compared with original outlooks" (Dallas Morning News, 2006-07-30).')
out.append('  (Also: Oklahoma City 2008 arena tax collected $103.5M vs $121M projected; Kansas City arena still without an anchor tenant.)')
open(OUT+'comparison.txt','w').write('\n'.join(out)+'\n')
# machine-readable copy of the main results, for the site
import json
def stats(sel):
    a=[r['public_m_2025'] for r in sel]; sh=[r['share'] for r in sel if r['share'] is not None]
    return dict(n=len(a), median_public_m_2025=st.median(a), mean_public_m_2025=st.mean(a), n_share=len(sh), median_share=st.median(sh), mean_share=st.mean(sh))
res=dict(deals=rows, threat=stats(T), no_threat=stats(N),
         p_dollars=mannwhitneyu([r['public_m_2025'] for r in T],[r['public_m_2025'] for r in N],alternative='two-sided').pvalue,
         p_share=mannwhitneyu([r['share'] for r in T if r['share'] is not None],[r['share'] for r in N if r['share'] is not None],alternative='two-sided').pvalue,
         episodes_explicit_or_implied=len(th), same_city_money=same, pending_money=pending, team_left=left, no_new_money=nomoney,
         lag_months=[dict(id=i,team=t,months=v) for i,t,v in sorted(lag,key=lambda z:z[2])], lag_median=st.median(lv), lag_within_24=sum(v<=24 for v in lv), lag_window_months=24)
json.dump(res, open(OUT+'comparison.json','w'), indent=1, sort_keys=True)
print('\n'.join(out))
