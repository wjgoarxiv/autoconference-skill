"""Tests for init_conference.py scaffolding script."""
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init_conference.py"


def run_init(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Helper to invoke init_conference.py."""
    return subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Optimize inference latency",
            "--metric", "p95_latency_ms",
            "--direction", "minimize",
            "--target", "< 50",
            "--researchers", "3",
            "--strategy", "assigned",
            "--output", str(tmp_path / "my-conference"),
            *extra_args,
        ],
        capture_output=True,
        text=True,
    )


def test_creates_conference_md(tmp_path):
    result = run_init(tmp_path)
    assert result.returncode == 0
    conf = tmp_path / "my-conference" / "conference.md"
    assert conf.exists()
    text = conf.read_text()
    assert "Optimize inference latency" in text
    assert "p95_latency_ms" in text
    assert "minimize" in text
    assert "< 50" in text


def test_creates_tsv_files(tmp_path):
    run_init(tmp_path)
    base = tmp_path / "my-conference"
    assert (base / "conference_results.tsv").exists()
    for rid in ["A", "B", "C"]:
        assert (base / f"researcher_{rid}_results.tsv").exists()
        assert (base / f"researcher_{rid}_log.md").exists()


def test_creates_events_jsonl(tmp_path):
    run_init(tmp_path)
    events = tmp_path / "my-conference" / "conference_events.jsonl"
    assert events.exists()
    assert events.read_text() == ""  # empty at init


def test_qualitative_mode(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Survey LLM agent papers",
            "--mode", "qualitative",
            "--criteria", "Comprehensive taxonomy with 15+ papers",
            "--researchers", "2",
            "--output", str(tmp_path / "qual-conf"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    conf = tmp_path / "qual-conf" / "conference.md"
    text = conf.read_text()
    assert "qualitative" in text
    assert "Comprehensive taxonomy" in text


def test_rejects_missing_metric_in_metric_mode(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--goal", "Something",
            "--output", str(tmp_path / "bad"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_guard_flag(tmp_path):
    result = run_init(tmp_path, "--guard", "Do not modify test data")
    assert result.returncode == 0
    conf = tmp_path / "my-conference" / "conference.md"
    text = conf.read_text()
    assert "Do not modify test data" in text
    assert "## Guard" in text


def test_noise_runs_flag(tmp_path):
    result = run_init(tmp_path, "--noise-runs", "5")
    assert result.returncode == 0
    conf = tmp_path / "my-conference" / "conference.md"
    text = conf.read_text()
    assert "**Noise runs:** 5" in text


def test_min_delta_flag(tmp_path):
    result = run_init(tmp_path, "--min-delta", "0.05")
    assert result.returncode == 0
    conf = tmp_path / "my-conference" / "conference.md"
    text = conf.read_text()
    assert "**Min consensus delta:** 0.05" in text


def test_tsv_has_evaluator_source_column(tmp_path):
    run_init(tmp_path)
    base = tmp_path / "my-conference"
    # Per-researcher TSV should have 8 columns
    researcher_tsv = (base / "researcher_A_results.tsv").read_text()
    header = researcher_tsv.split("\n")[0]
    assert "evaluator_source" in header
    assert len(header.split("\t")) == 8
    # Conference TSV should have 11 columns
    conf_tsv = (base / "conference_results.tsv").read_text()
    conf_header = conf_tsv.split("\n")[0]
    assert "evaluator_source" in conf_header
    assert len(conf_header.split("\t")) == 11
