from __future__ import annotations
import json, math, re, unicodedata
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from faker import Faker
from rapidfuzz import fuzz
from unidecode import unidecode
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; RES=ROOT/'results'; FIG=ROOT/'figures'
RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED=20260806

ARABIC_SUBS={
 'MOHAMMED':['MUHAMMAD','MOHAMMAD','MOHAMED'], 'ABDUL':['ABD AL','ABDEL','ABD EL'],
 'HUSSEIN':['HUSAYN','HUSAIN'], 'AHMED':['AHMAD'], 'YOUSEF':['YUSUF'], 'OSMAN':['UTHMAN']
}
CYR_SUBS={'YEV':['EV'],'IY':['II','Y'],'SKIY':['SKY'],'OV':['OFF'],'KH':['H'],'TS':['C']}

def norm(s:str)->str:
    s=unicodedata.normalize('NFKC',str(s))
    s=unidecode(s).upper()
    s=re.sub(r'[^A-Z0-9 ]',' ',s)
    return ' '.join(s.split())

def soundex(w:str)->str:
    w=norm(w)
    if not w:return ''
    m={'B':1,'F':1,'P':1,'V':1,'C':2,'G':2,'J':2,'K':2,'Q':2,'S':2,'X':2,'Z':2,'D':3,'T':3,'L':4,'M':5,'N':5,'R':6}
    out=w[0]; prev=m.get(w[0],0)
    for c in w[1:]:
        z=m.get(c,0)
        if z and z!=prev: out+=str(z)
        prev=z
    return (out+'000')[:4]

def parse_attrs(remarks:str):
    def grab(label):
        m=re.search(label+r'\s+([^;]+)',str(remarks),re.I)
        return norm(m.group(1)) if m else ''
    return {'dob':grab('DOB'),'pob':grab('POB'),'nationality':grab('nationality')}

def load_records():
    sdn=pd.read_csv(DATA/'ofac_sdn.csv',header=None,dtype=str,keep_default_na=False)
    sdn.columns=['ent','name','type','program','title','call','vessel','ton','grt','flag','owner','remarks']
    alt=pd.read_csv(DATA/'ofac_alt.csv',header=None,dtype=str,keep_default_na=False)
    alt.columns=['ent','alt_num','alias_type','name','remarks']
    add=pd.read_csv(DATA/'ofac_add.csv',header=None,dtype=str,keep_default_na=False)
    add.columns=['ent','add_num','address','city','country','remarks']
    amap=defaultdict(list)
    for _,r in alt.iterrows():
        if norm(r['name']): amap[str(r.ent)].append((r['name'],r['alias_type']))
    dmap=defaultdict(list)
    for _,r in add.iterrows(): dmap[str(r.ent)].append((f"{r.address} {r.city}",r.country))
    out=[]
    for _,r in sdn.iterrows():
        if not norm(r['name']): continue
        addr,country=(dmap.get(str(r.ent)) or [('', '')])[0]
        out.append({'ent':str(r.ent),'name':r['name'],'type':r['type'],'program':r['program'],
                    'aliases':amap.get(str(r.ent),[])[:25],**parse_attrs(r['remarks']),
                    'address':addr,'country':country})
    return out

def build_index(records):
    idx=defaultdict(set)
    for i,r in enumerate(records):
        for name,_typ in [(r['name'],'primary')]+r['aliases']:
            z=norm(name); toks=z.split()
            for t in toks:
                idx['p:'+t[:2]].add(i); idx['s:'+soundex(t)].add(i)
            for j in range(max(1,len(z)-2)): idx['g:'+z[j:j+3]].add(i)
    return idx

def retrieve(name,idx,cap=15):
    z=norm(name); counts=defaultdict(float)
    for t in z.split():
        for i in idx.get('p:'+t[:2],()): counts[i]+=2
        for i in idx.get('s:'+soundex(t),()): counts[i]+=1
    for j in range(max(1,len(z)-2)):
        for i in idx.get('g:'+z[j:j+3],()): counts[i]+=0.25
    return [i for i,_ in sorted(counts.items(), key=lambda kv:(-kv[1],kv[0]))[:cap]]

def best_name_features(qname,r):
    q=norm(qname); choices=[('primary',r['name'])]+[(t,n) for n,t in r['aliases']]
    best=None
    for typ,n in choices:
        nn=norm(n)
        qph={soundex(t) for t in q.split()}; nph={soundex(t) for t in nn.split()}
        f={'name_wratio':fuzz.WRatio(q,nn)/100,'name_token':fuzz.token_set_ratio(q,nn)/100,
           'name_partial':fuzz.partial_ratio(q,nn)/100,'phonetic':len(qph&nph)/max(1,len(qph)),
           'alias_strength':1.0 if typ in ('primary','aka') else .5}
        score=.45*f['name_wratio']+.25*f['name_token']+.15*f['name_partial']+.10*f['phonetic']+.05*f['alias_strength']
        if best is None or score>best[0]: best=(score,f,typ)
    return best[1],best[2]

def field_sim(a,b):
    a=norm(a);b=norm(b)
    return fuzz.WRatio(a,b)/100 if a and b else 0.0

def features(q,r):
    f,typ=best_name_features(q['name'],r)
    dobq,dobr=norm(q.get('dob','')),norm(r.get('dob',''))
    f.update({
      'dob_exact':float(bool(dobq and dobr and dobq==dobr)),
      'dob_year':float(bool(dobq and dobr and dobq[-4:]==dobr[-4:])),
      'pob':field_sim(q.get('pob',''),r.get('pob','')),
      'nationality':float(bool(norm(q.get('nationality','')) and norm(q.get('nationality',''))==norm(r.get('nationality','')))),
      'address':field_sim(q.get('address',''),r.get('address','')),
      'country':float(bool(norm(q.get('country','')) and norm(q.get('country',''))==norm(r.get('country','')))),
      'type_match':float(bool(norm(q.get('type','')) and norm(q.get('type',''))==norm(r.get('type','')))),
      'used_alias':float(typ!='primary')
    })
    return f

def typo(s,rng):
    x=list(norm(s)); ids=[i for i,c in enumerate(x) if c.isalpha()]
    if not ids:return norm(s)
    i=int(rng.choice(ids)); op=rng.choice(['drop','swap','sub','double'])
    if op=='drop': x.pop(i)
    elif op=='swap' and i+1<len(x): x[i],x[i+1]=x[i+1],x[i]
    elif op=='double': x.insert(i,x[i])
    else: x[i]=rng.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    return ''.join(x)

def translit_stress(s,rng):
    z=norm(s)
    for k,vals in {**ARABIC_SUBS,**CYR_SUBS}.items():
        if k in z and rng.random()<.8: z=z.replace(k,str(rng.choice(vals)))
    if rng.random()<.5: z=z.replace('AL ','EL ')
    if rng.random()<.3: z=z.replace(' ', '')
    return z

def make_positive_queries(records, selected_ids, split, rng):
    rows=[]
    for i in selected_ids:
        r=records[i]
        variants=[('exact',r['name']),('token_order',' '.join(reversed(norm(r['name']).split()))),
                  ('ocr',typo(r['name'],rng)),('transliteration',translit_stress(r['name'],rng)),
                  ('sparse_attributes',r['name'])]
        if r['aliases']: variants.append(('official_alias',r['aliases'][0][0]))
        for kind,n in variants:
            q={'name':n,'dob':r['dob'],'pob':r['pob'],'nationality':r['nationality'],'address':r['address'],'country':r['country'],'type':r['type']}
            if kind=='sparse_attributes':
                for k in ['dob','pob','nationality','address','country']:
                    if rng.random()<.75:q[k]=''
            else:
                for k in ['dob','pob','nationality','address','country']:
                    if rng.random()<.25:q[k]=''
            rows.append({'label':1,'target':i,'kind':kind,'split':split,'query':q})
    return rows

def legitimate_queries(n,split,rng):
    locales=['en_US','en_GB','es_ES','fr_FR','de_DE','it_IT','pt_BR','ru_RU','uk_UA','ar_EG','fa_IR','hi_IN','zh_CN','ja_JP','ko_KR','tr_TR','id_ID']
    fs={l:Faker(l) for l in locales}
    for j,l in enumerate(locales): fs[l].seed_instance(SEED+j+100)
    rows=[]
    for j in range(n):
        l=locales[j%len(locales)]; fk=fs[l]
        rows.append({'label':0,'target':-1,'kind':'legitimate_'+l,'split':split,'query':{
          'name':fk.name(),'dob':str(fk.date_of_birth(minimum_age=18,maximum_age=95)),
          'pob':fk.city(),'nationality':l,'address':fk.address(),'country':l,'type':'individual'}})
    return rows

def hard_negatives(records,n,split,rng):
    rows=[]
    fk=Faker('en_US');fk.seed_instance(SEED+999)
    for _ in range(n):
        r=records[int(rng.integers(len(records)))]
        rows.append({'label':0,'target':-1,'kind':'hard_near_match','split':split,'query':{
          'name':typo(r['name'],rng),'dob':str(fk.date_of_birth(minimum_age=18,maximum_age=95)),
          'pob':fk.city(),'nationality':'UNITED STATES','address':fk.address(),'country':'UNITED STATES','type':r['type']}})
    return rows

def materialize(records,idx,queries):
    feat_names=['name_wratio','name_token','name_partial','phonetic','alias_strength','dob_exact','dob_year','pob','nationality','address','country','type_match','used_alias']
    rows=[]
    for z in queries:
        cand=retrieve(z['query']['name'],idx)
        best=None
        for i in cand:
            f=features(z['query'],records[i])
            heuristic=.42*f['name_wratio']+.22*f['name_token']+.13*f['name_partial']+.08*f['phonetic']+.15*max(f['dob_exact'],f['dob_year'],f['country'],f['address'])
            if best is None or heuristic>best[0]:best=(heuristic,i,f)
        if best is None:best=(0,-1,{k:0.0 for k in feat_names})
        row={'label':z['label'],'target':z['target'],'kind':z['kind'],'split':z['split'],'candidate_count':len(cand),
             'target_retrieved':float(z['target'] in cand) if z['target']>=0 else np.nan,'top_candidate':best[1]}
        row.update(best[2]);rows.append(row)
    return pd.DataFrame(rows),feat_names

def choose_threshold(y,p,max_fpr=.001):
    best=None
    for t in np.linspace(.01,.99,990):
        pred=p>=t;tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel();fpr=fp/max(1,fp+tn);rec=tp/max(1,tp+fn);prec=tp/max(1,tp+fp)
        if fpr<=max_fpr and (best is None or rec>best[1] or (rec==best[1] and prec>best[2])):best=(t,rec,prec,fpr)
    return best or (.99,0,0,0)

def ownership_engine(graph,blocked):
    # OFAC-style propagation: an entity is blocked when blocked owners, directly or through already-blocked entities,
    # own at least 50% in aggregate. DAG only; cycles are rejected upstream for legal review.
    n=max(max(u,v) for u,v,_ in graph)+1 if graph else max(blocked)+1
    status=np.zeros(n,dtype=bool);status[list(blocked)]=True
    changed=True
    while changed:
        changed=False
        for v in range(n):
            if status[v]:continue
            agg=sum(share for u,w,share in graph if w==v and status[u])
            if agg>=.5-1e-12:status[v]=True;changed=True
    return status

def ownership_tests():
    cases=[
      ('aggregate_direct',[(0,2,.25),(1,2,.25)],{0,1},{2}),
      ('indirect_chain',[(0,1,.5),(1,2,.5)],{0},{1,2}),
      ('direct_plus_indirect',[(0,1,.8),(1,2,.4),(0,2,.1)],{0},{1,2}),
      ('below_threshold',[(0,1,.49),(1,2,.9)],{0},set()),
      ('control_not_ownership',[(0,1,.2)],{0},set())]
    out=[]
    for name,g,b,expected in cases:
        st=ownership_engine(g,b); got={i for i,x in enumerate(st) if x and i not in b}
        out.append({'case':name,'pass':got==expected,'expected':sorted(expected),'computed':sorted(got)})
    pd.DataFrame(out).to_csv(RES/'sanctions_v6_ownership_cases.csv',index=False)
    return all(x['pass'] for x in out)

def main():
    rng=np.random.default_rng(SEED); records=load_records();idx=build_index(records)
    eligible=np.array([i for i,r in enumerate(records) if len(norm(r['name']))>=5])
    rng.shuffle(eligible); selected=eligible[:300]
    train_ids=selected[:180];cal_ids=selected[180:240];test_ids=selected[240:]
    queries=[]
    queries+=make_positive_queries(records,train_ids,'train',rng)
    queries+=make_positive_queries(records,cal_ids,'cal',rng)
    queries+=make_positive_queries(records,test_ids,'test',rng)
    queries+=legitimate_queries(1200,'train',rng)+hard_negatives(records,200,'train',rng)
    queries+=legitimate_queries(400,'cal',rng)+hard_negatives(records,80,'cal',rng)
    queries+=legitimate_queries(1200,'test',rng)+hard_negatives(records,200,'test',rng)
    df,fn=materialize(records,idx,queries)
    pipe=Pipeline([('scale',StandardScaler()),('lr',LogisticRegression(max_iter=1200,class_weight='balanced',C=.8,random_state=SEED))])
    tr=df[df.split=='train'].copy();ca=df[df.split=='cal'].copy();te=df[df.split=='test'].copy()
    pipe.fit(tr[fn],tr.label)
    for part in [ca,te]:part.loc[:,'prob']=pipe.predict_proba(part[fn])[:,1]
    threshold,_,_,_=choose_threshold(ca.label.values,ca.prob.values,.001)
    y=te.label.values;p=te.prob.values;pred=p>=threshold
    tn,fp,fnn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel();fpr=fp/max(1,fp+tn);rec=tp/max(1,tp+fnn);prec=tp/max(1,tp+fp)
    positive=te[te.label==1].copy();positive['screen_hit']=positive.prob>=threshold
    by=positive.groupby('kind').agg(n=('label','size'),candidate_recall=('target_retrieved','mean'),screen_recall=('screen_hit','mean'),median_score=('prob','median')).reset_index()
    by.to_csv(RES/'sanctions_v6_by_kind.csv',index=False)
    # Operational workload projections at realistic low prevalence.
    work=[]
    for prevalence in [.0001,.0005,.001]:
        false_per_m=1_000_000*(1-prevalence)*fpr;true_per_m=1_000_000*prevalence*rec
        for minutes in [3,7,15]:
            work.append({'prevalence':prevalence,'true_alerts_per_million':true_per_m,'false_alerts_per_million':false_per_m,
                         'analyst_minutes_per_alert':minutes,'analyst_hours_per_million':(true_per_m+false_per_m)*minutes/60})
    pd.DataFrame(work).to_csv(RES/'sanctions_v6_workload.csv',index=False)
    # Threshold curve.
    grid=[]
    for t in np.linspace(.05,.99,120):
        pr=p>=t;tn0,fp0,fn0,tp0=confusion_matrix(y,pr,labels=[0,1]).ravel()
        grid.append({'threshold':t,'precision':tp0/max(1,tp0+fp0),'recall':tp0/max(1,tp0+fn0),'fpr':fp0/max(1,fp0+tn0)})
    gd=pd.DataFrame(grid);gd.to_csv(RES/'sanctions_v6_thresholds.csv',index=False)
    own=ownership_tests()
    out={'ofac_records_indexed':len(records),'official_aliases_indexed':int(sum(len(r['aliases']) for r in records)),
         'positive_entities_train_cal_test':[len(train_ids),len(cal_ids),len(test_ids)],'total_queries':len(df),
         'test_queries':len(te),'threshold_selected_on_calibration':threshold,'test_precision':prec,'test_recall':rec,
         'test_false_positive_rate':fpr,'test_pr_auc':average_precision_score(y,p),'test_roc_auc':roc_auc_score(y,p),
         'positive_candidate_recall':float(positive.target_retrieved.mean()),'ownership_rule_cases_passed':own,
         'claim_boundary':'Full official OFAC legacy list snapshot indexed; entity-disjoint positive splits and multilingual generated customer/hard-negative stress queries. Operational validation still requires real customer distributions, licensed transliteration, analyst adjudication, list-governance audit, and live beneficial-ownership data.'}
    (RES/'sanctions_v6_summary.json').write_text(json.dumps(out,indent=2));df.to_csv(RES/'sanctions_v6_scored_queries.csv',index=False)
    # Figures
    fig,ax=plt.subplots(figsize=(8.2,4.6));ax.plot(gd.threshold,gd.precision,label='Precision');ax.plot(gd.threshold,gd.recall,label='Recall');ax.axvline(threshold,ls='--',lw=1,label=f'calibrated {threshold:.2f}');ax.set(xlabel='Decision threshold',ylabel='Metric',title='Held-out sanctions screening trade-off');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'sanctions_v6_tradeoff.png',dpi=260);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.4,4.8));x=np.arange(len(by));ax.bar(x-.18,by.candidate_recall,.36,label='Candidate recall');ax.bar(x+.18,by.screen_recall,.36,label='End-to-end recall');ax.set_xticks(x);ax.set_xticklabels(by.kind,rotation=30,ha='right');ax.set_ylim(0,1.05);ax.set_ylabel('Rate');ax.set_title('Sanctions performance by perturbation class');ax.grid(axis='y',alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'sanctions_v6_by_kind.png',dpi=260);plt.close(fig)
    print(json.dumps(out,indent=2));print(by.to_string(index=False))
if __name__=='__main__':main()
