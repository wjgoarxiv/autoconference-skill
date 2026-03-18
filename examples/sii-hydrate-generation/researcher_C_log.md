# Researcher C -- Iteration Log

**Focus:** Water placement strategy, z-range filtering, exclusion zone enforcement

---

## Round 1

### Iteration 0: Rep 2, scale to 3.6, water everywhere
- **Hypothesis:** Standard approach -- scale crystal to target box, fill with water.
- **Result:** Composite 34.5 (crystal_integrity=0, slab_exclusion=0)
- **Status:** BASELINE
- **Analysis:** Both constraints violated. Scaling deforms crystal. No water filtering.

### Iteration 1: Scale to 3.6, partial water filter 50%
- **Hypothesis:** Remove half the waters from slab region.
- **Result:** Composite 34.5 (crystal_integrity=0, slab_exclusion=0)
- **Status:** KEPT (tied)
- **Analysis:** Even 50% removal leaves ~240 waters in slab. slab_exclusion still 0. Crystal still scaled.

### Iteration 2: Scale to 3.5, partial water filter 70%
- **Hypothesis:** Smaller scale + more aggressive filtering.
- **Result:** Composite 40.5 (crystal_integrity=0, slab_exclusion=0)
- **Status:** KEPT
- **Analysis:** Geometric improved slightly. But 70% filtering still leaves ~130 waters in slab. And scaling still breaks crystal.

### Iteration 3: Native dims, water still in slab
- **Hypothesis:** Stop scaling, focus on native dimensions. Water filtering later.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** KEPT
- **Analysis:** Big improvement from fixing crystal dims. Crystal integrity jumps from 0 to 100. But water exclusion still needed.

**Round 1 Best: 65.0 (iteration 3)**

---

## Round 2 (with shared knowledge)

Shared knowledge confirms: partial filtering is a dead end. Must place water exclusively outside slab from the start.

### Iteration 0: Scale to 3.5, proper water exclusion
- **Hypothesis:** Try intermediate box size with proper exclusion.
- **Result:** Composite 75.4 (crystal_integrity=0, slab_exclusion=100)
- **Status:** KEPT
- **Analysis:** Water exclusion works. But crystal integrity is 0 due to scaling.

### Iteration 1: Scale to 3.45, proper water exclusion
- **Hypothesis:** Get closer to native dims.
- **Result:** Composite 78.4 (crystal_integrity=0, slab_exclusion=100)
- **Status:** KEPT
- **Analysis:** Approaching native dims but still not exact. Crystal integrity remains 0.

### Iteration 2: Native crystal dims, proper exclusion (FIXED)
- **Hypothesis:** Use exact GenIce2 box dimensions + z-exclusive water.
- **Result:** Composite 99.9 (crystal_integrity=100, slab_exclusion=100)
- **Status:** KEPT -- **Round 2 BEST**
- **Analysis:** Both constraints finally satisfied simultaneously.

### Iteration 3: Native dims, proper exclusion, density 1000
- **Hypothesis:** Confirm result with explicit density target.
- **Result:** Composite 99.9
- **Status:** KEPT

**Round 2 Best: 99.9 (iteration 2)**

---

## Round 3 (refinement)

### Iteration 0: Native dims + exclusion, seed 320
- **Result:** Composite 99.9
- **Status:** KEPT

### Iteration 1: Native dims + exclusion, density 999
- **Result:** Composite 99.9
- **Status:** KEPT

### Iteration 2: Native dims + exclusion, optimized (FINAL)
- **Result:** Composite 99.9
- **Status:** KEPT -- **FINAL**

**Round 3 Best: 99.9**

---

## Key Learnings
1. Partial water filtering is fundamentally flawed -- even 90% removal fails the strict exclusion scoring.
2. Water placement must be designed from the start with z-range awareness, not patched post-hoc.
3. The two constraints (crystal integrity + slab exclusion) must be solved simultaneously, not sequentially.
