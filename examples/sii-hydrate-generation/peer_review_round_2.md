# Peer Review -- Round 2

**Reviewer verdict on each researcher's claims.**

---

## Researcher A -- Progressive Fix

### Claim: Native dims fix crystal_integrity
**Verdict: VALIDATED**
- Confirmed: using GenIce2 native box dimensions (3.42420 nm) preserves all crystal coordinates within 0.001 nm tolerance.

### Claim: Partial water filter 60-90% improves exclusion
**Verdict: CHALLENGED**
- 60% filter: ~170 waters remain in slab -> slab_exclusion=0
- 90% filter: ~35 waters remain in slab -> slab_exclusion=0
- The scoring threshold is strict. Even 1 water in slab costs 10 points. 35 waters = score capped at 0.
- **Lesson: post-hoc filtering cannot guarantee zero overlap.** Must use exclusive placement.

### Claim: Proper z-exclusive placement gives 99.9 composite
**Verdict: VALIDATED**
- Iteration 3 achieves crystal_integrity=100 AND slab_exclusion=100.
- This confirms the solution: native dims + z-exclusive water placement.

---

## Researcher B -- Converging on Solution

### Claim: 3.5 nm box with proper exclusion gives 75.4
**Verdict: VALIDATED**
- Correct: water exclusion works (slab_exclusion=100), but crystal scaling still breaks integrity.
- Geometric improvement from 3.6 to 3.5 is incremental but crystal_integrity remains 0.

### Claim: 3.45 nm gives 78.4
**Verdict: VALIDATED**
- Continued improvement in geometric score. Crystal integrity still 0.
- Demonstrates that crystal_integrity is binary: native dims or nothing.

### Claim: Native dims + exclusion gives 99.9
**Verdict: VALIDATED**
- Both constraints satisfied. The box x,y MUST equal the crystal dimensions exactly.

---

## Researcher C -- Same Convergence Path

### Claim: Intermediate scaling (3.5, 3.45) gives improving scores
**Verdict: VALIDATED**
- Geometric improvement is real but crystal_integrity remains 0 until exact native dims are used.

### Claim: Native dims + exclusion gives 99.9
**Verdict: VALIDATED**
- Independently confirms the same solution as A and B.

---

## Summary

| Researcher | Final Best | Crystal Integrity | Slab Exclusion | Verdict |
|-----------|-----------|------------------|----------------|---------|
| A | 99.9 | 100 | 100 | VALIDATED |
| B | 99.9 | 100 | 100 | VALIDATED |
| C | 99.9 | 100 | 100 | VALIDATED |

**Convergence detected:** All three researchers independently converged on the same solution:
- Box x,y = GenIce2 native crystal dimensions (3.42420 nm)
- Water placed exclusively in z < z_bot and z > z_top
- Both binding constraints satisfied simultaneously

**Validated findings for shared knowledge:**
1. Crystal_integrity is binary: native dims = 100, any scaling = 0.
2. Slab_exclusion requires zero overlap -- no partial filtering works.
3. Water density is naturally accurate when targeting 1000 kg/m^3 in the water-only volume.
