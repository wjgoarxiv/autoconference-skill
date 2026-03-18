"""
Auto-research loop runner: sII hydrate + water .gro generation conference.

33 iterations total: 3 researchers x 11 iterations x 3 rounds.
Each iteration generates a .gro with specific parameters (some intentionally wrong),
evaluates it, and records the scores.

Convergence narrative:
  Round 1: Crystal scaling + water in slab -> low scores
  Round 2: Peer review fixes one or both issues -> improving
  Round 3: Both constraints satisfied -> high scores
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
GEN_SCRIPT = HERE / "generate_hydrate.py"
EVAL_SCRIPT = HERE / "evaluate.py"
ITER_DIR = HERE / "iterations"

# Crystal constants (from GenIce2 CS2 rep 2 2 2)
CRYSTAL_XY = 3.42420
CRYSTAL_Z = 3.42420
BOX_Z = 5.0
Z_BOT = (BOX_Z - CRYSTAL_Z) / 2.0  # 0.7879
Z_TOP = Z_BOT + CRYSTAL_Z  # 4.2121

# Iteration configurations: (researcher, round, local_iter, description, gen_args)
# gen_args override defaults to simulate mistakes
ITERATIONS = [
    # ── Round 1: Naive attempts — both constraints violated ──────────────
    # Researcher A: Scales crystal to fit 3.6 nm box + water everywhere
    ("A", 1, 0, "Baseline: scale crystal to 3.6 nm, water everywhere",
     {"scale_xy": 3.6 / CRYSTAL_XY, "force_box_xy": 3.6, "water_in_slab": True, "seed": 100}),
    ("A", 1, 1, "Reduce scaling to 3.5 nm, still water everywhere",
     {"scale_xy": 3.5 / CRYSTAL_XY, "force_box_xy": 3.5, "water_in_slab": True, "seed": 101}),
    ("A", 1, 2, "Try rep 3 (too large crystal), water everywhere",
     {"scale_xy": 1.0, "force_box_xy": 5.136, "water_in_slab": True, "seed": 102, "rep": "3 3 2"}),
    ("A", 1, 3, "Back to rep 2, scale to 3.6, partial water filter 30%",
     {"scale_xy": 3.6 / CRYSTAL_XY, "force_box_xy": 3.6, "water_in_slab": True,
      "water_partial_filter": 0.3, "seed": 103}),

    # Researcher B: Wrong rep (rep 1 = tiny crystal) + water in slab
    ("B", 1, 0, "Baseline: rep 1 1 1 (tiny crystal), water everywhere",
     {"rep": "1 1 2", "water_in_slab": True, "seed": 200}),
    ("B", 1, 1, "Rep 1 1 2, force box to 3.6 nm, water everywhere",
     {"rep": "1 1 2", "force_box_xy": 3.6, "water_in_slab": True, "seed": 201}),
    ("B", 1, 2, "Rep 2 2 2 but scale to 3.6, water everywhere",
     {"scale_xy": 3.6 / CRYSTAL_XY, "force_box_xy": 3.6, "water_in_slab": True, "seed": 202}),
    ("B", 1, 3, "Rep 2, native dims, but water everywhere",
     {"water_in_slab": True, "seed": 203}),

    # Researcher C: Right rep but scales x,y, some water filtering
    ("C", 1, 0, "Rep 2, scale to 3.6, water everywhere",
     {"scale_xy": 3.6 / CRYSTAL_XY, "force_box_xy": 3.6, "water_in_slab": True, "seed": 300}),
    ("C", 1, 1, "Rep 2, scale to 3.6, partial water filter 50%",
     {"scale_xy": 3.6 / CRYSTAL_XY, "force_box_xy": 3.6, "water_in_slab": True,
      "water_partial_filter": 0.5, "seed": 301}),
    ("C", 1, 2, "Rep 2, scale to 3.5, partial water filter 70%",
     {"scale_xy": 3.5 / CRYSTAL_XY, "force_box_xy": 3.5, "water_in_slab": True,
      "water_partial_filter": 0.7, "seed": 302}),
    ("C", 1, 3, "Rep 2, native dims, but still water in slab",
     {"water_in_slab": True, "seed": 303}),

    # ── Round 2: Peer review flags issues — partial fixes ────────────────
    # Researcher A: Fixes crystal dims, still has water issues
    ("A", 2, 0, "Native crystal dims, but water still in slab",
     {"water_in_slab": True, "seed": 110}),
    ("A", 2, 1, "Native dims, partial water filter 60%",
     {"water_in_slab": True, "water_partial_filter": 0.6, "seed": 111}),
    ("A", 2, 2, "Native dims, partial water filter 90%",
     {"water_in_slab": True, "water_partial_filter": 0.9, "seed": 112}),
    ("A", 2, 3, "Native dims, proper water exclusion (FIXED)",
     {"seed": 113}),

    # Researcher B: Fixes water exclusion first, then crystal dims
    ("B", 2, 0, "Scale to 3.5, proper water exclusion",
     {"scale_xy": 3.5 / CRYSTAL_XY, "force_box_xy": 3.5, "seed": 210}),
    ("B", 2, 1, "Scale to 3.45, proper water exclusion",
     {"scale_xy": 3.45 / CRYSTAL_XY, "force_box_xy": 3.45, "seed": 211}),
    ("B", 2, 2, "Native dims, proper water exclusion (FIXED)",
     {"seed": 212}),
    ("B", 2, 3, "Native dims, proper exclusion, tuned density",
     {"seed": 213, "water_density": 998}),

    # Researcher C: Fixes water first, then crystal
    ("C", 2, 0, "Scale to 3.5, proper water exclusion",
     {"scale_xy": 3.5 / CRYSTAL_XY, "force_box_xy": 3.5, "seed": 310}),
    ("C", 2, 1, "Scale to 3.45, proper water exclusion",
     {"scale_xy": 3.45 / CRYSTAL_XY, "force_box_xy": 3.45, "seed": 311}),
    ("C", 2, 2, "Native crystal dims, proper exclusion (FIXED)",
     {"seed": 312}),
    ("C", 2, 3, "Native dims, proper exclusion, density 1000",
     {"seed": 313}),

    # ── Round 3: All converge — both constraints met ─────────────────────
    ("A", 3, 0, "Native dims + exclusion, seed 120",
     {"seed": 120}),
    ("A", 3, 1, "Native dims + exclusion, density 998",
     {"seed": 121, "water_density": 998}),
    ("A", 3, 2, "Native dims + exclusion, optimized (FINAL)",
     {"seed": 122}),

    ("B", 3, 0, "Native dims + exclusion, seed 220",
     {"seed": 220}),
    ("B", 3, 1, "Native dims + exclusion, density 1000",
     {"seed": 221}),
    ("B", 3, 2, "Native dims + exclusion, optimized (FINAL)",
     {"seed": 222}),

    ("C", 3, 0, "Native dims + exclusion, seed 320",
     {"seed": 320}),
    ("C", 3, 1, "Native dims + exclusion, density 999",
     {"seed": 321, "water_density": 999}),
    ("C", 3, 2, "Native dims + exclusion, optimized (FINAL)",
     {"seed": 322}),
]


def run_iteration(researcher, rnd, local_iter, desc, gen_args, global_idx):
    """Run one iteration: generate .gro, evaluate, return scores."""
    tag = f"R{rnd}_{researcher}_{local_iter}"
    gro_name = f"{tag}.gro"
    gro_path = ITER_DIR / gro_name
    ref_path = HERE / "reference_crystal.gro"

    print(f"\n{'='*60}")
    print(f"[{global_idx:02d}] Round {rnd} | Researcher {researcher} | Iter {local_iter}")
    print(f"  {desc}")
    print(f"{'='*60}")

    # Build generate command
    cmd = [
        sys.executable, str(GEN_SCRIPT),
        "--output", str(gro_path),
        "--reference", str(ref_path),
        "--box_z", str(BOX_Z),
    ]

    rep = gen_args.get("rep", "2 2 2")
    cmd.extend(["--rep", rep])

    if gen_args.get("scale_xy", 1.0) != 1.0:
        cmd.extend(["--scale_xy", str(gen_args["scale_xy"])])
    if gen_args.get("force_box_xy", 0) > 0:
        cmd.extend(["--force_box_xy", str(gen_args["force_box_xy"])])
    if gen_args.get("water_in_slab", False):
        cmd.append("--water_in_slab")
    if gen_args.get("water_partial_filter", 0) > 0:
        cmd.extend(["--water_partial_filter", str(gen_args["water_partial_filter"])])
    if "seed" in gen_args:
        cmd.extend(["--seed", str(gen_args["seed"])])
    if "water_density" in gen_args:
        cmd.extend(["--water_density", str(gen_args["water_density"])])
    if gen_args.get("z_shift", 0) != 0:
        cmd.extend(["--z_shift", str(gen_args["z_shift"])])

    # Generate
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  GENERATE FAILED: {result.stderr}")
        return None
    print(result.stdout)

    # Evaluate
    # Compute actual slab z bounds (may differ for wrong reps)
    # Always evaluate against the reference from this run
    eval_cmd = [
        sys.executable, str(EVAL_SCRIPT),
        str(gro_path),
        "--reference", str(ref_path),
        "--slab_z_min", str(round(Z_BOT, 4)),
        "--slab_z_max", str(round(Z_TOP, 4)),
        "--target_z", str(BOX_Z),
        "--json_output", str(ITER_DIR / f"{tag}_scores.json"),
    ]
    result = subprocess.run(eval_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  EVALUATE FAILED: {result.stderr}")
        return None

    scores = json.loads(result.stdout)
    print(f"  Composite: {scores['composite']}")
    print(f"  Structural: {scores['structural']} | Density: {scores['density']} | "
          f"Geometric: {scores['geometric']}")
    print(f"  PBC: {scores['pbc']} | Slab Exclusion: {scores['slab_exclusion']} | "
          f"Crystal Integrity: {scores['crystal_integrity']}")

    return scores


def main():
    ITER_DIR.mkdir(exist_ok=True)

    all_results = []
    tsv_rows = []
    events = []
    researcher_results = {"A": [], "B": [], "C": []}

    base_time = "2026-03-19T10:00:00Z"

    events.append(json.dumps({
        "event": "conference.started",
        "timestamp": base_time,
        "payload": {
            "researchers": 3,
            "mode": "metric",
            "goal": "Generate sII hydrate + water .gro with crystal integrity and water exclusion",
            "config_summary": "metric=composite_score, direction=maximize, target=>=80, 6 sub-metrics",
        },
    }))

    global_idx = 0
    for researcher, rnd, local_iter, desc, gen_args in ITERATIONS:
        scores = run_iteration(researcher, rnd, local_iter, desc, gen_args, global_idx)
        if scores is None:
            scores = {
                "composite": 0.0, "structural": 0.0, "density": 0.0,
                "geometric": 0.0, "pbc": 0.0, "slab_exclusion": 0.0,
                "crystal_integrity": 0.0, "details": {},
            }

        entry = {
            "researcher": researcher,
            "round": rnd,
            "iteration": local_iter,
            "global_idx": global_idx,
            "description": desc,
            "scores": scores,
        }
        all_results.append(entry)
        researcher_results[researcher].append(entry)

        # Determine status
        composite = scores["composite"]
        if local_iter == 0 and rnd == 1:
            status = "baseline"
            delta = "-"
            delta_pct = "-"
        else:
            prev_entries = [e for e in researcher_results[researcher][:-1]]
            if prev_entries:
                prev_best = max(e["scores"]["composite"] for e in prev_entries)
                d = composite - prev_best
                delta = f"{d:+.1f}"
                delta_pct = f"{d / prev_best * 100:+.1f}%" if prev_best > 0 else "-"
                status = "kept" if composite >= prev_best else "reverted"
            else:
                delta = "-"
                delta_pct = "-"
                status = "baseline"

        # Peer review verdict
        if rnd == 1:
            if scores["crystal_integrity"] < 50 and scores["slab_exclusion"] < 50:
                verdict = "challenged"
            elif scores["crystal_integrity"] < 50 or scores["slab_exclusion"] < 50:
                verdict = "challenged"
            else:
                verdict = "validated"
        elif rnd == 2:
            if composite >= 80:
                verdict = "validated"
            elif composite >= 50:
                verdict = "validated"
            else:
                verdict = "challenged"
        else:
            verdict = "validated"

        tsv_rows.append(
            f"{rnd}\t{researcher}\t{local_iter}\t{composite}\t{delta}\t{delta_pct}\t"
            f"{status}\t{desc}\t{verdict}\t2026-03-19T{10 + global_idx // 6:02d}:{(global_idx % 6) * 10:02d}:00Z"
        )

        # Event
        events.append(json.dumps({
            "event": "researcher.iteration",
            "timestamp": f"2026-03-19T{10 + global_idx // 6:02d}:{(global_idx % 6) * 10:02d}:00Z",
            "payload": {
                "researcher": researcher,
                "round": rnd,
                "iteration": local_iter,
                "metric_value": composite,
                "delta": delta,
                "status": status,
                "sub_metrics": {
                    "structural": scores["structural"],
                    "density": scores["density"],
                    "geometric": scores["geometric"],
                    "pbc": scores["pbc"],
                    "slab_exclusion": scores["slab_exclusion"],
                    "crystal_integrity": scores["crystal_integrity"],
                },
            },
        }))

        # Round boundary events
        if local_iter == 3 and researcher == "C" and rnd < 3:
            events.append(json.dumps({
                "event": f"round.{rnd}.completed",
                "timestamp": f"2026-03-19T{10 + global_idx // 6:02d}:{(global_idx % 6) * 10 + 5:02d}:00Z",
                "payload": {"round": rnd},
            }))
        elif local_iter == 2 and researcher == "C" and rnd == 3:
            events.append(json.dumps({
                "event": "round.3.completed",
                "timestamp": f"2026-03-19T{10 + global_idx // 6:02d}:{(global_idx % 6) * 10 + 5:02d}:00Z",
                "payload": {"round": rnd},
            }))

        global_idx += 1

    # Write conference_results.tsv
    header = "round\tresearcher\titeration\tmetric_value\tdelta\tdelta_pct\tstatus\tdescription\tpeer_review_verdict\ttimestamp"
    tsv_path = HERE / "conference_results.tsv"
    tsv_path.write_text(header + "\n" + "\n".join(tsv_rows) + "\n")
    print(f"\nWrote {tsv_path}")

    # Write per-researcher TSVs
    for rid in ["A", "B", "C"]:
        rows = [r for r in tsv_rows if r.split("\t")[1] == rid]
        path = HERE / f"researcher_{rid}_results.tsv"
        path.write_text(header + "\n" + "\n".join(rows) + "\n")

    # Write events JSONL
    events_path = HERE / "conference_events.jsonl"
    events_path.write_text("\n".join(events) + "\n")
    print(f"Wrote {events_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for rid in ["A", "B", "C"]:
        entries = researcher_results[rid]
        best = max(entries, key=lambda e: e["scores"]["composite"])
        print(f"  Researcher {rid}: best composite = {best['scores']['composite']:.1f} "
              f"(Round {best['round']}, iter {best['iteration']})")
        print(f"    crystal_integrity={best['scores']['crystal_integrity']:.0f}, "
              f"slab_exclusion={best['scores']['slab_exclusion']:.0f}")

    # Final best
    overall_best = max(all_results, key=lambda e: e["scores"]["composite"])
    print(f"\n  Overall best: {overall_best['scores']['composite']:.1f} "
          f"(Researcher {overall_best['researcher']}, R{overall_best['round']}-{overall_best['iteration']})")


if __name__ == "__main__":
    main()
