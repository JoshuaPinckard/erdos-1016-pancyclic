/*
 * pancyc.c -- exact search for h(n): the minimum number of chords that must be added
 * to the n-cycle C_n so that the resulting graph is pancyclic (cycle of every length 3..n).
 *
 * Usage:  pancyc n k [mode]
 *   Decides whether some set of exactly k chords makes C_n pancyclic.  Prints a witness
 *   (as vertex pairs) or "NONE".  Every pancyclic graph contains a triangle, and up to
 *   rotation of the cycle a triangle is one of three shapes, so the search is split:
 *     A: chord (0,2) present                              [a span-2 chord]
 *     B: no span-2 chord; chords (0,b),(1,b) present        [two chords + one cycle edge]
 *     C: no span-2 chord, no shape-B pair; (0,b),(b,c),(0,c) present [three chords]
 *   mode = "A", "B", "C" or "all" (default all).  Rotation symmetry only is used, so the
 *   enumeration is exhaustive: if all three modes print NONE, no k-chord graph is pancyclic.
 *
 * Cycles are enumerated through the cycle space: basis = the Hamilton cycle plus, for each
 * chord (a,b), the chord together with the path a,a+1,...,b.  Every cycle of the graph is a
 * XOR of basis elements (2^(k+1) elements); an element is a cycle iff all vertex degrees are
 * 0 or 2 and its edges are connected.  Lengths are collected in a bitmask.
 *
 * Pruning (sound): with j chords placed the graph has at most 2^(j+1)-1 cycles, and adding
 * the remaining k-j chords can create at most 2^(k+1) - 2^(j+1) further cycle-space
 * elements, so the final number of distinct lengths is at most
 * |L_j| + 2^(k+1) - 2^(j+1).  If that is below n-2 the partial set is abandoned.
 */
/* LIMIT (reviewer note, 2026-09-14): edge masks are unsigned __int128, so n + k must be <= 128.
 * MAXN=120 with MAXK=12 would overflow; in practice this program is only run with n <= 60, k <= 6. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 u128;
#define MAXN 120
#define MAXK 12

static int n, K;
static int nch;                      /* number of candidate chords */
static int cha[MAXN * MAXN / 2], chb[MAXN * MAXN / 2];
static int span2[MAXN * MAXN / 2];   /* chord has span 2 (forms triangle with cycle) */

static int sel[MAXK];                /* selected chord indices */
static u128 basis[MAXK + 1];         /* basis cycles as edge masks: bit i (i<n) = cycle edge (i,i+1); bit n+j = chord j */
static int ca[MAXK], cb[MAXK];       /* endpoints of selected chords */
static long long tested = 0, nwit = 0;
static int found = 0;
static int enumerate_all = 0;
static int shard = 0, nshards = 1;
static int mode_all = 1;

static inline int popc128(u128 x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }

/* Compute the set of cycle lengths (as a bitmask over 0..n) of C_n + selected chords 0..j-1. */
static u128 length_set(int j) {
    int m = j + 1;                   /* basis size */
    u128 lens = 0;
    u128 cur = 0;
    int deg[MAXN];
    /* incident chords per vertex among the first j chords */
    int inc[MAXN][MAXK], ninc[MAXN];
    for (int v = 0; v < n; v++) ninc[v] = 0;
    for (int t = 0; t < j; t++) { inc[ca[t]][ninc[ca[t]]++] = t; inc[cb[t]][ninc[cb[t]]++] = t; }
    unsigned long total = 1UL << m;
    for (unsigned long g = 1; g < total; g++) {
        /* Gray code: flip the basis element at the lowest set bit of g */
        int bit = __builtin_ctzl(g);
        cur ^= basis[bit];
        /* degrees */
        int ne = popc128(cur);
        if (ne < 3) continue;
        for (int v = 0; v < n; v++) deg[v] = 0;
        for (int i = 0; i < n; i++) if ((cur >> i) & 1) { deg[i]++; deg[(i + 1) % n]++; }
        for (int t = 0; t < j; t++) if ((cur >> (n + t)) & 1) { deg[ca[t]]++; deg[cb[t]]++; }
        int ok = 1, start = -1;
        for (int v = 0; v < n; v++) { if (deg[v] != 0 && deg[v] != 2) { ok = 0; break; } if (deg[v] == 2 && start < 0) start = v; }
        if (!ok || start < 0) continue;
        /* connectivity walk: from start, follow edges; count edges traversed */
        int v = start, prev_edge = -1, cnt = 0;
        while (1) {
            int next_edge = -1, w = -1;
            /* cycle edge (v-1,v) index v-1 */
            int e1 = (v - 1 + n) % n;
            if (((cur >> e1) & 1) && e1 != prev_edge) { next_edge = e1; w = e1; }
            if (next_edge < 0 && ((cur >> v) & 1) && v != prev_edge) { next_edge = v; w = (v + 1) % n; }
            if (next_edge < 0) {
                for (int q = 0; q < ninc[v]; q++) {
                    int t = inc[v][q];
                    if (((cur >> (n + t)) & 1) && (n + t) != prev_edge) { next_edge = n + t; w = (ca[t] == v) ? cb[t] : ca[t]; break; }
                }
            }
            if (next_edge < 0) break;
            cnt++;
            prev_edge = next_edge; v = w;
            if (v == start) break;
        }
        if (v == start && cnt == ne) lens |= ((u128)1) << ne;
    }
    return lens;
}

static u128 needmask;

static void print_witness(int k) {
    printf("WITNESS n=%d k=%d :", n, k);
    for (int t = 0; t < k; t++) printf(" (%d,%d)", ca[t], cb[t]);
    printf("\n");
    fflush(stdout);
}

/* place chord index c as selected slot j */
static inline void place(int j, int c) {
    sel[j] = c; ca[j] = cha[c]; cb[j] = chb[c];
    u128 b = ((u128)1) << (n + j);
    for (int i = cha[c]; i < chb[c]; i++) b |= ((u128)1) << i;
    basis[j + 1] = b;
}

/* extend from slot j, choosing chords with index > lastidx, subject to filter */
static int (*filter)(int c);

static char used[MAXN * MAXN / 2];

static void rec(int j, int lastidx) {
    if (found) return;
    if (j == K) {
        tested++;
        if ((tested & ((1LL<<24)-1)) == 0) { printf("progress tested=%lld last=(%d,%d)\n", tested, ca[1], cb[1]); fflush(stdout); }
        u128 L = length_set(K);
        if ((L & needmask) == needmask) { if (!enumerate_all) found = 1; nwit++; print_witness(K); }
        return;
    }
    if (j >= 1) {
        u128 L = length_set(j);
        int distinct = 0;
        for (int l = 3; l <= n; l++) if ((L >> l) & 1) distinct++;
        long long bound = (long long)distinct + ((1LL << (K + 1)) - (1LL << (j + 1)));
        if (bound < n - 2) return;
    }
    for (int c = lastidx + 1; c < nch; c++) {
        if (used[c]) continue;
        if (j == 1 && nshards > 1 && (c % nshards) != shard) continue;
        if (filter && !filter(c)) continue;
        place(j, c); used[c] = 1;
        rec(j + 1, c);
        used[c] = 0;
        if (found) return;
    }
}

static int f_nospan2(int c) { return !span2[c]; }

/* does the selected set (first K chords) contain a shape-B pair (a,b),(a+1,b) or (a,b),(a,b+1) up to rotation? */
static int has_shapeB(int k) {
    for (int s = 0; s < k; s++) for (int t = 0; t < k; t++) {
        if (s == t) continue;
        int a1 = ca[s], b1 = cb[s], a2 = ca[t], b2 = cb[t];
        if (b1 == b2 && (a2 == (a1 + 1) % n)) return 1;
        if (a1 == a2 && (b2 == (b1 + 1) % n)) return 1;
        /* wrap-around forms: chords (x,y) with y = n-1 and (0,y)? handled by rotation: (n-1, y) is stored as (y, n-1); pair (y,n-1),(0,y): a=y,b=n-1 and (0,y) -> vertices y, n-1, 0 with edge (n-1,0) */
        if (b1 == n - 1 && a2 == 0 && b2 == a1) return 1;
        if (b2 == n - 1 && a1 == 0 && b1 == a2) return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: pancyc n k [A|B|C|all]\n"); return 2; }
    n = atoi(argv[1]); K = atoi(argv[2]);
    const char *mode = argc >= 4 ? argv[3] : "all";
    if (argc >= 5 && !strcmp(argv[4], "--all")) enumerate_all = 1;
    if (argc >= 6) { shard = atoi(argv[4]); nshards = atoi(argv[5]); }
    if (n < 3 || n > MAXN || K < 0 || K > MAXK) { fprintf(stderr, "bad args\n"); return 2; }
    nch = 0;
    for (int a = 0; a < n; a++) for (int b = a + 2; b < n; b++) {
        if (a == 0 && b == n - 1) continue;      /* that is a cycle edge */
        int sp = b - a; if (n - sp < sp) sp = n - sp;
        cha[nch] = a; chb[nch] = b; span2[nch] = (sp == 2);
        nch++;
    }
    basis[0] = 0; for (int i = 0; i < n; i++) basis[0] |= ((u128)1) << i;
    needmask = 0; for (int l = 3; l <= n; l++) needmask |= ((u128)1) << l;
    if (K == 0) { u128 L = length_set(0); printf("%s\n", (L & needmask) == needmask ? "WITNESS n=3 k=0 :" : "NONE"); return 0; }
    int idx02 = -1; for (int c = 0; c < nch; c++) if (cha[c] == 0 && chb[c] == 2) idx02 = c;

    if (!strcmp(mode, "A") || !strcmp(mode, "all")) {
        memset(used, 0, sizeof used);
        filter = NULL; place(0, idx02); used[idx02] = 1; rec(1, -1); used[idx02] = 0;
    }
    if (found) { printf("tested=%lld\n", tested); return 0; }
    if (!strcmp(mode, "B") || !strcmp(mode, "BC") || !strcmp(mode, "all")) {
        if (K >= 2) for (int b = 3; b <= n - 2 && !found; b++) {
            int i0 = -1, i1 = -1;
            for (int c = 0; c < nch; c++) { if (cha[c] == 0 && chb[c] == b) i0 = c; if (cha[c] == 1 && chb[c] == b) i1 = c; }
            if (i0 < 0 || i1 < 0) continue;
            memset(used, 0, sizeof used);
            filter = f_nospan2; place(0, i0); place(1, i1); used[i0] = used[i1] = 1; rec(2, -1);
        }
    }
    if (found) { printf("tested=%lld\n", tested); return 0; }
    if (!strcmp(mode, "C") || !strcmp(mode, "BC") || !strcmp(mode, "all")) {
        if (K >= 3) for (int b = 3; b <= n - 5 && !found; b++) for (int c2 = b + 3; c2 <= n - 3 && !found; c2++) {
            int i0 = -1, i1 = -1, i2 = -1;
            for (int c = 0; c < nch; c++) { if (cha[c] == 0 && chb[c] == b) i0 = c; if (cha[c] == b && chb[c] == c2) i1 = c; if (cha[c] == 0 && chb[c] == c2) i2 = c; }
            if (i0 < 0 || i1 < 0 || i2 < 0) continue;
            memset(used, 0, sizeof used);
            filter = f_nospan2; place(0, i0); place(1, i1); place(2, i2); used[i0] = used[i1] = used[i2] = 1; rec(3, -1);
        }
    }
    if (!found && nwit == 0) printf("NONE n=%d k=%d tested=%lld\n", n, K, tested); else printf("tested=%lld witnesses=%lld\n", tested, nwit);
    return 0;
}
