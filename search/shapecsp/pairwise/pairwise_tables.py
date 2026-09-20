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

Arcs are assigned in the order given by `order` (default natural 0..b-1): level
k assigns natural arc order[k].  A PREFIX is the first b-2 assigned arcs; the
last two are the COMPLETION and are enumerated in-thread on the GPU.  A itself
does not depend on order, so total_compositions is invariant under it while
total_prefixes is not: putting the two widest arcs last moves work out of the
per-prefix unrank (b-2 dependent global loads) into the in-thread completion
loop.  lows, hi, Tarr and forms stay in NATURAL arc order -- they describe the
shape; states, trans, P and C are in ASSIGNMENT order, and natural()/permuted()
move a vector between the two.

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

FORMAT = "pairwise-tables-v1"      # legacy header: no shape_index, no order, natural order only
FORMAT_V2 = "pairwise-tables-v2"   # header records shape_index and order, and hashes both
FORMATS = (FORMAT, FORMAT_V2)
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


# ------------------------------------------------------------------ arc order
def check_order(b, order):
    """Validate an assignment order; None means the natural 0..b-1."""
    if order is None:
        return list(range(b))
    order = [int(x) for x in order]
    if sorted(order) != list(range(b)):
        raise ValueError(f"order must be a permutation of 0..{b - 1}, got {order}")
    return order


def ordered_view(order, lows, hi, Tarr):
    """lows/hi/Tarr re-indexed by assignment position: position k holds natural
    arc order[k].  Tarr values are ABSOLUTE arc values, so the value axis is not
    touched -- only the two arc axes are permuted."""
    idx = np.asarray(order, dtype=np.int64)
    return ([lows[i] for i in order], [hi[i] for i in order],
            np.ascontiguousarray(Tarr[np.ix_(idx, idx)]))


def natural(tab, a_ord):
    """Assignment-order arc vector -> natural arc order."""
    order = tab["order"]
    if len(a_ord) != len(order):
        raise ValueError("vector length does not match b")
    out = [0] * len(order)
    for k, i in enumerate(order):
        out[i] = int(a_ord[k])
    return out


def permuted(tab, a_nat):
    """Natural arc vector -> assignment order."""
    if len(a_nat) != len(tab["order"]):
        raise ValueError("vector length does not match b")
    return [int(a_nat[i]) for i in tab["order"]]


def ord_lows(tab):
    return [tab["lows"][i] for i in tab["order"]]


def ord_hi(tab):
    return [tab["hi"][i] for i in tab["order"]]


def permute_mask(mask, order):
    """Form mask over natural arcs -> over assignment positions: bit k of the
    result is bit order[k] of the input, so the kernel's a[j] indexing lines up
    with the arcs it actually assigned."""
    out = 0
    for k, i in enumerate(order):
        if mask >> i & 1:
            out |= 1 << k
    return out


ORDER_RULES = ("natural", "product", "min-width", "pair-mass-mean", "pair-mass-total")
REST_RULES = ("narrow-first", "wide-first", "natural")
MEASURED_RULE = "measured"                 # not in ORDER_RULES: it needs builds, not just derived data

# Measured over 40 real manifest shapes at n=68 b=11 and b=12, every completion
# pair built (papers/REPORT-pairwise-order.md): NO cheap rule beats the natural
# order.  Median gain in total_prefixes was 1.151 (product), 1.165 (min-width),
# 1.138 (pair-mass-total), 1.000 (pair-mass-mean), and each of them was WORSE
# than natural on 11 to 19 of the 40 shapes -- on the n68-b11 sample product and
# min-width lose by 1.56x in aggregate.  Only MEASURED_RULE, which builds every
# candidate pair, beat it (tier gain 1.42x at b=11, 1.79x at b=12), and it costs
# C(b,2) extra builds per shape.  So the default stays natural until the GPU
# benchmark window shows prefix count converting into GPU seconds.
DEFAULT_ORDER_RULE = "natural"


def pair_admissible_mass(lows, hi, Tarr, i, j):
    """counts[t] = how many (v, w) with v + w = t the pair (i, j) admits on its
    own: the box on both arcs and both staircase directions, and nothing else.

    A prefix with sum s draws its completions from the single column t = n - s,
    so the mean of this over the feasible totals estimates compositions per
    prefix, and it costs no DP at all.  The product of the two arc widths does
    NOT estimate it -- a completion is one point on the line v + w = t, not a
    point of the rectangle -- which is why the widest-product rule measured
    badly (papers/REPORT-pairwise-order.md)."""
    vs = np.arange(lows[i], hi[i] + 1)
    ws = np.arange(lows[j], hi[j] + 1)
    if vs.size == 0 or ws.size == 0:
        return np.zeros(1, dtype=np.int64)
    ok = (ws[None, :] <= Tarr[i, j, vs][:, None]) & (vs[:, None] <= Tarr[j, i, ws][None, :])
    return np.bincount((vs[:, None] + ws[None, :])[ok].ravel())


def order_from_derived(lows, hi, Tarr, rule=DEFAULT_ORDER_RULE, rest=REST_RULES[0]):
    """Assignment order from already-derived shape data.

    Separate from choose_order so that build() can resolve a rule name without a
    second derive(): derive() computes the pair staircases, which dominate the
    per-shape CPU cost at the levels this is built for."""
    if rule == MEASURED_RULE:
        raise ValueError(f"{MEASURED_RULE!r} cannot be resolved from derived data alone; "
                         f"call choose_order_measured(), which builds every candidate pair")
    if rule not in ORDER_RULES:
        raise ValueError(f"unknown order rule {rule!r}, expected one of {ORDER_RULES}")
    if rest not in REST_RULES:
        raise ValueError(f"unknown rest rule {rest!r}, expected one of {REST_RULES}")
    b = len(lows)
    if rule == "natural":
        return list(range(b))
    width = [hi[k] - lows[k] + 1 for k in range(b)]

    def score(i, j):
        if rule == "product":
            return float(width[i] * width[j])
        if rule == "min-width":
            return float(min(width[i], width[j]))
        counts = pair_admissible_mass(lows, hi, Tarr, i, j)
        if rule == "pair-mass-total":
            return float(counts.sum())
        nz = counts[counts > 0]
        return float(nz.mean()) if nz.size else 0.0

    # best score wins; ties go to the lowest index pair
    _, _, _, i, j = max((score(p, q), -p, -q, p, q)
                        for p in range(b) for q in range(p + 1, b))
    keep = [k for k in range(b) if k not in (i, j)]
    if rest == "narrow-first":
        keep.sort(key=lambda k: (width[k], k))
    elif rest == "wide-first":
        keep.sort(key=lambda k: (-width[k], k))
    return keep + [i, j]


def choose_order(n, b, chords, lows=None, rule=DEFAULT_ORDER_RULE, rest=REST_RULES[0]):
    """Standalone order for one shape, deriving the shape first.  build() takes
    a rule name directly and does not call this."""
    _forms, lows, hi, T = derive(n, b, chords, lows)
    Tarr, _vmax = tarr_from(b, lows, hi, T)
    return order_from_derived(lows, hi, Tarr, rule=rule, rest=rest)


def choose_order_measured(n, b, chords, lows=None, rest=REST_RULES[0]):
    """The completion pair that actually minimises total_prefixes, found by
    building the tables once for every candidate pair and keeping the smallest.

    Exact, deterministic, and the only rule measured to beat the natural order
    (papers/REPORT-pairwise-order.md: tier gain 1.42x at n68-b11 and 1.79x at
    n68-b12 over a 20-shape sample per tier).  It costs C(b,2) extra builds per
    shape -- about 70 s at n=68 b=11 and 120 s at b=12 on one core -- so it is a
    tier-build cost, never something to call per launch.  total_compositions does
    not depend on the order, so the minimum here is exactly the maximum of
    compositions per prefix, which is what the kernel is paid in."""
    _forms, lows, hi, T = derive(n, b, chords, lows)
    Tarr, _vmax = tarr_from(b, lows, hi, T)
    width = [hi[k] - lows[k] + 1 for k in range(b)]
    best, best_order = None, None
    for i in range(b):
        for j in range(i + 1, b):
            keep = [k for k in range(b) if k not in (i, j)]
            if rest == "narrow-first":
                keep.sort(key=lambda k: (width[k], k))
            elif rest == "wide-first":
                keep.sort(key=lambda k: (-width[k], k))
            order = keep + [i, j]
            tab = build(n, b, chords, lows, check=False, order=order)
            key = (tab["total_prefixes"], i, j)
            if best is None or key < best:
                best, best_order = key, order
    return best_order


# ----------------------------------------------------------------------- build
def build(n, b, chords, lows=None, shape_index=None, check=True, order=None, fmt=FORMAT_V2):
    """All tables for one shape.  check=True also runs the independent counter,
    which is given the same order and so checks the permuted DP against an
    independently written one rather than against itself.

    order is a permutation of the b arcs, the NAME of an order rule, or None for
    the natural order.  A name is resolved here, after derive(), so a build pays
    for the pair staircases exactly once.

    fmt selects the header: FORMAT_V2 records shape_index and order and hashes
    both; FORMAT is the legacy v1 header, which records neither and therefore
    accepts only the natural order.  Legacy exists so that a tier built before
    those keys can still be rebuilt hash-identically -- which is what
    verify_tier_exhaustion_pairwise.py --rebuild -1 does to earn its claim."""
    t0 = time.perf_counter()
    if b < 4:
        raise ValueError("need b >= 4 (two completion arcs and at least two prefix arcs)")
    chords = [tuple(int(x) for x in c) for c in chords]
    forms, lows, hi, T = derive(n, b, chords, lows)
    Tarr, vmax = tarr_from(b, lows, hi, T)
    if isinstance(order, str):
        order = order_from_derived(lows, hi, Tarr, rule=order)
    order = check_order(b, order)
    if fmt not in FORMATS:
        raise ValueError(f"unknown tables format {fmt!r}, expected one of {FORMATS}")
    if fmt == FORMAT and order != list(range(b)):
        raise ValueError(f"the legacy {FORMAT} header cannot record an arc order; "
                         f"use fmt={FORMAT_V2!r} for order {order}")
    lows_o, hi_o, Tarr_o = ordered_view(order, lows, hi, Tarr)
    lowsA = np.array(lows_o, dtype=np.int64)
    empty = sum(lows) > n or any(hi[i] < lows[i] for i in range(b))

    state_lists = [[tuple(hi_o)]]
    trans = []
    if not empty:
        for k in range(b - 2):
            cur = state_lists[k]
            nxt_index, nxt_list = {}, []
            tr = np.full((len(cur), vmax + 1), -1, dtype=np.int32)
            lo_rest = lowsA[k + 1:]
            for si, caps in enumerate(cur):
                cap0 = caps[0]
                if cap0 < lows_o[k]:
                    continue
                vs = np.arange(lows_o[k], cap0 + 1)
                sub = Tarr_o[k, k + 1:, :][:, vs]                   # (b-k-1, V)
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
    Tlast = Tarr_o[b - 2, b - 1]
    C = np.zeros((len(last), n + 1), dtype=np.int64)
    ss = np.arange(n + 1)
    for si, (cA, cB) in enumerate(last):
        if cA < lows_o[b - 2] or cB < lows_o[b - 1]:
            raise ValueError("a dead state reached the completion level")
        vs = np.arange(lows_o[b - 2], cA + 1)
        w = n - ss[None, :] - vs[:, None]
        valid = (w >= lows_o[b - 1]) & (w <= cB) & (w <= Tlast[vs][:, None])
        C[si] = valid.sum(axis=0)

    # backward counts P and forward counts F
    P = [None] * (b - 1)
    F = [None] * (b - 1)
    if not empty:
        P[b - 2] = (C > 0).astype(np.int64)
        for k in range(b - 3, -1, -1):
            Pk = np.zeros((len(state_lists[k]), n + 1), dtype=np.int64)
            tr = trans[k]
            for v in range(lows_o[k], min(vmax, n) + 1):
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
            for v in range(lows_o[k], min(vmax, n) + 1):
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
            independent, _ = PP.pair_count_dp(n, lows, hi, T, order=order)
        if independent != total_compositions:
            raise ValueError(f"pair_count_dp {independent} != table total {total_compositions}")

    tab = dict(format=fmt, n=int(n), b=int(b), chords=[list(c) for c in chords],
               shape_index=shape_index, order=order, lows=lows, hi=hi, vmax=int(vmax),
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
# v2 hashes shape_index and order with the rest: without shape_index a table
# file is bound to a shape but not to the index it is filed under (review finding
# 1/6), and without order the permuted arrays below are uninterpretable.  The key
# set is selected by the header's own format string, so a v1 file keeps hashing
# over exactly the v1 keys and its recorded hash still verifies -- and a v1 tier
# stays rebuildable byte-identically through build(fmt=FORMAT).
_HEADER_KEYS_V1 = ("format", "n", "b", "chords", "lows", "hi", "vmax", "forms", "nstates",
                   "total_prefixes", "total_compositions", "empty")
_HEADER_KEYS_V2 = ("format", "n", "b", "shape_index", "chords", "order", "lows", "hi", "vmax",
                   "forms", "nstates", "total_prefixes", "total_compositions", "empty")
_HEADER_KEYS = {FORMAT: _HEADER_KEYS_V1, FORMAT_V2: _HEADER_KEYS_V2}


def header(tab):
    fmt = tab["format"]
    if fmt not in _HEADER_KEYS:
        raise ValueError(f"unknown tables format {fmt!r}, expected one of {FORMATS}")
    return {k: tab[k] for k in _HEADER_KEYS[fmt]}


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


def tables_sha256(tab, hdr=None):
    """hdr overrides the derived header so load() hashes exactly the bytes that
    were stored, rather than a header this version would have written."""
    h = hashlib.sha256()
    h.update(json.dumps(header(tab) if hdr is None else hdr,
                        sort_keys=True, separators=(",", ":")).encode())
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
    if hd["format"] not in FORMATS:
        raise ValueError(f"unexpected tables format {hd['format']!r}, expected one of {FORMATS}")
    b = hd["b"]
    tab = dict(hd)
    tab["Tarr"] = z["Tarr"]
    tab["states"] = [z[f"states_{k}"] for k in range(b - 1)]
    tab["trans"] = [z[f"trans_{k}"] for k in range(b - 2)]
    tab["P"] = [z[f"P_{k}"] for k in range(b - 1)]
    tab["C"] = z["C"]
    tab["tables_sha256"] = tables_sha256(tab, hdr=hd)
    tab.setdefault("shape_index", None)
    tab.setdefault("order", list(range(b)))
    if expected_sha256 is not None and tab["tables_sha256"] != expected_sha256:
        raise ValueError(f"tables hash mismatch for {path}: {tab['tables_sha256']} != {expected_sha256}")
    return tab


# ------------------------------------------------------------- rank / unrank
def unrank_prefix(tab, r):
    """r -> (the first b-2 arcs in ASSIGNMENT order, end state index, prefix
    sum).  CPU mirror of the kernel's loop.  Use natural(tab, ...) for a vector
    in natural arc order."""
    n, b, vmax = tab["n"], tab["b"], tab["vmax"]
    lows = ord_lows(tab)
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
    """Inverse of unrank_prefix; prefix is in ASSIGNMENT order.  Raises on a
    prefix outside the admissible set."""
    n, b, vmax = tab["n"], tab["b"], tab["vmax"]
    lows = ord_lows(tab)
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
    """Valid values of the two completion arcs (assignment positions b-2 and
    b-1, i.e. natural arcs order[b-2] and order[b-1]) from (end state, prefix
    sum), by increasing first value."""
    n, b = tab["n"], tab["b"]
    lows, order = ord_lows(tab), tab["order"]
    cA, cB = (int(x) for x in tab["states"][b - 2][st])
    Tlast = tab["Tarr"][order[b - 2], order[b - 1]]
    out = []
    vlo = max(lows[b - 2], n - s - cB)
    vhi = min(cA, n - s - lows[b - 1])
    for v in range(vlo, vhi + 1):
        w = n - s - v
        if w <= int(Tlast[v]):
            out.append((v, w))
    return out


def iterate_compositions(tab):
    """Every a in A in NATURAL arc order, sequenced by (prefix rank, first
    completion value) -- the kernel's visiting order.  Under a non-natural order
    that sequence is not lexicographic in the natural coordinates, which is why
    the tests compare it as a set plus a per-prefix ordered block."""
    for r in range(tab["total_prefixes"]):
        a, st, s = unrank_prefix(tab, r)
        for v, w in completions(tab, st, s):
            yield natural(tab, a + [v, w])


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
    b, n, order = tab["b"], tab["n"], tab["order"]
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
        lows=np.array(ord_lows(tab), np.int32), hi=np.array(ord_hi(tab), np.int32),
        trans_flat=trans_flat, trans_off=np.array(trans_off, np.int64),
        P_flat=P_flat, P_off=np.array(P_off, np.int64),
        capA=last[:, 0].astype(np.int32), capB=last[:, 1].astype(np.int32),
        Tlast=tab["Tarr"][order[b - 2], order[b - 1]].astype(np.int32),
        masks=np.array([permute_mask(m, order) for m, _ in tab["forms"]], np.int32),
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
    n, row, out_dir, affinity, rule, fmt = args
    _pin(affinity)
    # a cheap rule NAME goes through to build(), which resolves it after
    # derive(); resolving it here would derive the shape twice.  The measured
    # rule is different: it has to build every candidate pair, so it is resolved
    # to an explicit order first.
    order = (choose_order_measured(n, row["b"], row["chords"], row["lows"])
             if rule == MEASURED_RULE else rule)
    tab = build(n, row["b"], row["chords"], row["lows"], shape_index=row["shape_index"],
                order=order, fmt=fmt)
    if out_dir:
        save(Path(out_dir) / f"shape-{row['shape_index']}.npz", tab)
    return row["shape_index"], dict(tables_sha256=tab["tables_sha256"],
                                    total_prefixes=tab["total_prefixes"],
                                    total_compositions=tab["total_compositions"],
                                    unrestricted_total=int(row["total"]),
                                    nstates=tab["nstates"],
                                    order=tab["order"],
                                    empty=tab["empty"]), tab["build_seconds"]


def build_tier(source, n, b, out_dir, workers=1, affinity=None, shapes=None, save_arrays=True,
               rule=DEFAULT_ORDER_RULE, fmt=FORMAT_V2):
    """Tables for every manifest shape of tier (n, b), plus tier-manifest.json.
    Deterministic: the same inputs give byte-identical hashes on any machine.

    rule names the arc-order rule; "natural" keeps 0..b-1.  The order chosen for
    each shape is recorded per shape in the manifest and hashed into that shape's
    tables_sha256, so a verifier rebuilds against the recorded order rather than
    against whatever this version's default rule happens to be."""
    if fmt == FORMAT and rule != "natural":      # noqa: E501 - legacy header carries no order
        raise ValueError(f"{FORMAT} cannot record an arc order; use rule='natural' or fmt={FORMAT_V2!r}")
    source_sha256, rows = manifest_rows(source, n, b)
    if shapes is not None:
        keep = set(shapes)
        rows = [r for r in rows if r["shape_index"] in keep]
    out = Path(out_dir) / f"n{n}-b{b}"
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(n, r, str(out) if save_arrays else None, affinity, rule, fmt) for r in rows]
    t0 = time.perf_counter()
    results, timings = {}, {}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for idx, meta, secs in ex.map(_build_one, jobs, chunksize=1):
                results[idx] = meta
                timings[idx] = secs
                print(json.dumps({"shape_index": idx, **{k: meta[k] for k in ("total_prefixes", "total_compositions")}, "build_seconds": secs}), flush=True)
    else:
        _pin(affinity)
        for job in jobs:
            idx, meta, secs = _build_one(job)
            results[idx] = meta
            timings[idx] = secs
            print(json.dumps({"shape_index": idx, **{k: meta[k] for k in ("total_prefixes", "total_compositions")}, "build_seconds": secs}), flush=True)
    # The manifest carries no wall-clock field, so two builds of the same tier
    # are byte-identical and its file hash is a real binding (review finding 3).
    # Timings go to a sidecar.
    manifest = dict(format=fmt, n=n, b=b, source_sha256=source_sha256, unit_prefix=UNIT_PREFIX,
                    order_rule=rule,
                    shapes={str(k): results[k] for k in sorted(results)},
                    tier_total_prefixes=sum(m["total_prefixes"] for m in results.values()),
                    tier_total_compositions=sum(m["total_compositions"] for m in results.values()),
                    tier_unrestricted_ranks=sum(m["unrestricted_total"] for m in results.values()),
                    excluded=[k for k in sorted(results) if results[k]["total_compositions"] == 0],
                    shapes_count=len(results), partial=shapes is not None)
    with (out / "tier-manifest.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    with (out / "tier-build.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(n=n, b=b, build_wall_seconds=round(time.perf_counter() - t0, 1), workers=workers,
                       build_seconds={str(k): timings[k] for k in sorted(timings)}), f, indent=1, sort_keys=True)
        f.write("\n")
    manifest["build_wall_seconds"] = round(time.perf_counter() - t0, 1)   # returned, not written
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
    t.add_argument("--order", default=DEFAULT_ORDER_RULE, choices=list(ORDER_RULES) + [MEASURED_RULE],
                   help=f"arc-order rule; natural keeps 0..b-1, {MEASURED_RULE} builds every candidate pair")
    t.add_argument("--format", default=FORMAT_V2, choices=list(FORMATS),
                   help=f"{FORMAT} is the legacy header and requires --order natural")
    o = sub.add_parser("one")
    o.add_argument("--source", default=str(PROD / "gpu-blast"))
    o.add_argument("--n", type=int, required=True)
    o.add_argument("--shape-index", type=int, required=True)
    o.add_argument("--order", default="natural", choices=list(ORDER_RULES) + [MEASURED_RULE])
    o.add_argument("--format", default=FORMAT_V2, choices=list(FORMATS))
    args = p.parse_args()
    if args.cmd == "build-tier":
        shapes = json.loads(Path(args.shapes).read_text()) if args.shapes else None
        m = build_tier(args.source, args.n, args.b, args.out, args.workers, args.affinity, shapes,
                       save_arrays=not args.no_save, rule=args.order, fmt=args.format)
        print(json.dumps({k: m[k] for k in m if k != "shapes"}), flush=True)
    else:
        _, rows = manifest_rows(args.source, args.n, None)
        rows = [json.loads(l) for l in (Path(args.source) / f"n{args.n}.jsonl").read_text().splitlines()]
        row = next(r for r in rows if r["shape_index"] == args.shape_index)
        order = (choose_order_measured(args.n, row["b"], row["chords"], row["lows"])
                 if args.order == MEASURED_RULE else args.order)
        tab = build(args.n, row["b"], row["chords"], row["lows"], shape_index=row["shape_index"],
                    order=order, fmt=args.format)
        print(json.dumps({k: tab[k] for k in ("n", "b", "format", "order", "lows", "hi", "vmax", "nstates",
                                                "total_prefixes", "total_compositions", "build_seconds",
                                                "tables_sha256")}))


if __name__ == "__main__":
    main()
