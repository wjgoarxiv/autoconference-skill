# Poster Session -- Round 2

**Baseline (from Round 1):** Best composite 65.0 (native dims, water in slab)
**Target:** Composite >= 80

---

## Researcher A -- Progressive Constraint Fixing

**Best metric:** 99.9 (iteration 3)
**Iterations run:** 4
**Approach trajectory:** Native dims + water in slab (65.0) -> filter 60% (65.0) -> filter 90% (65.0) -> proper z-exclusion (99.9)

**Key findings:**
1. Native crystal dimensions are now established as mandatory (from Round 1 peer review).
2. Partial filtering at 60% and even 90% fails to clear the slab. The scoring is strict.
3. Only z-exclusive water placement (generating water only outside slab z-range) achieves slab_exclusion=100.
4. When both constraints are met simultaneously, composite jumps from 65 to 99.9.

---

## Researcher B -- Converging from Geometry Side

**Best metric:** 99.9 (iteration 2)
**Iterations run:** 4
**Approach trajectory:** Scale 3.5 + exclusion (75.4) -> scale 3.45 + exclusion (78.4) -> native + exclusion (99.9) -> density tuning (99.8, reverted)

**Key findings:**
1. Water exclusion works even with wrong box dims -- slab_exclusion=100 at all scales.
2. Crystal_integrity is binary: 3.45 nm = 0, 3.42420 nm = 100. No interpolation.
3. The approach of gradually reducing scaling converges to native dims as the only solution.
4. Density tuning (998 vs 1000 kg/m^3) has minimal effect -- 0.1 point difference.

---

## Researcher C -- Same Convergence

**Best metric:** 99.9 (iteration 2)
**Iterations run:** 4
**Approach trajectory:** Scale 3.5 + exclusion (75.4) -> scale 3.45 + exclusion (78.4) -> native + exclusion (99.9) -> confirm (99.9)

**Key findings:**
1. Mirrors Researcher B's path -- independently confirms the binary nature of crystal_integrity.
2. Z-exclusive water placement is robust across different random seeds.

---

## Cross-Researcher Observations

| Researcher | Best | Crystal Integrity | Slab Exclusion | Path to Solution |
|-----------|------|------------------|----------------|------------------|
| A | 99.9 | 100 | 100 | Fixed dims first, then fixed water placement |
| B | 99.9 | 100 | 100 | Fixed water first, then converged to native dims |
| C | 99.9 | 100 | 100 | Fixed water first, then converged to native dims |

**All researchers achieved target.** Convergence confirmed.

**Key Round 2 insight:** The two constraints have different fix characteristics:
- **Crystal integrity:** Binary switch (native dims = 100, anything else = 0)
- **Slab exclusion:** Also binary in practice (z-exclusive = 100, any overlap = 0 due to strict scoring)

Both must be satisfied simultaneously. There is no partial-credit path.
