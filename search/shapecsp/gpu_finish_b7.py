"""Controls-first exhaustive completion of the small b=7 residual spaces.

The source manifests must come from gpu_search.py. Output is explicitly only
the eligible b=7 subset, not a census of all six-chord shapes.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
import gpu_search as G


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('output',type=Path)
    args=p.parse_args(); args.output.mkdir(parents=True,exist_ok=False)
    engine=G.Engine(12,70,127)
    control=G.controls(engine)
    (args.output/'controls.json').write_text(json.dumps(control,indent=2)+'\n',encoding='utf-8')
    print('POSITIVE CONTROL PASS',flush=True)
    summary=dict(scope='all eligible b=7 shapes from source manifests',levels=[])
    for n in (68,69,70):
        raw=(args.source/f'n{n}.jsonl').read_bytes()
        rows=[json.loads(x) for x in raw.splitlines()]
        rows=[r for r in rows if r['b']==7]
        t0=time.time(); seconds=0; hits=[]
        with (args.output/f'n{n}.jsonl').open('x',encoding='utf-8',newline='\n') as f:
            for row in rows:
                d=G.record(row['b'],row['chords'])
                found,dt,_=engine.run(n,[d],[row['start']],[row['step']],row['total'])
                for hit in found:
                    hit['shape_index']=row['shape_index']
                    print('VERIFIED SAT',json.dumps(hit),flush=True)
                hits.extend(found); seconds+=dt
                row['count']=row['total']; f.write(json.dumps(row)+'\n'); f.flush()
        level=dict(n=n,eligible=len(rows),tested=sum(r['count'] for r in rows),gpu_seconds=seconds,
            wall_seconds=time.time()-t0,start_time=t0,end_time=time.time(),hits=hits,
            source_sha256=hashlib.sha256(raw).hexdigest())
        summary['levels'].append(level)
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(level),flush=True)


if __name__=='__main__': main()
