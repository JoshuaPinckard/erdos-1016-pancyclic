"""Run bounded exhaustive b=6..9 chunks sequentially."""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("output_root", type=Path)
    p.add_argument("--n", type=int, choices=(68, 69), required=True)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--b8-chunk", type=int, default=32)
    p.add_argument("--b9-chunk", type=int, default=16)
    p.add_argument("--pause", type=float, default=10.0)
    args = p.parse_args()
    args.log.parent.mkdir(parents=True, exist_ok=True)
    sys.stdout = args.log.open("w", encoding="utf-8", buffering=1)
    sys.stderr = sys.stdout
    script = Path(__file__).with_name("gpu_finish_b8_b9.py")
    import json
    counts = {}
    for line in (args.source / f"n{args.n}.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if 6 <= row["b"] <= 9:
            counts[row["b"]] = counts.get(row["b"], 0) + 1
    specs = ((b, chunk, counts.get(b, 0)) for b, chunk in ((6, 32), (7, 16), (8, args.b8_chunk), (9, args.b9_chunk)))
    for b, chunk, total in specs:
        for first in range(0, total, chunk):
            last = min(first + chunk, total)
            out = args.output_root / f"b{b}-{first:04d}-{last:04d}"
            if (out / "summary.json").exists():
                print(f"SKIP {out}", flush=True)
                continue
            print(f"START b={b} first={first} last={last}", flush=True)
            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(args.source),
                    str(out),
                    "--b",
                    str(b),
                    "--n",
                    str(args.n),
                    "--first",
                    str(first),
                    "--last",
                    str(last),
                ],
                check=True,
            )
            print(f"DONE b={b} first={first} last={last}", flush=True)
            import time
            time.sleep(args.pause)


if __name__ == "__main__":
    main()
