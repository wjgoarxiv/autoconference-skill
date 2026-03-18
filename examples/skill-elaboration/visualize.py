"""Generate visualization for the skill elaboration conference."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager


def setup_rcparams():
    rcParams['figure.figsize'] = 5, 4
    rcParams['font.family'] = 'sans-serif'
    available_fonts = set([f.name for f in font_manager.fontManager.ttflist])
    if 'Pretendard' in available_fonts:
        rcParams['font.sans-serif'] = ['Pretendard']
    elif 'Arial' in available_fonts:
        rcParams['font.sans-serif'] = ['Arial']
    else:
        print("WARNING: Pretendard and Arial not installed. Using default font.")
    rcParams['axes.labelpad'] = 8
    rcParams['xtick.major.pad'] = 7
    rcParams['ytick.major.pad'] = 7
    rcParams['xtick.minor.visible'] = True
    rcParams['ytick.minor.visible'] = True
    rcParams['xtick.major.width'] = 1
    rcParams['ytick.major.width'] = 1
    rcParams['xtick.minor.width'] = 0.5
    rcParams['ytick.minor.width'] = 0.5
    rcParams['xtick.major.size'] = 5
    rcParams['ytick.major.size'] = 5
    rcParams['xtick.minor.size'] = 3
    rcParams['ytick.minor.size'] = 3
    rcParams['xtick.color'] = 'black'
    rcParams['ytick.color'] = 'black'
    rcParams['font.size'] = 14
    rcParams['axes.titlepad'] = 10
    rcParams['axes.titleweight'] = 'normal'
    rcParams['axes.titlesize'] = 18
    rcParams['axes.labelweight'] = 'normal'
    rcParams['xtick.labelsize'] = 12
    rcParams['ytick.labelsize'] = 12
    rcParams['axes.labelsize'] = 16
    rcParams['xtick.direction'] = 'in'
    rcParams['ytick.direction'] = 'in'


def load_conference_results(tsv_path):
    """Load conference_results.tsv and return per-researcher iteration data."""
    researchers = {}
    with open(tsv_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rid = row["researcher"]
            if rid not in researchers:
                researchers[rid] = {"iterations": [], "metrics": [], "statuses": []}
            researchers[rid]["iterations"].append(int(row["iteration"]))
            researchers[rid]["metrics"].append(float(row["metric_value"]))
            researchers[rid]["statuses"].append(row["status"])
    return researchers


def main():
    here = Path(__file__).parent
    tsv_path = here / "conference_results.tsv"

    if not tsv_path.exists():
        print(f"No conference_results.tsv found in {here}. Run the conference first.")
        return

    setup_rcparams()
    researchers = load_conference_results(tsv_path)

    colors = {"A": "#2563EB", "B": "#D97706", "C": "#059669"}
    markers = {"A": "o", "B": "s", "C": "^"}

    fig, ax = plt.subplots()

    for rid, data in sorted(researchers.items()):
        iters = data["iterations"]
        metrics = [m * 100 for m in data["metrics"]]  # Convert to percentage

        # Best-so-far trajectory (maximize)
        best_so_far = []
        current_best = metrics[0]
        for m in metrics:
            if m > current_best:
                current_best = m
            best_so_far.append(current_best)

        ax.plot(iters, best_so_far,
                marker=markers.get(rid, "o"),
                color=colors.get(rid, "#333"),
                linewidth=2, markersize=6,
                label=f"Researcher {rid}")

    # Target line
    ax.axhline(y=85, color="#DC2626", linestyle="--", linewidth=1.2, alpha=0.7, label="Target (> 85%)")

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Composite Score (%)")
    ax.set_title("P&ID Skill Elaboration")
    ax.legend(fontsize=10, frameon=True, edgecolor="#ccc")

    plt.tight_layout()
    out = here / "results.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
