# FAMILY_SPEC — 5 new canvas-safe families (Architect → impl)

Architect has fully designed + pure-python-validated all 5 constructions over
the FULL pair set (train+test+arc-gen). Your job: translate each into minimal
canvas-safe ONNX in `engine/families.py`, register them, and iterate against
the **official grader** (`python run.py solve <n>`) until every target task is
`solved` with `n_fail==0` and measurable. The grader is the only acceptance
gate; do not hand-wave — a family is done only when its tasks show `solved`
in `logs/results.json`.

## Targets (11 tasks, 5 families)

| Family | Tasks | Rule (validated) |
|---|---|---|
| `symmetry_fill` | 113, 385 | same-shape: `out[r][c]=in[r][c] if in[r][c]!=0 else flipud_H(in)[r][c]` (flipud within data-dependent grid height H) |
| `crop_bbox` | 31 | output = input cropped to bounding box of NON-background (colour≥1) cells, re-embedded top-left |
| `quadrant_upscale` | 83,142,152 (mirror); 106,194 (rot) | 2× block: mirror = `[[A, fliplrA],[flipudA, rot180A]]`; rot = `[[A, rot90cwA],[rot90ccwA, rot180A]]` |
| `int_scale` | 223 (k=3), 307 (k=2) | each cell → k×k block, k constant per task |
| `tiling` | 249 (tr=1,tc=2) | output = A tiled tr×tc |

327 and 108 are NOT in scope (different rules — leave unsolved).

## Hard rules / proven gotchas (DO NOT violate)

1. **Do NOT modify `GlobalGeom`, `Fractal3`, or any existing family / the
   existing 8 REGISTRY entries.** Regression on the 42 solved tasks = failure.
   Copy GlobalGeom's `flip_rows` / `flip_cols` *closure bodies* into NEW
   module-level helpers; leave GlobalGeom byte-identical.
2. **Opset:** flip/matmul/crop/quadrant/tiling/symmetry_fill families use
   **opset 10** (`_model(...)`, like GlobalGeom): `Squeeze/Unsqueeze/
   ReduceSum/ReduceMax/ReduceMin` take `axes` as an **attribute**; `Slice`
   takes `starts/ends/axes` as **input tensors** (init INT64). `int_scale`
   uses **opset 13** standalone (copy Fractal3's `op=[h.make_opsetid("",13)]`
   + `Resize` pattern).
3. **No channel-axis implicit broadcast on Mul/Add/Sub.** Spatial broadcasts
   that GlobalGeom already uses ([30,30]·[30,1], [30,1]+[1,30]) are PROVEN ok
   — keep them. But to multiply a `[1,1,30,30]` mask against a `[1,10,30,30]`
   one-hot you MUST first `Tile` the mask to `[1,10,30,30]` (rep const
   `[1,10,1,1]`), exactly like Fractal3 does `Tile(MB,"mb_rep")` before
   `Mul(TG,MBt)`. Never Mul a 1-channel by a 10-channel directly.
4. **Disjoint-region Add keeps one-hot valid.** Every quadrant/tile copy lands
   in a region no other copy touches, so summing the `[1,10,30,30]` tensors
   never makes >1 channel hot in a graded cell. This is required for a valid
   decode — verify the math, do not add overlapping regions.
5. **Canvas-safety (already proven by the construction):** input padding cells
   are all-zero one-hot; every flip/translation matrix is built from
   data-dependent occupancy with FIXED [30,30]/[.,.,30,30] shapes (data-
   dependent VALUES only) so the grader's strict shape_inference passes (same
   as GlobalGeom). Out-of-block cells stay all-zero → decode trims them.
   Interior colour-0 cells keep channel-0 hot → decode as 0 (NOT trimmed) —
   this is correct and required.
6. **detect() runs on train only; fit()+quick_apply re-check ALL pairs.** For
   `quadrant_upscale` the train ex0 can match BOTH variants (symmetric input)
   — disambiguate in `fit(spec, pairs)` by picking the variant whose `apply`
   reproduces EVERY pair (mirror first, then rot; rot requires every input
   square). Same fit-over-all-pairs discipline as `LocalNeighborhood.fit`.
7. **REGISTRY order** (cheapest-correct-first; new ones inserted AFTER
   `GlobalGeom`, BEFORE `LinearLocalConv`), final list:
   `Identity, ColorPermute, ColorLUT, Fractal3, GlobalGeom, SymmetryFill,
   CropBBox, QuadrantUpscale, IntScale, Tiling, LinearLocalConv,
   LocalConvMin, LocalNeighborhood`. (Shape-changing detects are disjoint
   from same-shape families; `SymmetryFill` is same-shape but its detect is
   exact — `out==fill(in,flipud(in))` for all train — so no shadowing.
   Fractal3 may detect-then-reject task223 via quick_apply; that's fine, the
   solver falls through to IntScale.)

## Shared module-level helpers to add (opset-10 node emitters)

Add these near the top of families.py (after `_same_shape`). They emit nodes
into a passed `nodes` list and return output tensor names; `_u` is a fresh-uid
counter dict so names never collide when a family uses several.

- `_occ_all(nodes, src, pfx)` → returns scalar float names `H`, `W`:
  `chA=ReduceSum(src,axes=[1],keepdims=1)` [1,1,30,30];
  `colocc=ReduceMax(chA,axes=[2],keepdims=1)` [1,1,1,30];
  `W=ReduceSum(colocc,axes=[3],keepdims=1)`; `Wsq=Squeeze(W,axes=[0,1,2,3])`
  (scalar). Same for H via axes [3] then [2]. Counts every in-grid cell incl
  colour-0 (true grid extent).
- `_occ_nz(nodes,inits,src,pfx)` → `rvec`,`cvec` float [30]: Slice channels
  1..10 (`Slice(src,s=[1],e=[10],ax=[1])` with INT64 inits), `ReduceSum
  axes=[1] keepdims=1` → nz[1,1,30,30]; `rvec=Squeeze(ReduceMax(nz,axes=[3],
  keepdims=1),axes=[0,1,3])` [30]; `cvec=Squeeze(ReduceMax(nz,axes=[2],
  keepdims=1),axes=[0,1,2])` [30].
- `_idx(nodes,pfx)` → float index tensors: `ar`=Constant INT64[30]=range(30);
  `arf`=Cast→FLOAT; `ai=Unsqueeze(arf,axes=[1])` [30,1];
  `aj=Unsqueeze(arf,axes=[0])` [1,30].
- `_flip_rows_P(nodes,src,pfx)` and `_flip_cols_P(nodes,src,pfx)` → emit the
  EXACT node sequence from `GlobalGeom.flip_rows`/`flip_cols` closures but
  return the permutation matrix tensor name `P` ([30,30] float) instead of
  doing the final MatMul (so callers can MatMul or compose). Copy the bodies
  verbatim; only stop before step 10's MatMul and `return P`.

## Per-family construction (exact)

### SymmetryFill  (opset 10, est_points 14.0)
- detect(train): every pair same-shape AND for all train pairs
  `out == [[ (in[r][c] if in[r][c]!=0 else in[H-1-r][c]) ]]` with H=len(in).
  return `{"axis":"v"}` else None. (Only v needed; 113/385 both v.)
- apply: as above (numpy `np.where(a!=0,a,np.flipud(a))`).
- build_onnx:
  `Pr=_flip_rows_P(input)`; `flipOH=MatMul(Pr,input)` [1,10,30,30].
  `nzc=Slice(input,s=[1],e=[10],ax=[1])`; `mask=ReduceSum(nzc,axes=[1],
  keepdims=1)` [1,1,30,30] ∈{0,1}. `m10=Tile(mask,rep=[1,10,1,1])`
  [1,10,30,30]. `one=Constant FLOAT scalar 1.0`; `inv=Sub(one,m10)`
  (scalar−tensor broadcast on a const scalar is fine; if grader objects make
  `one` a `[1,10,30,30]` ones initializer via `ConstantOfShape`/init and
  `Sub`). `a=Mul(input,m10)`; `b=Mul(flipOH,inv)`; `output=Add(a,b)`.

### CropBBox  (opset 10, est_points 14.0)
- detect(train): for every train pair, crop input to non-bg bbox == output.
  return `{}` else None. apply: numpy argwhere(a!=0) min/max slice.
- build_onnx:
  `_idx` → ai[30,1],aj[1,30]. `_occ_nz` → rvec[30],cvec[30].
  consts: `BIG=Constant FLOAT scalar 1000.0`, `oneV=Constant FLOAT [30]` all
  1.0, `half=0.5`.
  `r_min=ReduceMin( Add(arf, Mul(Sub(oneV,rvec),BIG)) ,axes=[0])` scalar;
  `r_max=ReduceMax( Mul(arf,rvec) ,axes=[0])` scalar; same with cvec →
  `c_min`,`c_max`.
  Pr[k,j]=1 iff (j−k)==r_min and j≤r_max:
  `JmK=Sub(aj,ai)` [30,30]; `eqr=Less(Abs(Sub(JmK,r_min)),half)`;
  `jle=Less(aj, Add(r_max,half))` [1,30]; `Pr=Mul(Cast eqr→F, Cast jle→F)`
  [30,30] (jle broadcasts over rows — proven-style spatial broadcast).
  Pc[c,m]=1 iff (c−m)==c_min and c≤c_max:
  `CmM=Sub(ai,aj)` [30,30] (ai as c[30,1], aj as m[1,30]);
  `eqc=Less(Abs(Sub(CmM,c_min)),half)`; `cle=Less(ai,Add(c_max,half))`
  [30,1]; `Pc=Mul(Cast eqc→F,Cast cle→F)` [30,30].
  `T=MatMul(Pr,input)`; `output=MatMul(T,Pc)`.

### QuadrantUpscale  (opset 10, est_points 13.0)
- detect(train): all pairs out is exactly 2H×2W; return `{}`.
- fit(spec,pairs): mode = first of ("mirror","rot") whose `apply` matches
  EVERY pair; rot only if every input square. else None.
  mirror apply: `np.block([[A,fliplrA],[flipudA,np.flipud(np.fliplr(A))]])`.
  rot apply: `np.block([[A,np.rot90(A,-1)],[np.rot90(A,1),np.rot90(A,2)]])`.
- build_onnx (mode in spec):
  `_idx`, `_occ_all` → Hs,Ws scalars.
  `Prf=_flip_rows_P(input)` (flipud matrix); `Pcf=_flip_cols_P(input)`
  (fliplr matrix).
  `Trgt[c,j]=1 iff (j−c)==Ws`: `JmC=Sub(aj,ai)`;
  `Trgt=Cast(Less(Abs(Sub(JmC,Ws)),half))→F` [30,30].
  `Tdwn[r,s]=1 iff (r−s)==Hs`: `RmS=Sub(ai,aj)`;
  `Tdwn=Cast(Less(Abs(Sub(RmS,Hs)),half))→F` [30,30].
  Common: `flrA=MatMul(input,Pcf)`; `fudA=MatMul(Prf,input)`;
  `rot180A=MatMul(Prf,flrA)`.
  - mirror: `TL=input`; `TR=MatMul(flrA,Trgt)`;
    `BL=MatMul(Tdwn,fudA)`; `BR=MatMul(Tdwn,MatMul(rot180A,Trgt))`.
  - rot: `Tp=Transpose(input,perm=[0,1,3,2])`;
    `cw=MatMul(Tp,Pcf)` (=fliplr∘transpose);
    `ccw=MatMul(Prf,Tp)` (=flipud∘transpose);
    `TL=input`; `TR=MatMul(cw,Trgt)`; `BL=MatMul(Tdwn,ccw)`;
    `BR=MatMul(Tdwn,MatMul(rot180A,Trgt))`.
  `output=Add(Add(TL,TR),Add(BL,BR))`. (rot variant requires square input —
  guaranteed by fit; Ws==Hs there so Pcf/Trgt are consistent post-transpose.)

### IntScale  (opset 13, standalone — copy Fractal3 opset-13 skeleton)
- detect(train): k=len(out)//len(in); consistent & ≥2 & out==kron(in,ones
  (k,k)) for all train. return `{"k":k}`.
- build_onnx: `scales=Constant/init FLOAT[4]=[1,1,k,k]`;
  `R=Resize(input,"",scales, mode="nearest",
  coordinate_transformation_mode="asymmetric", nearest_mode="floor")`
  [1,10,30k,30k]; `output=Slice(R, starts=[0,0], ends=[30,30], axes=[2,3])`
  INT64 inits. (Resize/Slice exactly as Fractal3 uses them.)

### Tiling  (opset 10, est_points 13.0)
- detect(train): tr=len(out)//len(in), tc=len(out[0])//len(in[0]);
  consistent, (tr,tc)!=(1,1), out==np.tile(in,(tr,tc)) all train.
  return `{"tr":tr,"tc":tc}`.
- build_onnx: `_idx`,`_occ_all`→Hs,Ws. For q in range(tc): `Tq[c,j]=1 iff
  (j−c)==q*Ws` → const `qW = Mul(Ws, Constant FLOAT q)`; matrix as in
  QuadrantUpscale Trgt with qW. For p in range(tr): `Tp[r,s]=1 iff
  (r−s)==p*Hs`. `output = Add over p,q of MatMul(Tdp, MatMul(input,Trq))`.
  For 249 tr=1,tc=2 → `output=Add(input, MatMul(input,Trgt_1W))`.

## Acceptance / reporting

For each family in REGISTRY order, after coding run:
`python run.py solve <n>` for each of its tasks (or
`python run.py sweep` ranges). A task is accepted ONLY if the printed status
is `solved` (this means the official grader passed: n_fail==0, measurable).
If a task is NOT solved, debug the ONNX (opset/broadcast/shape) and retry —
the construction math is already proven correct in pure python, so any
failure is an ONNX-emission bug, not a rule bug.

Report back: a table of `task | family | status | points | memory | params`
for all 11 targets, the new total solved count + projected points
(`python run.py render` then read top of logs/TASK_INDEX.md), and note any
target that could not be made `solved` with the exact grader error string.
Do NOT commit — the Architect re-verifies a sample and commits per family.
