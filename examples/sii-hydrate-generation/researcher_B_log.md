# Researcher B -- Iteration Log

**Focus:** Crystal structure handling, rep selection, coordinate preservation

---

## Round 1

### Iteration 0: Rep 1 1 2 (tiny crystal), water everywhere
- **Hypothesis:** Start with smaller rep for faster generation, place water in full box.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** BASELINE
- **Analysis:** Rep 1 gives 1.712 nm crystal -- too small for target box. But since no scaling applied, crystal_integrity=100. Water in full box: slab_exclusion=0.

### Iteration 1: Rep 1 1 2, force box to 3.6 nm
- **Hypothesis:** Force box to 3.6 nm for correct geometry.
- **Result:** Composite 50.0 (geometric worsens due to box mismatch)
- **Status:** REVERTED
- **Analysis:** Rep 1 crystal is 1.712 nm but box forced to 3.6 nm -- huge geometric mismatch. Crystal atoms are only in a small corner of the box.

### Iteration 2: Rep 2 2 2, scale to 3.6 nm, water everywhere
- **Hypothesis:** Rep 2 gets closer to 3.6 nm, scale the rest.
- **Result:** Composite 34.5 (crystal_integrity=0, slab_exclusion=0)
- **Status:** REVERTED
- **Analysis:** Scaling breaks crystal integrity. Water everywhere breaks exclusion. Worst of both worlds.

### Iteration 3: Rep 2, native dims, water everywhere
- **Hypothesis:** Use native dimensions, fix water later.
- **Result:** Composite 65.0 (crystal_integrity=100, slab_exclusion=0)
- **Status:** KEPT
- **Analysis:** Good insight: native dims preserve crystal. But water exclusion still needed.

**Round 1 Best: 65.0 (iterations 0 and 3)**

---

## Round 2 (with shared knowledge)

Peer review confirmed: native dims + z-exclusive water placement is the solution path.

### Iteration 0: Scale to 3.5, proper water exclusion
- **Hypothesis:** Try 3.5 nm box with proper water exclusion -- compromise on geometry.
- **Result:** Composite 75.4 (crystal_integrity=0, slab_exclusion=100)
- **Status:** KEPT (improving)
- **Analysis:** Water exclusion works perfectly. But scaling still breaks crystal integrity.

### Iteration 1: Scale to 3.45, proper water exclusion
- **Hypothesis:** 3.45 nm is closer to 3.424 -- maybe close enough?
- **Result:** Composite 78.4 (crystal_integrity=0, slab_exclusion=100)
- **Status:** KEPT
- **Analysis:** Geometric score improves. But crystal_integrity is binary: any deviation from reference = 0.

### Iteration 2: Native dims, proper water exclusion (FIXED)
- **Hypothesis:** Accept 3.424 nm as the correct box dimension.
- **Result:** Composite 99.9 (crystal_integrity=100, slab_exclusion=100)
- **Status:** KEPT -- **Round 2 BEST**
- **Analysis:** Both constraints satisfied. The box IS the crystal -- you can't choose the box independently.

### Iteration 3: Native dims, proper exclusion, density 998
- **Hypothesis:** Fine-tune water density.
- **Result:** Composite 99.8 (density slightly off-target)
- **Status:** REVERTED
- **Analysis:** 998 kg/m^3 is close but 1000 gives better density score.

**Round 2 Best: 99.9 (iteration 2)**

---

## Round 3 (refinement)

### Iteration 0: Native dims + exclusion, seed 220
- **Result:** Composite 99.9
- **Status:** KEPT

### Iteration 1: Native dims + exclusion, density 1000
- **Result:** Composite 99.9
- **Status:** KEPT

### Iteration 2: Native dims + exclusion, optimized (FINAL)
- **Result:** Composite 99.9
- **Status:** KEPT -- **FINAL**

**Round 3 Best: 99.9**

---

## Key Learnings
1. Rep selection determines crystal dimensions -- rep 2 = 3.424 nm, this IS the box x,y.
2. Crystal integrity scoring is strict: any coordinate scaling, no matter how small, yields 0.
3. The insight that "box dims = crystal dims" is fundamental -- the crystal dictates the geometry.
