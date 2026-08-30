from pathlib import Path
import json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results';FIG=ROOT/'figures';RES.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
# Official/public anchors already documented in the manuscript. They define evidence bounds, not estimates.
DEPOSITS_EUR_BN=9860.95234
BIS_POINT=1750
ECB_LOW,ECB_HIGH=500,3000
limits=np.array([500,750,1000,1250,1500,1750,2000,2250,2500,2750,3000],float)
# Partial-identification arithmetic: H <= tau*D/(N*a).
rows=[]
for tau in [.03,.05,.075,.10]:
  for n_m in [250,300,358]:
    for adoption in [.25,.50,.75,1.0]:
      ceiling=tau*(DEPOSITS_EUR_BN*1e9)/(n_m*1e6*adoption)
      rows.append({'maximum_gross_exposure_share':tau,'eligible_users_million':n_m,'adoption_share':adoption,'implied_holding_limit_ceiling_eur':ceiling})
ceil=pd.DataFrame(rows);ceil.to_csv(RES/'economic_v7_identified_ceiling.csv',index=False)
# Candidate policy-set classification under disclosed constraints. No behavioral estimation is implied.
policy=[]
for h in limits:
    gross_300_full=300e6*h/(DEPOSITS_EUR_BN*1e9)
    policy.append({'holding_limit_eur':h,'inside_ecb_assessed_range':bool(ECB_LOW<=h<=ECB_HIGH),'distance_from_bis_point_eur':abs(h-BIS_POINT),'gross_exposure_share_300m_full':gross_300_full,'passes_5pct_exposure_cap':bool(gross_300_full<=.05),'passes_10pct_exposure_cap':bool(gross_300_full<=.10)})
pol=pd.DataFrame(policy);pol.to_csv(RES/'economic_v7_candidate_set.csv',index=False)
# Flow-limit arithmetic: minimum days to satisfy an aggregate conversion desire C with daily flow fraction f of deposits.
fr=[]
for stress in [.02,.05,.09]:
  for f in [.0025,.005,.01,.02]:
    fr.append({'desired_conversion_share':stress,'daily_system_flow_limit_share':f,'minimum_days_if_binding':int(np.ceil(stress/f))})
pd.DataFrame(fr).to_csv(RES/'economic_v7_flow_duration.csv',index=False)
# Data requirements and update rule.
req=pd.DataFrame([
 ['Household demand','wallet choice, desired balances, payment substitution, run-state conversion','representative panel + pilot telemetry','quarterly and stress-triggered'],
 ['Bank stability','LCR/NSFR, uninsured deposits, replacement funding, collateral and facility access','supervisory bank microdata','monthly in pilot, quarterly in steady state'],
 ['Distribution','income, age, disability, region, cash dependence and merchant acceptance','linked survey/service-quality data','semiannual'],
 ['Operations','sweep failures, rejected conversions, fraud loss and support burden','production observability and complaint data','continuous'],
 ['Macroeconomy','policy rates, deposit rates, funding spreads, credit response and confidence','central-bank macrofinancial models','policy cycle'],
],columns=['domain','parameters','minimum evidence','update cadence'])
req.to_csv(RES/'economic_v7_required_data.csv',index=False)
out={'method':'partial identification plus constrained robust policy selection','publicly_assessed_range_eur':[ECB_LOW,ECB_HIGH],'published_structural_point_eur':BIS_POINT,'universal_optimum_identified':False,'example_5pct_exposure_ceiling_300m_full_eur':float(ceil[(ceil.maximum_gross_exposure_share==.05)&(ceil.eligible_users_million==300)&(ceil.adoption_share==1.0)].implied_holding_limit_ceiling_eur.iloc[0]),'policy_conclusion':'Public evidence determines a feasible candidate set, not a universal point. A jurisdiction selects and updates H, flow limits and remuneration using predeclared stability, utility, inclusion and distributional constraints with local microdata.','claim_boundary':'Official public anchors and transparent accounting only; no new causal demand, welfare or bank-run estimate.'}
(RES/'economic_v7_summary.json').write_text(json.dumps(out,indent=2))
# Figures
fig,ax=plt.subplots(figsize=(8.8,4.7));
for a,g in ceil[(ceil.eligible_users_million==300)&(ceil.maximum_gross_exposure_share.isin([.03,.05,.10]))].groupby('maximum_gross_exposure_share'):
    ax.plot(100*g.adoption_share,g.implied_holding_limit_ceiling_eur,marker='o',label=f'{100*a:.0f}% gross-exposure ceiling')
ax.axhspan(ECB_LOW,ECB_HIGH,alpha=.10,label='ECB publicly assessed range');ax.axhline(BIS_POINT,ls='--',lw=1,label='BIS structural point');ax.set(xlabel='Adoption among 300 million eligible users (%)',ylabel='Implied holding-limit ceiling (EUR)',title='Partial identification: exposure constraints imply a policy set, not a universal point');ax.set_ylim(0,6500);ax.grid(alpha=.22);ax.legend(fontsize=8,ncol=2);fig.tight_layout();fig.savefig(FIG/'economic_v7_identified_set.png',dpi=260);fig.savefig(FIG/'economic_v7_identified_set.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.8,4.6));x=pol.holding_limit_eur;ax.plot(x,100*pol.gross_exposure_share_300m_full,marker='o');ax.axhline(5,ls='--',label='5% exposure constraint');ax.axhline(10,ls=':',label='10% exposure constraint');ax.axvline(BIS_POINT,ls='-.',label='BIS structural point');ax.set(xlabel='Candidate holding limit (EUR)',ylabel='Mechanical gross exposure / deposits (%)',title='Transparent exposure envelope for 300 million fully participating users');ax.grid(alpha=.22);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'economic_v7_exposure.png',dpi=260);fig.savefig(FIG/'economic_v7_exposure.svg');plt.close(fig)
print(json.dumps(out,indent=2))
