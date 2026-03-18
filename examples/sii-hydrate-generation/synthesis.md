# Synthesis: sII Hydrate + Water Generation Conference

## Unified Finding

The conference explored approaches to generating a valid sII clathrate hydrate + water .gro file with z-axis sandwich geometry. Three researchers independently converged on the same solution after discovering two binding constraints:

1. **Crystal integrity** requires using GenIce2's native box dimensions (3.42420 nm for rep 2)
2. **Water exclusion** requires placing water molecules only outside the slab z-range

Both constraints are binary in practice: satisfying them yields near-perfect scores; violating either yields composite < 70.

## The Two-Constraint Problem

The central insight from this conference is that generating a valid hydrate-water interface requires satisfying two **independent, simultaneously binding constraints**:

| Constraint | What It Demands | What Breaks It |
|-----------|----------------|----------------|
| Crystal integrity | Hydrate coords identical to GenIce2 reference | ANY coordinate scaling or deformation |
| Water exclusion | Zero water molecules in slab z-range | Water placement without z-filtering |

### Why Both Are Binding

Each constraint alone is easy to satisfy:
- Crystal integrity: just don't scale (use native dims) -- easy
- Water exclusion: just filter by z-range -- easy

But naive approaches typically violate BOTH because:
1. Researchers assume they can choose box dimensions freely -> they scale the crystal -> crystal_integrity=0
2. Researchers place water in the full box -> water overlaps with slab -> slab_exclusion=0

The difficulty is recognizing that these two constraints exist and must be addressed simultaneously.

## Convergence Path

### Phase 1: Discovery (Round 1)
All researchers started with naive approaches that violated both constraints:
- **Crystal scaling:** Multiplying coordinates to fit a 3.6 nm target box. This is natural -- you have a target, the crystal doesn't match, so you scale. But it destroys the Fd3m lattice symmetry.
- **Water everywhere:** Placing water in the full simulation box. This is the default -- you want water, you fill the box. But the slab region must be excluded.

Best composite in Round 1: 65.0 (native dims but water in slab).

### Phase 2: Partial Fixes (Round 2, early iterations)
After peer review flagged both issues, researchers tried partial fixes:
- Fix crystal dims but not water -> crystal_integrity=100, slab_exclusion=0 -> composite=65
- Fix water exclusion but not crystal -> slab_exclusion=100, crystal_integrity=0 -> composite=75-78
- Partial water filtering (60-90%) -> insufficient, scoring is strict

### Phase 3: Full Solution (Round 2, late iterations)
All researchers independently arrived at the same solution:
- Box x,y = GenIce2 crystal dimensions (3.42420 nm) -- read from GenIce2 output
- Water placed ONLY in z < z_bot and z > z_top -- designed into placement algorithm
- Composite: 99.9

## Why 99.9 and Not 100.0?

The 0.1 gap comes from water density: random placement of 617 molecules targets 1000 kg/m^3 but achieves ~999.0 due to the discrete nature of molecule placement. This is a physical accuracy limit, not an algorithmic deficiency.

## Anti-Patterns Discovered

1. **Crystal scaling** -- Never scale crystallographic coordinates to fit a target box. The crystal defines the box, not the other way around.
2. **Post-hoc water filtering** -- Partial removal of overlapping waters is unreliable. Design the placement to exclude the slab region from the start.
3. **Independent box dimension choice** -- Box x,y are not free parameters. They are determined by the crystal's periodicity.
4. **Gradual convergence to native dims** -- Researchers tried 3.6, 3.5, 3.45, then finally 3.42420. Crystal_integrity is binary: it's either native or broken.

## Recommendations

1. **Always read box dimensions from GenIce2 output.** Do not compute them independently.
2. **Design water placement with z-exclusion from the start.** The slab z-range is known before water placement begins.
3. **Save the GenIce2 reference for validation.** The crystal integrity check requires comparing against the original output.
4. **Use uniform z-translation only.** Centering the slab in the box is a pure translation -- it preserves all interatomic distances and crystal symmetry.
