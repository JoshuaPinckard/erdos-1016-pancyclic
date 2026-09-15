"""Audit exact per-shape coverage and resource measurements from a completed run."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics


def summarize(directory,resources,mutate=False):
    summary=json.loads((directory/'summary.json').read_text())
    samples=[json.loads(x) for x in resources.read_text().splitlines()]
    out=[]
    for level in summary['levels']:
        n=level['n']; path=directory/f'n{n}.jsonl'; raw=path.read_bytes()
        rows=[json.loads(x) for x in raw.splitlines()]
        if mutate: rows=rows[1:]
        if len(rows)!=level['eligible'] or len({r['shape_index'] for r in rows})!=len(rows):
            raise ValueError('coverage census missing or duplicated rows')
        if sum(r['count'] for r in rows)!=level['tested']:
            raise ValueError('tested count disagrees with coverage rows')
        by_b=collections.defaultdict(lambda:dict(exhausted=0,partial=0,total_ranks=0,tested=0,remaining=0))
        exhausted=[]
        for r in rows:
            total=math.comb(n-sum(r['lows'])+r['b']-1,r['b']-1)
            if r['total']!=total or not 0<r['count']<=total or math.gcd(r['step'],total)!=1 or not 0<=r['start']<total:
                raise ValueError('invalid rank coverage')
            entry=by_b[r['b']]
            entry['exhausted' if r['count']==total else 'partial']+=1
            entry['total_ranks']+=total; entry['tested']+=r['count']; entry['remaining']+=total-r['count']
            if r['count']==total: exhausted.append(r)
        if level['hits']: raise ValueError('SAT run must not be summarized as a miss')
        active=[r for r in samples if level['start_time']<=r['time']<=level['end_time']]
        util=[float(r['gpu'].split(',')[0]) for r in active if r['gpu_exit']==0 and r['gpu']]
        cpu=[r['child_cpu_percent'] for r in active]
        remaining=sum(r['total']-r['count'] for r in rows)
        out.append(dict(n=n,eligible=len(rows),exhausted=exhausted,by_b=dict(sorted(by_b.items())),
            remaining=remaining,estimated_remaining_days_at_observed_rate=remaining/level['assignments_per_second']/86400,
            max_per_shape_total=max(r['total'] for r in rows),manifest_sha256=hashlib.sha256(raw).hexdigest(),
            gpu_samples=len(util),gpu_util_mean=statistics.mean(util),gpu_util_median=statistics.median(util),
            gpu_util_min=min(util),gpu_util_max=max(util),child_cpu_mean=statistics.mean(cpu),child_cpu_max=max(cpu)))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path); p.add_argument('resources',type=Path)
    p.add_argument('--mutate',action='store_true'); args=p.parse_args()
    result=summarize(args.directory,args.resources,args.mutate)
    (args.directory/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
