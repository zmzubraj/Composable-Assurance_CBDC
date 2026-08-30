from __future__ import annotations
import itertools, json
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'results';RES.mkdir(exist_ok=True)
N=7;F=2;Q=5
HONEST=tuple(range(N-F));BYZ=tuple(range(N-F,N))
DECISIONS=('COMMIT','ABORT')

# State: honest locks, prepare votes, commit votes, certificates, ledger states.
# Byzantine votes are adversarially available for both decisions. Honest nodes vote once.
init=(tuple([None]*len(HONEST)), frozenset(), frozenset(), frozenset(), 'PREPARED','PREPARED')

def count_votes(votes,decision,phase):
    honest=sum(1 for p,n,d in votes if p==phase and d==decision and n in HONEST)
    return honest+len(BYZ)  # worst case: all Byzantine keys vote for either decision

def actions(s):
    locks,prep,commit,certs,la,lb=s
    out=[]
    # honest prepare vote if unlocked or same decision
    for hi,n in enumerate(HONEST):
        for d in DECISIONS:
            if locks[hi] in (None,d):
                nl=list(locks);nl[hi]=d
                np=set(prep);np.add(('PREPARE',n,d))
                out.append((f'prepare_{n}_{d}',(tuple(nl),frozenset(np),commit,certs,la,lb)))
    # honest commit vote after prepare quorum
    for hi,n in enumerate(HONEST):
        d=locks[hi]
        if d and count_votes(prep,d,'PREPARE')>=Q:
            nc=set(commit);nc.add(('COMMIT',n,d))
            out.append((f'commitvote_{n}_{d}',(locks,prep,frozenset(nc),certs,la,lb)))
    # certificate issue after commit quorum
    for d in DECISIONS:
        if count_votes(commit,d,'COMMIT')>=Q and d not in certs:
            cs=set(certs);cs.add(d)
            out.append((f'cert_{d}',(locks,prep,commit,frozenset(cs),la,lb)))
    # ledger finalization from certificate
    if 'COMMIT' in certs:
        if la=='PREPARED':out.append(('ledgerA_commit',(locks,prep,commit,certs,'COMMITTED',lb)))
        if lb=='PREPARED':out.append(('ledgerB_commit',(locks,prep,commit,certs,la,'COMMITTED')))
    if 'ABORT' in certs:
        if la=='PREPARED':out.append(('ledgerA_abort',(locks,prep,commit,certs,'ABORTED',lb)))
        if lb=='PREPARED':out.append(('ledgerB_abort',(locks,prep,commit,certs,la,'ABORTED')))
    return out

def unsafe(s):
    locks,prep,commit,certs,la,lb=s
    return {
        'conflicting_certificates': len(certs)>1,
        'split_finality': {la,lb}=={'COMMITTED','ABORTED'},
        'commit_without_certificate': ('COMMITTED' in (la,lb)) and 'COMMIT' not in certs,
        'abort_without_certificate': ('ABORTED' in (la,lb)) and 'ABORT' not in certs,
    }

q=deque([init]);seen={init};edges=0;violations=[];terminal=[];parent={init:(None,None)}
while q:
    s=q.popleft();acts=actions(s)
    if not acts:terminal.append(s)
    for name,nxt in acts:
        edges+=1
        bad=unsafe(nxt)
        if any(bad.values()):violations.append({'state':str(nxt),'bad':bad,'action':name})
        if nxt not in seen:
            seen.add(nxt);parent[nxt]=(s,name);q.append(nxt)

def trace(s):
    out=[]
    while parent[s][0] is not None:
        s0,a=parent[s];out.append(a);s=s0
    return list(reversed(out))

committed=[s for s in seen if s[-2:]==('COMMITTED','COMMITTED')]
aborted=[s for s in seen if s[-2:]==('ABORTED','ABORTED')]
summary={
    'nodes':N,'byzantine_keys':F,'quorum':Q,'honest_one_decision_lock':True,
    'reachable_states':len(seen),'transition_edges':edges,'terminal_states':len(terminal),
    'conflicting_certificate_violations':sum(v['bad']['conflicting_certificates'] for v in violations),
    'split_finality_violations':sum(v['bad']['split_finality'] for v in violations),
    'commit_without_certificate_violations':sum(v['bad']['commit_without_certificate'] for v in violations),
    'abort_without_certificate_violations':sum(v['bad']['abort_without_certificate'] for v in violations),
    'example_commit_trace':trace(committed[0]) if committed else [],
    'example_abort_trace':trace(aborted[0]) if aborted else [],
    'proof_boundary':'Exhaustive abstract model assumes at most two Byzantine signing keys, honest durable one-decision locks, signature unforgeability and correct ledger certificate verification. It does not model cryptographic side channels, key recovery, dynamic membership or denial-of-service liveness.'
}
(RES/'cross_border_model_v5.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
