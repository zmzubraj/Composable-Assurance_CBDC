from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
BLUE='#1f4e79'; MID='#5b9bd5'; PALE='#eaf2f8'; GREEN='#70ad47'; PG='#e2f0d9'; ORANGE='#ed7d31'; PO='#fce4d6'; GRAY='#5b6573'; LG='#f2f4f7'; RED='#c00000'; WHITE='white'; DARK='#222222'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})

def setup(w=11,h=5.8):
    fig,ax=plt.subplots(figsize=(w,h),dpi=220); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off'); return fig,ax

def box(ax,x,y,w,h,text,fc=PALE,ec=BLUE,lw=1.6,fs=10,bold=False,textcolor=DARK,pad=.014):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad={pad},rounding_size=0.018',facecolor=fc,edgecolor=ec,linewidth=lw)
    ax.add_patch(p); ax.text(
        x+w/2,y+h/2,text,
        ha='center',va='center',multialignment='center',linespacing=1.22,
        fontsize=fs,fontweight='bold' if bold else 'normal',color=textcolor,wrap=True,
    )
    return p

def arrow(ax,x1,y1,x2,y2,label=None,color=GRAY,rad=0):
    a=FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,linewidth=1.25,color=color,connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)
    if label: ax.text((x1+x2)/2,(y1+y2)/2+0.025,label,ha='center',va='bottom',fontsize=8.3,color=color)

def routed_arrow(ax,points,label=None,label_xy=None,color=GRAY,lw=1.25):
    """Draw an orthogonal connector whose final segment carries the arrowhead."""
    for (x1,y1),(x2,y2) in zip(points[:-2],points[1:-1]):
        ax.plot([x1,x2],[y1,y2],color=color,linewidth=lw,solid_capstyle='round',zorder=2)
    (x1,y1),(x2,y2)=points[-2],points[-1]
    ax.add_patch(FancyArrowPatch(
        (x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,
        linewidth=lw,color=color,connectionstyle='arc3,rad=0',zorder=3,
    ))
    if label and label_xy:
        ax.text(
            *label_xy,label,ha='center',va='center',fontsize=7.7,color=color,
            bbox=dict(boxstyle='round,pad=0.18',facecolor=WHITE,edgecolor='none',alpha=.96),
            zorder=4,
        )

# 1 composable assurance
fig,ax=setup(11,5.5)
box(ax,.03,.74,.94,.16,'COMPOSABLE ASSURANCE OBJECTIVE\nNo property is accepted in isolation; each claim must survive conflicts with the others.',BLUE,BLUE,fs=11.5,bold=True,textcolor=WHITE)
labels=[('Monetary correctness','Supply, reserves,\nfinality'),('Privacy','Linkability and\nlawful access'),('Financial integrity','AML/CFT and\nsanctions'),('Policy stability','Adoption, runs\nand inclusion'),('Operational resilience','Scale, recovery\nand cyber')]
xs=[.015,.21,.405,.60,.795]
for (title,sub),x in zip(labels,xs): box(ax,x,.40,.175,.22,title+'\n'+sub,fc=PALE,fs=8.1,bold=True)
for x in xs: arrow(ax,x+.0875,.40,x+.0875,.29)
box(ax,.08,.10,.84,.15,'EVIDENCE LADDER\nformal model -> synthetic benchmark -> prototype -> physical qualification -> governed pilot',fc=PG,ec=GREEN,fs=9.2,bold=True)
ax.text(.5,.02,'A deployment claim is permitted only at the highest evidence level actually completed.',ha='center',fontsize=9.2,color=GRAY)
fig.tight_layout(); fig.savefig(OUT/'v7_assurance_stack.png',bbox_inches='tight'); fig.savefig(OUT/'v7_assurance_stack.svg',bbox_inches='tight'); plt.close(fig)

# 2 architecture
fig,ax=setup(12,6.8)
box(ax,.03,.75,.18,.17,'Central bank\nmonetary core\nreserves | CBDC | audit',fc=PG,ec=GREEN,fs=9.0,bold=True)
box(ax,.28,.75,.18,.17,'Regulated PIPs\nwallets | KYC | fraud\ncustomer support',fc=PALE,fs=9.0,bold=True)
box(ax,.53,.75,.18,.17,'Identity & privacy\ncredentials | vaults\nselective disclosure',fc=PALE,fs=9.0,bold=True)
box(ax,.78,.75,.18,.17,'Financial integrity\nrules | analytics\ncase management',fc=PO,ec=ORANGE,fs=9.0,bold=True)
for i in range(3): arrow(ax,[.21,.46,.71][i],.835,[.28,.53,.78][i],.835)
box(ax,.08,.42,.36,.17,'Domestic deterministic ledger A\nreserve-settled issuance | conversion\nescrow | finality',fc=LG,ec=BLUE,fs=8.1,bold=True)
box(ax,.56,.42,.36,.17,'Domestic deterministic ledger B\nreserve-settled issuance | conversion\nescrow | finality',fc=LG,ec=BLUE,fs=8.1,bold=True)
box(ax,.34,.12,.32,.16,'Cross-border evidence service\nquotes | compliance proofs | prepare receipts\nPREPARE and COMMIT/ABORT certificates',fc=PO,ec=ORANGE,fs=7.6,bold=True)
# Blue paths carry signed domestic evidence inward; green paths return terminal certificates.
arrow(ax,.31,.42,.43,.28,color=BLUE)
arrow(ax,.69,.42,.57,.28,color=BLUE)
arrow(ax,.40,.28,.22,.42,color=GREEN)
arrow(ax,.60,.28,.78,.42,color=GREEN)
ax.text(.365,.365,'signed evidence',ha='center',va='center',fontsize=7.0,color=BLUE,
        bbox=dict(facecolor=WHITE,edgecolor='none',pad=1.2,alpha=.95))
ax.text(.635,.365,'signed evidence',ha='center',va='center',fontsize=7.0,color=BLUE,
        bbox=dict(facecolor=WHITE,edgecolor='none',pad=1.2,alpha=.95))
ax.text(.285,.315,'terminal certificate',ha='center',va='center',fontsize=7.0,color=GREEN,
        bbox=dict(facecolor=WHITE,edgecolor='none',pad=1.2,alpha=.95))
ax.text(.715,.315,'terminal certificate',ha='center',va='center',fontsize=7.0,color=GREEN,
        bbox=dict(facecolor=WHITE,edgecolor='none',pad=1.2,alpha=.95))
ax.text(.5,.04,'No wrapped CBDC, no foreign minting, no common global monetary ledger.',ha='center',fontsize=10,color=RED,fontweight='bold')
fig.tight_layout(); fig.savefig(OUT/'v7_architecture.png',bbox_inches='tight'); fig.savefig(OUT/'v7_architecture.svg',bbox_inches='tight'); plt.close(fig)

# 3 cross border
fig,ax=setup(12,7.2)
cols=[.055,.29,.525,.76]; names=['PIP / Ledger A','Decision quorum','PIP / Ledger B','Recovery & audit']
for x,n in zip(cols,names): box(ax,x,.89,.175,.075,n,fc=BLUE,ec=BLUE,fs=8.8,bold=True,textcolor=WHITE)
ys=[.765,.63,.495,.36,.225,.09]
steps=[('1. Lock amount A; emit PA','1. Validate PI, Q, CA, CB','1. Lock amount B; emit PB','Evidence is versioned'),('2. Send PA','2. Verify both receipts','2. Send PB','Reject stale/mismatch'),('3. Await PC','3. Issue 5-of-7 PREPARE','3. Await PC','No local-timeout abort'),('4. Receive terminal TC','4. Issue COMMIT or ABORT','4. Receive terminal TC','One decision per tx'),('5. Idempotent finalize','5. Publish certificate log','5. Idempotent finalize','Recover after restart'),('6. Reconcile balances','6. Audit quorum evidence','6. Reconcile balances','Legal evidence retained')]
for y,row in zip(ys,steps):
    for x,txt in zip(cols,row): box(ax,x,y,.175,.072,txt,fc=WHITE,ec=MID,lw=1,fs=7.45,pad=.010)
for x in cols:
    arrow(ax,x+.0875,.89,x+.0875,ys[0]+.072,color=GRAY)
    for upper_y,lower_y in zip(ys[:-1],ys[1:]):
        arrow(ax,x+.0875,upper_y,x+.0875,lower_y+.072,color=GRAY)
# Cross-lane messages are routed through row gutters so they never obscure step text.
routed_arrow(ax,[(.23,.666),(.252,.715),(.503,.715),(.525,.666)],
             'prepare evidence',(.378,.731),ORANGE)
routed_arrow(ax,[(.29,.531),(.268,.58),(.252,.58),(.23,.531)],color=GREEN)
routed_arrow(ax,[(.465,.531),(.487,.58),(.503,.58),(.525,.531)],
             'PREPARE certificate',(.378,.596),GREEN)
routed_arrow(ax,[(.465,.261),(.487,.31),(.738,.31),(.76,.261)],
             'terminal certificate',(.612,.326),GREEN)
fig.tight_layout(); fig.savefig(OUT/'v7_cross_border_sequence.png',bbox_inches='tight'); fig.savefig(OUT/'v7_cross_border_sequence.svg',bbox_inches='tight'); plt.close(fig)

# 4 privacy + DP
fig,ax=setup(12,6.2)
box(ax,.03,.70,.20,.20,'Customer identity\nfull KYC and recovery\nheld by responsible PIP',fc=PO,ec=ORANGE,fs=10,bold=True)
box(ax,.29,.70,.20,.20,'Rotating ledger view\npseudonyms | amount | state\nminimum settlement metadata',fc=PALE,fs=10,bold=True)
box(ax,.55,.70,.20,.20,'Compliance proof\ntransaction-bound predicate\nno stable presentation ID',fc=PG,ec=GREEN,fs=10,bold=True)
box(ax,.81,.70,.16,.20,'Threshold disclosure\nlegal basis + quorum\nimmutable access log',fc=LG,fs=9.5,bold=True)
arrow(ax,.23,.80,.29,.80); arrow(ax,.49,.80,.55,.80); arrow(ax,.75,.80,.81,.80)
box(ax,.06,.34,.25,.18,'Learned red-team attackers\nnetwork | merchant coalition\ncompromised PIP | auxiliary data',fc=LG,fs=9.5,bold=True)
box(ax,.38,.34,.25,.18,'Mitigations\nrelay standardization\nshielded batching | timing controls',fc=PG,ec=GREEN,fs=9.5,bold=True)
box(ax,.70,.34,.24,.18,'Measured residual risk\nAUC | top-k | MRR | rank\nunseen users + generator shift',fc=PO,ec=ORANGE,fs=9.5,bold=True)
arrow(ax,.31,.43,.38,.43); arrow(ax,.63,.43,.70,.43)
box(ax,.17,.08,.66,.14,'Registered public statistics: person-level add/remove adjacency -> contribution bound 3\nLaplace mechanism -> 12-release privacy accountant',fc=BLUE,ec=BLUE,fs=9.5,bold=True,textcolor=WHITE)
fig.tight_layout(); fig.savefig(OUT/'v7_privacy_dp_pipeline.png',bbox_inches='tight'); fig.savefig(OUT/'v7_privacy_dp_pipeline.svg',bbox_inches='tight'); plt.close(fig)

# 5 AML
fig,ax=setup(12,6.2)
fams=[('Profile mix',.04),('Calendar / payroll',.27),('Merchant network',.50),('Remittance corridor',.73)]
for n,x in fams: box(ax,x,.75,.19,.13,n+'\n4 independent graphs',fc=PALE,fs=9.4,bold=True)
for x in [.135,.365,.595,.825]: arrow(ax,x,.75,x,.62)
box(ax,.08,.47,.35,.14,'PIP-local baseline\nfeatures restricted to institution-visible transactions',fc=LG,fs=9.5,bold=True)
box(ax,.57,.47,.35,.14,'Minimized cross-PIP network view\ngraph features recomputed inside each split',fc=PG,ec=GREEN,fs=9.5,bold=True)
for x in [.365,.595]: arrow(ax,x,.47,.49,.35)
box(ax,.29,.22,.42,.13,'Paired graph-level inference\ndelta_i = AP_network,i - AP_local,i\nbootstrap CI + Wilcoxon + sign test + family heterogeneity',fc=PO,ec=ORANGE,fs=9.5,bold=True)
arrow(ax,.50,.22,.50,.12)
box(ax,.15,.02,.70,.10,'Prospective effectiveness gate: investigator time -> SAR/STR quality -> FIU feedback\nrestraint/recovery -> harm/fairness',fc=BLUE,ec=BLUE,fs=9.0,bold=True,textcolor=WHITE)
fig.tight_layout(); fig.savefig(OUT/'v7_aml_evaluation.png',bbox_inches='tight'); fig.savefig(OUT/'v7_aml_evaluation.svg',bbox_inches='tight'); plt.close(fig)

# 6 sanctions
fig,ax=setup(12,6.2)
items=[('Versioned\nofficial lists','records | aliases\nidentifiers'),('Candidate\nretrieval','multilingual | phonetic\ntoken'),('Evidence\nscoring','name + DOB + POB\naddress'),('Policy\nfrontier','recall vs workload\nversus harm'),('Analyst\ndisposition','reason code | escalation\naudit'),('Ownership\ngraph','direct + indirect\naggregate control')]
xs=[.015,.18,.345,.51,.675,.84]
for (a,b),x in zip(items,xs): box(ax,x,.66,.14,.22,a+'\n'+b,fc=PALE if x<.51 else PO,ec=BLUE if x<.51 else ORANGE,fs=7.1,bold=True)
for x1,x2 in zip(xs[:-1],xs[1:]): arrow(ax,x1+.135,.77,x2,.77)
box(ax,.06,.35,.26,.16,'Calibration split\nselect threshold before test\nreport PR-AUC, Brier and ECE',fc=LG,fs=9.2,bold=True)
box(ax,.37,.35,.26,.16,'Prevalence-adjusted workload\nPPV(pi), false alerts / million\nanalyst-hours / million',fc=PG,ec=GREEN,fs=9.2,bold=True)
box(ax,.68,.35,.26,.16,'Operational gate\nreal customer distribution\nmultilingual adjudication\nlive ownership and legal review',fc=PO,ec=ORANGE,fs=9.2,bold=True)
arrow(ax,.32,.43,.37,.43); arrow(ax,.63,.43,.68,.43)
box(ax,.16,.08,.68,.14,'A screening score ranks possible matches; it is not a legal determination\nof blocking, licensing or ownership.',fc=BLUE,ec=BLUE,fs=9.4,bold=True,textcolor=WHITE)
fig.tight_layout(); fig.savefig(OUT/'v7_sanctions_workflow.png',bbox_inches='tight'); fig.savefig(OUT/'v7_sanctions_workflow.svg',bbox_inches='tight'); plt.close(fig)

# 7 economic
fig,ax=setup(12,6.2)
box(ax,.04,.72,.20,.17,'Jurisdiction data\nhousehold demand | banks\nstress | distribution',fc=PALE,fs=9.5,bold=True)
box(ax,.30,.72,.20,.17,'Partial identification\nfeasible H, F and r ranges\nunder explicit exposure caps',fc=PG,ec=GREEN,fs=9.5,bold=True)
box(ax,.56,.72,.20,.17,'Robust optimization\nexpected loss + CVaR\nstability | utility | inclusion',fc=PO,ec=ORANGE,fs=9.5,bold=True)
box(ax,.82,.72,.15,.17,'Governed choice\npublish uncertainty\nreview quarterly',fc=LG,fs=9.2,bold=True)
for x1,x2 in [(.24,.30),(.50,.56),(.76,.82)]: arrow(ax,x1,.805,x2,.805)
box(ax,.08,.39,.24,.17,'Normal-state instruments\nholding threshold H\ntiered remuneration r\nautomatic sweep',fc=PALE,fs=9.4,bold=True)
box(ax,.38,.39,.24,.17,'Stress instruments\nflow limit F\nliquidity facilities\ntime-limited emergency rule',fc=PO,ec=ORANGE,fs=9.4,bold=True)
box(ax,.68,.39,.24,.17,'Outcome monitoring\ndeposit substitution | funding\npayment utility | subgroup burden',fc=PG,ec=GREEN,fs=9.4,bold=True)
arrow(ax,.32,.475,.38,.475); arrow(ax,.62,.475,.68,.475)
box(ax,.14,.09,.72,.15,'No universal correct limit: the valid output is a jurisdiction-specific feasible set\nplus a transparent update rule.',fc=BLUE,ec=BLUE,fs=9.7,bold=True,textcolor=WHITE)
fig.tight_layout(); fig.savefig(OUT/'v7_economic_decision.png',bbox_inches='tight'); fig.savefig(OUT/'v7_economic_decision.svg',bbox_inches='tight'); plt.close(fig)

# 8 performance
fig,ax=setup(12,6.8)
stages=[('1. Analytical lower bound','service demand | utilization cap\nheadroom | bottleneck units',.035),('2. Trace-driven digital twin','bursts | queues | region loss\nHSM slowdown | overload control',.275),('3. Physical qualification','3+ regions | certified HSMs\nproduction PIPs | sustained load',.515),('4. Governed pilot','real workload | operations\nindependent audit | exit gate',.755)]
for title,sub,x in stages: box(ax,x,.66,.205,.225,title+'\n'+sub,fc=PALE if x<.515 else PG,ec=BLUE if x<.515 else GREEN,fs=8.15,bold=True,pad=.012)
for x1,x2 in [(.24,.275),(.48,.515),(.72,.755)]: arrow(ax,x1,.772,x2,.772)
box(ax,.045,.345,.27,.15,'Necessary lower bound\n$n_j \\geq \\lceil \\lambda b_j s_j / \\rho_{max} \\rceil$\ndoes not guarantee hardware sufficiency',fc=LG,fs=8.05,bold=True,pad=.012)
box(ax,.365,.345,.27,.15,'Model falsification\n40k TPS + region loss breaches SLO\nqueues expose unsafe capacity claims',fc=PO,ec=ORANGE,fs=8.05,bold=True,pad=.012)
box(ax,.685,.345,.27,.15,'Acceptance evidence\np99 | availability | RTO/RPO\nno split finality | invariant closure',fc=PG,ec=GREEN,fs=8.05,bold=True,pad=.012)
arrow(ax,.315,.420,.365,.420); arrow(ax,.635,.420,.685,.420)
box(ax,.11,.075,.78,.15,'National-scale performance is demonstrated only after physical multi-region qualification\nand an independently observed pilot — never by a capacity equation alone.',fc=BLUE,ec=BLUE,fs=8.8,bold=True,textcolor=WHITE)
fig.tight_layout(); fig.savefig(OUT/'v7_national_qualification.png',bbox_inches='tight'); fig.savefig(OUT/'v7_national_qualification.svg',bbox_inches='tight'); plt.close(fig)

print('created v7 diagrams')
