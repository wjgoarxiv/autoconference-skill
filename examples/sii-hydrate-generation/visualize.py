"""Generate 4-panel visualization for the sII hydrate generation conference."""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/woojin/.claude/skills/045_scientific-visualization/scripts')
from style_presets import rcparams

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Okabe-Ito colors for researchers
COLORS = {
    "A": "#E69F00",  # orange
    "B": "#56B4E9",  # sky blue
    "C": "#009E73",  # bluish green
}


def setup_rcparams():
    rcparams()


def load_results(here: Path):
    """Load conference_results.tsv and per-iteration score JSONs."""
    researchers = {}
    with open(here / "conference_results.tsv") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rid = row["researcher"]
            rnd = int(row["round"])
            local_iter = int(row["iteration"])
            composite = float(row["metric_value"])

            if rid not in researchers:
                researchers[rid] = {
                    "global_iters": [],
                    "composites": [],
                    "rounds": [],
                    "sub_metrics": [],
                }

            tag = f"R{rnd}_{rid}_{local_iter}"
            score_file = here / "iterations" / f"{tag}_scores.json"
            sub = {}
            if score_file.exists():
                sub = json.loads(score_file.read_text())

            idx = len(researchers[rid]["global_iters"])
            researchers[rid]["global_iters"].append(idx)
            researchers[rid]["composites"].append(composite)
            researchers[rid]["rounds"].append(rnd)
            researchers[rid]["sub_metrics"].append(sub)

    return researchers


def find_round_boundaries(researchers):
    """Find global iteration indices where rounds change."""
    boundaries = []
    # Use researcher A as reference
    data = researchers.get("A", {})
    rounds = data.get("rounds", [])
    for i in range(1, len(rounds)):
        if rounds[i] != rounds[i - 1]:
            boundaries.append(i - 0.5)
    return boundaries


def plot_composite_convergence(ax, researchers, boundaries, show_title=True):
    """Panel 1: Composite score per researcher with round boundaries."""
    markers = {"A": "o", "B": "s", "C": "^"}

    lines = []
    for rid in sorted(researchers.keys()):
        data = researchers[rid]
        iters = data["global_iters"]
        composites = data["composites"]

        # Best-so-far trajectory
        best_so_far = []
        current_best = composites[0]
        for c in composites:
            if c > current_best:
                current_best = c
            best_so_far.append(current_best)

        color = COLORS.get(rid, "#333")
        line, = ax.plot(iters, best_so_far,
                marker=markers.get(rid, "o"),
                color=color,
                linestyle=":", linewidth=2, markersize=6,
                alpha=1.0,
                label=f"Researcher {rid}")
        lines.append((line, color))

    # Target line
    target_line = ax.axhline(y=80, color="#DC2626", linestyle="--", linewidth=1.2, alpha=0.7, label="Target (>= 80)")

    # Round boundaries
    for b in boundaries:
        ax.axvline(x=b, color="#9CA3AF", linestyle="-", linewidth=0.8, alpha=0.5)

    ax.set_xlabel("Iteration (global)")
    ax.set_ylabel("Composite Score")
    if show_title:
        ax.set_title("Composite Score Convergence")

    # Legend with matching text colors; black border, fully opaque
    leg = ax.legend(fontsize=10, frameon=True, edgecolor="black", framealpha=1, loc="lower right")
    for text, (line, color) in zip(leg.get_texts()[:-1], lines):
        text.set_color(color)
    leg.get_texts()[-1].set_color("#DC2626")

    all_iters = [i for r in researchers.values() for i in r["global_iters"]]
    ax.set_xlim(min(all_iters), max(all_iters))
    ax.set_ylim(0, 105)


def plot_submetric_breakdown(ax, researchers, boundaries, show_title=True):
    """Panel 2: 6 sub-metric lines for best researcher."""
    # Find best researcher (highest final composite)
    best_rid = max(researchers.keys(),
                   key=lambda r: researchers[r]["composites"][-1])
    data = researchers[best_rid]
    iters = data["global_iters"]
    sub_metrics_list = data["sub_metrics"]

    metric_names = ["structural", "density", "geometric", "pbc", "slab_exclusion", "crystal_integrity"]
    metric_colors = {
        "structural": "#0072B2",
        "density": "#CC79A7",
        "geometric": "#E69F00",
        "pbc": "#009E73",
        "slab_exclusion": "#D55E00",
        "crystal_integrity": "#56B4E9",
    }
    metric_labels = {
        "structural": "Structural (20%)",
        "density": "Density (15%)",
        "geometric": "Geometric (15%)",
        "pbc": "PBC (10%)",
        "slab_exclusion": "Slab Exclusion (20%)",
        "crystal_integrity": "Crystal Integrity (20%)",
    }

    lines = []
    for name in metric_names:
        values = []
        for sub in sub_metrics_list:
            values.append(sub.get(name, 0.0))
        line, = ax.plot(iters, values,
                color=metric_colors[name],
                linewidth=1.8, alpha=0.9,
                label=metric_labels[name],
                marker=".", markersize=4)
        lines.append((line, metric_colors[name]))

    for b in boundaries:
        ax.axvline(x=b, color="#9CA3AF", linestyle="-", linewidth=0.8, alpha=0.5)

    ax.set_xlabel("Iteration (global)")
    ax.set_ylabel("Sub-metric Score")
    if show_title:
        ax.set_title(f"Sub-metric Breakdown (Researcher {best_rid})")

    leg = ax.legend(fontsize=8, frameon=True, edgecolor="black", framealpha=1,
                    loc="center right", ncol=1)
    for text, (line, color) in zip(leg.get_texts(), lines):
        text.set_color(color)

    ax.set_xlim(min(iters), max(iters))
    ax.set_ylim(-5, 110)


def plot_researcher_heatmap(ax, researchers, show_title=True):
    """Panel 3: Best composite per researcher per round (heatmap)."""
    rids = sorted(researchers.keys())
    rounds = [1, 2, 3]

    matrix = []
    for rid in rids:
        data = researchers[rid]
        row = []
        for rnd in rounds:
            round_composites = [
                c for c, r in zip(data["composites"], data["rounds"]) if r == rnd
            ]
            row.append(max(round_composites) if round_composites else 0)
        matrix.append(row)

    matrix = np.array(matrix)
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(rounds)))
    ax.set_xticklabels([f"Round {r}" for r in rounds])
    ax.set_yticks(range(len(rids)))
    ax.set_yticklabels([f"Researcher {r}" for r in rids])

    # Annotate cells
    for i in range(len(rids)):
        for j in range(len(rounds)):
            val = matrix[i, j]
            color = "white" if val < 50 else "black"
            ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

    if show_title:
        ax.set_title("Best Composite by Researcher x Round")
    plt.colorbar(im, ax=ax, shrink=0.8, label="Composite Score")


def plot_peer_review(ax, researchers, show_title=True):
    """Panel 4: Stacked bar of peer review verdicts per round."""
    rounds = [1, 2, 3]

    # Count verdicts per round from TSV
    here = Path(__file__).parent
    verdicts_per_round = {r: {"validated": 0, "challenged": 0} for r in rounds}

    with open(here / "conference_results.tsv") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rnd = int(row["round"])
            verdict = row["peer_review_verdict"]
            if verdict in verdicts_per_round[rnd]:
                verdicts_per_round[rnd][verdict] += 1

    validated = [verdicts_per_round[r]["validated"] for r in rounds]
    challenged = [verdicts_per_round[r]["challenged"] for r in rounds]

    x = np.arange(len(rounds))
    width = 0.5

    validated_color = "#009E73"
    challenged_color = "#D55E00"
    ax.bar(x, validated, width, label="Validated", color=validated_color, alpha=0.85)
    ax.bar(x, challenged, width, bottom=validated, label="Challenged", color=challenged_color, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels([f"Round {r}" for r in rounds])
    ax.set_ylabel("Number of Iterations")
    if show_title:
        ax.set_title("Peer Review Verdicts")

    leg = ax.legend(fontsize=10, frameon=True, edgecolor="black", framealpha=1)
    for text, color in zip(leg.get_texts(), [validated_color, challenged_color]):
        text.set_color(color)

    max_total = max(v + c for v, c in zip(validated, challenged))
    ax.set_ylim(0, max_total * 1.15)

    # Annotate totals
    for i, r in enumerate(rounds):
        total = validated[i] + challenged[i]
        ax.text(i, total + 0.2, str(total), ha="center", va="bottom", fontsize=11)


def save_individual_plots(here, researchers, boundaries):
    """Save each panel as a standalone PNG at (7, 5), DPI 600."""
    individual_size = (7, 5)

    # Panel 1: composite convergence (no title for journal submission)
    fig, ax = plt.subplots(figsize=individual_size)
    plot_composite_convergence(ax, researchers, boundaries, show_title=False)
    plt.tight_layout()
    out = here / "plot_composite_convergence.png"
    plt.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # Panel 2: sub-metric breakdown (no title for journal submission)
    fig, ax = plt.subplots(figsize=individual_size)
    plot_submetric_breakdown(ax, researchers, boundaries, show_title=False)
    plt.tight_layout()
    out = here / "plot_submetric_breakdown.png"
    plt.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # Panel 3: researcher heatmap (no title for journal submission)
    fig, ax = plt.subplots(figsize=individual_size)
    plot_researcher_heatmap(ax, researchers, show_title=False)
    plt.tight_layout()
    out = here / "plot_researcher_heatmap.png"
    plt.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # Panel 4: peer review verdicts (no title for journal submission)
    fig, ax = plt.subplots(figsize=individual_size)
    plot_peer_review(ax, researchers, show_title=False)
    plt.tight_layout()
    out = here / "plot_peer_review_verdicts.png"
    plt.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def main():
    here = Path(__file__).parent
    tsv_path = here / "conference_results.tsv"

    if not tsv_path.exists():
        print(f"No conference_results.tsv found in {here}. Run run_iterations.py first.")
        return

    setup_rcparams()
    researchers = load_results(here)
    boundaries = find_round_boundaries(researchers)

    # Combined 4-panel figure (backwards compatible)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("sII Hydrate Generation Conference Results", fontsize=20, fontweight="bold", y=0.98)

    plot_composite_convergence(axes[0, 0], researchers, boundaries)
    plot_submetric_breakdown(axes[0, 1], researchers, boundaries)
    plot_researcher_heatmap(axes[1, 0], researchers)
    plot_peer_review(axes[1, 1], researchers)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = here / "results.png"
    plt.savefig(out, dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    # Individual plots
    save_individual_plots(here, researchers, boundaries)


if __name__ == "__main__":
    main()
