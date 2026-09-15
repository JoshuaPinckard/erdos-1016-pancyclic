"""Re-enumerate every b<=7 shape and audit the combined exhaustive manifests."""
import argparse
import collections
import json
import math
from pathlib import Path
import shapes as S
import bound as B


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('blast',type=Path); p.add_argument('b7',type=Path)
    p.add_argument('--mutate',action='store_true'); args=p.parse_args()
    census=S.shapes(6,b_values=range(4,8))
    data=[]
    for b,ch in census:
        forms=sorted(set(S.cycle_forms(b,ch))); iv,lows=B.intervals(b,ch,forms)
        data.append((b,ch,forms,iv,lows))
    result=dict(census_by_b=dict(collections.Counter(b for b,ch in census)),levels=[])
    for n in (68,69,70):
        original=[json.loads(x) for x in (args.blast/f'n{n}.jsonl').read_text().splitlines()]
        added=[json.loads(x) for x in (args.b7/f'n{n}.jsonl').read_text().splitlines()]
        rows=[r for r in original if r['b']<=6]+added
        if args.mutate: rows=rows[1:]
        expected={(b,ch) for b,ch,forms,iv,lows in data if len(forms)+2>=n and sum(lows)<=n and B.hall_ok(iv,n)}
        actual={(r['b'],tuple(map(tuple,r['chords']))) for r in rows}
        if actual!=expected or len(rows)!=len(actual): raise ValueError('small-shape census incomplete')
        for r in rows:
            total=math.comb(n-sum(r['lows'])+r['b']-1,r['b']-1)
            _,lows=B.intervals(r['b'],r['chords'])
            if r['lows']!=lows or r['total']!=total or r['count']!=total or math.gcd(r['step'],total)!=1:
                raise ValueError('small-shape rank space not exhausted')
        for source in (args.blast,args.b7):
            level=next(l for l in json.loads((source/'summary.json').read_text())['levels'] if l['n']==n)
            if level['hits']: raise ValueError('SAT contradicts exclusion')
        result['levels'].append(dict(n=n,exhausted_shapes=len(rows),ranks=sum(r['total'] for r in rows),
            exhausted_by_b=dict(collections.Counter(r['b'] for r in rows)),
            ineligible_small_shapes=len(census)-len(rows),result='EXHAUSTED; no SAT'))
    (args.b7/'census-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__': main()
