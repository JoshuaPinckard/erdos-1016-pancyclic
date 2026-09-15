/* Exact per-shape maximisation of n for the shape/CSP reformulation.
 *
 * Input (stdin), one shape per record:
 *     b m lo_0..lo_{b-1}  (arcmask chordcount) x m
 * argv[1] is a LOWER CUTOFF, not a single n.  argv[2] is a node budget PER SHAPE
 * (across the whole range, not per rung), argv[3] the arc order, argv[4] = 1 to
 * test ONLY n = argv[1] instead of the range.
 *
 * In range mode this walks n from that shape's own cap (#forms + 2) DOWN to the
 * cutoff and stops at the first n that is feasible, so:
 *     "SAT n=N"  -> N is the largest n >= cutoff this shape admits, and N can be
 *                   strictly greater than the cutoff.  Read the N from the line;
 *                   do not assume it equals the cutoff.
 *     "UNSAT"    -> NO n in [cutoff, cap] is feasible for this shape.  This is a
 *                   stronger statement than "n = cutoff is infeasible".
 *     "GAVEUP"   -> node budget hit.  UNKNOWN, never to be read as UNSAT.
 * In exact mode (argv[4]=1) only n = cutoff is tested, so UNSAT means just that
 * one value is infeasible -- it says nothing about larger n.  Exact mode is for
 * hunting: one search per shape instead of (cap - cutoff + 1) of them.
 * Feasible means: arc lengths a_i >= lo_i with sum a_i = n whose cycle lengths
 * cover [3,n].
 *
 * Search: DFS over the arcs.  At every node each cycle form f is confined to an
 * interval [lo_f, hi_f] of lengths, from the still-unassigned arcs' lower bounds
 * and the remaining slack, on both the "inside" (L_f) and "outside" (n - L_f)
 * sides.  Covering [3,n] needs a matching that saturates the values (one form
 * realises one length), and for interval neighbourhoods the greedy
 * "take the admissible form with the smallest hi" decides that exactly.  So the
 * greedy test is a sound prune at internal nodes and an exact check at leaves.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXB 16
#define MAXM 160
#define MAXN 200

static int b, m, lo[MAXB], nn;
static int fmask[MAXM], fch[MAXM];
static int order[MAXB];              /* arc assignment order */
static int a[MAXB];
static int inA[MAXM][MAXB];          /* inA[f][i] : form f uses arc i */
static int sufLoA[MAXM][MAXB + 1];   /* sum of lo_i over arcs of f at depth>=d */
static int sufLoB[MAXM][MAXB + 1];   /* same for the complement of f */
static int hasA[MAXM][MAXB + 1];     /* f still has an unassigned arc at depth d */
static int sumA[MAXM], sumB[MAXM];
static int sufLo[MAXB + 1];          /* sum of lo over arcs at depth >= d */
static long long nodes, nodecap;
static int arcorder, exact;

/* --- can every value in [3,n] get its own form? -----------------------------
 * Form f may realise any length in [lo_f, hi_f]; one form realises one length,
 * so covering [3,n] is a matching saturating the values.  With interval
 * neighbourhoods the greedy "give value x the admissible form with the smallest
 * hi" is optimal, so it decides the question exactly.  (Hall restricted to
 * value INTERVALS is not enough here -- e.g. n=8 with intervals
 * (4,5)(3,7)(4,5)(6,8)(5,8)(4,5) passes interval-Hall but has no matching --
 * so the greedy, not an interval count, is what is implemented.)
 * Counting sort by lo plus a bitmask over hi makes it O(m + n) per node.
 */
#define BMW ((MAXN + 64) / 64)
static int cntLo[MAXN + 3], startLo[MAXN + 3], sortHi[MAXM], bcnt[MAXN + 3];
static unsigned long long bm[BMW];

static inline int lowest_ge(int x)
{
    int w = x >> 6, off = x & 63;
    unsigned long long v = bm[w] & (~0ULL << off);
    while (!v) { if (++w >= BMW) return -1; v = bm[w]; }
    return (w << 6) + __builtin_ctzll(v);
}

static int matchable(int lov[], int hiv[])
{
    for (int v = 0; v <= nn + 2; v++) cntLo[v] = 0;
    int cnt = 0;
    for (int f = 0; f < m; f++) {
        int L = lov[f] < 3 ? 3 : lov[f];
        int H = hiv[f] > nn ? nn : hiv[f];
        if (L > H) continue;
        cntLo[L]++; cnt++;
    }
    if (cnt < nn - 2) return 0;
    int acc = 0;
    for (int v = 3; v <= nn + 1; v++) { startLo[v] = acc; acc += cntLo[v]; }
    static int fill[MAXN + 3];
    for (int v = 3; v <= nn + 1; v++) fill[v] = startLo[v];
    for (int f = 0; f < m; f++) {
        int L = lov[f] < 3 ? 3 : lov[f];
        int H = hiv[f] > nn ? nn : hiv[f];
        if (L > H) continue;
        sortHi[fill[L]++] = H;
    }
    for (int v = 0; v <= nn + 2; v++) bcnt[v] = 0;
    for (int w = 0; w < BMW; w++) bm[w] = 0;
    for (int x = 3; x <= nn; x++) {
        for (int p = startLo[x]; p < fill[x]; p++) {
            int h = sortHi[p];
            if (!bcnt[h]++) bm[h >> 6] |= 1ULL << (h & 63);
        }
        int h = lowest_ge(x);
        if (h < 0) return 0;
        if (!--bcnt[h]) bm[h >> 6] &= ~(1ULL << (h & 63));
    }
    return 1;
}

static int lov[MAXM], hiv[MAXM];

static int dfs(int d, int used)
{
    if (++nodes > nodecap) return -1;            /* -1 = gave up */
    int slack = nn - used - sufLo[d];
    if (slack < 0) return 0;
    for (int f = 0; f < m; f++) {
        int L = sumA[f] + sufLoA[f][d] + fch[f];
        int Hin = L + (hasA[f][d] ? slack : 0);
        int outLo = sumB[f] + sufLoB[f][d] - fch[f];
        if (outLo < 0) outLo = 0;
        int Hout = nn - outLo;
        lov[f] = L;
        hiv[f] = Hin < Hout ? Hin : Hout;
    }
    if (!matchable(lov, hiv)) return 0;
    if (d == b) return slack == 0;
    int i = order[d];
    for (int v = lo[i]; v <= lo[i] + slack; v++) {
        a[i] = v;
        for (int f = 0; f < m; f++) {
            if (inA[f][i]) sumA[f] += v; else sumB[f] += v;
        }
        int r = dfs(d + 1, used + v);
        for (int f = 0; f < m; f++) {
            if (inA[f][i]) sumA[f] -= v; else sumB[f] -= v;
        }
        if (r) return r;
    }
    return 0;
}

int main(int argc, char **argv)
{
    int target = atoi(argv[1]);
    nodecap = argc > 2 ? atoll(argv[2]) : 200000000LL;
    arcorder = argc > 3 ? atoi(argv[3]) : 0;
    exact = argc > 4 ? atoi(argv[4]) : 0;
    int shape = 0;
    while (scanf("%d %d", &b, &m) == 2) {
        for (int i = 0; i < b; i++) scanf("%d", &lo[i]);
        for (int f = 0; f < m; f++) scanf("%d %d", &fmask[f], &fch[f]);
        shape++;
        for (int f = 0; f < m; f++)
            for (int i = 0; i < b; i++) inA[f][i] = (fmask[f] >> i) & 1;
        /* arc order: ORDER=0 index, 1 by descending form-membership, 2 ascending.
           Assigning an arc that many forms use narrows many intervals at once. */
        {
            int deg[MAXB];
            for (int i = 0; i < b; i++) { deg[i] = 0; for (int f = 0; f < m; f++) deg[i] += inA[f][i]; }
            for (int i = 0; i < b; i++) order[i] = i;
            if (arcorder) for (int i = 0; i < b; i++) for (int j = i + 1; j < b; j++) {
                int swap = arcorder == 1 ? deg[order[j]] > deg[order[i]] : deg[order[j]] < deg[order[i]];
                if (swap) { int t = order[i]; order[i] = order[j]; order[j] = t; }
            }
        }
        sufLo[b] = 0;
        for (int d = b - 1; d >= 0; d--) sufLo[d] = sufLo[d + 1] + lo[order[d]];
        for (int f = 0; f < m; f++) {
            sufLoA[f][b] = sufLoB[f][b] = 0; hasA[f][b] = 0;
            for (int d = b - 1; d >= 0; d--) {
                int i = order[d];
                sufLoA[f][d] = sufLoA[f][d + 1] + (inA[f][i] ? lo[i] : 0);
                sufLoB[f][d] = sufLoB[f][d + 1] + (inA[f][i] ? 0 : lo[i]);
                hasA[f][d] = hasA[f][d + 1] || inA[f][i];
            }
        }
        int cap = m + 2, best = 0, gaveup = 0;
        int hi = exact ? target : cap;          /* exact mode tests only n=target */
        nodes = 0;                              /* budget is PER SHAPE, not per rung */
        for (int n = hi; n >= target; n--) {
            nn = n;
            for (int f = 0; f < m; f++) sumA[f] = sumB[f] = 0;
            int r = dfs(0, 0);
            if (r < 0) { gaveup = 1; break; }
            if (r) { best = n; break; }
        }
        long long tot = nodes;
        if (gaveup) printf("SHAPE %d GAVEUP nodes=%lld\n", shape, tot);
        else if (best) {
            printf("SHAPE %d SAT n=%d arcs=", shape, best);
            for (int i = 0; i < b; i++) printf("%d%s", a[i], i + 1 < b ? "," : "");
            printf(" nodes=%lld\n", tot);
        } else printf("SHAPE %d UNSAT nodes=%lld\n", shape, tot);
        fflush(stdout);
    }
    return 0;
}
