from __future__ import annotations
import hashlib,hmac,json,os
from pathlib import Path
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; FIG=ROOT/'figures'; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

def bci(x,seed=1,n=1200):
 x=np.asarray(x,float);r=np.random.default_rng(seed);b=np.array([r.choice(x,len(x),True).mean() for _ in range(n)]);return float(x.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975))

def gen(seed,n,family='profile',ood=False):
 r=np.random.default_rng(seed); out={}; cohorts=r.integers(0,20,n); bt=r.dirichlet(np.ones(12)*2.2,size=20); bm=r.dirichlet(np.ones(12)*1.9,size=20)
 for u in range(n):
  c=int(cohorts[u]);lt=r.dirichlet(bt[c]*55+1);lm=r.dirichlet(bm[c]*45+1);inc=r.beta(2.2,2);mu=2.6+1.45*inc+r.normal(0,.2);sig=np.clip(r.normal(.72,.12),.35,1.1);ep0=(3*c+r.integers(0,8))%24;cli=(c+r.integers(0,5))%8; ss=[]
  for s in range(3):
   d=.18+.08*s+(.10 if ood else 0);t=(1-d)*lt+d*r.dirichlet(np.ones(12)*(1.3 if family=='calendar' else 2.4));m=(1-d)*lm+d*r.dirichlet(np.ones(12)*(1.5 if ood else 2.1))
   if family=='calendar': k=(u+3*s)%12;t[k]+=.16;t[(k+1)%12]+=.07
   t/=t.sum();m/=m.sum();nn=int(r.integers(50,125));th=r.multinomial(nn,t)/nn;mh=r.multinomial(nn,m)/nn;vals=np.log1p(r.lognormal(mu+r.normal(0,.12),sig,nn));aq=np.quantile(vals,np.linspace(.1,.9,8));eps=r.integers(0,24,nn);mask=r.random(nn)<.38;eps[mask]=(ep0+r.integers(-3,4,mask.sum()))%24;eh=np.bincount(eps,minlength=24)/nn
   rep=float(np.clip(r.normal(.18+.35*np.max(lm),.10),0,1));bur=float(np.clip(r.normal(.17+.42*np.max(lt),.11),0,1));div=float(np.clip(r.normal(.58-.22*rep,.10),0,1));client=cli if r.random()<.58 else int(r.integers(0,8));ss.append({'t':th,'m':mh,'a':aq,'e':eh,'rep':rep,'bur':bur,'div':div,'cli':client,'cohort':c})
  out[u]=ss
 return out

def view(s,p,a):
 if p=='rotation_only': l=np.r_[s['t'],s['m'],s['a'],s['rep'],s['bur'],s['div']]; net=np.r_[l,s['e'],s['cli']/7]
 elif p=='relay_standardized': l=np.r_[s['t'].reshape(4,3).sum(1),s['m'].reshape(4,3).sum(1),np.round(s['a']/.35)*.35,round(s['rep'],1),round(s['bur'],1),round(s['div'],1)];net=l
 else: l=np.r_[np.round(s['t'].reshape(3,4).sum(1),1),np.round(np.sort(s['m'])[-3:],1),np.round(s['a'][[1,3,5]]/.7)*.7,round(s['bur'],1),round(s['div'],1)];net=l
 if a=='ledger':return l
 if a=='network':return net
 if a=='merchant':return np.r_[l,round(s['rep'],2),np.sort(s['m'])[-4:]]
 return np.r_[net,s['cli']/7,s['rep'],s['div']]

def sim(x,y):
 x=np.asarray(x);y=np.asarray(y);return float(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-12))

def evaluate(pop,p,a,rng,session=2):
 users=np.array(list(pop)); pos=[];neg=[]
 for u0 in users:
  u=int(u0); x=view(pop[u][0],p,a);pos.append(sim(x,view(pop[u][session],p,a))); v=int(rng.choice(users[users!=u]));neg.append(sim(x,view(pop[v][session],p,a)))
 y=np.r_[np.ones(len(pos)),np.zeros(len(neg))];s=np.r_[pos,neg];return roc_auc_score(y,s)

def rank(pop,p,a,cand,rng,n_targets=24,session=2):
 users=np.array(list(pop));cand=min(cand,len(users)); ranks=[]
 for u0 in rng.choice(users,n_targets,False):
  u=int(u0); dec=rng.choice(users[users!=u],cand-1,False); cs=np.r_[dec,u];rng.shuffle(cs);x=view(pop[u][0],p,a);M=np.vstack([view(pop[int(v)][session],p,a) for v in cs]);sc=(M@x)/(np.linalg.norm(M,axis=1)*np.linalg.norm(x)+1e-12);ranked=cs[np.argsort(-sc)];ranks.append(int(np.where(ranked==u)[0][0])+1)
 rr=np.asarray(ranks);return {'top1':float(np.mean(rr==1)),'top10':float(np.mean(rr<=10)),'mrr':float(np.mean(1/rr)),'median_rank':float(np.median(rr))}

def run_privacy():
 ps=['rotation_only','relay_standardized','shielded_batched']; ats=['ledger','network','merchant','compromised_pip'];rows=[];rrows=[]
 for seed in range(5):
  temporal=gen(2000+seed,1100,'profile');ood=gen(3000+seed,1100,'calendar',True)
  for p in ps:
   for a in ats:
    for split,pop in [('temporal_holdout',temporal),('independent_generator',ood)]: rows.append({'seed':seed,'profile':p,'attacker':a,'split':split,'auc':evaluate(pop,p,a,np.random.default_rng(4000+seed))})
   for split,pop in [('temporal_holdout',temporal),('independent_generator',ood)]:
    for c in (100,1000):rrows.append({'seed':seed,'profile':p,'split':split,'candidate_size':c,**rank(pop,p,'network',c,np.random.default_rng(5000+seed+c))})
 df=pd.DataFrame(rows);rd=pd.DataFrame(rrows);df.to_csv(RES/'privacy_v5_runs.csv',index=False);rd.to_csv(RES/'privacy_v5_ranking.csv',index=False)
 ss=[]
 for k,g in df.groupby(['profile','attacker','split']):m,lo,hi=bci(g.auc,7+len(ss));ss.append({'profile':k[0],'attacker':k[1],'split':k[2],'auc_mean':m,'auc_lo':lo,'auc_hi':hi})
 sdf=pd.DataFrame(ss);sdf.to_csv(RES/'privacy_v5_summary.csv',index=False);rs=[]
 for k,g in rd.groupby(['profile','split','candidate_size']):
  rec={'profile':k[0],'split':k[1],'candidate_size':k[2]}
  for z in ['top1','top10','mrr','median_rank']:m,lo,hi=bci(g[z],70+len(rs));rec.update({z+'_mean':m,z+'_lo':lo,z+'_hi':hi})
  rs.append(rec)
 rs=pd.DataFrame(rs);rs.to_csv(RES/'privacy_v5_ranking_summary.csv',index=False);q=sdf[(sdf.attacker=='network')&(sdf.split=='independent_generator')].set_index('profile').loc[ps];qr=rs[(rs.split=='independent_generator')&(rs.candidate_size==1000)].set_index('profile').loc[ps]
 fig,ax=plt.subplots(figsize=(8.4,4.8));x=np.arange(3);w=.36;ax.bar(x-w/2,q.auc_mean,w,label='Pairwise ROC-AUC');ax.bar(x+w/2,qr.top1_mean,w,label='Top-1 among 1,000');ax.axhline(.5,ls='--',lw=1,label='Pairwise random');ax.axhline(.001,ls=':',lw=1,label='Top-1 random');ax.set_xticks(x,['Rotation only','Relay + standard client','Shielded + batching']);ax.set_ylim(0,1);ax.set_ylabel('Attack performance');ax.set_title('Metadata linkability under generator shift');ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'privacy_v5_redteam.png',dpi=240);plt.close(fig)
 return sdf,rs

class Ledger:
 def __init__(self,total):self.total=float(total);self.spent=0.;self.r=[]
 def auth(self,name,e,s,u,c):
  if e<=0 or s<=0 or not u or not c:raise ValueError('invalid')
  if self.spent+e>self.total+1e-12:raise ValueError('exhausted')
  self.spent+=e;t=hashlib.sha256(f'{name}|{e}|{s}|{u}|{c}|{len(self.r)}'.encode()).hexdigest();self.r.append(t);return t

def hist(events,n=24,k=3):
 o=np.zeros(n)
 for cells in events:o[sorted(set(int(x)%n for x in cells))[:k]]+=1
 return o

def run_dp():
 r=np.random.default_rng(20260806);n=12000;cells=24;k=3;months=12;total=4.;e=total/months;l=Ledger(total);mx=0.
 for _ in range(10000):
  b=[r.integers(0,cells,r.integers(1,8)).tolist() for _ in range(20)];ex=r.integers(0,cells,r.integers(1,8)).tolist();mx=max(mx,float(np.abs(hist(b+[ex],cells,k)-hist(b,cells,k)).sum()))
 rows=[]
 for m in range(months):
  ev=[r.integers(0,cells,r.integers(1,9)).tolist() for _ in range(n)];true=hist(ev,cells,k);tok=l.auth(f'month-{m+1}',e,k,'person',f'one count in at most {k} cells');noisy=np.maximum(0,true+r.laplace(0,k/e,cells));rel=np.abs(noisy-true)/np.maximum(1,true);rows.append({'month':m+1,'epsilon_release':e,'epsilon_cumulative':l.spent,'sensitivity':k,'laplace_scale':k/e,'mae':float(np.abs(noisy-true).mean()),'median_relative_error':float(np.median(rel)),'p95_relative_error':float(np.quantile(rel,.95)),'token':tok})
 rej=False
 try:l.auth('extra',e,k,'person','same')
 except ValueError:rej=True
 df=pd.DataFrame(rows);df.to_csv(RES/'dp_v5_releases.csv',index=False);s={'privacy_unit':'person','adjacency':'add/remove one person','contribution_bound':'one count in at most three cells per monthly release','l1_sensitivity':3,'observed_max_neighbor_l1_over_10000_tests':mx,'mechanism':'Laplace plus non-negative post-processing','epsilon_total':4.0,'releases':12,'epsilon_per_release':e,'sequential_composition_spent':l.spent,'thirteenth_release_rejected':rej,'boundary':'Registered public histograms only; excludes AML graph analytics and ad hoc queries.'};(RES/'dp_v5_summary.json').write_text(json.dumps(s,indent=2));fig,ax=plt.subplots(figsize=(8.2,4.5));ax.plot(df.month,100*df.median_relative_error,marker='o',label='Median');ax.plot(df.month,100*df.p95_relative_error,marker='s',label='95th percentile');ax.set_xlabel('Registered monthly release');ax.set_ylabel('Relative error (%)');ax.set_title('User-level DP utility under enforced composition');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'dp_v5_utility.png',dpi=240);plt.close(fig);return s

def no_tracker():
 k=os.urandom(32);cid=os.urandom(32);ps=[];ns=[]
 for i in range(10000):tx=hashlib.sha256(f'tx-{i}'.encode()).digest();nonce=os.urandom(32);n=hmac.new(k,tx+b'policy-domain',hashlib.sha256).digest();ps.append(hashlib.sha256(cid+nonce+tx+n).hexdigest());ns.append(n.hex())
 o={'presentations':10000,'unique_presentation_objects':len(set(ps)),'unique_transaction_bound_nullifiers':len(set(ns)),'stable_identifier_fields_in_profile':0,'boundary':'Construction test vector, not cryptographic proof.'};(RES/'no_tracker_v5.json').write_text(json.dumps(o,indent=2));return o
if __name__=='__main__':run_privacy();print(json.dumps(run_dp(),indent=2));print(json.dumps(no_tracker(),indent=2))
