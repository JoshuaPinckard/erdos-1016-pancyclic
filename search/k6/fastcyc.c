/* fastcyc.c -- cycle-space pancyclicity evaluator for C_n + k chords, plus a wide random-restart
 * search with JOINT 2-chord and 3-chord moves.
 *
 * Evaluator: identical mathematics to cyclespace.py (see that file's header).  C_n + k chords has
 * cyclomatic number k+1, so every cycle of the graph is one of the 2^(k+1)-1 nonzero cycle-space
 * elements; each element is XOR-ed in along a Gray code and tested for "is a single cycle" by a
 * whole-mask degree test plus a union-find connectivity test over its maximal cycle-edge runs.
 *
 * Vertex/edge masks are unsigned __int128 (two 64-bit machine words), so n up to 127 is
 * representable -- the n <= 60 limit of search/gpu_pancyc.py does not apply here.
 *
 * Usage:
 *   fastcyc control                                positive control against recorded results
 *   fastcyc verify N "a,b a,b ..."                 print cycle lengths / missing lengths
 *   fastcyc bench  N ITERS                         evaluations per second at this n
 *   fastcyc search N SECONDS SEED ["a,b ..."] [J2] wide random-restart + joint 2/3-chord search
 *                                                  (J2 = run the exhaustive joint-2 sweep only when
 *                                                  the missing count is already <= J2; default 2)
 *   fastcyc climb  N0 "a,b ..." NMAX SECS SEED     same search, chained by single-vertex insertion
 *   fastcyc sweep2 N "a,b ..." [S1 S2]             COMPLETE joint 2-chord neighbourhood of one set
 *                                                  (optionally just slot pair S1,S2, to split it
 *                                                  across processes); no early exit, so the
 *                                                  "no 2-chord escape" claim is exhaustive
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef unsigned __int128 u128;
#define ONE ((u128)1)

static inline int pc128(u128 x) {
    return __builtin_popcountll((unsigned long long)x) +
           __builtin_popcountll((unsigned long long)(x >> 64));
}
static inline int ctz128(u128 x) {
    unsigned long long lo = (unsigned long long)x;
    return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((unsigned long long)(x >> 64));
}

/* connectivity of one cycle-space element: cycle-edge mask E plus selected-chord mask S.
 * R = rot1(E) is passed in because the caller already computed it for the degree test.
 * Union-find over the maximal runs of E and the selected chords; vertex -> local index uses a
 * stamped lookup table so there is no linear scan. */
static int vid[128], vstamp[128], cur_stamp = 0;

static int connected(int n, u128 E, u128 R, u128 full, const int *A, const int *B, unsigned S) {
    int eu[24], ev[24], ne = 0;
    if (E == full) return S == 0;            /* the whole Hamilton cycle */
    if (E) {
        u128 starts = E & ~R & full;         /* edge p starts a maximal run */
        u128 notE = (~E) & full;
        while (starts) {
            int p = ctz128(starts);
            starts &= starts - 1;
            u128 above = notE & ~((ONE << (p + 1)) - 1);
            int q = above ? ctz128(above) : ctz128(notE);   /* first unset edge after p */
            eu[ne] = p; ev[ne] = q; ne++;    /* run = path from vertex p to vertex q */
        }
    }
    unsigned s = S;
    while (s) {
        int j = __builtin_ctz(s);
        s &= s - 1;
        eu[ne] = A[j]; ev[ne] = B[j]; ne++;
    }
    int par[32], nn = 0;
    ++cur_stamp;
    for (int i = 0; i < ne; i++) {
        int vv[2] = {eu[i], ev[i]};
        for (int t = 0; t < 2; t++) {
            int v = vv[t];
            if (vstamp[v] != cur_stamp) { vstamp[v] = cur_stamp; vid[v] = nn; par[nn] = nn; nn++; }
        }
    }
    int comp = nn;
    for (int i = 0; i < ne; i++) {
        int ru = vid[eu[i]], rv = vid[ev[i]];
        while (par[ru] != ru) ru = par[ru] = par[par[ru]];
        while (par[rv] != rv) rv = par[rv] = par[par[rv]];
        if (ru != rv) { par[ru] = rv; comp--; }
    }
    return comp == 1;
}

/* bit L of the result is set iff C_n + chords has a cycle of length L */
static u128 eval_mask(int n, int k, const int *A, const int *B) {
    u128 full = (n >= 128) ? ~(u128)0 : ((ONE << n) - 1);
    u128 basis[9];
    basis[0] = full;
    for (int j = 0; j < k; j++) basis[j + 1] = (ONE << B[j]) - (ONE << A[j]);
    signed char cdeg[128];
    memset(cdeg, 0, sizeof cdeg);
    u128 ch1 = 0, ch2 = 0, E = 0, lens = 0;
    int nbad = 0;
    unsigned S = 0, total = 1u << (k + 1);
    for (unsigned g = 1; g < total; g++) {
        int bit = __builtin_ctz(g);
        E ^= basis[bit];
        if (bit) {
            int j = bit - 1;
            S ^= 1u << j;
            int d = ((S >> j) & 1) ? 1 : -1;
            int vs[2] = {A[j], B[j]};
            for (int t = 0; t < 2; t++) {
                int v = vs[t], old = cdeg[v], nw = old + d;
                cdeg[v] = (signed char)nw;
                if (old == 1) ch1 &= ~(ONE << v);
                else if (old == 2) ch2 &= ~(ONE << v);
                else if (old >= 3) nbad--;
                if (nw == 1) ch1 |= (ONE << v);
                else if (nw == 2) ch2 |= (ONE << v);
                else if (nw >= 3) nbad++;
            }
        }
        if (nbad) continue;
        u128 R = ((E << 1) | (E >> (n - 1))) & full;
        if ((E ^ R) != ch1) continue;
        if ((E & R) & ch2) continue;
        int ne = pc128(E) + __builtin_popcount(S);
        if (ne < 3) continue;
        if ((lens >> ne) & 1) continue;      /* that length is already witnessed */
        if (connected(n, E, R, full, A, B, S)) lens |= ONE << ne;
    }
    return lens;
}

static u128 need_mask(int n) {                 /* bits 3..n */
    u128 m = (n + 1 >= 128) ? ~(u128)0 : ((ONE << (n + 1)) - 1);
    return m & ~(u128)7;
}
static int missing_count(int n, int k, const int *A, const int *B) {
    return pc128(need_mask(n) & ~eval_mask(n, k, A, B));
}

/* ------------------------------------------------------------------ search */

#define K 6
static int joint2_at = 2;        /* run the exhaustive joint-2 sweep only at missing <= this */
static int nV;                   /* n */
static int *CA, *CB, NC;         /* candidate chord list */
static unsigned long long evals = 0;
static time_t deadline = 0;
static inline int out_of_time(void) { return deadline && time(NULL) >= deadline; }

static void build_candidates(int n) {
    NC = 0;
    CA = malloc(sizeof(int) * n * n);
    CB = malloc(sizeof(int) * n * n);
    for (int a = 0; a < n; a++)
        for (int b = a + 2; b < n; b++) {
            if (a == 0 && b == n - 1) continue;      /* that is a cycle edge */
            CA[NC] = a; CB[NC] = b; NC++;
        }
}

static uint64_t rngs;
/* splitmix-style mix.  An earlier version used "rngs = seed | 1", which silently mapped seeds
 * 2k and 2k+1 to the SAME stream, so half of every parallel wave was a duplicate run. */
static void seed_rng(uint64_t seed) {
    uint64_t z = seed + 0x9E3779B97F4A7C15ULL;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    rngs = (z ^ (z >> 31)) | 1ULL;
}
static inline uint64_t rnd64(void) {
    rngs ^= rngs << 13; rngs ^= rngs >> 7; rngs ^= rngs << 17; return rngs;
}
static inline int rndn(int m) { return (int)(rnd64() % (unsigned)m); }

static inline int dup(const int *A, const int *B, int slot, int a, int b) {
    for (int i = 0; i < K; i++) if (i != slot && A[i] == a && B[i] == b) return 1;
    return 0;
}
static inline int cost(const int *A, const int *B) { evals++; return missing_count(nV, K, A, B); }

static void print_set(const char *tag, int n, const int *A, const int *B, int c) {
    printf("%s n=%d missing=%d chords=", tag, n, c);
    for (int i = 0; i < K; i++) printf("(%d,%d)", A[i], B[i]);
    printf("\n");
    fflush(stdout);
}

/* exhaustive best-improvement over every single chord replacement */
static int descent1(int *A, int *B, int *c) {
    int moved = 0;
    for (int round = 0; round < 40; round++) {
        int improved = 0;
        for (int s = 0; s < K; s++) {
            int oa = A[s], ob = B[s], ba = oa, bb = ob, bc = *c;
            for (int i = 0; i < NC; i++) {
                if (dup(A, B, s, CA[i], CB[i])) continue;
                A[s] = CA[i]; B[s] = CB[i];
                int cc = cost(A, B);
                if (cc < bc) { bc = cc; ba = CA[i]; bb = CB[i]; }
                if ((i & 0xFFF) == 0 && out_of_time()) break;
            }
            A[s] = ba; B[s] = bb;
            if (bc < *c) { *c = bc; improved = 1; moved = 1; }
            else { A[s] = oa; B[s] = ob; }
            if (*c == 0) return 1;
        }
        if (!improved || out_of_time()) break;
    }
    return moved;
}

/* JOINT 2-chord move: every pair of slots x every pair of replacement chords, exhaustive.
 * First improvement: a better set is taken as soon as it is seen, so a full sweep is only paid
 * when the current set really is a 2-chord local optimum. */
static int joint2(int *A, int *B, int *c) {
    for (int s1 = 0; s1 < K; s1++) for (int s2 = s1 + 1; s2 < K; s2++) {
        int o1a = A[s1], o1b = B[s1], o2a = A[s2], o2b = B[s2];
        for (int i = 0; i < NC; i++) {
            A[s1] = CA[i]; B[s1] = CB[i];
            if (dup(A, B, s1, CA[i], CB[i])) continue;
            for (int j = 0; j < NC; j++) {
                A[s2] = CA[j]; B[s2] = CB[j];
                if (dup(A, B, s2, CA[j], CB[j])) continue;
                int cc = cost(A, B);
                if (cc < *c) { *c = cc; return 1; }
            }
            if (out_of_time()) { A[s1] = o1a; B[s1] = o1b; A[s2] = o2a; B[s2] = o2b; return 0; }
        }
        A[s1] = o1a; B[s1] = o1b; A[s2] = o2a; B[s2] = o2b;
    }
    return 0;
}

/* JOINT 3-chord move, sampled: NS random (slot triple, chord triple) draws, first improvement.
 * DECLARED CAP: the full 3-chord neighbourhood is C(6,3)*NC^3 ~ 1e11 at n=60; it is NOT enumerated. */
static int joint3(int *A, int *B, int *c, long NS) {
    int oa[K], ob[K];
    memcpy(oa, A, sizeof oa); memcpy(ob, B, sizeof ob);
    for (long t = 0; t < NS; t++) {
        int s[3];
        s[0] = rndn(K);
        do { s[1] = rndn(K); } while (s[1] == s[0]);
        do { s[2] = rndn(K); } while (s[2] == s[0] || s[2] == s[1]);
        for (int z = 0; z < 3; z++) { int i = rndn(NC); A[s[z]] = CA[i]; B[s[z]] = CB[i]; }
        int bad = 0;
        for (int x = 0; x < K && !bad; x++)
            for (int y = x + 1; y < K; y++) if (A[x] == A[y] && B[x] == B[y]) { bad = 1; break; }
        if (!bad) {
            int cc = cost(A, B);
            if (cc < *c) { *c = cc; return 1; }
        }
        memcpy(A, oa, sizeof oa); memcpy(B, ob, sizeof ob);
        if ((t & 0x3FFF) == 0 && out_of_time()) return 0;
    }
    return 0;
}

static void random_set(int *A, int *B) {
    for (int i = 0; i < K; i++) {
        int ok = 0;
        while (!ok) {
            int t = rndn(NC);
            A[i] = CA[t]; B[i] = CB[t];
            ok = 1;
            for (int j = 0; j < i; j++) if (A[j] == A[i] && B[j] == B[i]) ok = 0;
        }
    }
}

/* iterated local search from one starting set: single-chord descent, then sampled joint-3,
 * then (only when already close) exhaustive joint-2.  Returns the missing-count reached. */
static int ils(int *A, int *B) {
    int c = cost(A, B);
    for (;;) {
        int moved = descent1(A, B, &c);
        if (c == 0) return 0;
        if (!moved) moved = joint3(A, B, &c, 40000);
        if (c == 0) return 0;
        if (!moved && c <= joint2_at) moved = joint2(A, B, &c);
        if (c == 0) return 0;
        if (!moved || out_of_time()) break;
    }
    return c;
}

/* wide random-restart search at one n.  Restart sources rotate: supplied seeds (first pass
 * unperturbed, later perturbed), kicks off the incumbent, and fresh uniform-random chord sets. */
static int attack(int n, int (*sA)[K], int (*sB)[K], int nseeds, int *outA, int *outB) {
    int A[K], B[K], bA[K], bB[K], best = 1 << 30;
    long restarts = 0;
    random_set(bA, bB);
    while (!out_of_time()) {
        if (nseeds && restarts < nseeds) {                      /* every seed, unperturbed */
            memcpy(A, sA[restarts], sizeof A); memcpy(B, sB[restarts], sizeof B);
        } else if (nseeds && restarts % 4 < 2) {                /* perturbed seed */
            int s = rndn(nseeds);
            memcpy(A, sA[s], sizeof A); memcpy(B, sB[s], sizeof B);
            for (int z = 0, np = 1 + rndn(3); z < np; z++) { int t = rndn(K), i = rndn(NC); A[t] = CA[i]; B[t] = CB[i]; }
        } else if (best < (1 << 30) && restarts % 4 == 2) {     /* kick the incumbent */
            memcpy(A, bA, sizeof A); memcpy(B, bB, sizeof B);
            for (int z = 0, np = 2 + rndn(2); z < np; z++) { int t = rndn(K), i = rndn(NC); A[t] = CA[i]; B[t] = CB[i]; }
        } else {
            random_set(A, B);
        }
        restarts++;
        int c = ils(A, B);
        if (c <= 2) print_set("LOCOPT", n, A, B, c);   /* harvest every near miss, not just record-breakers */
        if (c < best) {
            best = c;
            memcpy(bA, A, sizeof bA); memcpy(bB, B, sizeof bB);
            print_set(c ? "BEST" : "WITNESS", n, A, B, c);
        }
        if (best == 0) break;
    }
    memcpy(outA, bA, sizeof(int) * K); memcpy(outB, bB, sizeof(int) * K);
    printf("n=%d restarts=%ld evals=%llu best_missing=%d\n", n, restarts, evals, best);
    fflush(stdout);
    return best;
}

static int parse_chords(const char *s, int *A, int *B) {
    int k = 0, a, b;
    const char *p = s;
    while (*p) {
        while (*p && (*p == ' ' || *p == '(' || *p == ')')) p++;
        if (!*p) break;
        if (sscanf(p, "%d,%d", &a, &b) != 2) break;
        if (a > b) { int t = a; a = b; b = t; }
        A[k] = a; B[k] = b; k++;
        while (*p && *p != ' ' && *p != ')') p++;
    }
    return k;
}

int main(int argc, char **argv) {
    if (argc < 2 || (argc < 3 && strcmp(argv[1], "control"))) { printf("see header for usage\n"); return 2; }
    if (!strcmp(argv[1], "verify")) {
        int n = atoi(argv[2]);
        int A[9], B[9];
        int k = parse_chords(argv[3], A, B);
        u128 lens = eval_mask(n, k, A, B);
        printf("n=%d k=%d lengths=", n, k);
        for (int L = 3; L <= n; L++) if ((lens >> L) & 1) printf("%d ", L);
        printf("\nmissing=");
        int mc = 0;
        for (int L = 3; L <= n; L++) if (!((lens >> L) & 1)) { printf("%d ", L); mc++; }
        printf("\n%s (missing %d)\n", mc ? "NOT pancyclic" : "PANCYCLIC", mc);
        return mc ? 1 : 0;
    }
    if (!strcmp(argv[1], "bench")) {
        int n = atoi(argv[2]);
        long iters = atol(argv[3]);
        nV = n; build_candidates(n); seed_rng(12345);
        int A[K], B[K];
        clock_t t0 = clock();
        long acc = 0;
        for (long i = 0; i < iters; i++) { random_set(A, B); acc += missing_count(n, K, A, B); }
        double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;
        printf("n=%d iters=%ld seconds=%.2f evals_per_sec=%.0f (checksum %ld)\n", n, iters, dt, iters / dt, acc);
        return 0;
    }
    if (!strcmp(argv[1], "search")) {            /* search N SECONDS SEED ["a,b ..."] */
        int n = atoi(argv[2]);
        double budget = atof(argv[3]);
        seed_rng((uint64_t)strtoull(argv[4], NULL, 10));
        nV = n; build_candidates(n);
        int sA[1][K], sB[1][K], nseeds = 0;
        if (argc > 5 && parse_chords(argv[5], sA[0], sB[0]) == K) nseeds = 1;
        if (argc > 6) joint2_at = atoi(argv[6]);
        deadline = time(NULL) + (time_t)budget;
        printf("search n=%d budget=%.0fs rngseed=%s candidates=%d seeds=%d\n", n, budget, argv[4], NC, nseeds);
        fflush(stdout);
        int oA[K], oB[K];
        int best = attack(n, sA, sB, nseeds, oA, oB);
        print_set("FINAL", n, oA, oB, best);
        return best == 0 ? 0 : 1;
    }
    if (!strcmp(argv[1], "climb")) {             /* climb N0 "a,b ..." NMAX SECS_PER_N SEED */
        int n = atoi(argv[2]);
        int curA[K], curB[K];
        if (parse_chords(argv[3], curA, curB) != K) { printf("need %d chords\n", K); return 2; }
        int nmax = atoi(argv[4]);
        double per = atof(argv[5]);
        seed_rng((uint64_t)strtoull(argv[6], NULL, 10));
        nV = n; build_candidates(n);
        int c0 = missing_count(n, K, curA, curB);
        if (c0 != 0) { printf("ABORT: start set is not pancyclic at n=%d (missing %d)\n", n, c0); return 2; }
        print_set("START", n, curA, curB, 0);
        static int sA[130][K], sB[130][K];
        while (n < nmax) {
            int n1 = n + 1;
            free(CA); free(CB);
            nV = n1; build_candidates(n1);
            int sc[130], ns = 0;
            for (int p = 0; p < n; p++) {            /* every single-vertex insertion image */
                for (int i = 0; i < K; i++) {
                    int a = curA[i] + (curA[i] > p ? 1 : 0);
                    int b = curB[i] + (curB[i] > p ? 1 : 0);
                    sA[ns][i] = a < b ? a : b;
                    sB[ns][i] = a < b ? b : a;
                }
                sc[ns] = missing_count(n1, K, sA[ns], sB[ns]);
                ns++;
            }
            for (int i = 1; i < ns; i++)             /* insertion sort by missing count */
                for (int j = i; j > 0 && sc[j] < sc[j - 1]; j--) {
                    int t = sc[j]; sc[j] = sc[j - 1]; sc[j - 1] = t;
                    for (int z = 0; z < K; z++) {
                        t = sA[j][z]; sA[j][z] = sA[j - 1][z]; sA[j - 1][z] = t;
                        t = sB[j][z]; sB[j][z] = sB[j - 1][z]; sB[j - 1][z] = t;
                    }
                }
            printf("n=%d insertion seeds: best missing=%d worst missing=%d\n", n1, sc[0], sc[ns - 1]);
            fflush(stdout);
            deadline = time(NULL) + (time_t)per;
            int oA[K], oB[K];
            int best = attack(n1, sA, sB, ns, oA, oB);
            if (best != 0) { print_set("STALL", n1, oA, oB, best); break; }
            memcpy(curA, oA, sizeof curA); memcpy(curB, oB, sizeof curB);
            n = n1;
            print_set("CLIMB", n, curA, curB, 0);
        }
        printf("FINAL largest n reached: %d\n", n);
        print_set("FINAL", n, curA, curB, 0);
        return 0;
    }
    if (!strcmp(argv[1], "sweep2")) {            /* sweep2 N "a,b ..." [S1 S2] */
        int n = atoi(argv[2]);
        nV = n; build_candidates(n);
        int A[K], B[K];
        if (parse_chords(argv[3], A, B) != K) { printf("need %d chords\n", K); return 2; }
        int only1 = -1, only2 = -1;
        if (argc > 5) { only1 = atoi(argv[4]); only2 = atoi(argv[5]); }
        int c0 = missing_count(n, K, A, B), bc = c0, bA[K], bB[K];
        memcpy(bA, A, sizeof bA); memcpy(bB, B, sizeof bB);
        print_set("START", n, A, B, c0);
        unsigned long long tried = 0;
        int npairs = 0;
        time_t t0 = time(NULL);
        for (int s1 = 0; s1 < K; s1++) for (int s2 = s1 + 1; s2 < K; s2++) {
            if (only1 >= 0 && !(s1 == only1 && s2 == only2)) continue;
            npairs++;
            int o1a = A[s1], o1b = B[s1], o2a = A[s2], o2b = B[s2];
            for (int i = 0; i < NC; i++) {
                A[s1] = CA[i]; B[s1] = CB[i];
                if (dup(A, B, s1, CA[i], CB[i])) continue;
                for (int j = 0; j < NC; j++) {
                    A[s2] = CA[j]; B[s2] = CB[j];
                    if (dup(A, B, s2, CA[j], CB[j])) continue;
                    tried++;
                    int cc = missing_count(n, K, A, B);
                    if (cc == 0) print_set("FOUND", n, A, B, 0);   /* every witness in the neighbourhood */
                    if (cc < bc) {
                        bc = cc;
                        memcpy(bA, A, sizeof bA); memcpy(bB, B, sizeof bB);
                        print_set("IMPROVE", n, A, B, cc);
                    }
                }
            }
            A[s1] = o1a; B[s1] = o1b; A[s2] = o2a; B[s2] = o2b;
        }
        printf("sweep2 COMPLETE n=%d slot_pairs=%d evaluations=%llu seconds=%ld start_missing=%d best_missing=%d\n",
               n, npairs, tried, (long)(time(NULL) - t0), c0, bc);
        print_set("BEST", n, bA, bB, bc);
        return bc < c0 ? 0 : 1;
    }
    if (!strcmp(argv[1], "scan3")) {         /* scan3 N "f1 f2 f3" ILO IHI */
        /* Three chords are held fixed (the skeleton shared by the n=61..64 witnesses); the other
         * three slots are scanned EXHAUSTIVELY -- slot 3 over candidate indices [ILO,IHI), slots 4
         * and 5 over every unordered pair of candidates.  Splitting [ILO,IHI) splits the work
         * across processes.  This is a complete joint-3 move inside the declared subfamily. */
        int n = atoi(argv[2]);
        nV = n; build_candidates(n);
        int A[K], B[K];
        if (parse_chords(argv[3], A, B) != 3) { printf("need 3 fixed chords\n"); return 2; }
        int ilo = atoi(argv[4]), ihi = atoi(argv[5]);
        if (ihi > NC) ihi = NC;
        int bc = 1 << 30, bA[K], bB[K];
        unsigned long long tried = 0;
        time_t t0 = time(NULL);
        for (int i = ilo; i < ihi; i++) {
            A[3] = CA[i]; B[3] = CB[i];
            for (int j = 0; j < NC; j++) {
                if (dup(A, B, 4, CA[j], CB[j])) continue;
                A[4] = CA[j]; B[4] = CB[j];
                for (int m = j + 1; m < NC; m++) {
                    if (dup(A, B, 5, CA[m], CB[m])) continue;
                    A[5] = CA[m]; B[5] = CB[m];
                    tried++;
                    int cc = missing_count(n, K, A, B);
                    if (cc == 0) print_set("FOUND", n, A, B, 0);
                    if (cc < bc) { bc = cc; memcpy(bA, A, sizeof bA); memcpy(bB, B, sizeof bB); }
                }
            }
            printf("  scan3 n=%d slot3=%d/%d (%d,%d) best=%d %llu evals %lds\n",
                   n, i - ilo + 1, ihi - ilo, CA[i], CB[i], bc, tried, (long)(time(NULL) - t0));
            fflush(stdout);
        }
        printf("scan3 COMPLETE n=%d range=[%d,%d) evaluations=%llu seconds=%ld best_missing=%d\n",
               n, ilo, ihi, tried, (long)(time(NULL) - t0), bc);
        print_set("BEST", n, bA, bB, bc);
        return bc == 0 ? 0 : 1;
    }
    if (!strcmp(argv[1], "control")) {        /* positive control: recorded results must reproduce */
        struct { int n; int k; const char *ch; int want; const char *what; } T[] = {
            {56, 6, "0,2 0,53 1,39 20,39 39,48 48,53", 0, "recorded n=56 6-chord witness is pancyclic"},
            {40, 5, "0,5 1,5 2,30 3,10 4,11",          0, "recorded n=40 5-chord witness (t_5 lower side)"},
            {41, 5, "0,5 1,5 2,30 3,10 4,11",          2, "those 5 chords at n=41 miss exactly 2 lengths"},
            {66, 6, "0,2 0,48 1,40 11,41 44,47 47,52", 3, "REPORT-k6-upper n=66 local optimum misses 3"},
            {61, 6, "0,2 0,58 1,44 20,45 44,53 53,58", 1, "n=61 insertion image misses exactly 1"},
        };
        int ok = 1;
        for (unsigned t = 0; t < sizeof(T) / sizeof(T[0]); t++) {
            int A[9], B[9];
            parse_chords(T[t].ch, A, B);
            int got = missing_count(T[t].n, T[t].k, A, B);
            int pass = (got == T[t].want);
            ok &= pass;
            printf("[%s] %s: missing=%d expected=%d\n", pass ? "PASS" : "FAIL", T[t].what, got, T[t].want);
        }
        printf("CONTROL %s\n", ok ? "GREEN" : "RED");
        return ok ? 0 : 1;
    }
    printf("unknown mode\n");
    return 2;
}
