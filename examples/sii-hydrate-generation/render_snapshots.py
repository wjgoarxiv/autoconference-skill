"""
Render 3D molecular structure snapshots from .gro files at different iterations.

Shows how the sII hydrate + water sandwich structure improves over time:
  - Round 1 (bad):  water scattered everywhere, including inside slab region
  - Round 2 (mid):  water partially excluded from slab
  - Final (best):   clean separation, blue slab in middle, red water flanking it

Usage:
    python render_snapshots.py

Outputs:
    snapshot_round1.png
    snapshot_round2.png
    snapshot_final.png
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SLAB_Z_MIN = 0.7879  # nm  (from evaluate.py default)
SLAB_Z_MAX = 4.2121  # nm
N_HYDRATE_ATOMS = 3264  # from reference_crystal.gro line count

HERE = Path(__file__).parent

SNAPSHOTS = [
    {
        "gro": HERE / "iterations" / "R1_A_0.gro",
        "scores": HERE / "iterations" / "R1_A_0_scores.json",
        "label": "Round 1 — Iteration 0",
        "outfile": HERE / "snapshot_round1.png",
    },
    {
        "gro": HERE / "iterations" / "R2_A_2.gro",
        "scores": HERE / "iterations" / "R2_A_2_scores.json",
        "label": "Round 2 — Iteration 2",
        "outfile": HERE / "snapshot_round2.png",
    },
    {
        "gro": HERE / "sii_hydrate_water.gro",
        "scores": None,  # use known values
        "label": "Final Best",
        "outfile": HERE / "snapshot_final.png",
    },
]

# Final score is from R3_A_2 which produced sii_hydrate_water.gro
FINAL_SCORES = {
    "composite": 99.9,
    "details": {"n_water_in_slab": 0},
}


# ---------------------------------------------------------------------------
# rcParams (match visualize.py style)
# ---------------------------------------------------------------------------
def setup_rcparams():
    rcParams["font.family"] = "sans-serif"
    available = {f.name for f in font_manager.fontManager.ttflist}
    if "Pretendard" in available:
        rcParams["font.sans-serif"] = ["Pretendard"]
    elif "Arial" in available:
        rcParams["font.sans-serif"] = ["Arial"]
    rcParams["font.size"] = 13
    rcParams["axes.titlesize"] = 15
    rcParams["axes.titleweight"] = "normal"
    rcParams["axes.titlepad"] = 12


# ---------------------------------------------------------------------------
# .gro parsing
# ---------------------------------------------------------------------------
def parse_gro(filepath: Path):
    """Return list of dicts: {resname, atomname, x, y, z} plus box tuple."""
    text = filepath.read_text()
    lines = text.strip().split("\n")
    natoms = int(lines[1].strip())
    atom_lines = lines[2 : 2 + natoms]
    box_parts = lines[2 + natoms].split()
    box = (float(box_parts[0]), float(box_parts[1]), float(box_parts[2]))

    atoms = []
    for line in atom_lines:
        resname = line[5:10].strip()
        atomname = line[10:15].strip()
        x = float(line[20:28])
        y = float(line[28:36])
        z = float(line[36:44])
        atoms.append({"resname": resname, "atomname": atomname, "x": x, "y": y, "z": z})

    return atoms, box


def split_atoms(atoms):
    """
    Split atoms into hydrate vs water sections.
    Hydrate: all atoms before the first OW/HW1/HW2 atom.
    Water:   OW, HW1, HW2 atoms (added water molecules).
    """
    hydrate = []
    water = []
    in_water = False
    for a in atoms:
        if a["atomname"] in ("OW", "HW1", "HW2"):
            in_water = True
        if in_water:
            water.append(a)
        else:
            hydrate.append(a)
    return hydrate, water


# ---------------------------------------------------------------------------
# Hydrogen bond detection
# ---------------------------------------------------------------------------
def find_hbonds(water_atoms, box, max_dist=0.35, stride=3):
    """
    Return list of (i, j) index pairs for water O atoms within max_dist nm.
    Only considers every `stride`-th oxygen to avoid clutter.
    Uses minimum image convention for PBC.
    """
    ow = [a for a in water_atoms if a["atomname"] == "OW"]
    # Subsample
    ow_sub = ow[::stride]
    coords = np.array([[a["x"], a["y"], a["z"]] for a in ow_sub])
    bx, by, bz = box

    bonds = []
    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            dx = coords[j, 0] - coords[i, 0]
            dy = coords[j, 1] - coords[i, 1]
            dz = coords[j, 2] - coords[i, 2]
            # Minimum image
            dx -= bx * round(dx / bx)
            dy -= by * round(dy / by)
            dz -= bz * round(dz / bz)
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            if dist <= max_dist:
                bonds.append((
                    coords[i],
                    coords[i] + np.array([dx, dy, dz]),
                ))
    return bonds, coords


# ---------------------------------------------------------------------------
# Slab boundary planes
# ---------------------------------------------------------------------------
def draw_slab_planes(ax, box, z_min, z_max, alpha=0.12):
    """Draw semi-transparent horizontal quads at z_min and z_max."""
    bx, by = box[0], box[1]
    xs = [0, bx, bx, 0, 0]
    ys = [0, 0, by, by, 0]

    for z_val in (z_min, z_max):
        zs = [z_val] * 5
        ax.plot(xs, ys, zs, color="#6B7280", linewidth=0.8, alpha=0.5)
        # Filled quad via poly3d
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        verts = [list(zip(
            [0, bx, bx, 0],
            [0, 0, by, by],
            [z_val, z_val, z_val, z_val],
        ))]
        poly = Poly3DCollection(verts, alpha=alpha, facecolor="#9CA3AF", edgecolor="none")
        ax.add_collection3d(poly)


# ---------------------------------------------------------------------------
# Render one snapshot
# ---------------------------------------------------------------------------
def render_snapshot(snap_cfg):
    gro_path = snap_cfg["gro"]
    label = snap_cfg["label"]
    outfile = snap_cfg["outfile"]

    # Load scores
    if snap_cfg["scores"] is not None and Path(snap_cfg["scores"]).exists():
        scores = json.loads(Path(snap_cfg["scores"]).read_text())
    else:
        scores = FINAL_SCORES

    composite = scores.get("composite", 0.0)
    n_in_slab = scores.get("details", {}).get("n_water_in_slab", "?")

    # Parse structure
    atoms, box = parse_gro(gro_path)
    hydrate, water = split_atoms(atoms)

    # Extract O atoms from hydrate (atom names: O, OW, O1, O2 ... anything with 'O')
    # In GenIce2 crystal, atom names are 'O' and 'H'
    hydrate_O = [a for a in hydrate if a["atomname"].startswith("O")]
    water_O = [a for a in water if a["atomname"] == "OW"]
    water_H = [a for a in water if a["atomname"] in ("HW1", "HW2")]

    hyd_O_xyz = np.array([[a["x"], a["y"], a["z"]] for a in hydrate_O]) if hydrate_O else np.empty((0, 3))
    wat_O_xyz = np.array([[a["x"], a["y"], a["z"]] for a in water_O]) if water_O else np.empty((0, 3))

    # H-bonds
    hbond_pairs, ow_sub_coords = find_hbonds(water, box, max_dist=0.35, stride=3)

    # Figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    bx, by, bz = box

    # Hydrate O atoms — blue spheres
    if len(hyd_O_xyz) > 0:
        ax.scatter(
            hyd_O_xyz[:, 0], hyd_O_xyz[:, 1], hyd_O_xyz[:, 2],
            c="#1D4ED8", s=18, alpha=0.75, linewidths=0,
            label=f"Hydrate O ({len(hyd_O_xyz)})",
            depthshade=True,
            zorder=3,
        )

    # Water O atoms — red spheres
    if len(wat_O_xyz) > 0:
        ax.scatter(
            wat_O_xyz[:, 0], wat_O_xyz[:, 1], wat_O_xyz[:, 2],
            c="#DC2626", s=10, alpha=0.70, linewidths=0,
            label=f"Water O ({len(wat_O_xyz)})",
            depthshade=True,
            zorder=4,
        )

    # Hydrogen bonds — thin gray dashed lines
    for (p1, p2) in hbond_pairs:
        ax.plot(
            [p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
            color="#9CA3AF", linewidth=0.5, alpha=0.45, linestyle="--",
            zorder=1,
        )

    # Slab boundary planes
    draw_slab_planes(ax, box, SLAB_Z_MIN, SLAB_Z_MAX, alpha=0.10)

    # Axes and view
    ax.set_xlim(0, bx)
    ax.set_ylim(0, by)
    ax.set_zlim(0, bz)
    ax.set_xlabel("x (nm)", labelpad=8, fontsize=11)
    ax.set_ylabel("y (nm)", labelpad=8, fontsize=11)
    ax.set_zlabel("z (nm)", labelpad=8, fontsize=11)
    ax.tick_params(labelsize=9)

    # Viewing angle: slightly elevated, see the sandwich structure
    ax.view_init(elev=28, azim=-55)

    # Title
    title = (
        f"{label}\n"
        f"Composite: {composite:.1f}  |  "
        f"Waters in slab: {n_in_slab}"
    )
    ax.set_title(title, fontsize=13, pad=14)

    # Legend
    ax.legend(
        loc="upper left",
        fontsize=9,
        frameon=True,
        framealpha=0.85,
        edgecolor="#E5E7EB",
    )

    # Slab boundary annotation
    ax.text(bx * 0.02, by * 0.98, SLAB_Z_MIN, f"z={SLAB_Z_MIN:.2f}", fontsize=7,
            color="#6B7280", ha="left")
    ax.text(bx * 0.02, by * 0.98, SLAB_Z_MAX, f"z={SLAB_Z_MAX:.2f}", fontsize=7,
            color="#6B7280", ha="left")

    plt.tight_layout()
    plt.savefig(outfile, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {outfile}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    setup_rcparams()
    for snap in SNAPSHOTS:
        print(f"Rendering {snap['label']} from {snap['gro'].name} ...")
        render_snapshot(snap)
    print("Done.")


if __name__ == "__main__":
    main()
