"""
Generate sII clathrate hydrate slab + water sandwich .gro file.

Pipeline:
1. Run GenIce2 CS2 to produce reference crystal
2. Parse .gro format, extract atom lines and box vector
3. Center slab in z with uniform translation
4. Place water molecules ONLY outside slab z-bounds
5. Write combined .gro with hydrate atoms first, then water
"""

import argparse
import math
import random
import subprocess
import sys
from pathlib import Path


def run_genice2(rep: str) -> str:
    """Run GenIce2 and return raw stdout."""
    rx, ry, rz = rep.split()
    cmd = ["genice2", "CS2", "--rep", rx, ry, rz, "--format", "gromacs"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"GenIce2 failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_gro(text: str) -> tuple[str, list[str], str]:
    """Parse .gro text into (title, atom_lines, box_line)."""
    lines = text.strip().split("\n")
    title = lines[0]
    natoms = int(lines[1].strip())
    atom_lines = lines[2 : 2 + natoms]
    box_line = lines[2 + natoms]
    return title, atom_lines, box_line


def parse_box(box_line: str) -> tuple[float, float, float]:
    """Parse box vector line -> (x, y, z) in nm."""
    parts = box_line.split()
    return float(parts[0]), float(parts[1]), float(parts[2])


def parse_atom_coords(line: str) -> tuple[float, float, float]:
    """Extract x, y, z from a .gro atom line (fixed-width format)."""
    # .gro format: columns 20-28 x, 28-36 y, 36-44 z (8 chars each, 3 decimals)
    x = float(line[20:28])
    y = float(line[28:36])
    z = float(line[36:44])
    return x, y, z


def shift_atom_z(line: str, dz: float) -> str:
    """Shift z-coordinate of a .gro atom line by dz, preserving formatting."""
    x, y, z = parse_atom_coords(line)
    z_new = z + dz
    # Reconstruct: keep first 36 chars, replace z (8 chars, 3 decimals), keep rest
    prefix = line[:36]
    suffix = line[44:] if len(line) > 44 else ""
    return f"{prefix}{z_new:8.3f}{suffix}"


def generate_water_molecule(
    ox: float, oy: float, oz: float, rng: random.Random
) -> list[tuple[float, float, float]]:
    """Generate OW + HW1 + HW2 positions with tetrahedral geometry."""
    bond_len = 0.09572  # nm (TIP3P O-H bond length)
    angle = 104.52 * math.pi / 180.0  # H-O-H angle

    # Random orientation
    phi = rng.uniform(0, 2 * math.pi)
    theta = rng.uniform(0, math.pi)

    # First H relative to O
    hx1 = bond_len * math.sin(theta) * math.cos(phi)
    hy1 = bond_len * math.sin(theta) * math.sin(phi)
    hz1 = bond_len * math.cos(theta)

    # Second H: rotate by H-O-H angle around a perpendicular axis
    # Use Rodrigues' rotation around z-axis for simplicity, then align
    psi = rng.uniform(0, 2 * math.pi)
    half_angle = angle / 2.0
    # Direction for H2: rotate H1 direction by the bond angle
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # Arbitrary perpendicular vector
    if abs(hx1) < abs(hy1):
        px, py, pz = 0.0, -hz1, hy1
    else:
        px, py, pz = -hz1, 0.0, hx1
    norm_p = math.sqrt(px * px + py * py + pz * pz)
    if norm_p < 1e-10:
        px, py, pz = 0.0, 1.0, 0.0
        norm_p = 1.0
    px /= norm_p
    py /= norm_p
    pz /= norm_p

    # Rodrigues' rotation of (hx1,hy1,hz1) around (px,py,pz) by angle
    dot = hx1 * px + hy1 * py + hz1 * pz
    cx = py * hz1 - pz * hy1
    cy = pz * hx1 - px * hz1
    cz = px * hy1 - py * hx1
    hx2 = hx1 * cos_a + cx * sin_a + px * dot * (1 - cos_a)
    hy2 = hy1 * cos_a + cy * sin_a + py * dot * (1 - cos_a)
    hz2 = hz1 * cos_a + cz * sin_a + pz * dot * (1 - cos_a)

    return [
        (ox, oy, oz),
        (ox + hx1, oy + hy1, oz + hz1),
        (ox + hx2, oy + hy2, oz + hz2),
    ]


def place_waters(
    box_x: float,
    box_y: float,
    box_z: float,
    z_bot: float,
    z_top: float,
    density: float,
    min_dist: float,
    seed: int,
) -> list[list[tuple[float, float, float]]]:
    """Place water molecules in z < z_bot and z > z_top regions."""
    rng = random.Random(seed)

    # Water-only volume in nm^3
    water_vol_bot = box_x * box_y * z_bot  # z from 0 to z_bot
    water_vol_top = box_x * box_y * (box_z - z_top)  # z from z_top to box_z
    water_vol = water_vol_bot + water_vol_top

    # Number of water molecules: density (kg/m^3) -> molecules
    # 1 nm^3 = 1e-24 L = 1e-27 m^3
    # n = density * volume_m3 / molar_mass * avogadro
    molar_mass = 0.018015  # kg/mol
    avogadro = 6.02214076e23
    vol_m3 = water_vol * 1e-27
    n_waters = int(density * vol_m3 / molar_mass * avogadro)

    print(f"  Water volume: {water_vol:.3f} nm^3")
    print(f"  Target water molecules: {n_waters}")

    # Place oxygen atoms with minimum distance check
    margin = 0.05  # nm margin from box edges
    ow_positions = []
    max_attempts = n_waters * 200
    attempts = 0

    while len(ow_positions) < n_waters and attempts < max_attempts:
        attempts += 1
        x = rng.uniform(margin, box_x - margin)
        y = rng.uniform(margin, box_y - margin)

        # Choose bottom or top region proportionally
        if rng.random() < water_vol_bot / water_vol:
            z = rng.uniform(margin, z_bot - margin)
        else:
            z = rng.uniform(z_top + margin, box_z - margin)

        # Check minimum distance against existing OW positions
        too_close = False
        for ox, oy, oz in ow_positions:
            dx = abs(x - ox)
            dy = abs(y - oy)
            dz = abs(z - oz)
            # PBC minimum image for x and y
            dx = min(dx, box_x - dx)
            dy = min(dy, box_y - dy)
            if dx * dx + dy * dy + dz * dz < min_dist * min_dist:
                too_close = True
                break
        if not too_close:
            ow_positions.append((x, y, z))

    print(f"  Placed {len(ow_positions)} water molecules ({attempts} attempts)")

    # Generate full water molecules (O + 2H), wrap into box via PBC
    molecules = []
    for ox, oy, oz in ow_positions:
        mol = generate_water_molecule(ox, oy, oz, rng)
        wrapped = []
        for ax, ay, az in mol:
            ax = ax % box_x
            ay = ay % box_y
            az = az % box_z
            wrapped.append((ax, ay, az))
        molecules.append(wrapped)

    return molecules


def place_waters_full_box(
    box_x: float,
    box_y: float,
    box_z: float,
    z_bot: float,
    z_top: float,
    density: float,
    min_dist: float,
    seed: int,
) -> list[list[tuple[float, float, float]]]:
    """Place water molecules across the FULL box (including slab region).

    Used to simulate the 'water everywhere' mistake in early iterations.
    Uses the same target density applied to the water-only volume for molecule count,
    but distributes them across the entire box z-range.
    """
    rng = random.Random(seed)

    # Compute water count based on water-only volume (same as correct version)
    water_vol_bot = box_x * box_y * z_bot
    water_vol_top = box_x * box_y * (box_z - z_top)
    water_vol = water_vol_bot + water_vol_top
    if water_vol <= 0:
        water_vol = box_x * box_y * box_z  # fallback for edge case

    molar_mass = 0.018015  # kg/mol
    avogadro = 6.02214076e23
    vol_m3 = water_vol * 1e-27
    n_waters = int(density * vol_m3 / molar_mass * avogadro)

    full_vol = box_x * box_y * box_z
    print(f"  Full box volume: {full_vol:.3f} nm^3")
    print(f"  Target water molecules (from water-only vol): {n_waters}")

    margin = 0.05
    ow_positions = []
    max_attempts = n_waters * 200
    attempts = 0

    while len(ow_positions) < n_waters and attempts < max_attempts:
        attempts += 1
        x = rng.uniform(margin, box_x - margin)
        y = rng.uniform(margin, box_y - margin)
        z = rng.uniform(margin, box_z - margin)  # full z-range

        too_close = False
        for ox, oy, oz in ow_positions:
            dx = abs(x - ox)
            dy = abs(y - oy)
            ddz = abs(z - oz)
            dx = min(dx, box_x - dx)
            dy = min(dy, box_y - dy)
            if dx * dx + dy * dy + ddz * ddz < min_dist * min_dist:
                too_close = True
                break
        if not too_close:
            ow_positions.append((x, y, z))

    print(f"  Placed {len(ow_positions)} water molecules ({attempts} attempts)")

    molecules = []
    for ox, oy, oz in ow_positions:
        mol = generate_water_molecule(ox, oy, oz, rng)
        wrapped = []
        for ax, ay, az in mol:
            ax = ax % box_x
            ay = ay % box_y
            az = az % box_z
            wrapped.append((ax, ay, az))
        molecules.append(wrapped)

    return molecules


def format_gro_atom(
    resid: int, resname: str, atomname: str, atomid: int, x: float, y: float, z: float
) -> str:
    """Format a single .gro atom line (fixed-width)."""
    # .gro format: %5d%-5s%5s%5d%8.3f%8.3f%8.3f
    return f"{resid:5d}{resname:<5s}{atomname:>5s}{atomid:5d}{x:8.3f}{y:8.3f}{z:8.3f}"


def main():
    parser = argparse.ArgumentParser(description="Generate sII hydrate + water .gro")
    parser.add_argument("--rep", default="2 2 2", help="GenIce2 rep values (default: '2 2 2')")
    parser.add_argument("--box_z", type=float, default=5.0, help="Total box z in nm (default: 5.0)")
    parser.add_argument(
        "--water_density", type=float, default=1000, help="Water density kg/m^3 (default: 1000)"
    )
    parser.add_argument(
        "--min_dist", type=float, default=0.23, help="Min distance between waters nm (default: 0.23)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--output", default="sii_hydrate_water.gro", help="Output path")
    parser.add_argument(
        "--reference", default="reference_crystal.gro", help="Reference crystal output path"
    )
    # Simulation parameters for intentionally wrong iterations
    parser.add_argument(
        "--scale_xy", type=float, default=1.0, help="Scale factor for x,y coords (1.0 = no scaling)"
    )
    parser.add_argument(
        "--water_in_slab", action="store_true", help="Place water in slab region too (intentionally wrong)"
    )
    parser.add_argument(
        "--water_partial_filter", type=float, default=0.0,
        help="Fraction of slab waters to remove (0=none, 1=all)",
    )
    parser.add_argument(
        "--force_box_xy", type=float, default=0.0,
        help="Force box x,y to this value (0 = use crystal native)",
    )
    parser.add_argument(
        "--z_shift", type=float, default=0.0,
        help="Additional z shift for centering offset error (nm)",
    )
    args = parser.parse_args()

    here = Path(__file__).parent

    # Step 1: Run GenIce2
    print("Running GenIce2...")
    raw_output = run_genice2(args.rep)

    # Step 2: Save reference crystal
    ref_path = here / args.reference
    ref_path.write_text(raw_output)
    print(f"  Saved reference crystal: {ref_path}")

    # Step 3: Parse .gro
    title, atom_lines, box_line = parse_gro(raw_output)
    crystal_x, crystal_y, crystal_z = parse_box(box_line)
    n_hydrate_atoms = len(atom_lines)

    print(f"  Crystal dimensions: {crystal_x:.5f} x {crystal_y:.5f} x {crystal_z:.5f} nm")
    print(f"  Number of hydrate atoms: {n_hydrate_atoms}")

    # Step 4: Determine slab z-bounds after centering
    dz = (args.box_z - crystal_z) / 2.0 + args.z_shift
    z_bot = dz
    z_top = dz + crystal_z

    print(f"  Slab z-range after centering: [{z_bot:.4f}, {z_top:.4f}]")

    # Step 5: Apply uniform z-shift to hydrate atoms
    shifted_lines = []
    for line in atom_lines:
        shifted = shift_atom_z(line, dz)
        shifted_lines.append(shifted)

    # Step 5b: Optionally scale x,y (for simulating crystal deformation in early iterations)
    if args.scale_xy != 1.0:
        print(f"  WARNING: Scaling x,y by {args.scale_xy} (crystal deformation!)")
        scaled_lines = []
        for line in shifted_lines:
            x, y, z = parse_atom_coords(line)
            x_new = x * args.scale_xy
            y_new = y * args.scale_xy
            prefix = line[:20]
            suffix = line[44:] if len(line) > 44 else ""
            scaled_lines.append(f"{prefix}{x_new:8.3f}{y_new:8.3f}{z:8.3f}{suffix}")
        shifted_lines = scaled_lines

    # Step 6: Determine box dimensions
    if args.force_box_xy > 0:
        box_x = args.force_box_xy
        box_y = args.force_box_xy
        print(f"  WARNING: Forcing box x,y to {box_x:.5f} nm (overrides crystal)")
    else:
        box_x = crystal_x
        box_y = crystal_y

    box_z = args.box_z

    # Step 7: Place water molecules
    print("Placing water molecules...")
    if args.water_in_slab:
        print("  WARNING: Placing water in slab region (intentionally wrong)")
        # Place water in the FULL box (no exclusion), then optionally filter some out
        waters = place_waters_full_box(
            box_x, box_y, box_z, z_bot, z_top,
            args.water_density, args.min_dist, args.seed,
        )
        if args.water_partial_filter > 0:
            filtered = []
            filt_rng = random.Random(args.seed + 9999)
            for mol in waters:
                oz = mol[0][2]
                if z_bot <= oz <= z_top:
                    if filt_rng.random() < args.water_partial_filter:
                        continue  # remove this water from slab
                filtered.append(mol)
            print(f"  Filtered {len(waters) - len(filtered)} waters from slab region")
            waters = filtered
    else:
        waters = place_waters(
            box_x, box_y, box_z, z_bot, z_top,
            args.water_density, args.min_dist, args.seed,
        )

    n_water_molecules = len(waters)
    n_water_atoms = n_water_molecules * 3
    total_atoms = n_hydrate_atoms + n_water_atoms

    print(f"  Water molecules: {n_water_molecules}")
    print(f"  Total atoms: {total_atoms}")

    # Step 8: Write final .gro
    out_path = here / args.output
    with open(out_path, "w") as f:
        f.write(f"sII hydrate + water sandwich, box {box_x:.3f} x {box_y:.3f} x {box_z:.3f} nm\n")
        f.write(f"{total_atoms}\n")

        # Hydrate atoms first (shifted but otherwise unchanged from GenIce2)
        for line in shifted_lines:
            f.write(line + "\n")

        # Water atoms
        # Continue residue numbering from hydrate
        # Parse last hydrate residue id
        last_resid = int(shifted_lines[-1][:5]) if shifted_lines else 0
        atom_id = n_hydrate_atoms

        for i, mol in enumerate(waters):
            resid = (last_resid + 1 + i) % 100000  # wrap at 99999
            for j, (ax, ay, az) in enumerate(mol):
                atom_id += 1
                atom_id_wrapped = atom_id % 100000
                if j == 0:
                    aname = "OW"
                elif j == 1:
                    aname = "HW1"
                else:
                    aname = "HW2"
                f.write(format_gro_atom(resid, "SOL", aname, atom_id_wrapped, ax, ay, az) + "\n")

        # Box vector line
        f.write(f"{box_x:12.5f}{box_y:12.5f}{box_z:12.5f}\n")

    print(f"\nOutput: {out_path}")
    print(f"  Box: {box_x:.5f} x {box_y:.5f} x {box_z:.5f} nm")
    print(f"  Hydrate atoms: {n_hydrate_atoms}")
    print(f"  Water molecules: {n_water_molecules}")
    print(f"  Slab z-range: [{z_bot:.4f}, {z_top:.4f}]")


if __name__ == "__main__":
    main()
