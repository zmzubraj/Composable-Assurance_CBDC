from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix,average_precision_score,roc_auc_score,brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import sanctions_v6 as base
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results';FIG=ROOT/'figures';SEED=20260807
FEATURES=['name_wratio','name_token','name_partial','phonetic','alias_strength','dob_exact','dob_year','pob','nationality','address','country','type_match','used_alias']

def metrics(y,p,t):
    pr=p>=t;tn,fp,fn,tp=confusion_matrix(y,pr,labels=[0,1]).ravel();return {'threshold':t,'precision_benchmark':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),'fpr':fp/max(1,fp+tn),'tp':tp,'fp':fp,'tn':tn,'fn':fn}

def threshold_for_fpr(y,p,max_fpr):
    best=None
    for t in np.linspace(.01,.999,2000):
        m=metrics(y,p,t)
        if m['fpr']<=max_fpr and (best is None or m['recall']>best['recall'] or (m['recall']==best['recall'] and m['precision_benchmark']>best['precision_benchmark'])):best=m
    return best or metrics(y,p,.999)

def ece(y,p,bins=10):
    edges=np.linspace(0,1,bins+1);v=0
    for a,b in zip(edges[:-1],edges[1:]):
        q=(p>=a)&(p<(b if b<1 else b+1e-9))
        if q.any():v+=q.mean()*abs(p[q].mean()-y[q].mean())
    return float(v)

def own_engine(edges,blocked,nodes):
    status=np.zeros(nodes,dtype=bool);status[list(blocked)]=True
    changed=True
    while changed:
        changed=False
        for v in range(nodes):
            if status[v]: continue
            agg=sum(share for u,w,share in edges if w==v and status[u])
            if agg>=.5-1e-12: status[v]=True; changed=True
    return status

def ownership_properties(rng,n=500):
    passed=0
    for _ in range(n):
        nodes=12;edges=[]
        for v in range(1,nodes):
            for u in range(v):
                if rng.random()<.15:edges.append((u,v,float(rng.choice([.1,.2,.25,.3,.4,.49,.5,.6,.8]))))
        blocked=set(rng.choice(nodes,2,False).tolist());a=own_engine(edges,blocked,nodes);b=own_engine(edges,blocked|{int(rng.integers(nodes))},nodes)
        if np.all(~a | b):passed+=1
    return passed,n

def main():
    df=pd.read_csv(RES/'sanctions_v6_scored_queries.csv');tr=df[df.split=='train'].copy();ca=df[df.split=='cal'].copy();te=df[df.split=='test'].copy()
    pipe=Pipeline([('scale',StandardScaler()),('lr',LogisticRegression(max_iter=1000,class_weight='balanced',C=.8,random_state=SEED))]).fit(tr[FEATURES],tr.label)
    ca['prob']=pipe.predict_proba(ca[FEATURES])[:,1];te['prob']=pipe.predict_proba(te[FEATURES])[:,1]
    pres=[]
    thresholds={
      'high_recall': float(np.quantile(ca.loc[ca.label==1,'prob'],.05)),
      'balanced': float(threshold_for_fpr(ca.label.values,ca.prob.values,.001)['threshold']),
      'low_workload': float(max(.90,ca.loc[ca.label==0,'prob'].max()+1e-6))
    }
    ceilings={'high_recall':None,'balanced':.001,'low_workload':0.0}
    for name,t in thresholds.items():
        mt=metrics(te.label.values,te.prob.values,t);mt.update({'policy':name,'calibration_fpr_ceiling':ceilings[name]});pres.append(mt)
    pf=pd.DataFrame(pres);pf.to_csv(RES/'sanctions_v7_policy_points.csv',index=False);bal=pf[pf.policy=='balanced'].iloc[0]
    pos=te[te.label==1].copy();pos['hit']=pos.prob>=bal.threshold;by=pos.groupby('kind').agg(n=('label','size'),candidate_recall=('target_retrieved','mean'),end_to_end_recall=('hit','mean'),median_score=('prob','median')).reset_index();by.to_csv(RES/'sanctions_v7_by_kind.csv',index=False)
    workload=[]
    for _,m in pf.iterrows():
      for prev in [.0001,.0005,.001]:
        ppv=(m.recall*prev)/(m.recall*prev+m.fpr*(1-prev)+1e-15);false=1_000_000*(1-prev)*m.fpr;true=1_000_000*prev*m.recall
        workload.append({'policy':m.policy,'prevalence':prev,'prevalence_adjusted_ppv':ppv,'true_alerts_per_million':true,'false_alerts_per_million':false,'analyst_hours_per_million_at_7min':(true+false)*7/60})
    wf=pd.DataFrame(workload);wf.to_csv(RES/'sanctions_v7_workload.csv',index=False)
    pp,nn=ownership_properties(np.random.default_rng(SEED));base.ownership_tests()
    src=json.loads((RES/'sanctions_v6_summary.json').read_text())
    out={'official_records_indexed':src['ofac_records_indexed'],'official_aliases_indexed':src['official_aliases_indexed'],'total_queries':len(df),'test_queries':len(te),'balanced_threshold':float(bal.threshold),'balanced_recall':float(bal.recall),'balanced_fpr':float(bal.fpr),'balanced_benchmark_precision':float(bal.precision_benchmark),'test_pr_auc':float(average_precision_score(te.label,te.prob)),'test_roc_auc':float(roc_auc_score(te.label,te.prob)),'brier_score':float(brier_score_loss(te.label,te.prob)),'expected_calibration_error_10bin':ece(te.label.values,te.prob.values),'positive_candidate_recall':float(pos.target_retrieved.mean()),'ownership_monotonicity_properties_passed':pp,'ownership_properties_tested':nn,'claim_boundary':'Official OFAC list snapshot and aliases with entity-disjoint positive splits, generated multilingual legitimate and near-match negatives, calibrated policy frontier and prevalence-adjusted workload. Operational certification requires real customer distributions, independent multilingual adjudication, live ownership data and institution-specific legal review.'}
    (RES/'sanctions_v7_summary.json').write_text(json.dumps(out,indent=2));te.to_csv(RES/'sanctions_v7_test_scored.csv',index=False)
    fig,ax=plt.subplots(figsize=(8.8,4.7));x=np.arange(len(pf));ax.bar(x-.2,pf.recall,.4,label='Recall');ax.bar(x+.2,pf.fpr,.4,label='False-positive rate');ax.set_xticks(x,pf.policy);ax.set_yscale('log');ax.set_ylabel('Rate (log scale)');ax.set_title('Calibrated sanctions policy frontier');ax.grid(axis='y',alpha=.22);ax.legend();fig.tight_layout();fig.savefig(FIG/'sanctions_v7_policy_frontier.png',dpi=260);fig.savefig(FIG/'sanctions_v7_policy_frontier.svg');plt.close(fig)
    ww=wf[wf.prevalence==.0001];fig,ax=plt.subplots(figsize=(8.8,4.7));ax.bar(ww.policy,ww.false_alerts_per_million,label='False alerts');ax.bar(ww.policy,ww.true_alerts_per_million,bottom=ww.false_alerts_per_million,label='True alerts');ax.set_ylabel('Alerts per million screenings');ax.set_title('Operational alert workload at 0.01% prevalence');ax.grid(axis='y',alpha=.22);ax.legend();fig.tight_layout();fig.savefig(FIG/'sanctions_v7_workload.png',dpi=260);fig.savefig(FIG/'sanctions_v7_workload.svg');plt.close(fig)
    print(json.dumps(out,indent=2));print(pf.to_string(index=False));print(by.to_string(index=False))
if __name__=='__main__':main()
