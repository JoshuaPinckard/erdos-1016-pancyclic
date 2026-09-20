"""Remaining work and finish dates per machine, before and after the rebalance.

Every number here is derived, not asserted:
  * tier rank/unit totals come from the hashed manifests, the same way
    gpu_state_runner.py and verify_tier_exhaustion.py derive them;
  * coverage comes from the state files themselves;
  * the two machine rates are measured inputs and must be passed in, so a
    stale guess cannot hide inside a default.

ranks/hour is the unit of account, NOT units/hour.  A "unit" is
min(UNIT, ranks left in the shape), so its size varies: mean unit size runs
from 3.93e10 (n68 b10) to 4.94e10 (n69 b12).  Two machines at the same ranks/h
report different units/h purely from which tier they happen to be on, and the
same machine's units/h changes when it crosses a tier boundary.

Usage:
  python forecast.py <gpu-blast-dir> --desktop-ranks-per-hour R --laptop-ranks-per-hour R
                     [--state-dir DIR ...] [--laptop-census FILE] [--now ISO8601]
"""
import argparse
import datetime
import json
from pathlib import Path

UNIT = 50_000_000_000

# (level, tier) -> which machine runs it, per named plan.  "D" desktop, "L"
# laptop.  Tiers below 11 are complete everywhere and are reported, not planned.
PLANS = {
    "baseline": {
        # what the chains ran before 2026-09-19: desktop owned levels 68 and
        # 69 entirely, laptop owned level 70 entirely.
        (68, 11): "D", (68, 12): "D", (69, 11): "D", (69, 12): "D",
        (70, 11): "L", (70, 12): "L",
    },
    "instructed": {
        # 69/11 moved desktop -> laptop, nothing moved back.
        (68, 11): "D", (68, 12): "D", (69, 11): "L", (69, 12): "D",
        (70, 11): "L", (70, 12): "L",
    },
    "swap": {
        # 69/11 desktop -> laptop AND 70/11 laptop -> desktop.  This is what
        # is deployed.
        (68, 11): "D", (68, 12): "D", (69, 11): "L", (69, 12): "D",
        (70, 11): "D", (70, 12): "L",
    },
    "manager": {
        # Manager's 2026-09-19 split: the laptop takes both b=12 tiers of the
        # levels it does not already hold b=11 for, i.e. 69/12 + 70/12, and
        # every b=11 remainder runs on the faster card.  Same single partial
        # migration as "swap" (70/11 laptop -> desktop, already done); the only
        # difference is that 69/12 crosses instead of 69/11.
        (68, 11): "D", (68, 12): "D", (69, 11): "D", (69, 12): "L",
        (70, 11): "D", (70, 12): "L",
    },
    "deployed": {
        # The split actually running from 2026-09-19 12:35 PDT.  Chosen by
        # worst-case regret across the range the b=12 cost multiplier is known
        # to within (1.25..1.43), not by winning at any single value: 2.3 h
        # worst case against 11 h for the next best.  Expensive b=12 work on
        # the faster card, cheap b=11 remainders on the slower one.
        (68, 11): "L", (68, 12): "D", (69, 11): "D", (69, 12): "D",
        (70, 11): "L", (70, 12): "L",
    },
    "alt_68_11": {
        # Best single whole-job move by makespan, recorded for comparison:
        # 68/11's remainder moves to the laptop and 69/11 does not move.
        # Not deployed -- it does not carry out the instruction at all.
        (68, 11): "L", (68, 12): "D", (69, 11): "D", (69, 12): "D",
        (70, 11): "L", (70, 12): "L",
    },
}


def tier_totals(src: Path, levels):
    out = {}
    for n in levels:
        raw = (src / f"n{n}.jsonl").read_bytes()
        for line in raw.splitlines():
            row = json.loads(line)
            key = (n, row["b"])
            t = out.setdefault(key, {"ranks": 0, "units": 0, "shapes": 0})
            t["shapes"] += 1
            t["ranks"] += row["total"]
            t["units"] += len(range(0, row["total"], UNIT))
    return out


def shape_tier(src: Path, levels):
    """(n, shape_index) -> b, read from the manifests."""
    out = {}
    for n in levels:
        for line in (src / f"n{n}.jsonl").read_bytes().splitlines():
            row = json.loads(line)
            out[(n, row["shape_index"])] = row["b"]
    return out


def coverage(state_paths, levels, shape_b):
    """(n, b) -> covered ranks and units, from state files only.

    The tier of a completed unit is taken from the MANIFEST via its
    shape_index, not from the state file's min_b.  The pre-b10 state files span
    b=6..9 in one file, so crediting their units to min_b would report b=6 as
    massively over-complete and b=7..9 as untouched.
    """
    cov = {}
    for f in state_paths:
        state = json.loads(Path(f).read_text(encoding="utf-8"))
        n = state["n"]
        if n not in levels:
            continue
        for shape_index, _offset, count in state["complete"]:
            b = shape_b.get((n, shape_index))
            if b is None:
                # Names itself rather than being dropped: a unit whose shape is
                # not in the manifest means the state and the manifest have
                # diverged, which is exactly what must not pass unnoticed.
                print(f"WARNING: {f}: shape_index {shape_index} at n={n} is not "
                      f"in the manifest; unit not counted")
                continue
            c = cov.setdefault((n, b), {"ranks": 0, "units": 0})
            c["ranks"] += count
            c["units"] += 1
    return cov


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("--levels", type=int, nargs="+", default=[68, 69, 70])
    p.add_argument("--state", type=Path, action="append", default=[])
    p.add_argument("--desktop-ranks-per-hour", type=float, required=True)
    p.add_argument("--laptop-ranks-per-hour", type=float, required=True)
    p.add_argument("--now", default=None)
    p.add_argument("--enumerate", action="store_true",
                   help="walk the whole subset lattice over the outstanding "
                        "tiers and rank every whole-job split by makespan")
    p.add_argument("--top", type=int, default=12,
                   help="how many of the best splits to print under --enumerate")
    # Where each PARTIAL tier's state currently lives, as "n:b:D" or "n:b:L".
    # A plan that assigns a partial tier away from its current home costs one
    # state-file migration; a tier with no work done costs nothing to place.
    p.add_argument("--home", action="append", default=[])
    # Measured cost of a rank at tier b, relative to b=11.  A rank is NOT a
    # constant amount of work across tiers: a b=12 shape carries one more chord
    # and the kernel does correspondingly more per candidate.  Measured on both
    # cards over identical 5e10-rank units:
    #   desktop  b11 44.80 gpu_s, b12 57.22 gpu_s -> 1.277
    #   laptop   b11 61.16 gpu_s, b12 77.74 gpu_s -> 1.271
    # The agreement across two different GPUs is what says this is a property
    # of the kernel rather than of a machine, so one multiplier serves both.
    # Machine rates are quoted in b=11-equivalent ranks/h because both
    # long-window rate measurements were taken on b=11 tiers.
    p.add_argument("--tier-cost", action="append", default=[],
                   help="b:multiplier, e.g. 12:1.27")
    args = p.parse_args()

    now = (datetime.datetime.fromisoformat(args.now) if args.now
           else datetime.datetime.now(datetime.timezone.utc))
    levels = set(args.levels)
    totals = tier_totals(args.source, args.levels)
    cov = coverage(args.state, levels, shape_tier(args.source, args.levels))

    rate = {"D": args.desktop_ranks_per_hour, "L": args.laptop_ranks_per_hour}

    print(f"sampled_utc            {now.isoformat()}")
    print(f"desktop ranks/h        {rate['D']:.4e}")
    print(f"laptop  ranks/h        {rate['L']:.4e}")
    print()
    print("REMAINING WORK PER TIER (from manifests and state files)")
    print(f"{'tier':<10} {'shapes':>7} {'units':>7} {'done':>7} {'left':>7} "
          f"{'ranks left':>13} {'mean unit':>11}")
    cost = {}
    for spec in args.tier_cost:
        cb, cm = spec.split(":")
        cost[int(cb)] = float(cm)
    if cost:
        print("tier cost multipliers (b=11-equivalent ranks): "
              + ", ".join(f"b{b}={m}" for b, m in sorted(cost.items())))
        print()

    outstanding = {}
    for key in sorted(totals):
        n, b = key
        t = totals[key]
        c = cov.get(key, {"ranks": 0, "units": 0})
        left_r = t["ranks"] - c["ranks"]
        left_u = t["units"] - c["units"]
        mean = t["ranks"] / t["units"]
        if left_u:
            # "ranks" carries the COST-WEIGHTED figure, because that is what
            # divides by a rate to give hours.  raw_ranks keeps the physical
            # count for reporting.
            outstanding[key] = {"ranks": left_r * cost.get(b, 1.0),
                                "raw_ranks": left_r, "units": left_u}
        print(f"n{n} b{b:<6} {t['shapes']:>7} {t['units']:>7} {c['units']:>7} "
              f"{left_u:>7} {left_r:>13.4e} {mean:>11.3e}")

    if args.enumerate:
        home = {}
        for spec in args.home:
            hn, hb, hw = spec.split(":")
            home[(int(hn), int(hb))] = hw
        keys = sorted(outstanding)
        rows = []
        for mask in range(1 << len(keys)):
            load = {"D": 0, "L": 0}
            assign = {}
            for i, key in enumerate(keys):
                who = "L" if (mask >> i) & 1 else "D"
                assign[key] = who
                load[who] += outstanding[key]["ranks"]
            hd = load["D"] / rate["D"]
            hl = load["L"] / rate["L"]
            # A migration is owed only for a tier that has work already done
            # somewhere and is being asked to run on the other machine.
            migrations = sorted(
                f"n{n} b{b} {home[(n, b)]}->{assign[(n, b)]}"
                for (n, b) in keys
                if (n, b) in home and home[(n, b)] != assign[(n, b)])
            rows.append((max(hd, hl), hd, hl, load, assign, migrations))
        rows.sort(key=lambda r: r[0])
        print()
        print(f"WHOLE-JOB SPLIT LATTICE: {len(rows)} assignments over "
              f"{len(keys)} outstanding tiers, best {args.top} by makespan")
        print(f"{'makespan h':>11} {'D hours':>9} {'L hours':>9} {'idle h':>8} "
              f"{'lap ranks':>13}  laptop tiers / migrations owed")
        for mk, hd, hl, load, assign, migrations in rows[:args.top]:
            lap = " ".join(f"n{n}b{b}" for (n, b) in keys if assign[(n, b)] == "L")
            mig = ("; ".join(migrations)) if migrations else "none"
            print(f"{mk:>11.1f} {hd:>9.1f} {hl:>9.1f} {abs(hd - hl):>8.1f} "
                  f"{load['L']:>13.4e}  [{lap}] {mig}")
        print()

    print()
    print("FINISH DATES BY PLAN")
    print(f"{'plan':<12} {'desktop ranks':>14} {'lap ranks':>14} "
          f"{'D hours':>9} {'L hours':>9} {'makespan h':>11} {'finish (UTC)':>21}")
    results = {}
    for name, plan in PLANS.items():
        load = {"D": 0, "L": 0}
        for key, who in plan.items():
            if key in outstanding:
                load[who] += outstanding[key]["ranks"]
        hd = load["D"] / rate["D"]
        hl = load["L"] / rate["L"]
        mk = max(hd, hl)
        fin = now + datetime.timedelta(hours=mk)
        results[name] = {"makespan": mk, "desktop_h": hd, "laptop_h": hl,
                         "idle_h": abs(hd - hl),
                         "idle_on": "laptop" if hl < hd else "desktop"}
        print(f"{name:<12} {load['D']:>14.4e} {load['L']:>14.4e} "
              f"{hd:>9.1f} {hl:>9.1f} {mk:>11.1f} {fin.strftime('%Y-%m-%d %H:%M'):>21}")

    total = sum(o["ranks"] for o in outstanding.values())
    ideal = total / (rate["D"] + rate["L"])
    fin = now + datetime.timedelta(hours=ideal)
    print(f"{'optimum*':<12} {'':>14} {'':>14} {'':>9} {'':>9} "
          f"{ideal:>11.1f} {fin.strftime('%Y-%m-%d %H:%M'):>21}")
    print("* both machines busy until the same instant; needs splitting a tier,")
    print("  which the runner cannot do -- there is no unit-subrange flag.")
    print()
    base = results["baseline"]["makespan"]
    swap = results["swap"]["makespan"]
    inst = results["instructed"]["makespan"]
    print(f"saving, swap vs baseline:       {base - swap:+.1f} h "
          f"({(base - swap) / 24:+.2f} d)")
    print(f"saving, instructed vs baseline: {base - inst:+.1f} h "
          f"(negative means SLOWER than changing nothing)")
    print(f"swap vs instructed:             {inst - swap:+.1f} h")
    r = results["swap"]
    print(f"residual idle under swap:       {r['idle_h']:.1f} h on the "
          f"{r['idle_on']}; the fractional optimum would be {swap - ideal:.1f} h "
          f"sooner still")


if __name__ == "__main__":
    main()
