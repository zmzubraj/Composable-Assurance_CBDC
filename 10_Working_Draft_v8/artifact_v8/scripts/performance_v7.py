from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import heapq, json, math
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; FIG=ROOT/'figures'; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

@dataclass
class Stage:
    name:str
    mean_ms:float
    cv:float
    servers:int

BASE_STAGES=[
    Stage('API and authentication',0.45,0.75,16),
    Stage('Policy and sanctions fast path',0.90,1.00,24),
    Stage('HSM signature verification',0.28,0.55,16),
    Stage('Monetary-state transition',0.62,0.80,24),
    Stage('Durable audit append',0.36,0.70,16),
]

def lognormal_params(mean,cv):
    sigma2=math.log(1+cv*cv); sigma=math.sqrt(sigma2); mu=math.log(mean)-sigma2/2
    return mu,sigma

def arrivals(seed,rate_tps,duration_s,burst=1.0):
    """Open-loop Markov-modulated arrivals. burst=1 approximates Poisson; >1 adds short high-rate regimes."""
    r=np.random.default_rng(seed); t=0.; out=[]; state=0
    while t<duration_s:
        if r.random()<0.0025: state=1-state
        mult=((2.0/(1.0+burst)) if state==0 else (2.0*burst/(1.0+burst))) if burst>1 else 1.0
        dt=r.exponential(1/(rate_tps*mult)); t+=dt
        if t<duration_s: out.append(t)
    return np.asarray(out)

def process_stage(times,stage,rng,server_factor=1.0):
    c=max(1,int(math.floor(stage.servers*server_factor)))
    avail=[0.0]*c; heapq.heapify(avail); out=np.empty_like(times); waits=np.empty_like(times)
    mu,sig=lognormal_params(stage.mean_ms/1000.0,stage.cv)
    for i,a in enumerate(times):
        free=heapq.heappop(avail); start=max(a,free); svc=float(rng.lognormal(mu,sig)); done=start+svc
        waits[i]=start-a; out[i]=done; heapq.heappush(avail,done)
    return out,waits,c

def simulate(seed,rate_tps,duration_s,burst=1.0,server_factor=1.0,region_loss=False,hsm_slowdown=1.0):
    r=np.random.default_rng(seed); a=arrivals(seed,rate_tps,duration_s,burst); t=a.copy(); stage_rows=[]
    stages=[Stage(s.name,s.mean_ms*(hsm_slowdown if 'HSM' in s.name else 1.0),s.cv,s.servers) for s in BASE_STAGES]
    if region_loss: server_factor*=2/3
    for s in stages:
        t,w,c=process_stage(t,s,r,server_factor)
        stage_rows.append({'stage':s.name,'servers':c,'mean_wait_ms':1000*w.mean(),'p99_wait_ms':1000*np.quantile(w,.99),'utilization_est':min(9.99,rate_tps*(s.mean_ms/1000)/c)})
    # Two regional network legs and replicated commit delay; explicitly scenario inputs, not measurements.
    net_mean=0.018 if not region_loss else 0.032
    net_cv=.45
    mu,sig=lognormal_params(net_mean,net_cv)
    network=r.lognormal(mu,sig,len(t))+r.lognormal(mu,sig,len(t))
    latency=(t-a+network)*1000
    return {'n':len(a),'p50_ms':float(np.quantile(latency,.5)),'p95_ms':float(np.quantile(latency,.95)),'p99_ms':float(np.quantile(latency,.99)),'max_ms':float(latency.max()),'throughput_observed_tps':len(a)/duration_s,'stage_rows':stage_rows}

def cross_border_from_domestic(seed,rate_tps,duration_s,burst=1.0,region_loss=False):
    # Conservative composition: two parallel domestic prepare paths, quorum decision, two finalizations.
    d=simulate(seed,rate_tps,duration_s,burst,region_loss=region_loss)
    r=np.random.default_rng(seed+10000); n=d['n']
    prepare_a=r.lognormal(math.log(max(1,d['p50_ms']))/1.15,.35,n)
    prepare_b=r.lognormal(math.log(max(1,d['p50_ms']))/1.15,.35,n)
    quorum=r.lognormal(math.log(75 if not region_loss else 120),.38,n)
    finalize=r.lognormal(math.log(65 if not region_loss else 105),.35,n)
    total=np.maximum(prepare_a,prepare_b)+quorum+finalize
    return {'n':n,'p50_ms':float(np.quantile(total,.5)),'p95_ms':float(np.quantile(total,.95)),'p99_ms':float(np.quantile(total,.99)),'max_ms':float(total.max())}

def main():
    scenarios=[
      ('TIPS-reference steady',2000,40,1.0,False,1.0),
      ('FuSSE-reference steady',10000,20,1.0,False,1.0),
      ('FuSSE-reference burst',10000,20,2.0,False,1.0),
      ('10k with one region unavailable',10000,20,1.4,True,1.0),
      ('10k with HSM service doubled',10000,20,1.2,False,2.0),
      ('20k qualification stress',20000,12,1.6,False,1.0),
      ('40k overload control with region loss',40000,8,1.8,True,1.0),
    ]
    rows=[]; stage_all=[]
    for i,(name,rate,dur,burst,loss,hslow) in enumerate(scenarios):
        z=simulate(7000+i,rate,dur,burst,1.0,loss,hslow); cb=cross_border_from_domestic(9000+i,min(rate,2500),dur,burst,loss)
        rows.append({'scenario':name,'arrival_target_tps':rate,'observed_arrival_tps':z['throughput_observed_tps'],'domestic_p50_ms':z['p50_ms'],'domestic_p95_ms':z['p95_ms'],'domestic_p99_ms':z['p99_ms'],'cross_border_p99_ms':cb['p99_ms'],'region_loss':loss,'hsm_slowdown':hslow,'domestic_slo_pass':z['p99_ms']<2000,'cross_border_slo_pass':cb['p99_ms']<10000})
        for q in z['stage_rows']: stage_all.append({'scenario':name,**q})
    df=pd.DataFrame(rows); sf=pd.DataFrame(stage_all); df.to_csv(RES/'performance_v7_scenarios.csv',index=False); sf.to_csv(RES/'performance_v7_stage_utilization.csv',index=False)
    # Capacity lower bounds. This is necessary but not sufficient.
    plan=[]; rho=.60; headroom=2.0
    for lam in [2000,10000,20000]:
      for s in BASE_STAGES:
        units=math.ceil(lam*headroom*(s.mean_ms/1000)/rho)
        plan.append({'qualification_tps':lam,'stage':s.name,'mean_service_ms':s.mean_ms,'headroom':headroom,'rho_max':rho,'minimum_parallel_units':units})
    pd.DataFrame(plan).to_csv(RES/'performance_v7_capacity_lower_bounds.csv',index=False)
    out={'model':'open-loop Markov-modulated tandem-queue digital twin with explicit service-demand and regional-delay assumptions','scenarios':len(df),'all_domestic_slo_pass':bool(df.domestic_slo_pass.all()),'all_cross_border_slo_pass':bool(df.cross_border_slo_pass.all()),'worst_domestic_p99_ms':float(df.domestic_p99_ms.max()),'worst_cross_border_p99_ms':float(df.cross_border_p99_ms.max()),'national_scale_demonstrated':False,'claim_boundary':'Scenario model and qualification design only. A national claim requires physical multi-region execution, certified HSMs, production persistence, real PIP workloads, sustained open-loop load, fault injection, RTO/RPO measurement and independent audit.'}
    (RES/'performance_v7_summary.json').write_text(json.dumps(out,indent=2))
    # figures
    fig,ax=plt.subplots(figsize=(9.0,4.8));x=np.arange(len(df));ax.bar(x,df.domestic_p99_ms,label='Domestic p99');ax.plot(x,df.cross_border_p99_ms,marker='o',label='Cross-border p99');ax.axhline(2000,ls='--',lw=1,label='Domestic candidate SLO');ax.set_xticks(x);ax.set_xticklabels(['2k','10k','10k burst','10k N-1','10k HSM x2','20k','40k N-1'],rotation=0);ax.set_ylabel('Latency (ms)');ax.set_title('Trace-driven qualification scenarios (simulation, not deployment evidence)');ax.grid(axis='y',alpha=.22);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'performance_v7_scenarios.png',dpi=260);fig.savefig(FIG/'performance_v7_scenarios.svg');plt.close(fig)
    pp=pd.DataFrame(plan);fig,ax=plt.subplots(figsize=(9.0,4.8));
    for stage,g in pp.groupby('stage'):ax.plot(g.qualification_tps,g.minimum_parallel_units,marker='o',label=stage)
    ax.set(xlabel='Qualification arrival rate (TPS)',ylabel='Analytical lower-bound parallel units',title='Necessary capacity lower bounds at 60% utilization and 2x headroom');ax.grid(alpha=.22);ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(FIG/'performance_v7_capacity_bounds.png',dpi=260);fig.savefig(FIG/'performance_v7_capacity_bounds.svg');plt.close(fig)
    print(json.dumps(out,indent=2));print(df.to_string(index=False))
if __name__=='__main__':main()
