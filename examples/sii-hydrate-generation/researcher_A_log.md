# Researcher A -- Iteration Log

**Focus:** Box dimension optimization, crystal scaling, rep selection

---

## Round 1

### Iteration 0: Scale crystal to 3.6 nm, water everywhere
- **Hypothesis:** Scale crystal coordinates to fit a 3.6 nm target box, place water in full box.
- **Result:** Composite 34.5 (crystal_integrity=0, slab_exclusion=0, geometric=29.7)
- **Status:** BASELINE
- **Analysis:** Scaling x,y by 1.051 deforms crystal structure. GenIce2 reference coords no longer match. Water placed in full box including slab region.

### Iteration 1: Reduce scaling to 3.5 nm
- **Hypothesis:** Smaller scale factor might preserve crystal better.
- **Result:** Composite 40.5 (crystal_integrity=0, slab_exclusion=0, geometric=54.8)
- **Status:** KEPT
- **Analysis:** Geometric score improved (closer to crystal native), but ANY scaling destroys crystal integrity. Still water everywhere.

### Iteration 2: Try rep 3 (larger crystal)
- **Hypothesis:** Using rep 3 3 2 gives 5.136 nm crystal -- no scaling needed for larger box.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0, geometric varies)
- **Status:** KEPT
- **Analysis:** No scaling means crystal integrity=100. But water is still placed everywhere (slab_exclusion=0). Box dimensions don't match rep 2 target. Rep 3 gives too-large crystal for x,y.

### Iteration 3: Back to rep 2, scale to 3.6, partial water filter 30%
- **Hypothesis:** Filtering 30% of waters from slab region might help.
- **Result:** Composite 34.5 (crystal_integrity=0, slab_exclusion=0)
- **Status:** REVERTED
- **Analysis:** 30% filtering is nowhere near enough. Still hundreds of waters in slab. And scaling is back, breaking crystal integrity.

**Round 1 Best: 65.0 (iteration 2)**

---

## Round 2 (with shared knowledge)

Peer review from Round 1 flagged TWO critical issues:
1. Crystal scaling destroys integrity -- must use native GenIce2 dimensions
2. Water must be completely excluded from slab z-range

### Iteration 0: Native crystal dims, water still in slab
- **Hypothesis:** Fix crystal dims first, deal with water later.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** KEPT
- **Analysis:** Crystal integrity fixed. But water exclusion is the other binding constraint.

### Iteration 1: Native dims, partial water filter 60%
- **Hypothesis:** Filtering 60% of slab waters should help.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** KEPT (tied)
- **Analysis:** Even 60% filtering leaves ~170 waters in slab. slab_exclusion scoring penalizes 10 points per water -- score still 0.

### Iteration 2: Native dims, partial water filter 90%
- **Hypothesis:** 90% filtering should be nearly clean.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** KEPT (tied)
- **Analysis:** 90% still leaves ~35 waters. Scoring threshold is strict: any overlap is heavily penalized. Need 100% exclusion.

### Iteration 3: Native dims, proper water exclusion (FIXED)
- **Hypothesis:** Generate water ONLY in z < z_bot and z > z_top regions.
- **Result:** Composite 99.9 (crystal_integrity=100, slab_exclusion=100)
- **Status:** KEPT -- **Round 2 BEST**
- **Analysis:** Both constraints now satisfied. z-exclusive water placement ensures zero overlap. Native crystal dims preserve integrity.

**Round 2 Best: 99.9 (iteration 3)**

---

## Round 3 (refinement)

### Iteration 0: Native dims + exclusion, seed 120
- **Result:** Composite 99.9
- **Status:** KEPT

### Iteration 1: Native dims + exclusion, density 998
- **Result:** Composite 99.8 (slightly off-target density)
- **Status:** REVERTED

### Iteration 2: Native dims + exclusion, optimized (FINAL)
- **Result:** Composite 99.9
- **Status:** KEPT -- **FINAL**

**Round 3 Best: 99.9**

---

## Key Learnings
1. Crystal scaling is NEVER acceptable -- even small factors destroy the Fd3m symmetry.
2. Partial water filtering is insufficient -- must design placement to exclude slab region entirely.
3. The two constraints (crystal integrity + water exclusion) are independent and both must be solved.
