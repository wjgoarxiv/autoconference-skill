"""
Render 3D molecular snapshots using py3Dmol + Selenium headless Chrome.

Produces orthographic, side-view PNG snapshots showing sII hydrate (blue)
and water (red) with H-bond cylinders and translucent slab boundary planes.

Usage:
    python render_snapshots_3dmol.py

Outputs:
    snapshot_round1.png   (R1_A_0.gro  -- early: water everywhere)
    snapshot_round2.png   (R2_A_2.gro  -- middle: partial improvement)
    snapshot_final.png    (sii_hydrate_water.gro -- clean separation)
"""

import json
import math
import os
import re
import tempfile
import time
from pathlib import Path

import numpy as np
import py3Dmol
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SLAB_Z_MIN = 0.7879  # nm
SLAB_Z_MAX = 4.2121  # nm
N_HYDRATE_ATOMS = 3264
NM_TO_ANG = 10.0  # 1 nm = 10 Angstroms
HBOND_CUTOFF_NM = 0.35

HERE = Path(__file__).parent

SNAPSHOTS = [
    {
        "gro": HERE / "iterations" / "R1_A_0.gro",
        "scores": HERE / "iterations" / "R1_A_0_scores.json",
        "label": "Round 1 -- Iteration 0",
        "outfile": HERE / "snapshot_round1.png",
    },
    {
        "gro": HERE / "iterations" / "R2_A_2.gro",
        "scores": HERE / "iterations" / "R2_A_2_scores.json",
        "label": "Round 2 -- Iteration 6",
        "outfile": HERE / "snapshot_round2.png",
    },
    {
        "gro": HERE / "sii_hydrate_water.gro",
        "scores": None,
        "label": "Final Best",
        "outfile": HERE / "snapshot_final.png",
    },
]

FINAL_SCORES = {
    "composite": 99.9,
    "details": {"n_water_in_slab": 0},
}


# ---------------------------------------------------------------------------
# .gro parsing
# ---------------------------------------------------------------------------
def parse_gro(filepath):
    """Parse a .gro file. Returns (atoms_list, box_nm).

    Each atom: {resname, atomname, x, y, z} in nm.
    box_nm: (bx, by, bz) in nm.
    """
    text = Path(filepath).read_text()
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
        atoms.append({
            "resname": resname,
            "atomname": atomname,
            "x": x,
            "y": y,
            "z": z,
        })

    return atoms, box


def split_hydrate_water(atoms):
    """Split atoms into hydrate (first N_HYDRATE_ATOMS) and water (rest)."""
    hydrate = atoms[:N_HYDRATE_ATOMS]
    water = atoms[N_HYDRATE_ATOMS:]
    return hydrate, water


# ---------------------------------------------------------------------------
# XYZ generation for py3Dmol
# ---------------------------------------------------------------------------
def atoms_to_xyz(atoms, nm_to_ang=True):
    """Convert atom list to XYZ format string.

    Maps .gro atom names to element symbols:
      O, OW -> O
      H, HW1, HW2 -> H
    """
    scale = NM_TO_ANG if nm_to_ang else 1.0
    elem_map = {"O": "O", "H": "H", "OW": "O", "HW1": "H", "HW2": "H"}

    lines = [str(len(atoms)), ""]
    for a in atoms:
        elem = elem_map.get(a["atomname"], a["atomname"][0])
        lines.append(
            f"{elem} {a['x'] * scale:.4f} {a['y'] * scale:.4f} {a['z'] * scale:.4f}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# H-bond detection (water O--O within cutoff, with PBC minimum image)
# ---------------------------------------------------------------------------
def find_hbond_pairs(water_atoms, box_nm, cutoff_nm=HBOND_CUTOFF_NM, stride=3):
    """Find water O--O pairs within cutoff. Returns list of (xyz1, xyz2) in Angstroms.

    Uses stride to subsample O atoms for performance/clarity.
    """
    ow_atoms = [a for a in water_atoms if a["atomname"] == "OW"]
    ow_sub = ow_atoms[::stride]
    bx, by, bz = box_nm

    pairs = []
    n = len(ow_sub)
    for i in range(n):
        ai = ow_sub[i]
        for j in range(i + 1, n):
            aj = ow_sub[j]
            dx = aj["x"] - ai["x"]
            dy = aj["y"] - ai["y"]
            dz = aj["z"] - ai["z"]
            # Minimum image convention
            dx -= bx * round(dx / bx)
            dy -= by * round(dy / by)
            dz -= bz * round(dz / bz)
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            if dist <= cutoff_nm:
                # Store in Angstroms
                s = NM_TO_ANG
                pairs.append((
                    {"x": ai["x"] * s, "y": ai["y"] * s, "z": ai["z"] * s},
                    {"x": (ai["x"] + dx) * s, "y": (ai["y"] + dy) * s, "z": (ai["z"] + dz) * s},
                ))
    return pairs


# ---------------------------------------------------------------------------
# Build py3Dmol view
# ---------------------------------------------------------------------------
def build_view(atoms, box_nm, hbond_pairs):
    """Create a py3Dmol view with styled hydrate, water, H-bonds, and slab planes."""
    bx_a = box_nm[0] * NM_TO_ANG
    by_a = box_nm[1] * NM_TO_ANG
    slab_zmin_a = SLAB_Z_MIN * NM_TO_ANG
    slab_zmax_a = SLAB_Z_MAX * NM_TO_ANG

    hydrate, water = split_hydrate_water(atoms)

    view = py3Dmol.view(width=1600, height=1600)
    view.setBackgroundColor("white")

    # Add hydrate model (index 0)
    hydrate_xyz = atoms_to_xyz(hydrate)
    view.addModel(hydrate_xyz, "xyz")

    # Add water model (index 1)
    water_xyz = atoms_to_xyz(water)
    view.addModel(water_xyz, "xyz")

    # Style hydrate: blue spheres for O, small light-blue for H
    view.setStyle({"model": 0, "elem": "O"}, {"sphere": {"radius": 0.6, "color": "#1D4ED8"}})
    view.setStyle({"model": 0, "elem": "H"}, {"sphere": {"radius": 0.25, "color": "#60A5FA"}})

    # Style water: red spheres for O, white small for H
    view.setStyle({"model": 1, "elem": "O"}, {"sphere": {"radius": 0.35, "color": "#DC2626"}})
    view.setStyle({"model": 1, "elem": "H"}, {"sphere": {"radius": 0.15, "color": "#F5F5F5"}})

    # H-bond cylinders (thin gray)
    for p1, p2 in hbond_pairs:
        view.addCylinder({
            "start": p1,
            "end": p2,
            "radius": 0.04,
            "color": "#9CA3AF",
            "opacity": 0.4,
            "fromCap": False,
            "toCap": False,
        })

    # Slab boundary planes as thin translucent boxes
    plane_thickness = 0.15  # Angstroms
    for z_val in (slab_zmin_a, slab_zmax_a):
        view.addBox({
            "center": {"x": bx_a / 2, "y": by_a / 2, "z": z_val},
            "dimensions": {"w": bx_a, "h": by_a, "d": plane_thickness},
            "color": "#6B7280",
            "opacity": 0.18,
        })

    # Orthographic projection
    view.setProjection("orthographic")

    # Zoom to fit all atoms
    view.zoomTo()

    return view


# ---------------------------------------------------------------------------
# HTML wrapping and Selenium screenshot
# ---------------------------------------------------------------------------
def make_full_html(view, title_text):
    """Wrap py3Dmol HTML in a full page with title overlay and side-view rotation."""
    inner_html = view._make_html()

    # Extract the viewer variable name from the generated HTML.
    # py3Dmol generates: var viewer_NNNNN = $3Dmol.createViewer(...)
    match = re.search(r"var (viewer_\d+)\s*=", inner_html)
    viewer_var = match.group(1) if match else None

    # After 3Dmol renders, rotate 90 deg around x so z-axis appears vertical
    # (side view of the sandwich).
    rotate_js = ""
    if viewer_var:
        rotate_js = f"""
        <script>
        setTimeout(function() {{
            if (typeof {viewer_var} !== 'undefined') {{
                {viewer_var}.rotate(90, 'x');
                {viewer_var}.zoomTo();
                {viewer_var}.render();
            }}
        }}, 2000);
        </script>
        """

    title_div = f"""
    <div style="position:absolute; top:12px; left:50%; transform:translateX(-50%);
                font-family: Arial, Helvetica, sans-serif; font-size:18px;
                color:#111827; background:rgba(255,255,255,0.88);
                padding:6px 16px; border-radius:6px; z-index:100;
                text-align:center; pointer-events:none;">
        {title_text}
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; background:white; overflow:hidden; }}
  #container {{ position:relative; width:1600px; height:1600px; margin:0 auto; }}
</style>
</head>
<body>
<div id="container">
{title_div}
{inner_html}
</div>
{rotate_js}
</body>
</html>"""
    return full_html


def screenshot_html(html_content, output_png, wait_seconds=5):
    """Save an HTML string as PNG via headless Chrome with WebGL support."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        f.write(html_content)
        html_path = f.name

    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--window-size=1600,1600")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--enable-webgl")
        opts.add_argument("--use-gl=angle")
        opts.add_argument("--enable-unsafe-swiftshader")
        opts.add_argument("--force-device-scale-factor=1")

        driver = webdriver.Chrome(options=opts)
        driver.get(f"file://{html_path}")
        time.sleep(wait_seconds)
        driver.save_screenshot(str(output_png))
        driver.quit()
        print(f"  Screenshot saved: {output_png}")
    finally:
        os.unlink(html_path)


# ---------------------------------------------------------------------------
# Render one snapshot
# ---------------------------------------------------------------------------
def render_snapshot(snap_cfg):
    """Parse .gro, build py3Dmol view, screenshot to PNG."""
    gro_path = snap_cfg["gro"]
    outfile = snap_cfg["outfile"]
    label = snap_cfg["label"]

    # Load scores for title
    if snap_cfg["scores"] is not None and Path(snap_cfg["scores"]).exists():
        scores = json.loads(Path(snap_cfg["scores"]).read_text())
    else:
        scores = FINAL_SCORES

    composite = scores.get("composite", 0.0)
    n_in_slab = scores.get("details", {}).get("n_water_in_slab", "?")

    title_text = (
        f"{label} &nbsp;|&nbsp; Composite: {composite:.1f}"
        f" &nbsp;|&nbsp; Waters in slab: {n_in_slab}"
    )

    # Parse
    atoms, box = parse_gro(gro_path)

    # H-bonds (water only)
    _, water = split_hydrate_water(atoms)
    hbond_pairs = find_hbond_pairs(water, box, cutoff_nm=HBOND_CUTOFF_NM, stride=3)

    # Build view
    view = build_view(atoms, box, hbond_pairs)

    # Generate full HTML and screenshot
    full_html = make_full_html(view, title_text)
    screenshot_html(full_html, outfile, wait_seconds=5)


# ---------------------------------------------------------------------------
# Post-processing: auto-crop whitespace gap between title and molecule
# ---------------------------------------------------------------------------
def crop_whitespace(filepath):
    """Crop the large whitespace gap between title overlay and molecule region."""
    img = Image.open(filepath).convert('RGB')
    arr = np.array(img)
    non_white_rows = np.where(np.any(arr < 250, axis=(1, 2)))[0]
    non_white_cols = np.where(np.any(arr < 250, axis=(0, 2)))[0]

    if len(non_white_rows) == 0 or len(non_white_cols) == 0:
        return  # Nothing to crop

    row_diffs = np.diff(non_white_rows)
    big_gaps = np.where(row_diffs > 30)[0]

    if len(big_gaps) > 0:
        title_end = non_white_rows[big_gaps[0]]
        mol_start = non_white_rows[big_gaps[0] + 1]
        pad = 15
        col0 = max(0, non_white_cols[0] - pad)
        col1 = min(img.width, non_white_cols[-1] + pad)
        title_region = img.crop((col0, max(0, non_white_rows[0] - pad), col1, title_end + pad))
        mol_region = img.crop((col0, max(0, mol_start - pad), col1, min(img.height, non_white_rows[-1] + pad)))
        gap = 15
        new_w = max(title_region.width, mol_region.width)
        new_h = title_region.height + gap + mol_region.height
        combined = Image.new('RGB', (new_w, new_h), (255, 255, 255))
        combined.paste(title_region, ((new_w - title_region.width) // 2, 0))
        combined.paste(mol_region, ((new_w - mol_region.width) // 2, title_region.height + gap))
        combined.save(filepath)
        print(f"  Cropped whitespace gap: {filepath.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    for snap in SNAPSHOTS:
        print(f"Rendering {snap['label']} from {snap['gro'].name} ...")
        render_snapshot(snap)

    print("Post-processing: cropping whitespace gaps ...")
    for snap in SNAPSHOTS:
        crop_whitespace(snap["outfile"])

    print("Done.")


if __name__ == "__main__":
    main()
