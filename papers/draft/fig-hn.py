import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

root = Path(__file__).parents[2]
with (root / "search" / "hn.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))
exact = {int(r["n"]): int(r["h"]) for r in rows if int(r["n"]) <= 41}
n = list(range(3, 57))
lower = [math.ceil(math.log2(x - 1)) - 1 for x in n]
logn = [math.log2(x) for x in n]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), constrained_layout=True)
ax1.step(sorted(exact), [exact[x] for x in sorted(exact)], where="post", label="exact h(n)")
ax1.plot(n, lower, "--", label=r"counting lower bound $\lceil\log_2(n-1)\rceil-1$")
ax1.plot(n, logn, ":", label=r"$\log_2 n$")
ax1.plot([56], [6], "o", label="upper bound h(56) ≤ 6")
ax1.set_xlabel("n")
ax1.set_ylabel("h(n)")
ax1.set_xlim(3, 56)
ax1.grid(alpha=0.25)
ax1.legend(fontsize=9)

k = [1, 2, 3, 4, 5]
ratios = [1.25, 1.0, 0.875, 0.75, 0.625]
ax2.plot(k, ratios, "o-")
ax2.set_xlabel("k")
ax2.set_ylabel(r"$t_k / 2^{k+1}$")
ax2.set_xticks(k)
ax2.grid(alpha=0.25)
fig.savefig(Path(__file__).with_suffix(".png"), dpi=160)
