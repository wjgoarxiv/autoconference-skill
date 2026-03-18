# Conference: sII Hydrate + Water .gro Generation

## Goal
Generate a valid sII clathrate hydrate + water `.gro` file with z-axis sandwich geometry: hydrate slab centered, water above and below. Two binding constraints must be satisfied simultaneously:
1. **Crystal integrity**: hydrate coordinates identical to GenIce2 output (no scaling/deformation)
2. **Water exclusion**: zero water molecules in the hydrate slab z-range

## Mode
metric

## Success Metric
- **Metric:** Composite quality score (0-100)
- **Target:** >= 80
- **Direction:** maximize
- **Sub-metrics (6):**
  - Structural correctness (20%): atom count, valid residue names
  - Density accuracy (15%): water density in water-only region vs 1000 kg/m^3
  - Geometric accuracy (15%): box dimensions vs crystal 3.424 x 3.424 x 5.0 nm
  - PBC compliance (10%): all atoms within box bounds
  - Slab exclusion (20%): zero waters in slab z-range
  - Crystal integrity (20%): coordinate diff vs original GenIce2 output (< 0.001 nm)

## Researchers
- **Count:** 3
- **Iterations per round:** 4 (round 1-2), 3 (round 3)
- **Max rounds:** 3

## Search Space
- **Allowed changes:** GenIce2 rep values, box dimensions, water placement strategy, z-filtering, density targeting, coordinate handling
- **Forbidden changes:** GenIce2 crystal structure type (must be CS2/sII), output format (must be .gro)

## Search Space Partitioning
- **Strategy:** free (researchers explore independently)

### Researcher A Focus
Box dimension optimization: scaling crystal to target dimensions, rep selection, box z height tuning.

### Researcher B Focus
Crystal structure handling: rep selection, coordinate preservation, box vector compatibility.

### Researcher C Focus
Water placement strategy: z-range filtering, density targeting, exclusion zone enforcement.

## Constraints
- **Max total iterations:** 33
- **Time budget:** 2h
- GenIce2 CS2 unit cell: 1.7121 nm (cubic, Fd3m space group)
- Rep 2 -> 3.424 nm (chosen for x,y dimensions)
- Crystal coordinates must be IDENTICAL to GenIce2 output (tolerance: 0.001 nm)
- Zero water molecules in hydrate slab z-range
- Box x,y must equal crystal dimensions (not arbitrary target)

## Current Approach
Pipeline: GenIce2 -> parse .gro -> center slab in z -> place water outside slab -> merge + write.

Known pitfalls:
- Scaling crystal to fit arbitrary box dimensions destroys crystal structure
- Placing water without z-filtering creates overlap with slab
- Using wrong rep gives wrong crystal dimensions

## Shared Knowledge

### Round 1 Validated Findings
1. **Crystal scaling destroys integrity.** Scaling x,y coords by any factor != 1.0 makes coordinates diverge from GenIce2 reference, yielding crystal_integrity=0.
2. **Water must be z-excluded.** Placing water in the full box puts ~430 water molecules in the slab region, yielding slab_exclusion=0.
3. **Native crystal dimensions are mandatory.** Box x,y must be 3.42420 nm (from GenIce2 rep 2), not an arbitrary target like 3.6 nm.
4. **Both constraints are independent.** Fixing crystal dims alone still yields slab_exclusion=0; fixing water exclusion alone still yields crystal_integrity=0 if scaling.
5. **Partial water filtering is insufficient.** Even 90% removal of slab waters leaves enough to score slab_exclusion=0.

### Round 2 Validated Findings
6. **Native dims + proper z-exclusion = near-perfect scores.** When both constraints are met, composite reaches 99.9.
7. **Intermediate scaling (3.45, 3.5) improves geometric but not crystal_integrity.** Any deviation from native dims yields crystal_integrity=0.
8. **Water density is self-regulating.** Target density of 1000 kg/m^3 in water-only volume yields accurate results regardless of seed.

## Context & References
- GenIce2: `genice2 CS2 --rep 2 2 2 --format gromacs` -> 3264 atoms, box 3.42420 nm
- sII clathrate hydrate: Fd3m space group, cubic unit cell 1.7121 nm
- .gro format: GROMACS coordinate file, fixed-width columns
- Water placement: random with minimum distance check (0.23 nm), TIP3P geometry

---

## Conference Log
| Round | Researcher | Best Metric | Key Finding | Status |
|-------|-----------|-------------|-------------|--------|
| 1 | A | 40.5 | Crystal scaling to 3.5 nm: integrity=0, exclusion=0 | challenged |
| 1 | B | 65.0 | Native dims + water everywhere: integrity=100, exclusion=0 | challenged |
| 1 | C | 65.0 | Native dims + water in slab: integrity=100, exclusion=0 | challenged |
| 2 | A | 99.9 | Native dims + proper z-exclusion: both constraints met | validated |
| 2 | B | 99.9 | Native dims + proper z-exclusion: both constraints met | validated |
| 2 | C | 99.9 | Native dims + proper z-exclusion: both constraints met | validated |
| 3 | ALL | 99.9 | **CONVERGED** -- all researchers at 99.9, both constraints satisfied | converged |
