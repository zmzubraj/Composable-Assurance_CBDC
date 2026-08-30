from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import privacy_dp_v5 as base
ROOT=Path(__file__).resolve().parents[1];RES=ROOT/'results';FIG=ROOT/'figures';RES.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)

def pf_one_to_many(x,M):
    d=M-x
    cos=(M@x)/(np.linalg.norm(M,axis=1)*np.linalg.norm(x)+1e-12)
    return np.c_[np.abs(d),d*d,M*x,cos]

def matrix(pop,users,profile,attacker,session):
    return np.vstack([base.view(pop[int(u)][session],profile,attacker) for u in users])

def train_model(pop,users,profile,attacker,rng,n=1600):
    users=np.asarray(users);M0=matrix(pop,users,profile,attacker,0);M1=matrix(pop,users,profile,attacker,1);X=[];y=[]
    for _ in range(n):
        i=int(rng.integers(len(users)));X.append(pf_one_to_many(M0[i],M1[i:i+1])[0]);y.append(1)
        j=int(rng.integers(len(users)-1));j=j+(j>=i);X.append(pf_one_to_many(M0[i],M1[j:j+1])[0]);y.append(0)
    return Pipeline([('s',StandardScaler()),('lr',LogisticRegression(max_iter=500,C=.8,random_state=1))]).fit(np.asarray(X),y)

def pair_auc(model,pop,users,profile,attacker,rng,n=1200):
    users=np.asarray(users);M0=matrix(pop,users,profile,attacker,0);M2=matrix(pop,users,profile,attacker,2);X=[];y=[]
    for _ in range(n):
        i=int(rng.integers(len(users)));X.append(pf_one_to_many(M0[i],M2[i:i+1])[0]);y.append(1)
        j=int(rng.integers(len(users)-1));j=j+(j>=i);X.append(pf_one_to_many(M0[i],M2[j:j+1])[0]);y.append(0)
    return float(roc_auc_score(y,model.predict_proba(np.asarray(X))[:,1]))

def rank(model,pop,users,profile,attacker,cand,rng,n_targets=20):
    users=np.asarray(users);M0=matrix(pop,users,profile,attacker,0);M2=matrix(pop,users,profile,attacker,2);cand=min(cand,len(users));ranks=[]
    for i in rng.choice(len(users),n_targets,False):
        pool=np.delete(np.arange(len(users)),i);js=rng.choice(pool,cand-1,False);cs=np.r_[js,i];rng.shuffle(cs);p=model.predict_proba(pf_one_to_many(M0[i],M2[cs]))[:,1];ranked=cs[np.argsort(-p)];ranks.append(int(np.where(ranked==i)[0][0])+1)
    rr=np.asarray(ranks);return {'top1':float(np.mean(rr==1)),'top10':float(np.mean(rr<=10)),'mrr':float(np.mean(1/rr)),'median_rank':float(np.median(rr))}

def privacy_experiment():
    profiles=['rotation_only','relay_standardized','shielded_batched'];attackers=['network','compromised_pip'];rows=[];rr=[]
    for seed in range(2):
        tr=base.gen(21000+seed,1800,'profile');temp=base.gen(22000+seed,1800,'profile');ood=base.gen(23000+seed,3200,'calendar',True)
        train_users=np.arange(1200);test_users=np.arange(1200,1800);ood_users=np.arange(3200)
        for p in profiles:
          for a in attackers:
            model=train_model(tr,train_users,p,a,np.random.default_rng(24000+seed),1200)
            for split,pop,users in [('unseen_users',temp,test_users),('independent_generator',ood,ood_users)]:
                rows.append({'seed':seed,'profile':p,'attacker':a,'split':split,'pairwise_auc':pair_auc(model,pop,users,p,a,np.random.default_rng(25000+seed),800)})
                if a=='network':
                    for c in [100,1000,3000]:rr.append({'seed':seed,'profile':p,'split':split,'candidate_size':c,**rank(model,pop,users,p,a,c,np.random.default_rng(26000+seed+c),16)})
    df=pd.DataFrame(rows);rf=pd.DataFrame(rr);df.to_csv(RES/'privacy_v7_learned_attack.csv',index=False);rf.to_csv(RES/'privacy_v7_ranking.csv',index=False)
    sf=df.groupby(['profile','attacker','split']).pairwise_auc.agg(['mean','min','max']).reset_index().rename(columns={'mean':'auc_mean','min':'auc_min','max':'auc_max'});sf.to_csv(RES/'privacy_v7_summary.csv',index=False)
    rs=rf.groupby(['profile','split','candidate_size']).agg(top1_mean=('top1','mean'),top10_mean=('top10','mean'),mrr_mean=('mrr','mean'),median_rank_mean=('median_rank','mean')).reset_index();rs.to_csv(RES/'privacy_v7_ranking_summary.csv',index=False)
    q=sf[(sf.attacker=='network')&(sf.split=='independent_generator')].set_index('profile').loc[profiles];qr=rs[(rs.split=='independent_generator')&(rs.candidate_size==3000)].set_index('profile').loc[profiles]
    fig,ax=plt.subplots(figsize=(8.8,4.7));x=np.arange(3);w=.36;ax.bar(x-w/2,q.auc_mean,w,label='Pairwise ROC-AUC');ax.bar(x+w/2,qr.top1_mean,w,label='Top-1 among 3,000');ax.axhline(.5,ls='--',lw=1,label='Pairwise random');ax.axhline(1/3000,ls=':',lw=1,label='Top-1 random');ax.set_xticks(x,['Rotation only','Relay + standard client','Shielding + batching']);ax.set_ylim(0,1);ax.set_ylabel('Attack performance');ax.set_title('Learned metadata attacker on unseen users and generator shift');ax.grid(axis='y',alpha=.22);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'privacy_v7_learned_attack.png',dpi=260);fig.savefig(FIG/'privacy_v7_learned_attack.svg');plt.close(fig)
    return sf,rs

def hist(events,n=24,k=3):
    o=np.zeros(n)
    for e in events:o[sorted(set(int(x)%n for x in e))[:k]]+=1
    return o

def dp_experiment():
    rng=np.random.default_rng(20260807);cells=24;k=3;months=12;mx=0
    for _ in range(10000):
        b=[rng.integers(0,cells,rng.integers(1,9)).tolist() for _ in range(20)];ex=rng.integers(0,cells,rng.integers(1,9)).tolist();mx=max(mx,float(np.abs(hist(b+[ex],cells,k)-hist(b,cells,k)).sum()))
    rows=[]
    for total in [1,2,4,8]:
      eps=total/months;scale=k/eps
      for rep in range(30):
        for regime,n in [('sparse',250),('dense',12000)]:
          ev=[rng.integers(0,cells,rng.integers(1,9)).tolist() for _ in range(n)];true=hist(ev,cells,k);raw=true+rng.laplace(0,scale,cells);clip=np.maximum(0,raw);rows.append({'epsilon_total':total,'regime':regime,'mae':float(np.abs(clip-true).mean()),'clipping_bias':float((clip-raw).mean()),'median_relative_error':float(np.median(np.abs(clip-true)/np.maximum(1,true)))})
    df=pd.DataFrame(rows);df.to_csv(RES/'dp_v7_utility.csv',index=False);agg=df.groupby(['epsilon_total','regime']).mean(numeric_only=True).reset_index();agg.to_csv(RES/'dp_v7_summary_table.csv',index=False)
    out={'privacy_unit':'person','adjacency':'add/remove one person','contribution_bound':'one count in at most three cells per registered release','l1_sensitivity':3,'observed_max_neighbor_l1_over_10000_tests':mx,'mechanism':'Laplace with nonnegative post-processing','annual_release_count':12,'candidate_epsilon_totals':[1,2,4,8],'selected_example_epsilon_total':4,'selected_epsilon_per_release':4/12,'privacy_budget_ledger_required':True,'boundary':'Registered public histograms only; trusted-curator exposure, AML graph analytics, identity mappings and ad hoc queries are excluded.'};(RES/'dp_v7_summary.json').write_text(json.dumps(out,indent=2))
    fig,ax=plt.subplots(figsize=(8.8,4.6));
    for regime,g in agg.groupby('regime'):ax.plot(g.epsilon_total,100*g.median_relative_error,marker='o',label=regime)
    ax.set(xlabel='Annual epsilon budget across 12 releases',ylabel='Median relative error (%)',title='User-level DP utility and release-budget trade-off');ax.grid(alpha=.22);ax.legend();fig.tight_layout();fig.savefig(FIG/'dp_v7_utility.png',dpi=260);fig.savefig(FIG/'dp_v7_utility.svg');plt.close(fig);return out

def main():
    s,r=privacy_experiment();d=dp_experiment();o={'profiles':3,'attackers':2,'candidate_sizes':[100,1000,3000],'seeds':2,'claim_boundary':'Synthetic learned-attacker evidence only; governed real multi-PIP traces and independent red-team replication remain required.'};(RES/'privacy_v7_experiment_summary.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2));print(s.to_string(index=False));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
