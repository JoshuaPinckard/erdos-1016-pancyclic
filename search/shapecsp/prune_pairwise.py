"""PAIRWISE strengthening of the per-arc Hall prune in prune_probe.py.

prune_probe.py raises ONE arc's lower bound at a time: if `lows[i] = v` makes
bound.hall_ok fail, no pancyclic realisation has a_i >= v, so a_i <= v-1.  That
is a box [low_i, hi_i] and it measured 1.62x-1.91x on the n=70 manifests.

This module raises TWO arcs at once.  For every ordered pair (i, j) it computes

    T[i][j][u] = max { v : hall_ok still passes with lows_i = u and lows_j = v }

so the admissible region of (a_i, a_j) is the staircase under T.  Raising lows
only shrinks every form interval (see `soundness` below), so the feasible region
is downward closed in both coordinates and T is a complete description of it.

Counting the surviving compositions is exact, not estimated.  Assign the arcs in
a fixed order; the only thing an assigned arc does to the unassigned ones is
lower their caps, cap_j = min_k T[k][j][a_k].  So

    (arc index, partial sum, cap vector over the unassigned arcs)

is an exact DP state, and on the real manifests it stays small (peak a few
thousand states per shape).  The DP therefore yields the exact size of

    { a : sum a = n, low_i <= a_i <= hi_i, (a_i,a_j) in S_ij for every pair }

which is a superset of the pancyclic set, so using it as the GPU enumeration
domain cannot lose a solution.  The same table unranks, so the prune is
realisable in the kernel, not only measurable here.

Usage
  python prune_pairwise.py measure --source gpu-blast --n 70 --b 12
  python prune_pairwise.py selfcheck
  python prune_pairwise.py verify --source gpu-blast --n 68 --b 7
  python prune_pairwise.py verify --source gpu-blast --n 68 --b 7 --mutate-cap 1
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bound as B          # noqa: E402
import shapes as S         # noqa: E402


# --------------------------------------------------------------- soundness
#
# For arc lower bounds `lows` and a form f with arc mask M and |X_f| chords,
# bound.intervals gives L_f(a) in [mu_f, n - nu_f] for EVERY a with a >= lows
# and sum a = n.  Raising lows_i by d:
#   * forms with i in M       : `inside` and `tot` both rise by d, so mu_f rises
#                               by d and nu_f is unchanged;
#   * forms with i not in M   : `inside` is unchanged and `tot` rises by d, so
#                               nu_f rises by d and the upper end n - nu_f falls.
# Every interval therefore shrinks or stays, the value<->form bipartite graph
# only loses edges, and hall_ok is monotone non-increasing in `lows`.
#
# If a is pancyclic at n then each of the n-2 lengths in [3, n] is realised by a
# distinct cycle, i.e. a matching saturating [3, n] exists, so hall_ok must hold
# for ANY lows <= a.  Taking lows' = lows with lows'_i = a_i and lows'_j = a_j is
# legal (a >= lows'), so a pancyclic a satisfies every constraint derived here.
# Failure of hall_ok at (u, v) therefore excludes only non-pancyclic points.


def hall_batch(lo, hi, n):
    """Vectorised bound.hall_ok over a batch of interval systems.

    lo, hi : (K, F) int arrays, one row per candidate.  Rows where lo > hi are
    empty forms and must not count; they are folded to n+1 so they fall out of
    both cumulative counts.  Returns a (K,) bool array.

    cnt(x,y) = #{f : lo_f <= y and hi_f >= x} = #{lo <= y} - #{hi < x} because
    {lo > y} and {hi < x} are disjoint for x <= y.  Hall on value intervals is
    cnt(x,y) >= y-x+1 for all 3 <= x <= y <= n, i.e.

        (#{lo <= y} - y) + (x - #{hi < x}) >= 1,

    so a suffix minimum over y of the first term settles every y at once.
    """
    lo = np.asarray(lo)
    hi = np.asarray(hi)
    K, F = lo.shape
    dead = lo > hi
    lo = np.where(dead, n + 1, np.clip(lo, 0, n + 1))
    hi = np.where(dead, n + 1, np.clip(hi, 0, n + 1))
    width = n + 2
    base = (np.arange(K, dtype=np.int64) * width)[:, None]
    cl = np.bincount((base + lo).ravel(), minlength=K * width).reshape(K, width)
    chh = np.bincount((base + hi).ravel(), minlength=K * width).reshape(K, width)
    ys = np.arange(width, dtype=np.int64)
    g = np.cumsum(cl, axis=1) - ys                       # #{lo <= y} - y
    cum_hi = np.cumsum(chh, axis=1)
    h = ys - np.concatenate([np.zeros((K, 1), np.int64), cum_hi[:, :-1]], axis=1)
    # the suffix minimum must stop at y = n.  Bin n+1 is where the dead forms
    # were parked, so g[n+1] counts them and is meaningless; letting it into the
    # minimum rejects any shape with fewer than about n forms.
    gm = g[:, :n + 1]
    gmin = np.minimum.accumulate(gm[:, ::-1], axis=1)[:, ::-1]
    xs = np.arange(3, n + 1)
    return (gmin[:, xs] + h[:, xs] >= 1).all(axis=1)


class Shape:
    """One manifest row, with per-form vectors so a Hall test under raised lows
    costs O(F + n) and can be batched."""

    def __init__(self, b, chords, forms, lows):
        self.b = b
        self.chords = [tuple(c) for c in chords]
        self.lows = list(lows)
        self.forms = forms
        self.nforms = len(forms)
        ch = np.array([c for _, c in forms], dtype=np.int64)
        memb = np.array([[(m >> i) & 1 for m, _ in forms] for i in range(b)],
                        dtype=np.int64)
        low = np.array(lows, dtype=np.int64)
        inside = (memb * low[:, None]).sum(0)
        self.ch = ch
        self.memb = memb
        self.low = low
        self.base_lo = inside + ch                      # mu before max(3, .)
        self.base_up = (int(low.sum()) - inside) - ch    # nu before max(0, .)

    def hall_raises(self, n, D):
        """D: (K, b) int array of per-arc raises above `lows`.  One bool per row.

        This is the only place the Hall test is evaluated, so selfcheck, the
        per-arc scan and the pair grids all exercise the same arithmetic.
        """
        D = np.asarray(D, dtype=np.int64).reshape(-1, self.b)
        dlo = D @ self.memb                       # (K, F)
        dup = D @ (1 - self.memb)
        lo = np.maximum(3, self.base_lo[None, :] + dlo)
        up = np.minimum(n, n - np.maximum(0, self.base_up[None, :] + dup))
        ok = hall_batch(lo, up, n)
        # lows that already overshoot n admit no composition at all
        ok &= int(self.low.sum()) + D.sum(axis=1) <= n
        return ok

    def hall_grid(self, n, raises):
        """raises: list of {arc: delta}; convenience wrapper over hall_raises."""
        D = np.zeros((len(raises), self.b), dtype=np.int64)
        for k, spec in enumerate(raises):
            for arc, d in spec.items():
                D[k, arc] = d
        return self.hall_raises(n, D)

    # ---------------------------------------------------- per-arc (baseline)
    def per_arc_caps(self, n):
        hi = []
        for i in range(self.b):
            span = np.arange(self.lows[i], n + 1, dtype=np.int64)
            D = np.zeros((span.size, self.b), dtype=np.int64)
            D[:, i] = span - self.lows[i]
            ok = self.hall_raises(n, D)
            bad = np.nonzero(~ok)[0]
            first = int(bad[0]) if bad.size else span.size
            hi.append(int(span[first - 1]) if first else self.lows[i] - 1)
        return hi

    # ---------------------------------------------------------- pairwise
    def pair_staircases(self, n, hi):
        """T[(i, j)][u - lows[i]] = greatest a_j compatible with a_i = u.

        One batched Hall evaluation per unordered pair over the whole
        [low_i,hi_i] x [low_j,hi_j] grid; both orientations read off that grid,
        so the region is computed once and never approximated.
        """
        T = {}
        grids = 0
        for i in range(self.b):
            for j in range(i + 1, self.b):
                us = np.arange(self.lows[i], hi[i] + 1, dtype=np.int64)
                vs = np.arange(self.lows[j], hi[j] + 1, dtype=np.int64)
                if us.size == 0 or vs.size == 0:
                    T[(i, j)] = [self.lows[j] - 1] * int(us.size)
                    T[(j, i)] = [self.lows[i] - 1] * int(vs.size)
                    continue
                D = np.zeros((us.size * vs.size, self.b), dtype=np.int64)
                D[:, i] = np.repeat(us - self.lows[i], vs.size)
                D[:, j] = np.tile(vs - self.lows[j], us.size)
                ok = self.hall_raises(n, D).reshape(us.size, vs.size)
                grids += 1
                # greatest admissible v per u, and symmetrically greatest u per v
                any_v = ok.any(axis=1)
                last_v = vs.size - 1 - np.argmax(ok[:, ::-1], axis=1)
                T[(i, j)] = np.where(any_v, vs[last_v], self.lows[j] - 1).tolist()
                any_u = ok.any(axis=0)
                last_u = us.size - 1 - np.argmax(ok[::-1, :], axis=0)
                T[(j, i)] = np.where(any_u, us[last_u], self.lows[i] - 1).tolist()
        return T, grids


def box_count_dp(n, lows, hi):
    """Exact |{a : sum a = n, lows <= a <= hi}| -- the per-arc baseline."""
    f = np.zeros(n + 1, dtype=object)
    f[0] = 1
    for i in range(len(lows)):
        g = np.zeros(n + 1, dtype=object)
        for v in range(lows[i], hi[i] + 1):
            if v > n:
                break
            g[v:] += f[:n + 1 - v]
        f = g
    return int(f[n])


def box_count_incexc(n, lows, hi):
    """Independent inclusion-exclusion count, exactly prune_probe.bounded_count,
    kept as a cross-check on box_count_dp."""
    b = len(lows)
    slack = n - sum(lows)
    if slack < 0:
        return 0
    caps = [hi[i] - lows[i] for i in range(b)]
    if any(c < 0 for c in caps):
        return 0
    tot = 0
    for mask in range(1 << b):
        s, bits = slack, 0
        for i in range(b):
            if mask >> i & 1:
                s -= caps[i] + 1
                bits += 1
        if s < 0:
            continue
        tot += (-1) ** bits * math.comb(s + b - 1, b - 1)
    return tot


def pair_count_dp(n, lows, hi, T, order=None, state_cap=4_000_000):
    """Exact count of the pairwise-admissible compositions.

    State after assigning order[:step] is (partial sum, caps of the arcs not yet
    assigned).  Counts for one cap vector are held as a vector over the partial
    sum so the sum dimension moves by array shifts.
    """
    b = len(lows)
    order = list(range(b)) if order is None else list(order)
    cur = {tuple(hi[j] for j in order): np.zeros(n + 1, dtype=object)}
    for arr in cur.values():
        arr[0] = 1
    peak = 1
    for step, i in enumerate(order):
        rest = [order[q] for q in range(step + 1, b)]
        lo_rest = sum(lows[j] for j in rest)
        nxt = {}
        for caps, arr in cur.items():
            top = min(caps[0], n)
            for v in range(lows[i], top + 1):
                new_caps = []
                dead = False
                for q, j in enumerate(rest, start=1):
                    lim = min(caps[q], T[(i, j)][v - lows[i]])
                    if lim < lows[j]:
                        dead = True
                        break
                    new_caps.append(lim)
                if dead:
                    continue
                hi_rest = sum(new_caps)
                key = tuple(new_caps)
                tgt = nxt.get(key)
                if tgt is None:
                    tgt = nxt[key] = np.zeros(n + 1, dtype=object)
                # a prefix sum s is only useful when n-s-v is still reachable
                lo_s = max(0, n - v - hi_rest)
                hi_s = n - v - lo_rest
                if hi_s < lo_s:
                    continue
                src = arr[lo_s:hi_s + 1]
                tgt[lo_s + v:hi_s + v + 1] += src
        cur = nxt
        peak = max(peak, len(cur))
        if peak > state_cap:
            raise RuntimeError(f"pair DP state blow-up: {peak} states")
    return int(sum(int(arr[n]) for arr in cur.values())), peak


def build(row):
    chords = [tuple(c) for c in row["chords"]]
    forms = sorted(set(S.cycle_forms(row["b"], chords)))
    return Shape(row["b"], chords, forms, list(row["lows"]))


def load_rows(source, n, b):
    path = Path(source) / f"n{n}.jsonl"
    return [r for r in (json.loads(l) for l in path.read_text(encoding="utf-8").splitlines())
            if r["b"] == b]


# ------------------------------------------------------------------ measure
def cmd_measure(args):
    rows = load_rows(args.source, args.n, args.b)
    if args.limit:
        rows = rows[:args.limit]
    n = args.n
    # resume: a long run can be killed by whatever launched it, so re-read the
    # shapes already recorded and append rather than starting over
    done = {}
    if args.out and Path(args.out).exists():
        for line in Path(args.out).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue          # a kill can truncate the last line
            if "shape_index" in rec:
                done[rec["shape_index"]] = rec
    out = open(args.out, "a", encoding="utf-8", newline="\n") if args.out else None
    tot_base = tot_box = tot_pair = 0
    ratios_box, ratios_pair, secs, peaks = [], [], [], []
    empty_shapes = blow_ups = 0
    for r in rows:
        if r["shape_index"] in done:
            rec = done[r["shape_index"]]
            tot_base += rec["total"]
            tot_box += rec["box_admitted"]
            tot_pair += rec["pair_admitted"]
            ratios_box.append(rec["total"] / rec["box_admitted"]
                              if rec["box_admitted"] else float("inf"))
            ratios_pair.append(rec["total"] / rec["pair_admitted"]
                               if rec["pair_admitted"] else float("inf"))
            secs.append(rec["seconds"])
            peaks.append(rec["peak_states"])
            empty_shapes += (rec["pair_admitted"] == 0)
            blow_ups += bool(rec.get("dp_state_blow_up"))
            continue
        t0 = time.perf_counter()
        sh = build(r)
        hi = sh.per_arc_caps(n)
        box = box_count_dp(n, sh.lows, hi)
        if box != box_count_incexc(n, sh.lows, hi):
            raise RuntimeError(f"box count disagreement on shape {r['shape_index']}")
        base = math.comb(n - sum(sh.lows) + sh.b - 1, sh.b - 1)
        if base != r["total"]:
            raise RuntimeError(f"manifest total mismatch on shape {r['shape_index']}")
        T, grids = sh.pair_staircases(n, hi)
        try:
            pair, peak = pair_count_dp(n, sh.lows, hi, T)
            blew_up = False
        except RuntimeError:
            # fall back to the weaker but always-countable box, so one awkward
            # shape degrades the number instead of losing the whole tier
            pair, peak, blew_up = box, -1, True
        if pair > box:
            raise RuntimeError(f"pairwise count exceeds box count on {r['shape_index']}")
        dt = time.perf_counter() - t0
        tot_base += base
        tot_box += box
        tot_pair += pair
        ratios_box.append(base / box if box else float("inf"))
        ratios_pair.append(base / pair if pair else float("inf"))
        secs.append(dt)
        peaks.append(peak)
        empty_shapes += (pair == 0)
        rec = {"shape_index": r["shape_index"], "n": n, "b": sh.b, "lows": sh.lows,
               "hi": hi, "total": base, "box_admitted": box, "pair_admitted": pair,
               "f_perarc": round(base / box, 3) if box else None,
               "f_pairwise": round(base / pair, 3) if pair else None,
               "pair_over_perarc": round(box / pair, 3) if pair else None,
               "peak_states": peak, "pair_grids": grids, "seconds": round(dt, 3),
               "dp_state_blow_up": blew_up}
        if out:
            out.write(json.dumps(rec) + "\n")
            out.flush()
        else:
            print(json.dumps(rec), flush=True)
        blow_ups += blew_up
    summary = {
        "summary": True, "n": n, "b": args.b, "shapes": len(rows),
        "total_ranks": tot_base, "perarc_ranks": tot_box, "pairwise_ranks": tot_pair,
        "aggregate_prune_perarc": round(tot_base / tot_box, 4) if tot_box else None,
        "aggregate_prune_pairwise": round(tot_base / tot_pair, 4) if tot_pair else None,
        "pairwise_over_perarc": round(tot_box / tot_pair, 4) if tot_pair else None,
        "median_shape_prune_perarc": round(statistics.median(ratios_box), 3),
        "median_shape_prune_pairwise": round(statistics.median(ratios_pair), 3)
        if all(x != float("inf") for x in ratios_pair) else "inf-present",
        "shapes_emptied": empty_shapes,
        "shapes_fallen_back_to_box": blow_ups,
        "cpu_seconds_total": round(sum(secs), 2),
        "cpu_seconds_per_shape_mean": round(sum(secs) / len(secs), 4),
        "cpu_seconds_per_shape_max": round(max(secs), 3),
        "peak_dp_states_max": max(peaks),
    }
    (out.write(json.dumps(summary) + "\n") if out else print(json.dumps(summary)))
    if out:
        out.close()
        print(json.dumps(summary))


# ---------------------------------------------------------------- selfcheck
def cmd_selfcheck(args):
    """hall_batch must agree with bound.hall_ok, which is the trusted test."""
    rng = random.Random(args.seed)
    rows = []
    for n in (68, 69, 70):
        for b in (6, 7, 8, 9, 10, 11, 12):
            # small b means few forms; that is exactly where a mis-scoped
            # suffix minimum over the value range shows up, so do not skip it
            rows += [(n, r) for r in load_rows(args.source, n, b)[:args.shapes]]
    checked = disagree = 0
    for n, r in rows:
        sh = build(r)
        specs = []
        for _ in range(args.trials):
            specs.append({i: rng.randrange(0, 9) for i in range(sh.b)})
        mine = sh.hall_grid(n, specs)
        for k, spec in enumerate(specs):
            probe = [sh.lows[i] + spec.get(i, 0) for i in range(sh.b)]
            if sum(probe) > n:
                theirs = False
            else:
                iv, _ = B.intervals(sh.b, sh.chords, sh.forms, probe)
                theirs = B.hall_ok(iv, n)
            checked += 1
            disagree += int(bool(mine[k]) != theirs)
    print(json.dumps({"selfcheck": "hall_batch vs bound.hall_ok",
                      "checks": checked, "disagreements": disagree,
                      "verdict": "GREEN" if disagree == 0 else "RED"}))
    return 0 if disagree == 0 else 1


# ------------------------------------------------------------------- verify
def unrank_block(ranks, n, lows, table):
    """Vectorised colex unrank, the same map gpu_search.unrank implements.

    C(x, j) is non-decreasing in x, so the largest x with C(x, j) <= rank is a
    searchsorted; the cuts come out strictly decreasing on their own.
    """
    b = len(lows)
    m = n - sum(lows) + b - 1
    rem = ranks.astype(np.int64).copy()
    cuts = np.zeros((len(ranks), b - 1), dtype=np.int64)
    for j in range(b - 1, 0, -1):
        col = table[:m, j]
        x = np.searchsorted(col, rem, side="right") - 1
        cuts[:, j - 1] = x
        rem -= col[x]
    pts = np.concatenate([np.full((len(ranks), 1), -1, np.int64), cuts,
                          np.full((len(ranks), 1), m, np.int64)], axis=1)
    return np.diff(pts, axis=1) - 1 + np.array(lows, dtype=np.int64)[None, :]


def sat_mask(arcs, sh, n):
    """The GPU's own predicate, transcribed from the `scan` kernel in
    gpu_search.py: accumulate the realised lengths into two 64-bit words and
    demand every length in [3, n]."""
    K = arcs.shape[0]
    # form-major layout: every update is then a contiguous row add.  The
    # composition-major version needs fancy column indexing, which copies, and
    # measured 1.73 s per 200k rows against 0.05 s here.
    lensT = np.empty((sh.nforms, K), dtype=np.int32)
    lensT[:] = sh.ch.astype(np.int32)[:, None]
    for i in range(sh.b):
        ai = arcs[:, i].astype(np.int32)
        for f in np.nonzero(sh.memb[i])[0]:
            lensT[f] += ai
    # Covering [3, n] implies covering any single value in it.  Screening on a
    # few values first is cheaper than the full scatter and changes no verdict:
    # survivors still get the complete test below.
    ok = np.ones(K, dtype=bool)
    for v in (3, n, 4, n - 1):
        ok &= (lensT == v).any(axis=0)
        if not ok.any():
            return ok
    idx = np.nonzero(ok)[0]
    sub = lensT[:, idx].T
    cov = np.zeros((idx.size, n + 2), dtype=bool)
    np.put_along_axis(cov, np.where((sub >= 3) & (sub <= n), sub, n + 1).astype(np.intp),
                      True, axis=1)
    ok[idx] = cov[:, 3:n + 1].all(axis=1)
    return ok


def admitted_mask(arcs, lows, hi, T, mutate_cap=0):
    """Membership in the pairwise-admissible set, evaluated per composition.

    Deliberately written independently of pair_count_dp: this is the predicate,
    that is the counter, and cmd_verify plays one against the other.
    """
    b = len(lows)
    ok = np.ones(arcs.shape[0], dtype=bool)
    for i in range(b):
        ok &= (arcs[:, i] >= lows[i]) & (arcs[:, i] <= hi[i] - mutate_cap)
    if not ok.any():
        return ok
    for i in range(b):
        for j in range(b):
            if i == j or not T[(i, j)]:
                continue
            col = np.array(T[(i, j)], dtype=np.int64)
            idx = np.clip(arcs[:, i] - lows[i], 0, len(col) - 1)
            ok &= arcs[:, j] <= col[idx] - mutate_cap
    return ok


def _check_unrank(row, n, table, trials=400, seed=1016):
    """unrank_block must reproduce gpu_search.unrank, the map the kernel uses."""
    lows = list(row["lows"])
    b = row["b"]
    total = math.comb(n - sum(lows) + b - 1, b - 1)
    rng = random.Random(seed)
    ranks = np.array([0, total - 1] + [rng.randrange(total) for _ in range(trials)],
                     dtype=np.int64)
    got = unrank_block(ranks, n, lows, table[:, :b])
    for k, r in enumerate(ranks.tolist()):
        want = _reference_unrank(r, n, lows)
        if list(map(int, got[k])) != want:
            raise RuntimeError(f"unrank_block disagrees with the reference at rank {r}")


def _reference_unrank(rank, n, lows):
    """Verbatim copy of gpu_search.unrank; gpu_search itself imports cupy, so it
    cannot be imported on a machine whose GPU must not be touched."""
    b = len(lows)
    m = n - sum(lows) + b - 1
    cuts = [0] * (b - 1)
    hi = m - 1
    for j in range(b - 1, 0, -1):
        x = hi
        while math.comb(x, j) > rank:
            x -= 1
        cuts[j - 1] = x
        rank -= math.comb(x, j)
        hi = x - 1
    points = [-1] + cuts + [m]
    return [points[i + 1] - points[i] - 1 + lows[i] for i in range(b)]


def cmd_verify(args):
    """Exhaustive superset check: enumerate EVERY composition of the tier, count
    the ones the full feasibility test accepts and the ones the bound admits, and
    report any composition that is feasible but not admitted."""
    rows = load_rows(args.source, args.n, args.b)
    if args.limit:
        rows = rows[:args.limit]
    n = args.eval_n or args.n
    if n != args.n:
        # same shapes, different n.  lows depend only on the shape (an arc a
        # chord duplicates needs length >= 2), so the row just needs a new total.
        for r in rows:
            r["total"] = math.comb(n - sum(r["lows"]) + r["b"] - 1, r["b"] - 1)
    width = max(r["b"] for r in rows) + 1
    table = np.array([[math.comb(x, j) for j in range(width)]
                      for x in range(n + 2)], dtype=np.int64)
    # cross-check the vectorised unrank against the reference in gpu_search
    _check_unrank(rows[0], n, table)
    grand = {"enumerated": 0, "sat": 0, "admitted": 0, "sat_not_admitted": 0}
    t0 = time.perf_counter()
    for r in rows:
        sh = build(r)
        hi = sh.per_arc_caps(n)
        T, _ = sh.pair_staircases(n, hi)
        total = r["total"]
        col = table[:, :sh.b]
        enumerated = sat = adm = bad = 0
        first_bad = None
        for off in range(0, total, args.chunk):
            k = min(args.chunk, total - off)
            ranks = np.arange(off, off + k, dtype=object)
            arcs = unrank_block(ranks, n, sh.lows, col)
            assert (arcs.sum(axis=1) == n).all(), "unrank produced a bad composition"
            s = sat_mask(arcs, sh, n)
            a = admitted_mask(arcs, sh.lows, hi, T, args.mutate_cap)
            enumerated += k
            sat += int(s.sum())
            adm += int(a.sum())
            miss = s & ~a
            if miss.any():
                bad += int(miss.sum())
                if first_bad is None:
                    first_bad = arcs[np.nonzero(miss)[0][0]].tolist()
        # the enumeration counts the admissible set one composition at a time;
        # pair_count_dp counts it with a state machine.  They must agree, or one
        # of the two is lying about what the bound admits.
        dp_adm = None
        if not args.mutate_cap:
            dp_adm, _ = pair_count_dp(n, sh.lows, hi, T)
        print(json.dumps({"shape_index": r["shape_index"], "n": n, "b": sh.b,
                          "enumerated": enumerated, "total": total,
                          "feasible_full_test": sat, "admitted_by_bound": adm,
                          "admitted_by_dp": dp_adm,
                          "dp_matches_enumeration": None if dp_adm is None else dp_adm == adm,
                          "feasible_but_excluded": bad,
                          "first_excluded_feasible": first_bad}), flush=True)
        if dp_adm is not None and dp_adm != adm:
            raise RuntimeError(f"pair_count_dp {dp_adm} != enumerated {adm} "
                               f"on shape {r['shape_index']}")
        grand["enumerated"] += enumerated
        grand["sat"] += sat
        grand["admitted"] += adm
        grand["sat_not_admitted"] += bad
    grand.update({"summary": True, "n": n, "b": args.b, "shapes": len(rows),
                  "mutate_cap": args.mutate_cap,
                  "seconds": round(time.perf_counter() - t0, 1),
                  "verdict": "GREEN superset" if grand["sat_not_admitted"] == 0
                  else "RED: bound excludes a feasible composition"})
    print(json.dumps(grand))
    return 0 if grand["sat_not_admitted"] == 0 else 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--affinity", default=None,
                   help="comma-separated CPU cores to pin to, at below-normal "
                        "priority, e.g. --affinity 6,7")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("measure")
    m.add_argument("--source", default="gpu-blast")
    m.add_argument("--n", type=int, required=True)
    m.add_argument("--b", type=int, required=True)
    m.add_argument("--limit", type=int, default=0)
    m.add_argument("--out")
    m.set_defaults(fn=cmd_measure)

    c = sub.add_parser("selfcheck")
    c.add_argument("--source", default="gpu-blast")
    c.add_argument("--shapes", type=int, default=4)
    c.add_argument("--trials", type=int, default=150)
    c.add_argument("--seed", type=int, default=1016)
    c.set_defaults(fn=cmd_selfcheck)

    v = sub.add_parser("verify")
    v.add_argument("--source", default="gpu-blast")
    v.add_argument("--n", type=int, required=True)
    v.add_argument("--b", type=int, required=True)
    v.add_argument("--limit", type=int, default=0)
    v.add_argument("--chunk", type=int, default=200_000)
    v.add_argument("--eval-n", type=int, default=0,
                   help="take the shapes from the --n manifest but run the whole "
                        "check at this n instead; the point is to land on an n "
                        "where the feasible set is NOT empty, so containment has "
                        "something to contain")
    v.add_argument("--mutate-cap", type=int, default=0,
                   help="shave this much off every cap; a sound bound must go RED")
    v.set_defaults(fn=cmd_verify)

    args = p.parse_args()
    if args.affinity:
        try:
            import psutil
            proc = psutil.Process()
            proc.cpu_affinity([int(x) for x in args.affinity.split(",") if x != ""])
            if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS"):
                proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except Exception as exc:                       # never let pinning stop work
            print(f"WARNING could not pin: {exc!r}", file=sys.stderr)
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
