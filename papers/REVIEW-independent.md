# Independent direct-DFS review

## Algorithm

[indep.c](construction/indep.c) is a separate C implementation. It builds the adjacency matrix for (C_n) plus the chord set, then enumerates each simple cycle by depth-first search from each possible least vertex. It records a length only when the DFS closes back to its start; it does not use a cycle-space basis, XOR, Gray code, or degree-mask cycle test. The only bit mask is the DFS visited-vertex set, safe for the tested (n\le41).

Compiled with the requested executable:

```text
C:\Users\ToolsEnabled-Dev\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin\gcc.exe -O2 -std=c11 indep.c -o indep.exe
```

## Witness re-verification

Verdict: **confirmed independently**.

Command: `indep.exe witnesses`.

Measured output:

```text
CHECK n=38 k=5 lengths=36 pancyclic=yes
CHECK n=40 k=5 lengths=38 pancyclic=yes
CHECK n=41 k=6 lengths=39 pancyclic=yes
```

These counts equal (n-2), so every length 3 through n was found by direct DFS.

## n=24 and n=25 enumeration

The implementation uses the permitted rotation reduction: the first chord is fixed to `(0,b)` and every remaining 3-subset is enumerated without reflection or further symmetry reduction. Chunks (b=2,\ldots,12) were each run as a separate BelowNormal process. This is exhaustive up to rotation because every nonempty chord set can be rotated so one chord has first endpoint 0.

Verdict for n=24: **confirmed**. `indep-n24.log` records 26,974,255 tested sets, 15 raw pancyclic witnesses, and 1,062.123 summed CPU seconds. Dihedral canonicalization of the 15 raw witnesses gives exactly 2 classes:

```text
(0,2)(0,21)(1,19)(8,23)
(0,2)(1,5)(1,7)(3,18)
```

These are rotations/reflections of the two classes expected by the search owner (the first expected representative has an equivalent rotated/reflected form).

Verdict for n=25: **confirmed no witness** in the rotation-fixed exhaustive search. `indep-n25.log` records 35,303,774 tested sets, 0 pancyclic witnesses, and 673.767 summed CPU seconds over b=2..12.

## Reproducibility / uncertainty

No GPU process was run. No source search code was modified. The direct DFS’s positive witness results and the chunked exhaustive results are independent evidence. The only reduction is the explicitly documented rotation fixing; reflection and all other symmetries were retained and canonicalized only after enumeration.
