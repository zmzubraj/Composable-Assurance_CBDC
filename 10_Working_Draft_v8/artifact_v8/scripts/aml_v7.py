from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from scipy.stats import wilcoxon,binomtest
import aml_features as base
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results';FIG=ROOT/'figures';RES.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)

def family_dataset(seed,family):
    tx,acct=base.generate_dataset(seed,n=700,n_pips=7);r=np.random.default_rng(seed+91)
    if family=='calendar_payroll':
        tx=tx.copy();ben=tx.illicit.eq(0);tx.loc[ben,'time']=(tx.loc[ben,'time']//7)*7+r.choice([0,1,4,5,6],ben.sum(),p=[.12,.12,.18,.30,.28]);add=[]
        for _ in range(30):
            emp=int(r.integers(len(acct)));ees=r.choice([x for x in range(len(acct)) if x!=emp],r.integers(8,18),False);day=int(r.choice([14,29,44,59,74,89,104]))
            for e in ees:add.append((emp,int(e),float(r.uniform(900,4200)),day,0,'benign_payroll'))
        tx=pd.concat([tx,pd.DataFrame(add,columns=tx.columns)],ignore_index=True);m=tx.illicit.eq(1);tx.loc[m,'time']=(tx.loc[m,'time']+r.integers(0,45,m.sum()))%120
    elif family=='merchant_network':
        acct=acct.copy();acct['pip']=(acct.acct*5+r.integers(0,3,len(acct)))%7;add=[]
        for m in r.choice(len(acct),40,False):
            for b in r.choice([x for x in range(len(acct)) if x!=m],r.integers(12,25),False):add.append((int(b),int(m),float(r.lognormal(5.4,.7)),int(r.integers(0,120)),0,'benign_marketplace'))
        tx=pd.concat([tx,pd.DataFrame(add,columns=tx.columns)],ignore_index=True);m=tx.illicit.eq(1);tx.loc[m,'amount']*=r.uniform(.35,.72,m.sum());tx.loc[m,'time']=(tx.loc[m,'time']+r.integers(0,20,m.sum()))%120
    elif family=='remittance_corridor':
        acct=acct.copy();corridor=(acct.acct%5);acct['pip']=(corridor*2+r.integers(0,2,len(acct)))%7;add=[]
        hubs=r.choice(len(acct),28,False)
        for h in hubs:
            senders=r.choice([x for x in range(len(acct)) if x!=h],r.integers(10,24),False)
            for s in senders:add.append((int(s),int(h),float(r.lognormal(5.0,.8)),int(r.integers(0,120)),0,'benign_remittance'))
        tx=pd.concat([tx,pd.DataFrame(add,columns=tx.columns)],ignore_index=True);m=tx.illicit.eq(1);tx.loc[m,'amount']*=r.uniform(.5,.9,m.sum());tx.loc[m,'time']=(tx.loc[m,'time']+r.integers(0,35,m.sum()))%120
    return tx,acct

def budget_metrics(y,p,b):
    k=max(1,int(b*len(y)));idx=np.argsort(-p)[:k];return float(np.mean(np.isin(np.where(y==1)[0],idx))),float(y[idx].mean())

def evaluate(ds,fam,seed):
    tx,acct=family_dataset(seed,fam);tr,te=base.split_accounts(acct,seed+500);rows=[];models={}
    for name,A,B,cols in [('pip_local',base.local_features(tx,acct,tr),base.local_features(tx,acct,te),base.LOCAL_COLS),('network',base.network_features(tx,acct,tr),base.network_features(tx,acct,te),base.LOCAL_COLS+base.NET_COLS)]:
        mod=base.model(seed).fit(A[cols],A.label);p=mod.predict_proba(B[cols])[:,1];y=B.label.values;models[name]=(mod,cols,p,y)
        rec={'dataset_id':ds,'family':fam,'seed':seed,'model':name,'pr_auc':base.average_precision_score(y,p),'roc_auc':base.roc_auc_score(y,p),'n_test':len(y),'n_pos':int(y.sum())}
        for b in [.005,.01,.02]:rec[f'recall_{b:g}'],rec[f'precision_{b:g}']=budget_metrics(y,p,b)
        rows.append(rec)
    mod,cols,p0,y=models['network'];att=[]
    for j,k in enumerate(['dispersion','time_shift','combined']):
        tt=base.transform(tx,k,np.random.default_rng(seed*10+j));ev=base.network_features(tt,acct,te);p=mod.predict_proba(ev[cols])[:,1];att.append({'dataset_id':ds,'family':fam,'attack':k,'pr_auc':base.average_precision_score(y,p),'recall_1pct':budget_metrics(y,p,.01)[0]})
    return rows,att

def main():
    families=['profile_mix','calendar_payroll','merchant_network','remittance_corridor'];rows=[];att=[];ds=0
    for fi,f in enumerate(families):
        for rep in range(4):
            r,a=evaluate(ds,f,31000+fi*100+rep);rows+=r;att+=a;ds+=1
    df=pd.DataFrame(rows);ad=pd.DataFrame(att);df.to_csv(RES/'aml_v7_runs.csv',index=False);ad.to_csv(RES/'aml_v7_adversarial.csv',index=False)
    piv=df.pivot(index=['dataset_id','family'],columns='model',values='pr_auc').reset_index();piv['delta']=piv.network-piv.pip_local;piv.to_csv(RES/'aml_v7_paired_effects.csv',index=False)
    rng=np.random.default_rng(20260807);boot=np.array([rng.choice(piv.delta.values,len(piv),True).mean() for _ in range(10000)]);w=wilcoxon(piv.network,piv.pip_local,alternative='two-sided');sg=binomtest(int((piv.delta>0).sum()),len(piv),.5,alternative='two-sided')
    fam=piv.groupby('family').agg(local_mean=('pip_local','mean'),network_mean=('network','mean'),delta_mean=('delta','mean'),delta_sd=('delta','std')).reset_index();fam.to_csv(RES/'aml_v7_family_effects.csv',index=False)
    # Workload and outcome protocol.
    work=[]
    for b in [.005,.01,.02]:
      for model,g in df.groupby('model'):
        work.append({'alert_budget':b,'model':model,'mean_recall':g[f'recall_{b:g}'].mean(),'mean_precision':g[f'precision_{b:g}'].mean(),'alerts_per_million':int(b*1_000_000)})
    pd.DataFrame(work).to_csv(RES/'aml_v7_workload.csv',index=False)
    outcome=pd.DataFrame([
      ['Alert quality','precision, typology coverage, evidence sufficiency','model validation team','monthly'],['Investigation','time to disposition, escalation, repeat-alert rate','PIP investigators','quarterly'],['Reporting','SAR/STR quality, FIU feedback and timeliness','FIU and supervisors','quarterly'],['Disruption','holds, restraint, recovery and network dismantling','FIU/law enforcement','annual'],['Harm and fairness','false account restrictions, complaints and subgroup disparity','consumer protection/privacy authority','quarterly'],['Governance','drift, override, retraining and model-change approvals','model-risk committee','continuous']],columns=['outcome_layer','registered_measure','independent_owner','cadence']);outcome.to_csv(RES/'aml_v7_prospective_outcomes.csv',index=False)
    out={'independent_graphs':len(piv),'generator_families':len(families),'mean_pr_auc_delta':float(piv.delta.mean()),'bootstrap_95_ci':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],'wilcoxon_two_sided_p':float(w.pvalue),'sign_test_two_sided_p':float(sg.pvalue),'positive_effect_graphs':int((piv.delta>0).sum()),'claim_boundary':'Predictive synthetic benchmark evidence. FATF effectiveness requires prospective investigator, FIU, supervisory, disruption and harm outcomes on governed jurisdictional data.'};(RES/'aml_v7_summary.json').write_text(json.dumps(out,indent=2))
    fig,ax=plt.subplots(figsize=(8.8,4.7));x=np.arange(len(fam));w0=.36;ax.bar(x-w0/2,fam.local_mean,w0,label='PIP-local');ax.bar(x+w0/2,fam.network_mean,w0,label='Cross-PIP network');ax.set_xticks(x,['Profile mix','Calendar/payroll','Merchant network','Remittance corridor']);ax.set_ylabel('PR-AUC');ax.set_title('AML predictive performance across 16 independent graphs');ax.grid(axis='y',alpha=.22);ax.legend();fig.tight_layout();fig.savefig(FIG/'aml_v7_families.png',dpi=260);fig.savefig(FIG/'aml_v7_families.svg');plt.close(fig)
    print(json.dumps(out,indent=2));print(fam.to_string(index=False))
if __name__=='__main__':main()
