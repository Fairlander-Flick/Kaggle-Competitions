# NeuroGolf 2026 — Task Triage Report

**Generated:** 2026-05-17  
**Scope:** 365 unsolved tasks (400 total − 35 solved)  
**Method:** All example pairs (train + test + arc-gen) loaded via `dataio.all_pairs()`. A property is TRUE only if it holds for 100% of a task's pairs. Priority order for bucket assignment: identity > channel_only_recolor > global_geom > crop_bbox > symmetry_fill > int_scale > tiling > needs_analysis.

---

## Summary Table

| Bucket | Count | est_points ceiling | count × est_points | Notes |
|--------|------:|-------------------:|-------------------:|-------|
| global_geom | 7 | 22.0 | **154.0** | flip_h/v, rot90/180/270, transpose |
| crop_bbox | 1 | 20.0 | **20.0** | crop to non-zero bounding box |
| symmetry_fill | 2 | 18.0 | **36.0** | fill zeros by horizontal reflection |
| int_scale | 2 | 16.0 | **32.0** | uniform integer pixel scaling |
| tiling | 1 | 16.0 | **16.0** | m×n tile repeat |
| identity | 0 | 25.0 | 0.0 | — |
| channel_only_recolor | 0 | 22.7 / 20.4 | 0.0 | — |
| needs_analysis | 352 | 0.0 | 0.0 | see sub-groups below |

**Sorted by count × est_points (descending):**

| Rank | Bucket | count × est_points |
|-----:|--------|-------------------:|
| 1 | global_geom | 154.0 |
| 2 | symmetry_fill | 36.0 |
| 3 | int_scale | 32.0 |
| 4 | crop_bbox | 20.0 |
| 5 | tiling | 16.0 |

---

## Bucket: global_geom (7 tasks)

Each task's output is a consistent geometric transform of its input across all pairs.

| Task | Transform |
|-----:|-----------|
| 87 | rot180 |
| 140 | rot180 |
| 150 | flip_h |
| 155 | flip_v |
| 179 | transpose |
| 241 | transpose |
| 380 | rot90 |

**Full task list:** 87, 140, 150, 155, 179, 241, 380

---

## Bucket: crop_bbox (1 task)

Output equals input cropped to the bounding box of non-zero (non-background) cells, consistent across all pairs.

**Full task list:** 31

---

## Bucket: symmetry_fill (2 tasks)

Output equals input with zero cells filled by reflecting across the identified axis, consistent across all pairs.

| Task | Axis |
|-----:|------|
| 113 | h (top↔bottom) |
| 385 | h (top↔bottom) |

**Full task list:** 113, 385

---

## Bucket: int_scale (2 tasks)

Output is input with each cell scaled to a k×k pixel block (uniform integer factor k≥2), consistent across all pairs.

| Task | Scale factor |
|-----:|-------------|
| 223 | 3× |
| 307 | (verified ≥2×) |

**Full task list:** 223, 307

---

## Bucket: tiling (1 task)

Output is input tiled m×n times, consistent across all pairs.

**Full task list:** 249

---

## Bucket: identity (0 tasks)

No unsolved task has output == input for every single pair (train + test + arc-gen).

---

## Bucket: channel_only_recolor (0 tasks)

No unsolved task has a globally consistent single color map f: c→c that holds cellwise for every pair. (Many shape-eq + identical-palette tasks were checked; all failed due to color 0 being mapped to multiple target colors — indicating spatially-conditioned transformations, not pure LUT recolor.)

---

## Bucket: needs_analysis (352 tasks)

Sub-grouped by (shape_eq, size_ratio, colors_delta). A task enters exactly one sub-group based on its aggregate signal across all pairs.

### Sub-group A: shape_eq=True | size_ratio=same | colors=identical (111 tasks)
Same shape, same palette, but output differs from input non-trivially. Color 0 maps to different values at different positions — spatially-conditioned transforms (fill patterns, connectivity, object detection, etc.).

Tasks: 5, 8, 9, 12, 13, 18, 20, 24, 25, 28, 30, 32, 33, 35, 37, 41, 44, 45, 51, 54, 59, 64, 66, 68, 71, 76, 78, 80, 82, 84, 85, 86, 89, 92, 99, 101, 112, 117, 128, 129, 132, 133, 136, 137, 141, 143, 154, 158, 161, 163, 165, 168, 173, 181, 182, 190, 191, 192, 197, 202, 203, 208, 212, 215, 217, 222, 224, 225, 228, 234, 237, 240, 243, 245, 248, 250, 267, 268, 270, 280, 284, 285, 286, 288, 298, 301, 306, 313, 314, 322, 324, 328, 329, 333, 340, 343, 345, 353, 356, 358, 359, 361, 363, 370, 373, 375, 378, 379, 382, 383, 390

### Sub-group B: shape_eq=False | size_ratio=varies | colors=identical (44 tasks)
Output shape differs from input shape and varies across pairs, same palette. Likely object-detection / extraction tasks where output size depends on the input content.

Tasks: 14, 21, 29, 36, 65, 88, 91, 96, 109, 114, 115, 124, 134, 138, 159, 170, 174, 178, 185, 188, 195, 201, 205, 209, 221, 238, 244, 263, 269, 289, 295, 300, 308, 310, 319, 325, 326, 355, 366, 376, 377, 384, 396, 398

### Sub-group C: shape_eq=False | size_ratio=varies | colors_lost=[0] (15 tasks)
Output shape varies, background (color 0) is removed/lost. Likely bounding-box crop or object-isolation tasks where the exact crop size depends on object extent.

Tasks: 49, 177, 184, 216, 218, 233, 247, 264, 290, 291, 339, 346, 365, 391, 394

### Sub-group D: shape_eq=True | size_ratio=same | colors_gained=[3] (11 tasks)
Same shape, new color 3 appears in output. Likely flood-fill, connectivity-marking, or object-coloring tasks using red.

Tasks: 50, 58, 63, 70, 119, 196, 255, 278, 332, 371, 397

### Sub-group E: shape_eq=True | size_ratio=same | colors_gained=[4] (10 tasks)
Same shape, new color 4 appears. Yellow added — likely marking/highlighting tasks.

Tasks: 2, 77, 126, 148, 176, 199, 252, 299, 335, 367

### Sub-group F: shape_eq=True | size_ratio=same | colors_gained=[2] (10 tasks)
Same shape, new color 2 appears. Green added — likely marking/highlighting tasks.

Tasks: 27, 43, 47, 102, 105, 160, 166, 265, 273, 303

### Sub-group G: shape_eq=True | size_ratio=same | colors_gained=[8] (10 tasks)
Same shape, new color 8 (azure/teal) appears. Likely marking tasks.

Tasks: 42, 118, 131, 246, 279, 320, 336, 341, 348, 350

### Sub-group H: shape_eq=True | size_ratio=same | colors_lost=[0] (8 tasks)
Same shape, background color 0 disappears from output. Zero is replaced by actual colors — possibly a completion or inpainting task.

Tasks: 7, 17, 61, 110, 175, 214, 297, 305

### Sub-group I: shape_eq=False | size_ratio=(2.0, 2.0) | colors=identical (7 tasks)
Output is exactly 2× the input in both dimensions, same palette. Not classified as int_scale — meaning each 2×2 block is NOT a uniform copy of the source cell (spatial mixing or upsampling pattern).

Tasks: 83, 106, 108, 142, 152, 194, 327

### Sub-group J: shape_eq=True | size_ratio=same | colors_gained=[5] (6 tasks)
Same shape, new color 5 (gray) appears.

Tasks: 60, 200, 229, 232, 323, 387

### Sub-group K: shape_eq=True | size_ratio=same | colors_lost=[5] (6 tasks)
Same shape, color 5 (gray) is removed/replaced.

Tasks: 206, 260, 312, 354, 362, 368

### Sub-group L: shape_eq=True | size_ratio=same | colors_lost=[8] (4 tasks)
Same shape, color 8 (teal) is removed.

Tasks: 11, 69, 281, 342

### Sub-group M: shape_eq=True | size_ratio=same | colors_gained=[6] (3 tasks)
Same shape, new color 6 (magenta) appears.

Tasks: 90, 94, 292

### Sub-group N: shape_eq=False | size_ratio=(2.0, 1.0) | colors=identical (3 tasks)
Output is 2× input height only (vertical doubling), same palette.

Tasks: 116, 172, 210

### Sub-group O: shape_eq=True | size_ratio=same | colors_gained=[1] (3 tasks)
Same shape, new color 1 (blue) appears.

Tasks: 162, 219, 251

### Sub-group P: shape_eq=False | size_ratio=(1.0, 2.0) | colors=identical (3 tasks)
Output is 2× input width only (horizontal doubling), same palette.

Tasks: 164, 231, 311

### Sub-group Q: shape_eq=False | size_ratio=(2.0, 2.0) | colors_gained=[8] (2 tasks)
2× scale with new color 8 introduced.

Tasks: 19, 388

### Sub-group R: shape_eq=False | size_ratio=(0.3, 0.3) | colors=identical (2 tasks)
Output is ~30% of input size — downscaling / compression / extraction.

Tasks: 39, 316

### Sub-group S: shape_eq=False | size_ratio=varies | colors_lost=[5] (2 tasks)
Variable output size, gray (color 5) is removed.

Tasks: 46, 274

### Sub-group T: shape_eq=False | size_ratio=(0.444444, 1.0) | colors_gained=[3], lost=[1,2,4] (2 tasks)
Narrow output (44% of input height), significant color remapping.

Tasks: 236, 318

### Sub-group U: shape_eq=True | size_ratio=same | colors_gained=[1,2], lost=[5] (2 tasks)
Same shape, blue+green gained, gray lost.

Tasks: 254, 330

### Sub-group V: shape_eq=True | size_ratio=same | colors_gained=[1,3] (2 tasks)
Same shape, blue+red both gained.

Tasks: 256, 349

### Singleton sub-groups (1 task each — 66 tasks total)

| Task | shape_eq | size_ratio | colors |
|-----:|----------|-----------|--------|
| 3 | False | (1.5, 1.0) | gained=[2], lost=[1] |
| 6 | False | (1.0, 0.428571) | gained=[2], lost=[1,5] |
| 10 | True | same | gained=[1,2,3,4], lost=[5] |
| 22 | False | (0.272727, 0.272727) | identical |
| 23 | True | same | gained=[2,8], lost=[5] |
| 26 | False | (1.0, 0.428571) | gained=[8], lost=[1,9] |
| 34 | True | same | lost=[2] |
| 38 | False | (0.111111, 0.555556) | lost=[2] |
| 40 | True | same | lost=[3] |
| 48 | False | varies | lost=[2] |
| 52 | True | same | gained=[0,5], lost=[1,2,3,4,6,7,8,9] |
| 55 | True | same | gained=[1,2,3,4,6] |
| 56 | False | (0.333333, 0.333333) | lost=[0,4,5,7,8,9] |
| 57 | False | (0.375, 0.75) | identical |
| 62 | True | same | gained=[3], lost=[0,2] |
| 67 | False | (1.0, 0.333333) | identical |
| 72 | False | (0.461538, 1.0) | gained=[3], lost=[2,4] |
| 74 | True | same | lost=[9] |
| 75 | True | same | lost=[1] |
| 79 | False | (0.214286, 0.214286) | identical |
| 93 | True | same | lost=[1,2,3,4,6,7,8,9] |
| 100 | False | (0.2, 0.2) | lost=[0] |
| 103 | False | (0.333333, 0.333333) | gained=[1,7], lost=[0,2] |
| 104 | False | (3.0, 3.0) | lost=[2] |
| 107 | False | varies | gained=[2] |
| 111 | False | (0.3, 0.3) | lost=[5] |
| 121 | False | (0.230769, 0.230769) | lost=[8] |
| 123 | False | (2.0, 2.0) | lost=[0] |
| 125 | True | same | gained=[3,4] |
| 130 | False | (0.333333, 0.333333) | lost=[5] |
| 135 | False | (0.333333, 0.333333) | identical |
| 139 | True | same | gained=[7] |
| 144 | False | (0.444444, 1.0) | gained=[3], lost=[2,4,7] |
| 145 | True | same | gained=[1,8] |
| 146 | False | (0.333333, 1.0) | identical |
| 149 | False | (0.272727, 0.272727) | gained=[1], lost=[6,8] |
| 153 | False | (0.3, 0.3) | lost=[0] |
| 156 | True | same | gained=[1,2] |
| 157 | True | same | gained=[1], lost=[5] |
| 167 | True | same | gained=[0,5], lost=[2,3,4] |
| 180 | False | (0.5, 0.5) | identical |
| 183 | False | varies | lost=[1,8] |
| 186 | True | same | gained=[2], lost=[1] |
| 187 | True | same | gained=[2,3], lost=[0] |
| 189 | False | (0.666667, 0.666667) | lost=[3,8] |
| 198 | True | same | gained=[3,4], lost=[0] |
| 204 | True | same | gained=[2,7] |
| 207 | False | (0.4, 0.4) | identical |
| 211 | False | (3.0, 2.0) | identical |
| 213 | False | varies | lost=[0,5] |
| 226 | True | same | gained=[1,2,3] |
| 227 | False | (0.5, 1.0) | gained=[2], lost=[1,3] |
| 235 | False | (0.75, 0.214286) | gained=[2,3,4,8], lost=[0,5] |
| 239 | False | varies | gained=[0] |
| 242 | False | (0.1875, 0.1875) | lost=[0] |
| 253 | False | (0.307692, 0.307692) | identical |
| 257 | False | (0.444444, 0.444444) | lost=[1] |
| 259 | False | varies | gained=[0], lost=[1] |
| 271 | False | (0.333333, 0.333333) | lost=[0] |
| 275 | False | varies | lost=[8] |
| 277 | True | same | gained=[1,2], lost=[8] |
| 287 | True | same | lost=[4] |
| 296 | False | (0.6, 0.428571) | identical |
| 302 | True | same | gained=[6,7,8] |
| 304 | False | (3.0, 3.0) | gained=[0] |
| 315 | False | (3.0, 3.0) | identical |
| 321 | False | (1.0, 0.285714) | lost=[2] |
| 334 | False | (0.6, 0.6) | gained=[5], lost=[1,2,3] |
| 338 | True | same | gained=[3], lost=[2] |
| 347 | False | (1.0, 0.5) | gained=[6], lost=[3,4] |
| 351 | False | (0.3125, 0.3125) | lost=[3] |
| 357 | True | same | gained=[8], lost=[0] |
| 360 | False | (1.0, 0.444444) | lost=[5] |
| 364 | True | same | gained=[1,2,6], lost=[3] |
| 365 (dup check) | — | — | see subgroup C |
| 369 | True | same | gained=[1,2,3], lost=[0] |
| 372 | False | (0.454545, 1.0) | lost=[5] |
| 374 | True | same | gained=[1,2,4], lost=[5] |
| 381 | True | same | gained=[9] |
| 386 | False | (1.0, 0.428571) | gained=[3], lost=[1,5,7] |
| 389 | True | same | gained=[0], lost=[5] |
| 392 | True | same | gained=[5], lost=[0] |
| 393 | False | (0.25, 0.083333) | lost=[0] |
| 395 | False | (0.5, 1.0) | gained=[2], lost=[1,9] |
| 399 | False | varies | gained=[1], lost=[2] |
| 400 | False | (0.208333, 0.208333) | lost=[1] |

---

## Key Observations

1. **No identity or pure-LUT recolor tasks exist among the 365 unsolved.** Every task that has same-shape + identical-palette still has position-dependent transforms (color 0 maps to multiple targets). These are genuinely harder.

2. **global_geom is the best pure-value bucket** (7 tasks × 22.0 pts = 154.0). All 7 tasks use a single elementary geometric operation with zero ambiguity. These should be built first.

3. **Largest cluster (111 tasks): shape_eq + identical palette, spatially conditional.** These are the core of the remaining problem — flood-fill, connectivity, object detection, etc. No simple template applies; arc-pattern-analysis needed per task.

4. **Second-largest cluster (44 tasks): variable-size output, identical palette.** Object extraction / selection tasks. Output size depends on input content — requires content-aware routing.

5. **Sub-group I (7 tasks, 2× scale, not int_scale):** These look like upscaling but each 2×2 block is NOT a uniform copy of the source cell. Possibly: output[2r][2c] = f(input neighborhood). Worth investigating as a custom family.

6. **Many singleton tasks** (~66) with unique size ratios and color signatures — these likely each need individual arc-pattern-analysis passes.
