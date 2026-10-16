import sys
import csv, datetime, os, statistics as st
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT=ROOT+'/data/threats/'

def months(a,b):
    if not a or not b: return ''
    da=datetime.date(*map(int,a.split('-'))); db=datetime.date(*map(int,b.split('-')))
    return round((db-da).days/30.44,1)

# threat_class: explicit | implied | official_cited | none | unclear | lure_only
# league_role: backed | opposed | neutral/none documented | owned team
L=[]
def add(**k): L.append(k)

add(id='E01',team='MIN Timberwolves',owners='Marv Wolfenson & Harvey Ratner (sellers); Glen Taylor (buyer, Aug 1994, $88.5M)',period='1994-01 to 1995-03',
 threat_class='explicit',
 said_or_done='Paraphrase (Wikipedia citing Star Tribune 1994-02-12): owners sought a public or private buyer for the $73M remaining Target Center mortgage, otherwise the team "would be sold and in all likelihood moved"; owners met San Diego, Nashville and New Orleans representatives (Feb 1994). 1994-05-23: agreed to sell to Top Rank of Louisiana for $152.5M to move to New Orleans (Times-Picayune 1994-05-24).',
 alt_city='New Orleans (also San Diego, Nashville)',
 league_role='opposed: Stern mediated (1994-02-11); relocation committee unanimously blocked sale 1994-06-15; NBA sued to enjoin transfer',
 money_after='Public purchase of Target Center: Laws of Minnesota 1994 ch. 648 (HF 3041) signed 1994-05-10; reported purchase price $48M (Star Tribune via Wikipedia); Minneapolis final financing approval Mar 1995',
 money_usd_m=48, mechanism='Metropolitan Sports Facilities Commission/City purchase financed by bonds (ticket-surcharge backed; 1995 revised plan incl. $12.7M business bond commitments)',
 vote='Legislature + City Council; no referendum (poll: 60% opposed intervention)',
 threat_date='1994-02-11', approval_date='1994-05-10', approval_date_final='1995-03-15',
 outcome='stayed',
 sources='https://www.lrl.mn.gov/guides/target.aspx ; https://en.wikipedia.org/wiki/Minnesota_Timberwolves_failed_move_to_New_Orleans ; https://www.tampabay.com/archive/1994/05/24/timberwolves-sold-to-louisiana-group',
 label='b (LRL) + c', notes='Final-approval day in March 1995 not given by LRL (15th used as placeholder for month count).')

add(id='E02',team='SEA SuperSonics (now OKC)',owners='Barry Ackerley',period='1993-05',threat_class='none',
 said_or_done='No relocation threat documented; Ackerley had floated a private SoDo arena; city offered Coliseum renovation instead.',
 alt_city='', league_role='none documented',
 money_after='Seattle Center Coliseum -> KeyArena renovation: city $74.5M (Sonics ~$21M); council 7-2 (May 1993), 15-yr lease',
 money_usd_m=74.5, mechanism='City bonds repaid from arena revenue sharing', vote='City Council 7-2', threat_date='', approval_date='1993-05-15',
 outcome='stayed (until 2008)', sources='https://en.wikipedia.org/wiki/Climate_Pledge_Arena', label='c', notes='Comparison group N.')

add(id='E03',team='MIA Heat',owners='Micky Arison',period='1996-06 to 1996-11',threat_class='explicit',
 said_or_done='Verbatim (Miami New Times, 1996-11-14): "Back in June the shipping magnate forced the county into an agreement by threatening to move to Broward, a tactic his own negotiators later admitted was a bluff." Arison also sued (unsuccessfully) to block the ballot initiative, then funded an ad campaign.',
 alt_city='Broward County', league_role='none documented',
 money_after='Miami-Dade: $38M bayfront county land + county operating payments ($8.5M/yr in the deal announced days before the vote; later reported $6.4M/yr; $64M paid by 2010); county gets 40% of arena profits above $14M',
 money_usd_m=38, mechanism='Land + annual operating subsidy from county; Heat financed the $213M building', vote='County referendum 1996-11-05 ("overwhelming victory", MNT)',
 threat_date='1996-06-15', approval_date='1996-11-05', outcome='stayed (AmericanAirlines Arena opened 2000-01-02)',
 sources='https://www.miaminewtimes.com/opinion/arena-winners-and-losers-alex-shoots-alex-scores-6361111/ ; https://www.miaminewtimes.com/news/tricky-micky-arisons-heat-doesnt-pay-rent-for-county-owned-arena-6538489/',
 label='c', notes='Threat month June 1996 (day placeholder). Wikipedia dates the threat 1997; contemporaneous MNT (Nov 1996) places it in June 1996. FY2025-26 county budget still shows a $6.4M payment (prior round).')

add(id='E04',team='SAC Kings',owners='Jim Thomas',period='1996-12 to 1997',threat_class='implied',
 said_or_done='Council weighed a $70M loan to keep the Kings in town (SportsBusiness Daily headline 1997-01-31); later accounts say Thomas threatened to sell the money-losing team (secondary).',
 alt_city='none named', league_role='none documented',
 money_after='City loan to team ~$70M (1997); balance reported as $77M owed to the city in 2011',
 money_usd_m=70, mechanism='City loan (repayable), not a grant', vote='City Council (date/count not verified)',
 threat_date='1997-01-15', approval_date='', outcome='stayed',
 sources='https://www.sportsbusinessdaily.com/Daily/Issues/1997/01/31/Facilities-Venues/SACRAMENTO-CITY-COUNCIL-WRESTLES-WITH-KINGS-DECISION.aspx ; https://voiceofoc.org/2011/03/anaheim-council-approves-bond-deal-for-basketball-team/',
 label='u (weak documentation of threat; loan amount reported inconsistently $70M-$82M)', notes='Excluded from capital comparison (loan).')

add(id='E05',team='DAL Mavericks (with NHL Stars)',owners='Ross Perot Jr. (Mavs), Tom Hicks (Stars)',period='1997-1998',threat_class='unclear',
 said_or_done='No owner relocation statement found in this pass; owners supplied >$1.6M of the >$1.9M pro-arena campaign (backers outspent opponents ~20:1).',
 alt_city='', league_role='none documented',
 money_after='$125M city contribution to $420M American Airlines Center (+>$60M infrastructure; $185.3M public through 2018 per city)',
 money_usd_m=125, mechanism='New hotel-occupancy and car-rental taxes', vote='Referendum 1998-01-17: 62,861 to 61,237 (50.7%)',
 threat_date='', approval_date='1998-01-17', outcome='stayed',
 sources='https://www.hillwood.com/newsroom/news-articles/at-the-center-of-something-on-the-rise-5-years-on-aac-gleams-development-takes-shape/ (Dallas Morning News 2006-07-30 reprint) ; https://en.wikipedia.org/wiki/American_Airlines_Center',
 label='c', notes='Treated as no documented threat (N) with an "unclear" flag; sensitivity drops it.')

add(id='E06',team='SAS Spurs',owners='Peter M. Holt group (from 1996)',period='1999',threat_class='unclear',
 said_or_done='No specific 1998-99 owner threat found in this pass. Peter J. Holt (2022 letter): "My family became involved in the Spurs in the 90s because there was a real threat the team would be moved."',
 alt_city='', league_role='none documented',
 money_after='SBC (now Frost Bank) Center $175M: Bexar County bonds backed by hotel-occupancy and car-rental tax increases; Spurs $28.5M (public $146.5M, 84%)',
 money_usd_m=146.5, mechanism='County venue tax bonds', vote='Bexar County referendum Nov 1999 (passed)',
 threat_date='', approval_date='1999-11-02', outcome='stayed',
 sources='https://en.wikipedia.org/wiki/Frost_Bank_Center ; https://spectrumlocalnews.com/tx/san-antonio/news/2022/05/10/spurs-owner-insists-team-will-stay-in-san-antonio',
 label='c', notes='Treated as N with "unclear" flag.')

add(id='E07',team='HOU Rockets',owners='Leslie Alexander',period='1995-2000 (key: 1999-11 to 2000-11)',threat_class='explicit',
 said_or_done='After voters rejected the arena (Nov 1999), Commissioner David Stern: "if there\'s not a new building...I think it\'s certain that the team will be relocated." (Houston Chronicle, 2000-02-13). Rockets talked to other cities: looked at Anaheim in 1999-2000 (LA Times 2001-02-13) and negotiated with Louisville ("Louisville Woos Rockets", Houston Chronicle 2000-05-13).',
 alt_city='Louisville, Anaheim', league_role='backed (commissioner ultimatum)',
 money_after='Toyota Center: city/Harris County-Houston Sports Authority $182M of $235M (77%); Rockets $43M; city bought land',
 money_usd_m=182, mechanism='Harris County-Houston Sports Authority financing; campaign promised "no new taxes of any kind"',
 vote='City Council ~2000-09-13; voters 2000-11-07, 66% yes (1999 version had failed). Pro campaign: Enron/Ken Lay $590K, Reliant $400K',
 threat_date='2000-02-13', approval_date='2000-09-13', approval_date_final='2000-11-07', outcome='stayed',
 sources='http://www.chron.com/CDA/archives/archive.mpl?id=2000_3195424 ; http://www.chron.com/CDA/archives/archive.mpl?id=2000_3214398 ; http://www.chron.com/CDA/archives/archive.mpl?id=2000_3256380 ; http://www.chron.com/CDA/archives/archive.mpl?id=2003_3686610 ; https://en.wikipedia.org/wiki/Toyota_Center',
 label='c', notes='Stern quote via Wikipedia citation of the Chronicle (archive not fetched).')

add(id='E08',team='CHA Hornets (original; now NOP)',owners='George Shinn, Ray Wooldridge',period='1997-2002',threat_class='explicit',
 said_or_done='2001-03-26: Hornets applied to relocate to Memphis (SI/CNN 2001-03-26); withdrew when arena was put in a non-binding referendum; referendum failed June 2001 (43% yes / 57% no). City leaders then said they would not build unless Shinn sold; Hornets requested a move to New Orleans.',
 alt_city='Memphis; New Orleans', league_role='backed relocation (NBA approved move 2002-05-10) and promised Charlotte an expansion team if an arena deal was reached',
 money_after='Same owner/city: none. After departure: Charlotte City Council 2002-11-11 (8-3, no referendum) approved ~$260-265M arena for the expansion Bobcats. Destination: Louisiana 10-yr lease at state-owned New Orleans Arena ($114M, opened 1999) + practice facility (state pledged $6.5M) + inducements (not itemized)',
 money_usd_m=265, mechanism='Charlotte: city-financed arena, no referendum; local companies to put up $50M, recouped via city land incl. the old Coliseum site (ESPN 2002)', vote='Charlotte council 8-3; earlier referendum rejected',
 threat_date='2001-03-26', approval_date='2002-11-11', outcome='moved to New Orleans (2002)',
 sources='https://en.wikipedia.org/wiki/History_of_the_Charlotte_Hornets ; https://www.espn.com/espn/print?id=1334984&type=news ; https://www.espn.com/nba/news/2002/1111/1459528.html ; https://www.fieldofschemes.com/2002/11/12/13/charlotte-council-approves-260m-for-arena/ ; https://www2.ljworld.com/news/2002/may/03/committee_recommends_hornets/',
 label='c', notes='Money followed actual departure, for a new league-awarded team (league-conditioned).')

add(id='E09',team='VAN Grizzlies -> MEM',owners='Michael Heisley (bought 2001-01-25 for $160M); earlier buyer Bill Laurie (1999-2000)',period='1999-2001',threat_class='explicit',
 said_or_done='Heisley said at purchase he would keep the team in Vancouver (Chicago Tribune 2001-01-25), then sought relocation; NBA allowed him to explore a move (ABC News 2001-02-12); applied to move to Memphis 2001-03-26. Laurie\'s 1999 deal carried a $52M bonus if the team moved to St. Louis; NBA opposed.',
 alt_city='Memphis, Louisville, Anaheim, New Orleans, Las Vegas, Nashville, Tampa, Buffalo, San Diego (St. Louis in 1999)',
 league_role='Stern opposed relocation in 1999; Board approved Memphis move unanimously 2001-07-03',
 money_after='Destination: Memphis/Shelby County $250M FedExForum (Public Building Authority bonds; sales-tax rebates, hotel and car-rental taxes) = 100% public. Offers: Louisville $200M arena (+Tricon $5M/yr x20); Las Vegas free land. Vancouver: no public offer found',
 money_usd_m=250, mechanism='PBA bonds', vote='City/County approval 2001 (date not verified); no referendum',
 threat_date='2001-02-12', approval_date='2001-07-03', outcome='moved to Memphis (2001)',
 sources='https://en.wikipedia.org/wiki/Vancouver_Grizzlies_relocation_to_Memphis ; https://www.latimes.com/archives/la-xpm-2001-jul-04-sp-18655-story.html ; https://en.wikipedia.org/wiki/FedExForum',
 label='c', notes='Approval date = NBA approval (local approval preceded it); lag is an upper bound.')

add(id='E10',team='ORL Magic',owners='Rich DeVos family',period='2001-2007',threat_class='implied',
 said_or_done='AP via ESPN 2002-01-12: "Magic owner Rich DeVos plans to sell the team and won\'t require the new owners to keep it in Orlando." DeVos: "I can\'t ask him to do anything" but "I don\'t see any reason why he would want to leave Orlando." Team claimed ~$10M/yr losses blamed on arena.',
 alt_city='none named by owner (NY Sun later described Kansas City as leverage)', league_role='neutral (Vander Weide met Stern about finding a partner)',
 money_after='Amway (now Kia) Center $480M ($380M arena + $100M land/infrastructure): Magic >= $50M upfront + overruns + $1M/yr rent x30; rest public via Orange County tourist-development-tax bonds and city land (~90% public per PFM)',
 money_usd_m=430, mechanism='Tourist development (hotel) tax bonds; city land/infrastructure', vote='Orlando council 6-1 (2007-07-23); Orange County 5-2 (2007-07-26); final 2007-08-06; no referendum',
 threat_date='2002-01-12', approval_date='2007-07-26', outcome='stayed',
 sources='https://www.espn.com/nba/news/2002/0112/1310592.html ; https://www.espn.com/nba/news/2002/0114/1311348.html ; https://en.wikipedia.org/wiki/Kia_Center',
 label='c', notes='Long lag (66 months) - excluded under a 36-month-window sensitivity.')

add(id='E11',team='NOH Hornets (Katrina period)',owners='George Shinn',period='2005-2007',threat_class='explicit',
 said_or_done='Jan 2006 (Pollstar 2006-01-31): Shinn said New Orleans was not ready and argued the team should stay in Oklahoma City, asking "What if next October there\'s 10 feet of water in the city?"',
 alt_city='Oklahoma City', league_role='team returned for 2007-08 (league position not verified here)',
 money_after='No new public package identified in this pass; returned under the 2002 lease',
 money_usd_m='', mechanism='', vote='', threat_date='2006-01-31', approval_date='', outcome='returned to New Orleans (2007)',
 sources='https://news.pollstar.com/2006/01/31/hornets-move-in-question/ ; https://en.wikipedia.org/wiki/Paycom_Center',
 label='c (quote via search summary of Pollstar; not fetched)', notes='Counts as threat without new money.')

add(id='E12',team='POR Trail Blazers',owners='Paul Allen',period='2006-2007',threat_class='implied',
 said_or_done='"Allen\'s Trail Blazers Seek Help to Stay in Portland" (Seattle Times 2006-02-25); team put up for sale June 2006 (Oregonian 2006-06-07), later taken off the market; "much speculation that the Trail Blazers might leave".',
 alt_city='none named', league_role='none documented',
 money_after='None identified; Allen privately re-bought the Rose Garden from creditors in 2007',
 money_usd_m='', mechanism='', vote='', threat_date='2006-02-25', approval_date='', outcome='stayed',
 sources='https://en.wikipedia.org/wiki/Moda_Center ; http://seattletimes.nwsource.com/html/localnews/2002827693_trailblazers25m.html',
 label='c', notes='Counts as threat without new money.')

add(id='E13',team='SEA SuperSonics -> OKC Thunder',owners='Howard Schultz (sold 2006-07-18) -> Clay Bennett, Aubrey McClendon, Tom Ward et al. (PBC)',period='2006-2008',threat_class='explicit',
 said_or_done='Schultz sold to the Oklahoma City group after failing to get $220M for KeyArena (2006). 2007-08-13: McClendon told The Journal Record the group bought the team intending to move it to Oklahoma City (NBA fined him $250,000; Seattle Times 2007-08-23). 2007-11-02: Bennett told Stern the team would move to Oklahoma City (ESPN 2007-11-03).',
 alt_city='Oklahoma City (Renton, WA arena also proposed)', league_role='backed relocation: Board of Governors 28-2 (2008-04-18)',
 money_after='Seattle: none (Initiative 91, Nov 2006, 74% yes, restricted subsidies; state/local governments did not fund a $500M arena complex). Destination: Oklahoma City voters 2008-03-04 approved 15-month 1-cent sales tax for $121.6M Ford Center upgrades + practice facility (62%); collected $103.5M. Seattle got $45M lease-break settlement (2008-07-02)',
 money_usd_m=121.6, mechanism='Temporary city sales tax (destination city)', vote='OKC referendum 62% yes',
 threat_date='2007-11-02', approval_date='2008-03-04', outcome='moved to Oklahoma City (2008)',
 sources='http://www.seattletimes.com/sports/nba/sonics-co-owner-mcclendon-fined-250k ; https://www.espn.com/nba/news/story?id=3091416 ; https://www.espn.com/nba/news/story?id=3277413 ; http://www.nba.com/news/bog_sonics_080418.html ; https://www.seattlepi.com/news/article/sonics-are-oklahoma-city-bound-1278241.php',
 label='c', notes='Lag measured to destination-city money.')

add(id='E14',team='IND Pacers',owners='Herb & Mel Simon',period='2008-2010',threat_class='implied',
 said_or_done='Bond Buyer 2010-07-13: "The team has said for more than two years that it cannot afford the $18 million annual cost of running the fieldhouse." IBJ 2010-07-16: lease runs to 2019 "but the team has the right to opt out"; board member David Shane raised the possibility Simon might sell.',
 alt_city='none named', league_role='none documented',
 money_after='Capital Improvement Board 2010-07-16 (6-1): $33.5M over 3 years ($10M/yr operating + >=$3.5M capital); partial repayment if team leaves before 2019',
 money_usd_m=33.5, mechanism='Capital Improvement Board operating subsidy', vote='CIB 6-1; no referendum',
 threat_date='2008-07-13', approval_date='2010-07-16', outcome='stayed',
 sources='https://www.bondbuyer.com/news/indianapolis-cib-to-vote-on-plan-crafted-to-keep-pacers-in-town ; https://www.ibj.com/articles/21164-cib-approves-33-5-million-deal-to-keep-indiana-pacers',
 label='c', notes='Threat start approximated from "more than two years" (mid-2008). Operating money: excluded from capital comparison.')

add(id='E15',team='NOH Hornets (NBA-owned)',owners='George Shinn -> NBA (Dec 2010, ~$300M) -> Tom Benson (2012-04-13, $338M)',period='2010-12 to 2012',threat_class='implied',
 said_or_done='Lease let the team leave if two-year average attendance fell below a benchmark (reported 14,735; another report 14,883); league ran the team while seeking a local owner. Stern called the March 2012 lease "an important and necessary step toward reaching an agreement with a new owner."',
 alt_city='none named', league_role='owned the team; negotiated lease',
 money_after='2012-03-16 Gov. Jindal announced 10-yr extension to 2024 with ~$50M state-funded arena upgrades (bond issue needing legislative approval); exit clause removed. LSED audits show "revenue benchmark" inducement payments continued ($2.59M FY2014; $2.84M FY2023) plus players\' income-tax pass-through (~$2.1-2.6M/yr)',
 money_usd_m=50, mechanism='State bonds + ongoing LSED inducements', vote='Legislature (bonds); no referendum',
 threat_date='2010-12-05', approval_date='2012-03-16', outcome='stayed',
 sources='https://www.businessreport.com/article/lease-deal-on-n-o-arena-a-signal-of-hornets-commitment-to-stay ; https://www.espn.com/nba/news/story?id=5887687 ; LLA audits (prior round arena_cba/out/pelicans_lsed_payments.csv)',
 label='c + b (LLA audits)', notes='Governor\'s office said inducements would end; audits show benchmark payments continued under the restated agreement.')

add(id='E16',team='SAC Kings (Anaheim)',owners='Joe, Gavin & George Maloof',period='2011-02 to 2012-04',threat_class='explicit',
 said_or_done='2011-02-19: Stern acknowledged Kings-Anaheim relocation talks; team filed trademark "Anaheim Royals" (NBA.com 2011-03-16). Anaheim council (2011-03-29, unanimous) approved $75M bonds ($25M Honda Center upgrades, $50M working capital) to Henry Samueli\'s companies.',
 alt_city='Anaheim (Virginia Beach also courted)', league_role='no approval sought to completion: Maloofs withdrew the bid (April 2011) after Sacramento pledged support; Stern had acknowledged the talks',
 money_after='Sacramento council 2012-03-06 approved term sheet: city $255.5M of $391M arena; Maloofs backed out 2012-04-13 (not executed)',
 money_usd_m=255.5, mechanism='Parking monetization (term sheet)', vote='City Council (term sheet)',
 threat_date='2011-02-19', approval_date='2012-03-06', outcome='stayed (deal collapsed)',
 sources='http://www.nba.com/2011/news/03/16/kings-relocation.ap/ ; https://voiceofoc.org/2011/03/anaheim-council-approves-bond-deal-for-basketball-team/ ; https://www.espn.com/nba/story/_/id/7654643/sacramento-city-council-approves-new-arena-plan-keep-kings ; https://en.wikipedia.org/wiki/Sacramento_Kings_failed_relocation_attempts',
 label='c', notes='Not executed - excluded from money comparison.')

add(id='E17',team='SAC Kings (Seattle sale)',owners='Maloofs -> sale agreement with Chris Hansen & Steve Ballmer group (2013-01-21) -> Vivek Ranadive group (2013-05)',period='2013-01 to 2014-05',threat_class='explicit',
 said_or_done='2013-01-21: Maloofs agreed to sell 65% at a $525M valuation to the Seattle group, which was expected to relocate and use the SuperSonics name (USA Today 2013-01-21); relocation application filed (ESPN 2013-02-06); bid raised to $625M valuation (2013-05-10).',
 alt_city='Seattle (SoDo arena MOU: up to $200M public, approved 2012-09-24 city 6-2 / 2012-10-15 county)',
 league_role='opposed: relocation committee 7-0 against (2013-04-29); Board rejected relocation 22-8 (2013-05-15)',
 money_after='Golden 1 Center: council approved public financing 2014-05-20; city ~$223M cash ($212M bonds + $11M parking/econ-dev funds) of $507M; commonly reported $255M incl. land',
 money_usd_m=255, mechanism='Lease-revenue bonds backed by parking revenue', vote='City Council 2014-05-20; no public vote (petition drive opposed)',
 threat_date='2013-01-21', approval_date='2014-05-20', outcome='stayed',
 sources='https://www.usatoday.com/story/sports/nba/kings/2013/01/20/sacramento-seattle-maloofs-chris-hansen-sonics-supersonics/1850631/ ; http://www.nba.com/2013/news/05/15/kings-stay-in-sacramento.ap/index.html ; https://www.sacbee.com/news/local/city-arena/article2599400.html ; https://en.wikipedia.org/wiki/Golden_1_Center',
 label='c', notes='Non-binding term sheet reported March 2013 (vote count not verified).')

add(id='E18',team='MIL Bucks',owners='Herb Kohl -> Marc Lasry & Wes Edens (Apr 2014, $550M)',period='2014-04 to 2015-08',threat_class='explicit',
 said_or_done='Sale terms let the NBA "buy back the team for $575 million" if "construction on a new building in Milwaukee is not underway by the deadline" (BizTimes 2014-04-22, citing ESPN); Silver: league "prepared to insist that Milwaukee have a plan for a modern arena by 2017." 2015-07-06: Bucks president Peter Feigin told legislators the NBA could buy and move the team to "Las Vegas or Seattle" (KNPR 2015-07-07, citing Milwaukee Business Journal).',
 alt_city='Las Vegas, Seattle', league_role='backed (league buy-back clause)',
 money_after='2015 Wisconsin Act 60: Wisconsin Center District $203M bonds (state GPR $4M/yr to 2035-36 + $4M/yr via cut to county aid; WCD tax revenue bonds) + City $47M TIF ($35M parking, $12M plaza) = $250M of $524.1M (47.7%)',
 money_usd_m=250, mechanism='Appropriation & dedicated-tax revenue bonds; TIF', vote='Senate 21-10 (2015-07-15); Assembly 52-34 (2015-07-28); signed 2015-08-12; no referendum',
 threat_date='2014-04-22', approval_date='2015-08-12', outcome='stayed (Fiserv Forum 2018)',
 sources='https://biztimes.com/nba-will-reserve-right-to-buy-bucks-back/ ; https://knpr.org/knpr/2015-07/will-milwaukee-bucks-find-new-home-las-vegas ; https://www.wpr.org/economy/wisconsin-senate-passes-bucks-arena-deal-bipartisan-vote ; https://fox6now.com/2015/07/28/wisconsin-assembly-approves-milwaukee-bucks-arena-deal/ ; Wis. LFB Informational Paper 18 (Jan 2021) pp.2-3',
 label='b (LFB) + c', notes='Lag 15.7 months from the clause; 1.2 months from Feigin\'s warning.')

add(id='E19',team='PHX Suns',owners='Robert Sarver',period='2018-12 to 2019-01',threat_class='explicit',
 said_or_done='Arizona Republic (Laurie Roberts) reported Sarver told some council members he would move the team to Seattle or Las Vegas if no deal (HoopsRumors 2018-12-12). Disputed: Suns president Jason Rowley denied anyone in the organization threatened to leave (moving out of state a last resort); one council member backtracked; another reported Sarver said "just let me go somewhere else" (as reported; Republic said Sarver did not name the cities himself). Lease had a 2022 opt-out if the arena was deemed "obsolete".',
 alt_city='Seattle, Las Vegas', league_role='none documented',
 money_after='Council 2019-01-23 (6-2): city $150M (Sports Facilities Fund) of $230M renovation; Suns $80M; stay through 2037 (option to 2042); up to $200M penalty if they leave early',
 money_usd_m=150, mechanism='City Sports Facilities Fund', vote='City Council 6-2; no referendum (poll: 66% opposed)',
 threat_date='2018-12-12', approval_date='2019-01-23', outcome='stayed',
 sources='https://hoopsrumors.com/2018/12/sarver-threatens-to-move-suns-to-seattle-or-vegas.html ; https://www.athleticbusiness.com/facilities/stadium-arena/news/15156284/phoenix-suns-owner-mulls-move-amid-arena-fight ; https://www.si.com/nba/2019/01/23/phoenix-city-council-approves-suns-arena-rennovation-deal',
 label='c (threat reported, disputed)', notes='Sensitivity drops it as disputed.')

add(id='E20',team='MEM Grizzlies',owners='Robert Pera',period='2020-06 to 2022-04',threat_class='implied',
 said_or_done='Lease "Shortfall Season" clause (avg paid attendance < 14,900, 64 largest suites unsold, or < 2,500 club seats): city/county must buy the shortfall within 60 days or the team may terminate early (Commercial Appeal / Daily Memphian, June 2020).',
 alt_city='none named', league_role='none documented',
 money_after='Shelby County Commission 2022-04-13 (unanimous): city+county pay $4.95M/yr for four seasons from 2021-22, then $6.3M/yr for four seasons (= $44.8M); team through 2029',
 money_usd_m=44.8, mechanism='Annual operating payments', vote='County Commission unanimous; no referendum',
 threat_date='2020-06-25', approval_date='2022-04-13', outcome='stayed',
 sources='https://dailymemphian.com/article/15067/memphis-grizzlies-fedexforum-lease-provision-robert-pera ; https://www.actionnews5.com/2022/04/13/shelby-county-commissioners-vote-unanimously-keep-grizzlies-memphis-through-2029',
 label='c', notes='Operating money: excluded from capital comparison.')

add(id='E21',team='WAS Wizards (and NHL Capitals)',owners='Ted Leonsis (Monumental Sports & Entertainment)',period='2023-06 to 2024-06',threat_class='explicit',
 said_or_done='Washington Post 2023-06-23: Monumental considering moving both teams to National Landing (Arlington) if DC did not invest. 2023-12-13: Leonsis and Gov. Glenn Youngkin announced a Potomac Yard (Alexandria) arena; plan relied on ~$1.05B project-revenue + $416M lease-revenue bonds, Monumental $403M, Alexandria $106M. House passed HB 1514 59-40; Senate Finance chair L. Louise Lucas refused to docket it; Alexandria declared the deal dead 2024-03-27.',
 alt_city='Alexandria/Potomac Yard, Virginia (earlier Arlington/National Landing)', league_role='none documented',
 money_after='DC offered $500M (Dec 2023). 2024-03-27 deal: DC $515M (incl. ~$87.5M arena purchase), Monumental >= $285M; teams through 2050. Council unanimous emergency approval 2024-04-02; FY2025 budget 2024-06-12',
 money_usd_m=515, mechanism='DC capital budget over 3 years; arena bought and leased back', vote='DC Council unanimous; no referendum',
 threat_date='2023-12-13', approval_date='2024-04-02', outcome='stayed',
 sources='https://www.washingtonpost.com/sports/2023/06/23/monumental-nationals-dc-bowser ; https://www.usatoday.com/story/sports/2023/12/12/washington-wizards-capitals-virginia-relocation-possible/71900930007/ ; https://www.bondbuyer.com/news/financial-framework-for-arena-complex-in-northern-virginia-revealed ; https://wtop.com/local/2024/03/alexandria-says-capitals-wizards-arena-deal-is-dead/ ; https://www.axios.com/local/washington-dc/2024/04/03/capital-one-arena-deal-approved ; https://communityaffairs.dc.gov/node/7231',
 label='c', notes='3.6 months from the explicit announcement; 9.3 months from the June 2023 report.')

add(id='E22',team='POR Trail Blazers',owners='Paul Allen estate (Jody Allen) -> Tom Dundon group (agreement 2025-08-13; NBA approval 2026-03-30; ~$4.25B)',period='2025-08 to 2026-08',threat_class='implied',
 said_or_done='Sale to a Dallas-based buyer; per OPB, Dundon\'s representatives "convinced state and local officials to finance renovations" before the purchase. KATU 2026-07-15: Dundon "has not publicly suggested he intends to move the franchise, but he also has not made a long-term commitment to keeping the team in Portland." Silver: "We are working with both sides to ensure that the Trail Blazers can have a long-term future in Portland."',
 alt_city='none named', league_role='neutral (Silver urging a deal)',
 money_after='Oregon SB 1501 (passed early March 2026): state bonds up to $365M repaid from Rose Quarter income-tax withholding (incl. players), conditional on city/county commitments and a long-term lease; city/county ~$208M pending; council approved negotiating terms Aug 2026',
 money_usd_m=365, mechanism='State bonds repaid by income-tax withholding at the arena', vote='Legislature (early March 2026); no referendum',
 threat_date='2025-08-13', approval_date='2026-03-06', outcome='pending',
 sources='https://www.opb.org/article/2026/06/09/portland-unveils-timeline-for-moda-center-deal/ ; https://katu.com/sports/trail-blazers/story/silver-warns-moda-center-renovation-talks-off-track-fueling-blazers-future-concerns-portland-city-council-adam-national-basketball-association-nba-ripcity-mayor-wilson ; https://www.opb.org/article/2026/03/30/nba-approves-trail-blazers-sale-tom-dundon/ ; https://www.oregon.gov/das/Pages/moda-center-project.aspx',
 label='c (weak: implied only by the out-of-town sale rule)', notes='SB 1501 day in March 2026 not confirmed (06 used). Sensitivity drops it.')

add(id='E23',team='OKC Thunder',owners='Clay Bennett (Professional Basketball Club LLC)',period='2022-01 to 2023-12',threat_class='official_cited',
 said_or_done='Mayor David Holt (2022 State of the City): not funding a new arena could lead the Thunder to "look outside the state for a new home"; Holt (Nov 2023): without a yes vote "It will be the beginning of the end and there\'s no other real path" (PBS NewsHour 2023-11-15). No relocation statement by Bennett or the NBA found; Bennett: arena will "secure the long-term future of the Thunder."',
 alt_city='none named', league_role='none documented',
 money_after='Voters 2023-12-12: 1-cent sales tax for 72 months, >= $900M (incl. $70M MAPS 4); Thunder $50M (~5.5%); 25-yr license (June 2025) with > $1B exit penalties',
 money_usd_m=900, mechanism='Temporary city sales tax', vote='71% yes (41,129 / 16,797); pro side outspent opponents >= 48:1',
 threat_date='', approval_date='2023-12-12', outcome='stayed',
 sources='https://www.pbs.org/newshour/nation/voters-in-oklahoma-city-will-decide-whether-a-new-thunder-arena-is-worth-the-investment ; prior round r4_gov/out/arena_votes.csv',
 label='c', notes='Not an owner/league threat by the stated rule; sensitivity moves it into the threat group.')

add(id='E24',team='SAS Spurs',owners='Peter J. Holt / Julianna Hawn Holt (Spurs Sports & Entertainment)',period='2022-2026',threat_class='none',
 said_or_done='May 2022 request to play more home games outside San Antonio (Austin) raised move fears; Holt letter: "I want to reassure you that the Spurs are in San Antonio to stay." Lease ends 2032; no owner relocation statement found.',
 alt_city='(Austin games only)', league_role='none documented',
 money_after='Bexar County Prop B 2025-11-04 (52.14%): venue tax up to $311M; city up to $489M in non-binding term sheet (2025-08-21, 7-4); Spurs >= $500M + overruns; July 2026 county allowed up to 4 home games/season elsewhere',
 money_usd_m=311, mechanism='County venue tax (voted); city funds (not voted)', vote='Prop B 52.14%; Spurs-funded PAC $9.2M vs ~ $270K opposition',
 threat_date='', approval_date='2025-11-04', outcome='stayed',
 sources='https://spectrumlocalnews.com/tx/san-antonio/news/2022/05/10/spurs-owner-insists-team-will-stay-in-san-antonio ; prior round r4_gov/out/arena_votes.csv',
 label='c', notes='Ambiguous (Austin games) but no owner threat by the stated rule.')

add(id='E25',team='SAS Spurs',owners='Peter M. Holt group',period='2014',threat_class='none',said_or_done='None documented.',alt_city='',league_role='none documented',
 money_after='Bexar County $85M of $101.5M AT&T Center renovation (2014-12-09); lease to 2032 with break fees up to $124M',money_usd_m=85,mechanism='County venue tax',vote='Commissioners Court',threat_date='',approval_date='2014-12-09',outcome='stayed',
 sources='https://www.bexar.org/Archive.aspx?ADID=1520 ; https://en.wikipedia.org/wiki/Frost_Bank_Center',label='b/c',notes='')

add(id='E26',team='MIN Timberwolves',owners='Glen Taylor',period='2015-2016',threat_class='none',said_or_done='None documented.',alt_city='',league_role='none documented',
 money_after='Target Center renovation: city $74M of ~$140M (final approval Mar 2016); team ~$58M; AEG ~$6M',money_usd_m=74,mechanism='City sales taxes redirected under 2012 Vikings stadium law',vote='City Council',threat_date='',approval_date='2016-03-15',outcome='stayed',
 sources='https://www.lrl.mn.gov/guides/target.aspx',label='b',notes='Approval day approximate (March 2016).')

add(id='E27',team='ATL Hawks',owners='Tony Ressler group',period='2016',threat_class='none',said_or_done='None documented.',alt_city='',league_role='none documented',
 money_after='Philips (State Farm) Arena renovation: city $142.5M ($110M rental-car tax extension + $12.5M Turner Field sale + $20M property sales) of $192.5M; Hawks $50M; non-relocation to 2046, up to $200M break fee',money_usd_m=142.5,mechanism='Rental-car tax bonds; asset sales',vote='Atlanta City Council (late 2016)',threat_date='',approval_date='2016-11-07',outcome='stayed',
 sources='https://bondbuyer.com/news/atlanta-to-pay-200m-for-nba-arena-improvements ; https://www.nba.com/news/hawks-and-city-atlanta-plan-philips-arena-renovation',label='c',notes='Approval day approximate.')

add(id='E28',team='CLE Cavaliers',owners='Dan Gilbert',period='2016-12 to 2017-08',threat_class='none',
 said_or_done='No relocation threat documented. After petitions for a referendum, the team withdrew from the deal (2017-08-28/29, citing costs and delays) and revived it when Greater Cleveland Congregations withdrew petitions (2017-08-31).',alt_city='',league_role='none documented',
 money_after='"Q Transformation": public ~$70M principal of $140M (>= $160M with interest, Axios); lease extended to 2034; plus $40.5M (2019) county sin-tax bonds for repairs',money_usd_m=70,mechanism='County bonds, city admissions tax, Destination Cleveland',vote='County & City councils (2017); referendum petitions withdrawn',threat_date='',approval_date='2017-04-24',outcome='stayed',
 sources='https://www.news5cleveland.com/sports/basketball/cavaliers/cavaliers-withdraw-from-140-million-quicken-loans-arena-transformation-project ; https://en.wikipedia.org/wiki/Rocket_Arena ; https://www.axios.com/local/cleveland/2023/02/06/cleveland-cavs-impact',label='c',notes='Approval day approximate.')

add(id='E29',team='IND Pacers',owners='Herb Simon',period='2019',threat_class='none',said_or_done='None documented (lease expiring 2019).',alt_city='',league_role='none documented',
 money_after='CIB (Apr 2019): $360M renovation, state+CIB $270M + city $25M (= $295M public), Pacers $65M; plus ~$12.5M+/yr CIB operating reimbursements 2019-44; Pacers owe up to $750M if they leave',money_usd_m=295,mechanism='CIB bonds (state/county taxes)',vote='CIB',threat_date='',approval_date='2019-04-12',outcome='stayed',
 sources='https://www.wfyi.org/news/articles/city-officials-indiana-pacers-sign-deal-to-keep-team-for-25-years ; CIB ACFR FY2023 Note 9 (prior round)',label='b/c',notes='')

add(id='E30',team='CHA Hornets (current)',owners='Michael Jordan (seller 2023) -> Gabe Plotkin & Rick Schnall',period='2022-2023',threat_class='none',
 said_or_done='None documented. Lease required the city to keep the arena "among the most modern in the league" (WFAE paraphrase); city consultant said $173M was already contractually owed.',alt_city='',league_role='none documented',
 money_after='2022-06-13 (10-1): $215M arena renovation + $60M practice facility = $275M (tourism taxes); lease extended 2030 -> 2045. 2023 sale: no relocation talk found',money_usd_m=275,mechanism='Tourism (hotel/prepared-food) taxes',vote='City Council 10-1',threat_date='',approval_date='2022-06-13',outcome='stayed',
 sources='https://www.wbtv.com/2022/06/01/city-pay-275-million-renovate-spectrum-center-fund-new-practice-facility/ ; https://www.wfae.org/politics/2022-06-14/city-council-approves-arena-renovations-streetcar-study',label='c',notes='Team share not found -> public share n/a.')

add(id='E31',team='UTA Jazz',owners='Ryan & Ashley Smith (Smith Entertainment Group)',period='2024',threat_class='none',said_or_done='None documented for the Jazz (district deal paired with the NHL team relocated from Arizona).',alt_city='',league_role='none documented',
 money_after='Utah SB 272 (2024) + Salt Lake City 0.5% sales tax: ~$900M over 30 yrs ($525M Delta Center, $375M district); referendum drive dropped 2024-10-04',money_usd_m=525,mechanism='City sales tax',vote='No public vote',threat_date='',approval_date='2024-10-04',outcome='stayed',
 sources='prior round r4_gov/out/arena_votes.csv (Utah News Dispatch; SL Tribune 2024-10-04)',label='c',notes='Arena privately owned -> public share n/a.')

add(id='E32',team='ORL Magic',owners='DeVos family',period='2024',threat_class='none',said_or_done='None documented.',alt_city='',league_role='none documented',
 money_after='$226M Orange County tourist-tax package for Kia Center (Nov 2024); Magic $0',money_usd_m=226,mechanism='Tourist development tax',vote='County/City (Nov 2024)',threat_date='',approval_date='2024-11-20',outcome='stayed',
 sources='https://www.cfpublic.org/politics/2024-11-20/orlando-kia-center-camping-world-stadium-improvements-approved',label='c',notes='')

add(id='E33',team='HOU Rockets',owners='Tilman Fertitta',period='2026',threat_class='none',said_or_done='None documented.',alt_city='',league_role='none documented',
 money_after='$180M Toyota Center overhaul with ~$95M State of Texas grant (Apr 2026)',money_usd_m=95,mechanism='State grant',vote='HCHSA board 2026-04-08',threat_date='',approval_date='2026-04-08',outcome='stayed',
 sources='https://therealdeal.com/texas/2026/04/09/toyota-center-in-houston-set-for-180m-overhaul',label='c',notes='')

add(id='E34',team='MEM Grizzlies',owners='Robert Pera',period='2024-2026',threat_class='none',said_or_done='None documented; lease ends 2029.',alt_city='',league_role='none documented',
 money_after='2024 state money for FedExForum (~$230M of $350M with Liberty Bowl) toward ~$550M plan; long-term lease still unsigned (Daily Memphian)',money_usd_m='',mechanism='State appropriation + local hotel/sales taxes',vote='Legislature 2024',threat_date='',approval_date='',outcome='pending',
 sources='https://tennesseelookout.com/2024/07/09/state-spending-350-million-to-bolster-liberty-bowl-and-fedex-forum-in-memphis/ ; https://dailymemphian.com/article/53292',label='c',notes='Pending - excluded.')

add(id='E35',team='DAL Mavericks',owners='Miriam Adelson & Dumont family (majority, Dec 2023); Mark Cuban (minority)',period='2024-2026',threat_class='none',
 said_or_done='Owners pushed Texas casino legalization (2025 session); Patrick Dumont said a casino is not part of the arena plans; club "made it clear" it wants to stay in Dallas; preliminary deal (June 2026) for a site ~10 miles north of downtown; AAC lease runs to July 2031.',alt_city='(within Dallas)',league_role='none documented',
 money_after='None approved as of Oct 2026',money_usd_m='',mechanism='',vote='',threat_date='',approval_date='',outcome='pending',
 sources='https://wtop.com/news/2026/06/dallas-mavericks-have-deal-for-arena-site-that-would-move-club-out-of-downtown-for-1st-time/ ; https://casino.org/news/sands-ceo-dumont-says-mavs-arena-plans-dont-include-casino',label='c',notes='')

add(id='E36',team='NJ Nets -> BKN',owners='Bruce Ratner (bought 2004) -> Mikhail Prokhorov -> Joe Tsai',period='2004-2012',threat_class='implied',
 said_or_done='Team sold (2004) to a developer whose plan was to move it to a new arena in Brooklyn (Atlantic Yards); played in Newark 2010-12, opened Barclays Center 2012-09-21.',alt_city='Brooklyn',league_role='approved sale/move',
 money_after='Destination (NY): IBO (2009) present-value subsidies: NYC $350M and State/MTA $142M incl. tax breaks; federal $194M via tax-exempt PILOT bonds; city net loss $40M (cash) or $180M incl. tax breaks; below-market land worth $50M-$114M excluded',money_usd_m=492,mechanism='Triple-tax-exempt PILOT bonds via Brooklyn Arena LDC; city/state capital; MTA land sale; tax exemptions',vote='No public vote',threat_date='',approval_date='',outcome='moved to Brooklyn (2012)',
 sources='https://www.fieldofschemes.com/news/archives/2009/09/3825_nets_arena_subs.html ; https://www.ibo.nyc.gov/assets/ibo/downloads/pdf/economy-and-employment/2023/2023-march-description-of-public-subsidies-for-madison-square-garden-yankee-stadium-citi-field-and-barclays-center.pdf',label='c (IBO via Field of Schemes) + b (IBO 2023 structure)',notes='Dates for sale agreement and state approval are approximate (not verified here); lag not used.')

add(id='E37',team='GSW Warriors',owners='Joe Lacob & Peter Guber',period='2012-2019',threat_class='none',said_or_done='Moved from Oakland to privately financed Chase Center (San Francisco); no request for public construction money documented.',alt_city='San Francisco (same region)',league_role='approved',
 money_after='None for construction; Oakland/Alameda pursued Warriors for remaining 1996 renovation debt (see left_behind)',money_usd_m=0,mechanism='Private',vote='',threat_date='',approval_date='',outcome='moved within region (2019)',
 sources='https://bondbuyer.com/news/golden-state-warriors-lose-bid-to-escape-oakland-arena-debt',label='c',notes='')

add(id='E38',team='LAC Clippers',owners='Steve Ballmer',period='2017-2024',threat_class='none',said_or_done='Moved from Crypto.com Arena to privately financed Intuit Dome in Inglewood; bought The Forum from MSG for $400M (2020) to end litigation.',alt_city='Inglewood (same region)',league_role='none documented',
 money_after='No public construction money identified',money_usd_m=0,mechanism='Private',vote='',threat_date='',approval_date='',outcome='moved within region (2024)',sources='https://en.wikipedia.org/wiki/Intuit_Dome',label='c',notes='')

add(id='E39',team='DET Pistons',owners='Tom Gores',period='2016-2017',threat_class='lure_only',said_or_done='Detroit induced a move from (private) Palace of Auburn Hills to Little Caesars Arena; DDA notes describe bonds issued "to incentivize the Detroit Pistons to relocate to the City of Detroit."',alt_city='Detroit (from suburb)',league_role='approved move unanimously 2017-08-03',
 money_after='Detroit City Council 2017-06-20 approved $34.5M public funding for the Pistons move (Downtown Development Authority bonds); LCA overall public share est. 58% at 2013 plan',money_usd_m=34.5,mechanism='DDA tax-capture bonds',vote='City Council',threat_date='',approval_date='2017-06-20',outcome='moved within region (2017)',
 sources='https://www.freep.com/story/news/local/michigan/detroit/2017/06/20/detroit-pistons-council-downtown/411786001/ ; Detroit DDA FY2024 financial statements Note H (prior round)',label='b/c',notes='Destination-type money; excluded from T vs N.')

add(id='E40',team='PHI 76ers',owners='Josh Harris & David Blitzer (HBSE)',period='2014; 2022-2025',threat_class='none',said_or_done='No relocation threat documented. 2014: moved practice facility/offices to Camden NJ for a 10-yr $82M Grow NJ tax credit (EDA unanimous, June 2014). 2022-25: proposed privately financed 76 Place (approved by City Council), abandoned Jan 2025 for a joint South Philadelphia arena with Comcast Spectacor (~2031).',alt_city='Camden NJ (practice facility only)',league_role='none documented',
 money_after='NJ $82M tax credit (practice facility; 250-job minimum)',money_usd_m=82,mechanism='State tax credit',vote='NJ EDA',threat_date='',approval_date='2014-06-10',outcome='stayed',
 sources='https://www.cbsnews.com/amp/philadelphia/news/n-j-gives-76ers-82-million-to-build-practice-facility-and-offices-in-camden ; https://en.wikipedia.org/wiki/76_Place_at_Market_East',label='c',notes='Not an arena; excluded from comparison.')

for tid,team,txt in [('E41','BOS Celtics','TD Garden privately owned (Delaware North); lease extended to 2035-36 (2021). No threat or public arena money found.'),
                     ('E42','NYK Knicks','Madison Square Garden: full property-tax exemption since 1982 contingent on hosting the Knicks/Rangers; IBO (2023) assessed foregone tax at ~$42M/yr (FMV $867M). No relocation threat found 1990-2026.'),
                     ('E43','LAL Lakers','Crypto.com Arena privately financed by AEG (1999). No threat found.'),
                     ('E44','CHI Bulls','United Center privately built by Reinsdorf/Wirtz JV (1994); annual property-tax appeals (prior round). No threat found.'),
                     ('E45','DEN Nuggets','Ball (Pepsi) Arena privately built by Kroenke (1999); 2024 council approval of 64-acre private redevelopment. No threat found.'),
                     ('E46','TOR Raptors','Scotiabank (Air Canada) Centre privately financed by MLSE (1999). No threat found.'),
                     ('E47','NOP Pelicans','2023-06-13 amendment extended Smoothie King Center term to 2029; state pays $3.65M/yr Quality-Jobs-equivalent FY2023-29 plus ongoing LSED entitlements (FY2027 budget $17.7M). No threat found.')]:
    add(id=tid,team=team,owners='',period='1990-2026',threat_class='none',said_or_done=txt,alt_city='',league_role='none documented',money_after='',money_usd_m='',mechanism='',vote='',threat_date='',approval_date='',outcome='stayed',
        sources={'E42':'https://www.ibo.nyc.gov/assets/ibo/downloads/pdf/economy-and-employment/2023/2023-march-description-of-public-subsidies-for-madison-square-garden-yankee-stadium-citi-field-and-barclays-center.pdf','E47':'La. Senate Fiscal Services LSED FY26/FY27 presentations (prior round)'}.get(tid,'https://en.wikipedia.org (arena pages)'),label='c',notes='')

# lures without a team (context rows)
add(id='E48',team='(lure) Kansas City',owners='AEG (operator)',period='2004-2007',threat_class='lure_only',said_or_done='Sprint (T-Mobile) Center built without a tenant; used as relocation leverage by others (e.g., NHL Penguins 2006-07). No NBA team came.',alt_city='Kansas City',league_role='',
 money_after='Voters 2004-08-03 approved $4/day rental-car fee + $1.50/night hotel fee; $276M arena; AEG ~$50-54M, NABC $10M -> public ~ $212M (derived)',money_usd_m=212,mechanism='Rental-car and hotel fees',vote='Referendum 2004-08-03 (passed)',threat_date='',approval_date='2004-08-03',outcome='no team',
 sources='https://news.pollstar.com/2005/06/28/sprint-center-breaks-ground/ ; https://www.kcur.org/post/projects-kansas-city-taxpayers-are-still-paying',label='c + a',notes='')
add(id='E49',team='(lure) Seattle',owners='Chris Hansen group',period='2012-2017',threat_class='lure_only',said_or_done='SoDo arena MOU contingent on landing an NBA team; used in the 2013 Kings bid.',alt_city='Seattle',league_role='Board rejected Kings move 2013',
 money_after='Up to $200M public investment (city + county) repaid by arena revenues, contingent on a team; city 6-2 (2012-09-24), county unanimous (2012-10-15); never triggered; MOU lapsed',money_usd_m=200,mechanism='City/county bonds (contingent)',vote='City Council 6-2 / County unanimous',threat_date='',approval_date='2012-10-15',outcome='no team',
 sources='https://council.seattle.gov/2012/09/24/seattle-city-council-approves-arena-legislation/ ; https://en.wikipedia.org/wiki/Sonics_Arena',label='c',notes='')

for r in L:
    r['months_threat_to_approval']=months(r.get('threat_date',''),r.get('approval_date',''))
    r['months_threat_to_final']=months(r.get('threat_date',''),r.get('approval_date_final','')) if r.get('approval_date_final') else ''
cols=['id','team','owners','period','threat_class','said_or_done','alt_city','league_role','money_after','money_usd_m','mechanism','vote','threat_date','approval_date','approval_date_final','months_threat_to_approval','months_threat_to_final','outcome','sources','label','notes']
with open(OUT+'threat_ledger.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore'); w.writeheader()
    for r in L: w.writerow({c:r.get(c,'') for c in cols})
print('ledger rows',len(L))

# ---------------- LEFT BEHIND ----------------
LB=[
 dict(city='Seattle',arena='KeyArena (Seattle Center Coliseum)',team_left='SuperSonics -> Oklahoma City',year_left=2008,
      public_obligation='1995 renovation financed by city (city $74.5M); remaining KeyArena GO debt (Series 2002B, 2003, 2005) defeased in 2008',
      amount_usd_m=34.2, period='defeased 2008', who_paid='Paid from the team\'s $45M lease-break settlement, not taxpayers; rest of settlement: legal $2.8M, improvements $2.3M, other Seattle Center $3.8M, lost revenue $1.4M',
      notes='Contingent extra $30M (tied to 2009 state renovation funding and no new team in 5 years) - payment not confirmed. Seattle Center budget later reported thin arena reserves after the Sonics left.',
      sources='https://arenadigest.com/200809232477/basketball/nba-basketball/sonics-settlement-to-pay-off-keyarena-debt ; https://www.bondbuyer.com/news/seattle-to-pay-off-arena-gos ; https://www.seattlepi.com/news/article/sonics-are-oklahoma-city-bound-1278241.php',label='c'),
 dict(city='Oakland / Alameda County',arena='Oracle (Oakland) Arena',team_left='Warriors -> San Francisco',year_left=2019,
      public_obligation='Coliseum Authority $140M lease-revenue bonds (Aug 1996) for $121M renovation; $80M refunded 2015 (taxable); final maturity 2026; debt service $5.1-10.5M/yr FY2020-26 (Moody\'s)',
      amount_usd_m=55.7, period='par outstanding 2019-06-30', who_paid='Arbitrator (2018) held the Warriors liable for the shortfall between arena net revenue and remaining debt (reported ~ $40M); upheld by Superior Court, Court of Appeal (Aug 2020); Cal. Supreme Court denied review 2020-12-09. City and county (50/50 JPA owners) remain the backstop.',
      notes='Taxpayer exposure was limited by the arbitration win; arena lost its NBA tenant.',
      sources='https://bondbuyer.com/news/golden-state-warriors-lose-bid-to-escape-oakland-arena-debt ; https://www.ktvu.com/news/warriors-ordered-to-pay-40m-for-oracle-arena-upgrades',label='c'),
 dict(city='Charlotte',arena='Charlotte Coliseum (1988)',team_left='Hornets -> New Orleans',year_left=2002,
      public_obligation='$52M city arena financed with $47M general-obligation bonds approved by voters in 1984; debt still outstanding in the 1990s; payoff date not found',
      amount_usd_m=47, period='original GO bonds (1984)', who_paid='City of Charlotte',
      notes='Coliseum (14 yrs old at departure) demolished June 2007. City then built a ~$260-265M uptown arena (approved 2002-11-11) for the expansion Bobcats; city finance dept put total cost incl. debt at ~$430M over the building\'s life; 2022 added $275M more.',
      sources='https://lockerroom.johnlocke.org/2013/01/30/state-refuses-to-aid-panthers-stadium-upgrades/ ; https://reason.com/1997/07/01/building-buzz/ ; https://www.espn.com/nba/news/2002/1111/1459528.html',label='c (payoff not verified)'),
 dict(city='Vancouver',arena='General Motors Place (Rogers Arena)',team_left='Grizzlies -> Memphis',year_left=2001,
      public_obligation='None identified: arena built 1995 with C$160M private financing (Orca Bay)',amount_usd_m=0,period='',who_paid='n/a',
      notes='No public arena debt left behind found.',sources='https://en.wikipedia.org/wiki/Rogers_Arena',label='c'),
 dict(city='New Jersey (East Rutherford / Newark)',arena='Meadowlands (Izod) Arena; Prudential Center',team_left='Nets -> Brooklyn',year_left=2012,
      public_obligation='State-owned Meadowlands arena (NJSEA) lost tenants; projected $8.5M loss for 2015; NJSEA voted 2015-01-15 to close it. Newark had pledged $210M (airport-lease settlement money) toward the $375M Prudential Center, originally also meant for the Nets, who played there only 2010-12',
      amount_usd_m=210, period='Newark pledge (2000s)', who_paid='City of Newark; NJSEA/State',
      notes='NBA-specific share of NJSEA debt not quantified.',sources='https://en.wikipedia.org/wiki/Meadowlands_Arena ; https://en.wikipedia.org/wiki/Prudential_Center',label='c'),
 dict(city='Kansas City',arena='Sprint (T-Mobile) Center (2007)',team_left='(built to attract NBA/NHL; none came; Kings had left KC in 1985)',year_left='',
      public_obligation='Arena bonds repaid from $4/day rental-car and $1.50/night hotel fees (2004 vote); ~$213M variable-rate bonds later restructured',
      amount_usd_m=202.9, period='outstanding per KCUR list (date unclear); payoff 2040', who_paid='Visitor fees; general fund tapped for the first time (~$4.2M) in FY2021-22 for repairs',
      notes='No anchor tenant 17+ years after opening.',sources='https://www.kcur.org/post/projects-kansas-city-taxpayers-are-still-paying ; https://news.yahoo.com/kansas-city-may-spend-millions-100000159.html ; https://www.bondbuyer.com/news/kansas-city-on-track-to-sell-53m-for-performing-arts-center-garage',label='c (figure date unclear)'),
 dict(city='Memphis',arena='Pyramid Arena (1991)',team_left='Grizzlies -> FedExForum (same city)',year_left=2004,
      public_obligation='$65M public arena; city spent $7M to adapt it for the Grizzlies (2001); team contract barred competing use, building went dark 2004-2015 until Bass Pro lease',
      amount_usd_m=7, period='2001 adaptation spending', who_paid='City of Memphis',notes='Within-city move.',sources='https://en.wikipedia.org/wiki/Memphis_Pyramid',label='c'),
 dict(city='Sacramento',arena='ARCO / Sleep Train Arena',team_left='Kings -> Golden 1 Center (same city)',year_left=2016,
      public_obligation='City loan to team (1997, ~$70M; $77M balance in 2011)',amount_usd_m=77,period='2011 balance',who_paid='Loan owed by team to city; resolution not verified here',
      notes='Within-city move; old arena site later donated for a medical campus (2021).',sources='https://voiceofoc.org/2011/03/anaheim-council-approves-bond-deal-for-basketball-team/ ; https://en.wikipedia.org/wiki/ARCO_Arena',label='u'),
 dict(city='Oklahoma City (temporary host)',arena='Ford Center',team_left='Hornets -> New Orleans',year_left=2007,
      public_obligation='$200,000 renovation for Hornets lease; no debt found',amount_usd_m=0.2,period='2005',who_paid='City',notes='',sources='https://en.wikipedia.org/wiki/Paycom_Center',label='c'),
]
cols2=['city','arena','team_left','year_left','public_obligation','amount_usd_m','period','who_paid','notes','sources','label']
with open(OUT+'left_behind.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols2); w.writeheader()
    for r in LB: w.writerow(r)
print('left_behind rows',len(LB))
