# Peer Review -- Round 1

**Reviewer verdict on each researcher's claims.**

---

## Researcher A -- Crystal Scaling Approach

### Claim: Scaling crystal to 3.5 nm gives composite 40.5
**Verdict: CHALLENGED**
- Crystal scaling by any factor != 1.0 fundamentally breaks the Fd3m space group symmetry.
- GenIce2 produces coordinates on a precise cubic lattice with 1.712 nm periodicity. Multiplying x,y by 1.022 (for 3.5 nm) shifts every atom away from its crystallographic position.
- crystal_integrity=0 is the correct evaluation -- the reference diff shows max deviation of 0.076 nm, far exceeding the 0.001 nm tolerance.
- **Critical finding: crystal dimensions are NOT a free parameter.** Box x,y must equal the GenIce2 output dimensions exactly.

### Claim: Rep 3 3 2 gives crystal_integrity=100
**Verdict: CHALLENGED (partially)**
- True that no scaling preserves crystal integrity. But rep 3 gives x,y = 5.136 nm, which is a completely different crystal system than the target.
- The geometric score suffers because box dimensions don't match the target 3.424 nm.
- Recommendation: Use rep 2 2 2 (3.424 nm) and accept that box x,y = 3.424, not 3.6.

### Issue: Water placement
**Verdict: CHALLENGED**
- All iterations place water in the full box without z-filtering.
- 400+ water molecules overlap with the hydrate slab region.
- slab_exclusion=0 for all iterations -- this is a fundamental design flaw, not a tuning issue.
- Partial filtering (30%) is insufficient. Must redesign water placement to exclude slab z-range entirely.

---

## Researcher B -- Rep Selection

### Claim: Rep 1 gives crystal_integrity=100
**Verdict: CHALLENGED**
- Technically true: no scaling is applied, so coordinates match reference.
- But rep 1 gives a 1.712 nm crystal in a box that should be 3.424 nm. The crystal doesn't fill the periodic box correctly.
- Geometric score suffers. This is a valid exploration but not a viable solution.

### Claim: Native dims (rep 2) preserves crystal
**Verdict: VALIDATED**
- Correct insight: rep 2 2 2 with native box dimensions preserves crystal_integrity=100.
- This is the key breakthrough direction -- crystal dimensions are dictated by GenIce2.

### Issue: Water placement
**Verdict: CHALLENGED**
- Same issue as Researcher A: water placed in full box without z-filtering.
- Must implement z-exclusive water placement.

---

## Researcher C -- Partial Water Filtering

### Claim: Partial filtering (50-70%) improves slab_exclusion
**Verdict: CHALLENGED**
- slab_exclusion scoring is harsh: -10 points per overlapping water molecule.
- With 400+ waters in slab, even 70% removal leaves ~130 waters: score = max(0, 100 - 1300) = 0.
- Partial filtering is a dead-end strategy. Need 100% exclusion from placement logic.

### Claim: Native dims gives crystal_integrity=100 (iteration 3)
**Verdict: VALIDATED**
- Correct. Stopping the scaling immediately fixes crystal integrity.
- Combined with proper water exclusion, this would solve both constraints.

---

## Summary

| Researcher | Best | Crystal Integrity | Slab Exclusion | Verdict |
|-----------|------|------------------|----------------|---------|
| A | 65.0 | 100 (rep 3 only) | 0 (all iters) | CHALLENGED |
| B | 65.0 | 100 (native dims) | 0 (all iters) | CHALLENGED |
| C | 65.0 | 100 (native dims) | 0 (all iters) | CHALLENGED |

**Critical findings for Round 2:**
1. **Crystal scaling is forbidden.** Box x,y = crystal x,y = 3.424 nm. Non-negotiable.
2. **Water must be z-excluded.** Place water ONLY in z < z_bot and z > z_top. No partial filtering.
3. **Both constraints are binding.** Must solve both simultaneously to reach target composite >= 80.
