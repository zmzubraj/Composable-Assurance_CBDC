from __future__ import annotations
import json, math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import wilcoxon
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; RES=ROOT/'results'; FIG=ROOT/'figures'
RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
LOCAL_COLS=['out_count','out_sum','out_mean','out_unique','in_count','in_sum','in_mean','in_unique','turnover','pass_ratio','active_days','near_threshold','external_ratio']
NET_COLS=['in_degree','out_degree','pagerank','cross_pip_ratio','scc_size','two_hop','fan_in_score','fan_out_score']

def ci(vals):
    a=np.asarray(vals,float)
    if len(a)<2:return float(a.mean()),float(a.mean()),float(a.mean())
    boots=[];rng=np.random.default_rng(1947)
    for _ in range(1500):boots.append(float(rng.choice(a,len(a),replace=True).mean()))
    return float(a.mean()),float(np.quantile(boots,.025)),float(np.quantile(boots,.975))

def generate_dataset(seed:int,n:int=600,n_pips:int=6):
    rng=np.random.default_rng(seed)
    pips=rng.integers(0,n_pips,n); labels=np.zeros(n,int); typ=np.array(['benign']*n,object); groups=np.arange(n)+10_000_000
    tx=[]
    # heterogeneous benign activity; PIPs observe only their own incident transactions
    act=rng.gamma(2.1,2.4,n); wealth=rng.lognormal(4.1,.75,n)
    for src in range(n):
        k=int(rng.poisson(act[src]+1))
        for _ in range(k):
            same=rng.random()<.70
            pool=np.where(pips==pips[src])[0] if same else np.where(pips!=pips[src])[0]
            dst=int(rng.choice(pool));
            if dst==src: dst=(dst+1)%n
            amount=float(rng.lognormal(np.log(max(8,wealth[src]/45)),.8))
            day=int(rng.integers(0,120)); tx.append((src,dst,amount,day,0,'benign'))
    # benign look-alike motifs create difficult negatives
    for _ in range(24):
        hub=int(rng.integers(n)); senders=rng.choice([x for x in range(n) if x!=hub],rng.integers(5,10),replace=False); d=int(rng.integers(5,110))
        for src in senders: tx.append((int(src),hub,float(rng.uniform(500,1300)),d+int(rng.integers(0,5)),0,'benign_charity'))
    for _ in range(20):
        proc=int(rng.integers(n)); srcs=rng.choice([x for x in range(n) if x!=proc],rng.integers(4,7),replace=False); dsts=rng.choice([x for x in range(n) if x!=proc],rng.integers(2,4),replace=False); d=int(rng.integers(5,105)); total=0
        for src in srcs:
            am=float(rng.uniform(250,1500)); total+=am; tx.append((int(src),proc,am,d+int(rng.integers(0,3)),0,'benign_marketplace'))
        for dst in dsts: tx.append((proc,int(dst),total/len(dsts)*rng.uniform(.92,1.02),d+3,0,'benign_marketplace'))
    for _ in range(20):
        nodes=rng.choice(n,5,replace=False); base=float(rng.uniform(600,2600)); d=int(rng.integers(5,105))
        for i in range(4): tx.append((int(nodes[i]),int(nodes[i+1]),base*rng.uniform(.88,1.08),d+i,0,'benign_supply_chain'))
    gid=1
    def mark(nodes,name):
        nonlocal gid
        g=2_000_000+gid;gid+=1
        for x in nodes: labels[x]=1;typ[x]=name;groups[x]=g
    # independent components, with realistic variation per generated dataset
    for _ in range(7): # layering
        nodes=rng.choice(n,5,replace=False);mark(nodes,'layering');base=float(rng.uniform(600,2600));d=int(rng.integers(10,100))
        for i in range(4): tx.append((int(nodes[i]),int(nodes[i+1]),base*(.94**i),d+i,1,'layering'))
    for _ in range(7): # smurfing
        hub=int(rng.integers(n));senders=rng.choice([x for x in range(n) if x!=hub],rng.integers(6,12),replace=False);mark(np.r_[hub,senders],'smurfing');d=int(rng.integers(10,105))
        for s in senders:tx.append((int(s),hub,float(rng.uniform(450,1300)),d+int(rng.integers(0,4)),1,'smurfing'))
    for _ in range(7): # mule funnel
        mule=int(rng.integers(n));srcs=rng.choice([x for x in range(n) if x!=mule],rng.integers(4,8),replace=False);out=int(rng.integers(n));nodes=np.r_[mule,srcs,out];mark(nodes,'mule_funnel');d=int(rng.integers(10,103));tot=0
        for s in srcs:
            am=float(rng.uniform(250,1500));tot+=am;tx.append((int(s),mule,am,d+int(rng.integers(0,3)),1,'mule_funnel'))
        tx.append((mule,out,tot*rng.uniform(.89,.97),d+3,1,'mule_funnel'))
    for _ in range(5): # cyclic layering
        nodes=rng.choice(n,4,replace=False);mark(nodes,'cycle');base=float(rng.uniform(600,2600));d=int(rng.integers(10,105))
        for i in range(4):tx.append((int(nodes[i]),int(nodes[(i+1)%4]),base*rng.uniform(.88,1.03),d+i,1,'cycle'))
    acct=pd.DataFrame({'acct':np.arange(n),'pip':pips,'label':labels,'typology':typ,'group':groups})
    return pd.DataFrame(tx,columns=['src','dst','amount','time','illicit','typology']),acct

def local_features(tx:pd.DataFrame,acct:pd.DataFrame,allowed):
    allowed=set(map(int,allowed)); own=acct.set_index('acct').loc[sorted(allowed)]
    # Each PIP computes features only for its own accounts from incident payments it can lawfully observe.
    rows=[]
    for pip,part in own.groupby('pip'):
        ids=set(map(int,part.index)); t=tx[(tx.src.isin(ids)) | (tx.dst.isin(ids))].copy()
        out=t[t.src.isin(ids)].groupby('src').agg(out_count=('amount','size'),out_sum=('amount','sum'),out_mean=('amount','mean'),out_unique=('dst','nunique'),active_days=('time','nunique'),near_threshold=('amount',lambda x:float(((x>=700)&(x<1000)).mean())))
        inc=t[t.dst.isin(ids)].groupby('dst').agg(in_count=('amount','size'),in_sum=('amount','sum'),in_mean=('amount','mean'),in_unique=('src','nunique'))
        f=pd.DataFrame(index=part.index).join(out).join(inc).fillna(0)
        f['turnover']=f.out_sum+f.in_sum;f['pass_ratio']=np.minimum(f.out_sum,f.in_sum)/(np.maximum(f.out_sum,f.in_sum)+1)
        ext=defaultdict(lambda:[0,0])
        pipmap=acct.set_index('acct').pip.to_dict()
        for _,r in t[t.src.isin(ids)].iterrows():ext[int(r.src)][1]+=1;ext[int(r.src)][0]+=int(pipmap.get(int(r.dst),-1)!=pip)
        f['external_ratio']=[ext[int(a)][0]/max(1,ext[int(a)][1]) for a in f.index]
        rows.append(f)
    f=pd.concat(rows).sort_index();return f.join(own[['label','typology','group','pip']]).reset_index()

def network_features(tx:pd.DataFrame,acct:pd.DataFrame,allowed):
    allowed=set(map(int,allowed));t=tx[tx.src.isin(allowed)&tx.dst.isin(allowed)].copy();base=local_features(tx,acct,allowed).set_index('acct')
    agg=t.groupby(['src','dst']).agg(weight=('amount','sum'),count=('amount','size')).reset_index();g=nx.DiGraph();g.add_weighted_edges_from((int(r.src),int(r.dst),float(r.weight)) for _,r in agg.iterrows())
    base['in_degree']=[g.in_degree(a) if a in g else 0 for a in base.index];base['out_degree']=[g.out_degree(a) if a in g else 0 for a in base.index]
    pr=nx.pagerank(g,weight='weight',max_iter=200) if len(g) else {};base['pagerank']=[pr.get(a,0) for a in base.index]
    pipmap=acct.set_index('acct').pip.to_dict();cross=defaultdict(lambda:[0,0])
    for _,r in agg.iterrows():cross[int(r.src)][1]+=r['count'];cross[int(r.src)][0]+=r['count']*int(pipmap.get(int(r.src))!=pipmap.get(int(r.dst)))
    base['cross_pip_ratio']=[cross[a][0]/max(1,cross[a][1]) for a in base.index];base['scc_size']=0.0
    for comp in nx.strongly_connected_components(g):
        for a in comp:
            if a in base.index:base.loc[a,'scc_size']=len(comp)
    base['two_hop']=0.;base['fan_in_score']=0.;base['fan_out_score']=0.
    for a in base.index:
        if a in g:
            one=set(g.successors(a));two=set()
            for b in one:two.update(g.successors(b))
            base.loc[a,'two_hop']=len(two-{a});base.loc[a,'fan_in_score']=g.in_degree(a)*base.loc[a,'pass_ratio'];base.loc[a,'fan_out_score']=g.out_degree(a)*base.loc[a,'pass_ratio']
    return base.reset_index()

def split_accounts(acct,seed):
    ix=np.arange(len(acct));tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.35,random_state=seed).split(ix,acct.label,acct.group));return acct.iloc[tr].acct.values,acct.iloc[te].acct.values

def model(seed):return make_pipeline(RobustScaler(),HistGradientBoostingClassifier(max_iter=180,max_leaf_nodes=20,learning_rate=.055,l2_regularization=2,class_weight='balanced',random_state=seed))

def metrics(y,p):
    k=max(1,int(.01*len(y)));top=np.argsort(-p)[:k]
    return {'pr_auc':average_precision_score(y,p),'roc_auc':roc_auc_score(y,p),'recall_at_1pct':float(np.mean(np.isin(np.where(y==1)[0],top))),'precision_at_1pct':float(y[top].mean()),'alerts_per_100k':1000}

def transform(tx,kind,rng):
    good=tx[tx.illicit==0].copy();bad=tx[tx.illicit==1].copy();out=[]
    for _,r in bad.iterrows():
        if kind=='dispersion':
            k=4
            for j in range(k):out.append((int(r.src),int(r.dst),float(r.amount/k*rng.uniform(.88,1.12)),int(r.time+j*4+rng.integers(0,3)),1,r.typology))
        elif kind=='time_shift':out.append((int(r.src),int(r.dst),float(r.amount),int(r.time+rng.integers(10,35)),1,r.typology))
        elif kind=='combined':
            k=5
            for j in range(k):out.append((int(r.src),int(r.dst),float(r.amount/k*rng.uniform(.82,1.18)),int(r.time+j*6+rng.integers(0,4)),1,r.typology))
        else:out.append(tuple(r))
    return pd.concat([good,pd.DataFrame(out,columns=tx.columns)],ignore_index=True)

def eval_independent(n_datasets=8):
    rows=[];attack_rows=[]
    for ds in range(n_datasets):
        tx,acct=generate_dataset(7000+ds);train_ids,test_ids=split_accounts(acct,900+ds)
        tr_local=local_features(tx,acct,train_ids);te_local=local_features(tx,acct,test_ids)
        tr_net=network_features(tx,acct,train_ids);te_net=network_features(tx,acct,test_ids)
        ml=model(ds).fit(tr_local[LOCAL_COLS],tr_local.label);mn=model(ds+100).fit(tr_net[LOCAL_COLS+NET_COLS],tr_net.label)
        pl=ml.predict_proba(te_local[LOCAL_COLS])[:,1];pn=mn.predict_proba(te_net[LOCAL_COLS+NET_COLS])[:,1];y=te_net.label.values
        for name,p in [('pip_local',pl),('network',pn)]:rows.append({'dataset_id':ds,'model':name,**metrics(y,p),'n_test':len(y),'n_pos':int(y.sum())})
        # transaction-level evasion variants, scored with the unchanged trained network model
        score_by={'none':pn}
        for j,kind in enumerate(['dispersion','time_shift','combined']):
            tt=transform(tx,kind,np.random.default_rng(20_000+ds*10+j));et=network_features(tt,acct,test_ids);score_by[kind]=mn.predict_proba(et[LOCAL_COLS+NET_COLS])[:,1]
        illicit=(y==1);benign=~illicit
        # oracle-query upper-bound: adversary selects the lowest score-producing allowed transformation for its own illicit accounts
        oracle=np.array(pn,copy=True);stack=np.vstack([score_by[k] for k in score_by]);oracle[illicit]=stack[:,illicit].min(axis=0)
        for kind,p in list(score_by.items())+[('adaptive_oracle',oracle)]:
            mm=metrics(y,p);attack_rows.append({'dataset_id':ds,'attack':kind,**mm,'mean_illicit_score':float(p[illicit].mean()),'evasion_success_rate':float(np.mean(p[illicit]<pn[illicit]-1e-9)) if kind!='none' else 0.0})
    return pd.DataFrame(rows),pd.DataFrame(attack_rows)

def load_amlsim():
    tx=pd.read_csv(DATA/'amlsim_transactions.csv').rename(columns={'SENDER_ACCOUNT_ID':'src','RECEIVER_ACCOUNT_ID':'dst','TX_AMOUNT':'amount','TIMESTAMP':'time','IS_FRAUD':'illicit'})[['src','dst','amount','time','illicit']]
    tx['typology']=np.where(tx.illicit==1,'alert','benign')
    acct0=pd.read_csv(DATA/'amlsim_accounts.csv');alerts=pd.read_csv(DATA/'amlsim_alerts.csv')
    ids=acct0.ACCOUNT_ID.astype(int).values;rng=np.random.default_rng(991);pip=rng.integers(0,6,len(ids));bad=set(alerts.SENDER_ACCOUNT_ID)|set(alerts.RECEIVER_ACCOUNT_ID)
    # connected alert components define groups; benign accounts remain singleton
    parent={int(i):int(i) for i in ids}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        a,b=find(int(a)),find(int(b));parent[b]=a
    for _,r in alerts.iterrows():union(r.SENDER_ACCOUNT_ID,r.RECEIVER_ACCOUNT_ID)
    acct=pd.DataFrame({'acct':ids,'pip':pip});acct['label']=acct.acct.isin(bad).astype(int);acct['typology']=np.where(acct.label==1,'alert','benign');acct['group']=[find(x) if x in bad else 30_000_000+x for x in ids]
    return tx,acct

def eval_amlsim_sensitivity():
    tx,acct=load_amlsim();rows=[]
    for split in range(1):
        trids,teids=split_accounts(acct,500+split);tr_l=local_features(tx,acct,trids);te_l=local_features(tx,acct,teids);tr_n=network_features(tx,acct,trids);te_n=network_features(tx,acct,teids)
        for name,tr,te,cols in [('pip_local',tr_l,te_l,LOCAL_COLS),('network',tr_n,te_n,LOCAL_COLS+NET_COLS)]:
            m=model(400+split).fit(tr[cols],tr.label);p=m.predict_proba(te[cols])[:,1];rows.append({'sensitivity_split':split,'model':name,**metrics(te.label.values,p),'n_test':len(te),'n_pos':int(te.label.sum())})
    return pd.DataFrame(rows)

def main():
    runs,attacks=eval_independent(8);amlsim=eval_amlsim_sensitivity();runs.to_csv(RES/'aml_independent_runs.csv',index=False);attacks.to_csv(RES/'aml_adversarial_runs.csv',index=False);amlsim.to_csv(RES/'aml_amlsim_sensitivity.csv',index=False)
    summary=[]
    for m,g in runs.groupby('model'):
        for metric in ['pr_auc','roc_auc','recall_at_1pct','precision_at_1pct']:
            a=ci(g[metric]);summary.append({'benchmark':'8 independently generated graphs','model':m,'metric':metric,'mean':a[0],'ci_low':a[1],'ci_high':a[2]})
    piv=runs.pivot(index='dataset_id',columns='model',values='pr_auc');stat,p=wilcoxon(piv.network,piv.pip_local,alternative='two-sided')
    test={'independent_datasets':len(piv),'mean_pr_auc_delta':float((piv.network-piv.pip_local).mean()),'wilcoxon_two_sided_p':float(p),'interpretation':'valid across independently generated graphs; AMLSim split runs are reported only as sensitivity analysis and are not treated as independent replications'}
    for a,g in attacks.groupby('attack'):
        c=ci(g.pr_auc);summary.append({'benchmark':'adaptive transaction-evasion stress','model':a,'metric':'pr_auc','mean':c[0],'ci_low':c[1],'ci_high':c[2]})
    pd.DataFrame(summary).to_csv(RES/'aml_summary.csv',index=False);(RES/'aml_test.json').write_text(json.dumps(test,indent=2))
    # figures
    import matplotlib.pyplot as plt
    s=pd.DataFrame(summary);q=s[(s.benchmark=='8 independently generated graphs')&(s.metric=='pr_auc')];fig,ax=plt.subplots(figsize=(7.4,4.4));x=np.arange(len(q));ax.bar(x,q['mean']);ax.errorbar(x,q['mean'],yerr=[q['mean']-q.ci_low,q.ci_high-q['mean']],fmt='none',capsize=5,color='black');ax.set_xticks(x,['PIP-local only','Cross-PIP network']);ax.set_ylabel('PR-AUC');ax.set_title('AML evaluation across 8 independently generated graphs');ax.set_ylim(0,max(.8,q.ci_high.max()+.08));fig.tight_layout();fig.savefig(FIG/'aml_independent.png',dpi=220);plt.close(fig)
    q=s[(s.benchmark=='adaptive transaction-evasion stress')&(s.metric=='pr_auc')].copy();order=['none','dispersion','time_shift','combined','adaptive_oracle'];q=q.set_index('model').loc[order];fig,ax=plt.subplots(figsize=(8,4.4));x=np.arange(len(q));ax.bar(x,q['mean']);ax.errorbar(x,q['mean'],yerr=[q['mean']-q.ci_low,q.ci_high-q['mean']],fmt='none',capsize=4,color='black');ax.set_xticks(x,['Baseline','Split + disperse','Delay','Combined','Adaptive lower bound'],rotation=10);ax.set_ylabel('PR-AUC');ax.set_title('Transaction-level adversarial stress (unchanged trained model)');fig.tight_layout();fig.savefig(FIG/'aml_adversarial.png',dpi=220);plt.close(fig)
    print(json.dumps(test,indent=2));print(pd.DataFrame(summary).to_string(index=False))
if __name__=='__main__':main()
