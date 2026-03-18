# Poster Session -- Round 1

**Baseline:** Composite 0 (no valid .gro file exists yet)
**Target:** Composite >= 80

---

## Researcher A -- Box Dimension Optimization

**Best metric:** 65.0 (iteration 2)
**Iterations run:** 4
**Approach trajectory:** Scale to 3.6 (34.5) -> scale to 3.5 (40.5) -> rep 3 no scale (65.0) -> scale 3.6 + filter 30% (34.5, reverted)

**Key findings:**
1. Crystal scaling to ANY non-native dimension breaks crystal_integrity (score=0).
2. Using rep 3 avoids scaling but gives wrong box dimensions (5.136 nm vs 3.424 target).
3. Partial water filtering (30%) is ineffective -- hundreds of waters remain in slab.
4. The two constraints (crystal integrity + water exclusion) are both violated in naive approaches.

**Notable failures:**
- Scaling to 3.6 nm: max coordinate deviation 0.176 nm from reference (tolerance is 0.001 nm).
- Partial filtering: 30% removal of slab waters leaves ~300 waters still overlapping.

---

## Researcher B -- Crystal Structure Handling

**Best metric:** 65.0 (iterations 0 and 3)
**Iterations run:** 4
**Approach trajectory:** Rep 1 (65.0) -> rep 1 + force box (50.0, reverted) -> rep 2 + scale (34.5, reverted) -> rep 2 native (65.0)

**Key findings:**
1. Rep selection determines crystal dimensions: rep 1 = 1.712 nm, rep 2 = 3.424 nm.
2. Native crystal dimensions (no scaling) preserve crystal_integrity=100.
3. Forcing box dimensions independently of crystal dims creates geometric mismatch.
4. Water exclusion is a separate problem from crystal integrity -- both must be solved.

**Notable failures:**
- Rep 1 + forced 3.6 nm box: crystal occupies tiny fraction of box, geometric score drops.
- Rep 2 + scaling: crystal_integrity drops to 0 despite being close to target.

---

## Researcher C -- Water Placement Strategy

**Best metric:** 65.0 (iteration 3)
**Iterations run:** 4
**Approach trajectory:** Scale + water everywhere (34.5) -> scale + filter 50% (34.5) -> scale 3.5 + filter 70% (40.5) -> native dims + water everywhere (65.0)

**Key findings:**
1. Partial water filtering does NOT work: 50%, 70% removal still leaves enough waters for slab_exclusion=0.
2. The scoring is strict: -10 points per overlapping water molecule.
3. Switching to native crystal dimensions immediately gives crystal_integrity=100.
4. Water exclusion requires a fundamentally different approach: place water ONLY outside slab z-range.

**Notable failures:**
- 50% filter: ~240 waters remain in slab (score: 0).
- 70% filter: ~130 waters remain (score: still 0).

---

## Cross-Researcher Observations

| Researcher | Best | Crystal Integrity | Slab Exclusion | Key Insight |
|-----------|------|------------------|----------------|-------------|
| A | 65.0 | 100 (rep 3) | 0 | Scaling always breaks crystal |
| B | 65.0 | 100 (native) | 0 | Native dims preserve crystal |
| C | 65.0 | 100 (native) | 0 | Partial filtering fails |

**All researchers hit the same ceiling: 65.0.** The bottleneck is slab_exclusion=0 (water in slab region). No researcher has yet implemented z-exclusive water placement.

**Synthesis for Round 2:** Combine B's insight (native dims) with the need for z-exclusive water placement. The solution requires BOTH: (1) box x,y = crystal x,y, and (2) water placed only in z < z_bot and z > z_top.
