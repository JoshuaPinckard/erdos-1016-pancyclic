"""Pairwise-admissible composition space of one shape: exact DP-state tables,
prefix rank/unrank, and an independent reference enumeration.  See SPEC.md.

The set enumerated is

    A = { a in Z^b : sum a = n,  lows_i <= a_i <= hi_i,
                     a_j <= T[i][j][a_i]  for every ordered pair i != j }

with lows from bound.intervals, hi from prune_pairwise.Shape.per_arc_caps and T
from prune_pairwise.Shape.pair_staircases.  bound.hall_ok is a necessary
condition for pancyclicity that is monotone non-increasing in the arc lower
bounds, so raising (lows_i, lows_j) to (a_i, a_j) for a pancyclic a keeps it
true; hence every pancyclic composition lies in A (argument at the top of
prune_pairwise.py).  Enumerating A exactly is therefore an exhaustion of the
shape.

Arcs are assigned in index order.  A PREFIX is (a_0, .., a_{b-3}); the last two
arcs are the COMPLETION and are enumerated in-thread on the GPU.

    states[k]   cap vectors (upper bounds for arcs k..b-1) reachable after
                a_0..a_{k-1}; states[0] = [hi]
    trans[k]    (nst_k, vmax+1) int32: state index at level k+1 reached by
                a_k = v, or -1 (v below lows_k, v above the state's cap, or a
                cap of a later arc falling below its lows).  -1 is monotone in
                v once v >= lows_k; build() asserts this.
    C           (nst_{b-2}, n+1) int64: number of valid (a_{b-2}, a_{b-1})
                completions from (state, prefix sum s)
    P[k]        (nst_k, n+1) int64: number of prefix extensions (a_k..a_{b-3})
                from (state, s) whose end has at least one completion;
                P[b-2] = [C > 0]
    F[k]        forward counts of prefixes reaching (state, s); only used to
                cross-check totals, never by the kernel

Prefix rank r is the lexicographic position of (a_0..a_{b-3}) among prefixes
with P > 0.  total_prefixes = P[0][0][0].  total_compositions = sum F[b-2]*C,
which build() checks against prune_pairwise.pair_count_dp, an independently
written counter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
if str(PROD) not in sys.path:
    sys.path.insert(0, str(PROD))
import shapes as S              # noqa: E402
import bound as B               # noqa: E402
import prune_pairwise as PP     # noqa: E402

FORMAT = "pairwise-tables-v1"
UNIT_PREFIX = 1 << 30           # prefix ranks per runner unit, recorded in each tier manifest.
                                # 2^27 measured 0.15 gpu_s per unit against ~0.27 s of wall per
                                # unit (state write + launch), i.e. ~45% overhead; 2^30 is ~1.7 s
                                # of GPU per unit.  The runner reads the size from the manifest.


# ------------------------------------------------------------------ derivation
def derive(n, b, chords, lows=None):
    """forms, lows, hi, T for one shape at level n, all from the measured code."""
    chords = [tuple(int(x) for x in c) for c in chords]
    forms = sorted(set(S.cycle_forms(b, chords)))
    _, derived = B.intervals(b, chords, forms)
    derived = [int(x) for x in derived]
    if lows is not None and [int(x) for x in lows] != derived:
        raise ValueError("manifest lows disagree with bound.intervals")
    sh = PP.Shape(b, chords, forms, derived)
    hi = [int(x) for x in sh.per_arc_caps(n)]
    T, _ = sh.pair_staircases(n, hi)
    return forms, derived, hi, T


def tarr_from(b, lows, hi, T):
    """Tarr[i][j][u] = greatest admissible a_j when a_i = u (absolute), -1 outside
    [lows_i, hi_i].  Asserts the staircases are non-increasing in u, which is
    what downward closure of the Hall region predicts; a violation would mean
    the batched Hall test is not monotone and nothing below may rely on it."""
    vmax = max(max(hi), max(lows))
    Tarr = np.full((b, b, vmax + 1), -1, dtype=np.int32)
    for i in range(b):
        for j in range(b):
            if i == j:
                continue
            col = T[(i, j)]
            us = list(range(lows[i], hi[i] + 1))
            if len(col) != len(us):
                raise ValueError(f"staircase length {len(col)} != box width {len(us)} for pair {(i, j)}")
            for k, u in enumerate(us):
                Tarr[i, j, u] = int(col[k])
            for k in range(len(us) - 1):
                if col[k] < col[k + 1]:
                    raise ValueError(f"staircase T[{i}][{j}] increases at u={us[k]}: {col[k]} < {col[k + 1]}")
    return Tarr, vmax


# ----------------------------------------------------------------------- build
def build(n, b, chords, lows=None, shape_index=None, check=True):
    """All tables for one shape.  check=True also runs the independent counter."""
    t0 = time.perf_counter()
    if b < 4:
        raise ValueError("need b >= 4 (two completion arcs and at least two prefix arcs)")
    chords = [tuple(int(x) for x in c) for c in chords]
    forms, lows, hi, T = derive(n, b, chords, lows)
    Tarr, vmax = tarr_from(b, lows, hi, T)
    lowsA = np.array(lows, dtype=np.int64)
    empty = sum(lows) > n or any(hi[i] < lows[i] for i in range(b))

    state_lists = [[tuple(hi)]]
    trans = []
    if not empty:
        for k in range(b - 2):
            cur = state_lists[k]
            nxt_index, nxt_list = {}, []
            tr = np.full((len(cur), vmax + 1), -1, dtype=np.int32)
            lo_rest = lowsA[k + 1:]
            for si, caps in enumerate(cur):
                cap0 = caps[0]
                if cap0 < lows[k]:
                    continue
                vs = np.arange(lows[k], cap0 + 1)
                sub = Tarr[k, k + 1:, :][:, vs]                     # (b-k-1, V)
                newc = np.minimum(np.array(caps[1:], dtype=np.int64)[:, None], sub)
                dead = (newc < lo_rest[:, None]).any(axis=0)
                first_dead = int(np.argmax(dead)) if bool(dead.any()) else len(vs)
                if not bool(dead[first_dead:].all()):
                    raise ValueError(f"dead transitions are not monotone at level {k}, state {caps}")
                for t in range(first_dead):
                    key = tuple(int(x) for x in newc[:, t])
                    idx = nxt_index.get(key)
                    if idx is None:
                        idx = len(nxt_list)
                        nxt_index[key] = idx
                        nxt_list.append(key)
                    tr[si, int(vs[t])] = idx
            trans.append(tr)
            state_lists.append(nxt_list)

    # completions
    last = state_lists[b - 2] if not empty else []
    Tlast = Tarr[b - 2, b - 1]
    C = np.zeros((len(last), n + 1), dtype=np.int64)
    ss = np.arange(n + 1)
    for si, (cA, cB) in enumerate(last):
        if cA < lows[b - 2] or cB < lows[b - 1]:
            raise ValueError("a dead state reached the completion level")
        vs = np.arange(lows[b - 2], cA + 1)
        w = n - ss[None, :] - vs[:, None]
        valid = (w >= lows[b - 1]) & (w <= cB) & (w <= Tlast[vs][:, None])
        C[si] = valid.sum(axis=0)

    # backward counts P and forward counts F
    P = [None] * (b - 1)
    F = [None] * (b - 1)
    if not empty:
        P[b - 2] = (C > 0).astype(np.int64)
        for k in range(b - 3, -1, -1):
            Pk = np.zeros((len(state_lists[k]), n + 1), dtype=np.int64)
            tr = trans[k]
            for v in range(lows[k], min(vmax, n) + 1):
                col = tr[:, v]
                m = col >= 0
                if not bool(m.any()):
                    continue
                Pk[m, :n + 1 - v] += P[k + 1][col[m], v:]
            P[k] = Pk
        F[0] = np.zeros((1, n + 1), dtype=np.int64)
        F[0][0, 0] = 1
        for k in range(b - 2):
            Fn = np.zeros((len(state_lists[k + 1]), n + 1), dtype=np.int64)
            tr = trans[k]
            for v in range(lows[k], min(vmax, n) + 1):
                col = tr[:, v]
                m = col >= 0
                if not bool(m.any()):
                    continue
                np.add.at(Fn, (col[m], slice(v, n + 1)), F[k][m, :n + 1 - v])
            F[k + 1] = Fn
        total_prefixes = int(P[0][0, 0])
        total_compositions = int((F[b - 2] * C).sum())
        prefixes_forward = int((F[b - 2] * (C > 0)).sum())
        if prefixes_forward != total_prefixes:
            raise ValueError(f"forward/backward prefix counts disagree: {prefixes_forward} != {total_prefixes}")
    else:
        total_prefixes = 0
        total_compositions = 0
        P = [np.zeros((1, n + 1), dtype=np.int64) for _ in range(b - 1)]
        F = [np.zeros((1, n + 1), dtype=np.int64) for _ in range(b - 1)]
        for k in range(b - 2):
            trans.append(np.full((1, vmax + 1), -1, dtype=np.int32))
            state_lists.append([tuple([-1] * (b - k - 1))])
        C = np.zeros((1, n + 1), dtype=np.int64)

    if check:
        if empty:
            independent = 0
        else:
            independent, _ = PP.pair_count_dp(n, lows, hi, T)
        if independent != total_compositions:
            raise ValueError(f"pair_count_dp {independent} != table total {total_compositions}")

    tab = dict(format=FORMAT, n=int(n), b=int(b), chords=[list(c) for c in chords],
               shape_index=shape_index, lows=lows, hi=hi, vmax=int(vmax),
               forms=[[int(m), int(c)] for m, c in forms],
               nstates=[len(x) for x in state_lists],
               total_prefixes=total_prefixes, total_compositions=total_compositions,
               empty=bool(empty),
               Tarr=Tarr,
               states=[np.array(x, dtype=np.int32).reshape(len(x), -1) for x in state_lists],
               trans=trans, C=C, P=P,
               build_seconds=round(time.perf_counter() - t0, 3))
    tab["tables_sha256"] = tables_sha256(tab)
    return tab


# ------------------------------------------------------------------ hashing/io
_HEADER_KEYS = ("format", "n", "b", "chords", "lows", "hi", "vmax", "forms", "nstates",
                "total_prefixes", "total_compositions", "empty")


def header(tab):
    return {k: tab[k] for k in _HEADER_KEYS}


def _array_items(tab):
    b = tab["b"]
    yield "Tarr", tab["Tarr"]
    for k in range(b - 1):
        yield f"states_{k}", tab["states"][k]
    for k in range(b - 2):
        yield f"trans_{k}", tab["trans"][k]
    for k in range(b - 1):
        yield f"P_{k}", tab["P"][k]
    yield "C", tab["C"]


def tables_sha256(tab):
    h = hashlib.sha256()
    h.update(json.dumps(header(tab), sort_keys=True, separators=(",", ":")).encode())
    for name, arr in _array_items(tab):
        a = np.ascontiguousarray(arr)
        dt = "<i4" if a.dtype.kind == "i" and a.dtype.itemsize == 4 else "<i8"
        a = a.astype(dt, copy=False)
        h.update(f"\n{name}:{dt}:{a.shape}\n".encode())
        h.update(a.tobytes(order="C"))
    return h.hexdigest()


def save(path, tab):
    arrays = {name: arr for name, arr in _array_items(tab)}
    np.savez_compressed(str(path), header=np.frombuffer(
        json.dumps(header(tab), sort_keys=True).encode(), dtype=np.uint8), **arrays)


def load(path, expected_sha256=None):
    z = np.load(str(path))
    hd = json.loads(bytes(z["header"]).decode())
    if hd["format"] != FORMAT:
        raise ValueError(f"unexpected tables format {hd['format']!r}")
    b = hd["b"]
    tab = dict(hd)
    tab["Tarr"] = z["Tarr"]
    tab["states"] = [z[f"states_{k}"] for k in range(b - 1)]
    tab["trans"] = [z[f"trans_{k}"] for k in range(b - 2)]
    tab["P"] = [z[f"P_{k}"] for k in range(b - 1)]
    tab["C"] = z["C"]
    tab["tables_sha256"] = tables_sha256(tab)
    if expected_sha256 is not None and tab["tables_sha256"] != expected_sha256:
        raise ValueError(f"tables hash mismatch for {path}: {tab['tables_sha256']} != {expected_sha256}")
    return tab


# ------------------------------------------------------------- rank / unrank
def unrank_prefix(tab, r):
    """r -> (prefix arcs a_0..a_{b-3}, end state index, prefix sum).  CPU mirror
    of the kernel's loop."""
    n, b, lows, vmax = tab["n"], tab["b"], tab["lows"], tab["vmax"]
    if not 0 <= r < tab["total_prefixes"]:
        raise ValueError("prefix rank out of range")
    st, s, a = 0, 0, []
    for k in range(b - 2):
        tr = tab["trans"][k][st]
        Pn = tab["P"][k + 1]
        picked = None
        for v in range(lows[k], vmax + 1):
            st2 = int(tr[v])
            if st2 < 0 or s + v > n:
                break
            c = int(Pn[st2, s + v])
            if r < c:
                picked = v
                break
            r -= c
        if picked is None:
            raise RuntimeError("rank exhausted the transitions (tables inconsistent)")
        a.append(picked)
        st = int(tr[picked])
        s += picked
    if int(tab["C"][st, s]) <= 0:
        raise RuntimeError("unranked prefix has no completion (tables inconsistent)")
    return a, st, s


def rank_prefix(tab, prefix):
    """Inverse of unrank_prefix; raises on a prefix outside the admissible set."""
    n, b, lows, vmax = tab["n"], tab["b"], tab["lows"], tab["vmax"]
    if len(prefix) != b - 2:
        raise ValueError("prefix must have b-2 arcs")
    r, st, s = 0, 0, 0
    for k in range(b - 2):
        tr = tab["trans"][k][st]
        Pn = tab["P"][k + 1]
        ak = int(prefix[k])
        if ak < lows[k] or ak > vmax or int(tr[ak]) < 0 or s + ak > n:
            raise ValueError(f"a_{k}={ak} is not admissible after {prefix[:k]}")
        for v in range(lows[k], ak):
            st2 = int(tr[v])
            if st2 < 0 or s + v > n:
                break
            r += int(Pn[st2, s + v])
        st = int(tr[ak])
        s += ak
    if int(tab["C"][st, s]) <= 0:
        raise ValueError("prefix has no completion, so it has no rank")
    return r, st, s


def completions(tab, st, s):
    """Valid (a_{b-2}, a_{b-1}) from (end state, prefix sum), by increasing a_{b-2}."""
    n, b, lows = tab["n"], tab["b"], tab["lows"]
    cA, cB = (int(x) for x in tab["states"][b - 2][st])
    Tlast = tab["Tarr"][b - 2, b - 1]
    out = []
    vlo = max(lows[b - 2], n - s - cB)
    vhi = min(cA, n - s - lows[b - 1])
    for v in range(vlo, vhi + 1):
        w = n - s - v
        if w <= int(Tlast[v]):
            out.append((v, w))
    return out


def iterate_compositions(tab):
    """Every a in A, in (prefix rank, a_{b-2}) order -- the kernel's visiting order."""
    for r in range(tab["total_prefixes"]):
        a, st, s = unrank_prefix(tab, r)
        for v, w in completions(tab, st, s):
            yield a + [v, w]


def admitted(tab, a):
    """Membership in A, checked directly from Tarr in BOTH directions."""
    n, b, lows, hi, Tarr = tab["n"], tab["b"], tab["lows"], tab["hi"], tab["Tarr"]
    if len(a) != b or sum(a) != n:
        return False
    for i in range(b):
        if not lows[i] <= a[i] <= hi[i]:
            return False
    for i in range(b):
        for j in range(b):
            if i != j and a[j] > int(Tarr[i, j, a[i]]):
                return False
    return True


# ------------------------------------------------------------------ reference
def enumerate_admissible(n, lows, hi, Tarr):
    """Plain recursion over arcs in index order; no ranks, no DP, no tables.
    Every pair constraint is applied in both directions.  Lexicographic order."""
    b = len(lows)
    out = []
    cur = [0] * b

    def rec(k, left):
        if k == b - 1:
            v = left
            if v < lows[k] or v > hi[k]:
                return
            for j in range(k):
                if v > int(Tarr[j, k, cur[j]]) or cur[j] > int(Tarr[k, j, v]):
                    return
            cur[k] = v
            out.append(list(cur))
            return
        rest_low = sum(lows[k + 1:])
        for v in range(lows[k], hi[k] + 1):
            if left - v < rest_low:
                break
            ok = True
            for j in range(k):
                if v > int(Tarr[j, k, cur[j]]) or cur[j] > int(Tarr[k, j, v]):
                    ok = False
                    break
            if not ok:
                continue
            cur[k] = v
            rec(k + 1, left - v)

    if sum(lows) <= n and all(hi[i] >= lows[i] for i in range(b)):
        rec(0, n)
    return out


def sat(n, forms, a):
    """The kernel's satisfaction rule on the CPU: every length in [3, n] realised."""
    seen = set()
    for mask, ch in forms:
        ln = ch
        for j in range(len(a)):
            if mask >> j & 1:
                ln += a[j]
        if 3 <= ln <= n:
            seen.add(ln)
    return all(x in seen for x in range(3, n + 1))


# --------------------------------------------------------------- kernel pack
def kernel_pack(tab):
    """Flat little arrays for one shape, in the layout gpu_search_pairwise expects."""
    b, n = tab["b"], tab["n"]
    trans_off, parts, off = [], [], 0
    for k in range(b - 2):
        trans_off.append(off)
        parts.append(tab["trans"][k].ravel())
        off += tab["trans"][k].size
    trans_flat = np.concatenate(parts).astype(np.int32)
    P_off, parts, off = [0] * (b - 1), [], 0
    for k in range(1, b - 1):
        P_off[k] = off
        parts.append(tab["P"][k].ravel())
        off += tab["P"][k].size
    P_flat = np.concatenate(parts).astype(np.uint64)
    last = tab["states"][b - 2]
    return dict(
        n=n, b=b, vmax=tab["vmax"],
        lows=np.array(tab["lows"], np.int32), hi=np.array(tab["hi"], np.int32),
        trans_flat=trans_flat, trans_off=np.array(trans_off, np.int64),
        P_flat=P_flat, P_off=np.array(P_off, np.int64),
        capA=last[:, 0].astype(np.int32), capB=last[:, 1].astype(np.int32),
        Tlast=tab["Tarr"][b - 2, b - 1].astype(np.int32),
        masks=np.array([m for m, _ in tab["forms"]], np.int32),
        cs=np.array([c for _, c in tab["forms"]], np.int32),
        total_prefixes=int(tab["total_prefixes"]),
        total_compositions=int(tab["total_compositions"]))


# ----------------------------------------------------------------- tier build
def manifest_rows(source, n, b):
    raw = (Path(source) / f"n{n}.jsonl").read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    return hashlib.sha256(raw).hexdigest(), [r for r in rows if r["b"] == b]


def _pin(affinity):
    if not affinity:
        return
    try:
        import psutil
        p = psutil.Process()
        p.cpu_affinity([int(x) for x in affinity.split(",") if x != ""])
        if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS"):
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception as exc:                          # pinning must never stop the work
        print(f"WARNING could not pin: {exc!r}", file=sys.stderr)


def _build_one(args):
    n, row, out_dir, affinity = args
    _pin(affinity)
    tab = build(n, row["b"], row["chords"], row["lows"], shape_index=row["shape_index"])
    if out_dir:
        save(Path(out_dir) / f"shape-{row['shape_index']}.npz", tab)
    return row["shape_index"], dict(tables_sha256=tab["tables_sha256"],
                                    total_prefixes=tab["total_prefixes"],
                                    total_compositions=tab["total_compositions"],
                                    unrestricted_total=int(row["total"]),
                                    nstates=tab["nstates"], build_seconds=tab["build_seconds"],
                                    empty=tab["empty"])


def build_tier(source, n, b, out_dir, workers=1, affinity=None, shapes=None, save_arrays=True):
    """Tables for every manifest shape of tier (n, b), plus tier-manifest.json.
    Deterministic: the same inputs give byte-identical hashes on any machine."""
    source_sha256, rows = manifest_rows(source, n, b)
    if shapes is not None:
        keep = set(shapes)
        rows = [r for r in rows if r["shape_index"] in keep]
    out = Path(out_dir) / f"n{n}-b{b}"
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(n, r, str(out) if save_arrays else None, affinity) for r in rows]
    t0 = time.perf_counter()
    results = {}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for idx, meta in ex.map(_build_one, jobs, chunksize=1):
                results[idx] = meta
                print(json.dumps({"shape_index": idx, **{k: meta[k] for k in ("total_prefixes", "total_compositions", "build_seconds")}}), flush=True)
    else:
        _pin(affinity)
        for job in jobs:
            idx, meta = _build_one(job)
            results[idx] = meta
            print(json.dumps({"shape_index": idx, **{k: meta[k] for k in ("total_prefixes", "total_compositions", "build_seconds")}}), flush=True)
    manifest = dict(format=FORMAT, n=n, b=b, source_sha256=source_sha256, unit_prefix=UNIT_PREFIX,
                    shapes={str(k): results[k] for k in sorted(results)},
                    tier_total_prefixes=sum(m["total_prefixes"] for m in results.values()),
                    tier_total_compositions=sum(m["total_compositions"] for m in results.values()),
                    tier_unrestricted_ranks=sum(m["unrestricted_total"] for m in results.values()),
                    excluded=[k for k in sorted(results) if results[k]["total_compositions"] == 0],
                    shapes_count=len(results), partial=shapes is not None,
                    build_wall_seconds=round(time.perf_counter() - t0, 1))
    with (out / "tier-manifest.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("build-tier")
    t.add_argument("--source", default=str(PROD / "gpu-blast"))
    t.add_argument("--n", type=int, required=True)
    t.add_argument("--b", type=int, required=True)
    t.add_argument("--out", default=str(HERE / "tables"))
    t.add_argument("--workers", type=int, default=1)
    t.add_argument("--affinity", default=None)
    t.add_argument("--no-save", action="store_true", help="manifest only, no .npz arrays")
    t.add_argument("--shapes", default=None, help="JSON list of shape_index to restrict to")
    o = sub.add_parser("one")
    o.add_argument("--source", default=str(PROD / "gpu-blast"))
    o.add_argument("--n", type=int, required=True)
    o.add_argument("--shape-index", type=int, required=True)
    args = p.parse_args()
    if args.cmd == "build-tier":
        shapes = json.loads(Path(args.shapes).read_text()) if args.shapes else None
        m = build_tier(args.source, args.n, args.b, args.out, args.workers, args.affinity, shapes,
                       save_arrays=not args.no_save)
        print(json.dumps({k: m[k] for k in m if k != "shapes"}), flush=True)
    else:
        _, rows = manifest_rows(args.source, args.n, None)
        rows = [json.loads(l) for l in (Path(args.source) / f"n{args.n}.jsonl").read_text().splitlines()]
        row = next(r for r in rows if r["shape_index"] == args.shape_index)
        tab = build(args.n, row["b"], row["chords"], row["lows"], shape_index=row["shape_index"])
        print(json.dumps({k: tab[k] for k in ("n", "b", "lows", "hi", "vmax", "nstates", "total_prefixes",
                                                "total_compositions", "build_seconds", "tables_sha256")}))


if __name__ == "__main__":
    main()
