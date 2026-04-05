"""
Evaluate sII hydrate + water .gro quality with 6 sub-metrics.

Usage:
    python evaluate.py output.gro --reference reference_crystal.gro \
        --slab_z_min 0.788 --slab_z_max 4.212
"""

import argparse
import json
import sys
from pathlib import Path


def parse_gro(filepath: str) -> tuple[str, list[str], tuple[float, float, float]]:
    """Parse a .gro file -> (title, atom_lines, (box_x, box_y, box_z))."""
    text = Path(filepath).read_text()
    lines = text.strip().split("\n")
    title = lines[0]
    natoms = int(lines[1].strip())
    atom_lines = lines[2 : 2 + natoms]
    box_parts = lines[2 + natoms].split()
    box = (float(box_parts[0]), float(box_parts[1]), float(box_parts[2]))
    return title, atom_lines, box


def parse_coords(line: str) -> tuple[float, float, float]:
    """Extract x, y, z from a .gro atom line."""
    return float(line[20:28]), float(line[28:36]), float(line[36:44])


def parse_resname(line: str) -> str:
    """Extract residue name from .gro atom line."""
    return line[5:10].strip()


def parse_atomname(line: str) -> str:
    """Extract atom name from .gro atom line."""
    return line[10:15].strip()


def score_structural(atom_lines: list[str]) -> tuple[float, dict]:
    """Sub-metric 1: Structural correctness (20%)."""
    n_total = len(atom_lines)
    hydrate_atoms = []
    water_atoms = []
    valid_hydrate_resnames = {"SOL", "ICE", "CS2"}  # GenIce2 uses SOL for water in crystal
    water_resnames = {"SOL"}

    # Separate by position in file and atom names
    # Hydrate atoms come first (from GenIce2), water atoms after (OW, HW1, HW2)
    in_water_section = False
    for line in atom_lines:
        aname = parse_atomname(line)
        if aname in ("OW", "HW1", "HW2"):
            in_water_section = True
            water_atoms.append(line)
        elif not in_water_section:
            hydrate_atoms.append(line)
        else:
            water_atoms.append(line)

    n_hydrate = len(hydrate_atoms)
    n_water = len(water_atoms)

    # Score: expect > 0 hydrate atoms, > 0 water atoms, reasonable counts
    score = 100.0
    if n_hydrate == 0:
        score -= 50.0
    if n_water == 0:
        score -= 30.0
    # Water should be in multiples of 3 (O + 2H)
    if n_water % 3 != 0:
        score -= 20.0

    details = {
        "n_hydrate_atoms": n_hydrate,
        "n_water_atoms": n_water,
        "n_water_molecules": n_water // 3 if n_water % 3 == 0 else n_water / 3,
    }
    return max(0.0, score), details


def score_density(
    atom_lines: list[str],
    box: tuple[float, float, float],
    z_min: float,
    z_max: float,
) -> tuple[float, dict]:
    """Sub-metric 2: Water density in water-only region (15%)."""
    # Count water oxygens in water region
    n_ow = 0
    for line in atom_lines:
        aname = parse_atomname(line)
        if aname == "OW":
            _, _, z = parse_coords(line)
            if z < z_min or z > z_max:
                n_ow += 1

    # Water volume
    box_x, box_y, box_z = box
    water_vol_nm3 = box_x * box_y * (z_min + (box_z - z_max))

    if water_vol_nm3 <= 0:
        return 0.0, {"water_density_kg_m3": 0.0, "n_water_in_water_region": n_ow}

    # Density: n_molecules * molar_mass / (avogadro * volume_m3)
    molar_mass = 0.018015  # kg/mol
    avogadro = 6.02214076e23
    vol_m3 = water_vol_nm3 * 1e-27
    density = n_ow * molar_mass / (avogadro * vol_m3)

    # Score: 100 if within 5% of 1000 kg/m^3, linear penalty
    target = 1000.0
    deviation = abs(density - target) / target * 100  # percent
    score = max(0.0, 100.0 - deviation * 4)  # -4 points per 1% deviation

    return score, {"water_density_kg_m3": round(density, 1), "n_water_in_water_region": n_ow}


def score_geometric(
    box: tuple[float, float, float],
    crystal_x: float,
    crystal_y: float,
    target_z: float,
) -> tuple[float, dict]:
    """Sub-metric 3: Geometric accuracy (15%)."""
    box_x, box_y, box_z = box
    score = 100.0

    # x,y should match crystal dims
    dx = abs(box_x - crystal_x)
    dy = abs(box_y - crystal_y)
    dz = abs(box_z - target_z)

    # Penalty: -20 per 0.1 nm deviation in x,y; -10 per 0.1 nm in z
    score -= dx / 0.1 * 20
    score -= dy / 0.1 * 20
    score -= dz / 0.1 * 10

    return max(0.0, score), {
        "box": [round(box_x, 5), round(box_y, 5), round(box_z, 5)],
        "crystal_xy": [round(crystal_x, 5), round(crystal_y, 5)],
        "deviations": [round(dx, 5), round(dy, 5), round(dz, 5)],
    }


def score_pbc(
    atom_lines: list[str], box: tuple[float, float, float]
) -> tuple[float, dict]:
    """Sub-metric 4: PBC compliance (10%)."""
    box_x, box_y, box_z = box
    n_outside = 0
    for line in atom_lines:
        x, y, z = parse_coords(line)
        # Tolerance: 0.05 nm accounts for GenIce2 crystal H atoms slightly
        # outside the unit cell boundary (normal for periodic crystals)
        tol = 0.05
        if x < -tol or x > box_x + tol or y < -tol or y > box_y + tol or z < -tol or z > box_z + tol:
            n_outside += 1

    score = max(0.0, 100.0 - n_outside * 0.5)
    return score, {"n_atoms_outside_box": n_outside}


def score_slab_exclusion(
    atom_lines: list[str], z_min: float, z_max: float
) -> tuple[float, dict]:
    """Sub-metric 5: Slab exclusion (20%) — no water in slab region."""
    n_water_in_slab = 0
    for line in atom_lines:
        aname = parse_atomname(line)
        if aname == "OW":
            _, _, z = parse_coords(line)
            if z_min <= z <= z_max:
                n_water_in_slab += 1

    score = max(0.0, 100.0 - n_water_in_slab * 10)
    return score, {"n_water_in_slab": n_water_in_slab}


def score_crystal_integrity(
    atom_lines: list[str], ref_atom_lines: list[str], dz: float
) -> tuple[float, dict]:
    """Sub-metric 6: Crystal integrity (20%) — hydrate coords match reference."""
    # Extract hydrate atoms from output (before water section)
    hydrate_lines = []
    for line in atom_lines:
        aname = parse_atomname(line)
        if aname in ("OW", "HW1", "HW2"):
            break
        hydrate_lines.append(line)

    n_hydrate = len(hydrate_lines)
    n_ref = len(ref_atom_lines)

    if n_hydrate != n_ref:
        return 0.0, {
            "max_coord_deviation_nm": 999.0,
            "n_hydrate": n_hydrate,
            "n_ref": n_ref,
            "mismatch": "atom_count",
        }

    max_dev = 0.0
    for out_line, ref_line in zip(hydrate_lines, ref_atom_lines):
        ox, oy, oz = parse_coords(out_line)
        rx, ry, rz = parse_coords(ref_line)
        # Reference coords are shifted by dz for comparison
        rz_shifted = rz + dz
        dev = max(abs(ox - rx), abs(oy - ry), abs(oz - rz_shifted))
        if dev > max_dev:
            max_dev = dev

    # Score: 100 if max_dev < 0.001 nm, else penalize heavily
    if max_dev < 0.001:
        score = 100.0
    else:
        score = max(0.0, 100.0 - max_dev * 10000)

    return score, {"max_coord_deviation_nm": round(max_dev, 6)}


def main():
    parser = argparse.ArgumentParser(description="Evaluate sII hydrate .gro quality")
    parser.add_argument("gro_file", help="Path to .gro file to evaluate")
    parser.add_argument("--reference", required=True, help="Path to reference crystal .gro")
    parser.add_argument("--slab_z_min", type=float, required=True, help="Slab z minimum (nm)")
    parser.add_argument("--slab_z_max", type=float, required=True, help="Slab z maximum (nm)")
    parser.add_argument("--target_z", type=float, default=5.0, help="Target box z (nm)")
    parser.add_argument("--json_output", default=None, help="Path to write JSON results")
    parser.add_argument("--threshold", type=float, default=0.0, help="Pass threshold for composite score")
    args = parser.parse_args()

    # Parse files
    _, atom_lines, box = parse_gro(args.gro_file)
    _, ref_atom_lines, ref_box = parse_gro(args.reference)
    ref_crystal_x, ref_crystal_y, ref_crystal_z = ref_box

    # Compute expected z-shift
    dz = (args.target_z - ref_crystal_z) / 2.0

    # Run all sub-metrics
    s_structural, d_structural = score_structural(atom_lines)
    s_density, d_density = score_density(atom_lines, box, args.slab_z_min, args.slab_z_max)
    s_geometric, d_geometric = score_geometric(box, ref_crystal_x, ref_crystal_y, args.target_z)
    s_pbc, d_pbc = score_pbc(atom_lines, box)
    s_exclusion, d_exclusion = score_slab_exclusion(atom_lines, args.slab_z_min, args.slab_z_max)
    s_integrity, d_integrity = score_crystal_integrity(atom_lines, ref_atom_lines, dz)

    # Weighted composite
    composite = (
        s_structural * 0.20
        + s_density * 0.15
        + s_geometric * 0.15
        + s_pbc * 0.10
        + s_exclusion * 0.20
        + s_integrity * 0.20
    )

    result = {
        "pass": composite >= args.threshold,
        "score": round(composite, 1),
        "composite": round(composite, 1),
        "structural": round(s_structural, 1),
        "density": round(s_density, 1),
        "geometric": round(s_geometric, 1),
        "pbc": round(s_pbc, 1),
        "slab_exclusion": round(s_exclusion, 1),
        "crystal_integrity": round(s_integrity, 1),
        "details": {
            "natoms": len(atom_lines),
            "n_hydrate_atoms": d_structural["n_hydrate_atoms"],
            "n_waters": d_structural.get("n_water_molecules", 0),
            "n_water_in_slab": d_exclusion["n_water_in_slab"],
            "max_coord_deviation_nm": d_integrity.get("max_coord_deviation_nm", 999.0),
            "box": d_geometric["box"],
            "slab_z_range": [args.slab_z_min, args.slab_z_max],
            "water_density_kg_m3": d_density["water_density_kg_m3"],
        },
    }

    print(json.dumps(result, indent=2))

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    main()
