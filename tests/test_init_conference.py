"""Tests for init_conference.py scaffolding script."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init_conference.py"


class InitConferenceTests(unittest.TestCase):
    def run_init(self, tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
        """Invoke init_conference.py."""
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--goal",
                "Optimize inference latency",
                "--metric",
                "p95_latency_ms",
                "--direction",
                "minimize",
                "--target",
                "< 50",
                "--researchers",
                "3",
                "--strategy",
                "assigned",
                "--output",
                str(tmp_path / "my-conference"),
                *extra_args,
            ],
            capture_output=True,
            text=True,
        )

    def test_creates_conference_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            self.assertTrue(conf.exists())
            text = conf.read_text()
            self.assertIn("Optimize inference latency", text)
            self.assertIn("p95_latency_ms", text)
            self.assertIn("minimize", text)
            self.assertIn("< 50", text)

    def test_conference_md_contains_preflight_confirmation_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path, "--devils-advocate", "yes")
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            text = conf.read_text()
            self.assertIn("## Pre-Flight Gate", text)
            self.assertIn("**Researcher count:** 3", text)
            self.assertIn("**Final confirmation:** pending", text)
            self.assertIn("Do not start Phase 1", text)
            self.assertIn("**Critic / Devil's Advocate:** enabled", text)
            self.assertIn("Max total iterations: 60", result.stdout)

    def test_conference_md_marks_unspecified_devil_advocate_as_user_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            text = conf.read_text()
            self.assertIn("**Critic / Devil's Advocate:** ask user before run", text)

    def test_help_mentions_devils_advocate_gate_flag(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--devils-advocate", result.stdout)
        self.assertIn("required user prompt before running", result.stdout)

    def test_creates_tsv_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.run_init(tmp_path)
            base = tmp_path / "my-conference"
            self.assertTrue((base / "conference_results.tsv").exists())
            for rid in ["A", "B", "C"]:
                self.assertTrue((base / f"researcher_{rid}_results.tsv").exists())
                self.assertTrue((base / f"researcher_{rid}_log.md").exists())

    def test_creates_events_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.run_init(tmp_path)
            events = tmp_path / "my-conference" / "conference_events.jsonl"
            self.assertTrue(events.exists())
            self.assertEqual(events.read_text(), "")

    def test_qualitative_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--goal",
                    "Survey LLM agent papers",
                    "--mode",
                    "qualitative",
                    "--criteria",
                    "Comprehensive taxonomy with 15+ papers",
                    "--researchers",
                    "2",
                    "--output",
                    str(tmp_path / "qual-conf"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "qual-conf" / "conference.md"
            text = conf.read_text()
            self.assertIn("qualitative", text)
            self.assertIn("Comprehensive taxonomy", text)

    def test_rejects_missing_metric_in_metric_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--goal",
                    "Something",
                    "--output",
                    str(tmp_path / "bad"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_rejects_missing_target_in_metric_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--goal",
                    "Optimize latency",
                    "--metric",
                    "p95_latency_ms",
                    "--direction",
                    "minimize",
                    "--output",
                    str(tmp_path / "bad"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--target is required", result.stderr)

    def test_rejects_placeholder_target_in_metric_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--goal",
                    "Optimize latency",
                    "--metric",
                    "p95_latency_ms",
                    "--direction",
                    "minimize",
                    "--target",
                    "TBD ",
                    "--output",
                    str(tmp_path / "bad"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--target is required", result.stderr)

    def test_rejects_whitespace_target_in_metric_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--goal",
                    "Optimize latency",
                    "--metric",
                    "p95_latency_ms",
                    "--direction",
                    "minimize",
                    "--target",
                    "   ",
                    "--output",
                    str(tmp_path / "bad"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--target is required", result.stderr)

    def test_guard_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path, "--guard", "Do not modify test data")
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            text = conf.read_text()
            self.assertIn("Do not modify test data", text)
            self.assertIn("## Guard", text)

    def test_noise_runs_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path, "--noise-runs", "5")
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            text = conf.read_text()
            self.assertIn("**Noise runs:** 5", text)

    def test_min_delta_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = self.run_init(tmp_path, "--min-delta", "0.05")
            self.assertEqual(result.returncode, 0, result.stderr)
            conf = tmp_path / "my-conference" / "conference.md"
            text = conf.read_text()
            self.assertIn("**Min consensus delta:** 0.05", text)

    def test_tsv_has_evaluator_source_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.run_init(tmp_path)
            base = tmp_path / "my-conference"
            researcher_tsv = (base / "researcher_A_results.tsv").read_text()
            header = researcher_tsv.split("\n")[0]
            self.assertIn("evaluator_source", header)
            self.assertEqual(len(header.split("\t")), 8)
            conf_tsv = (base / "conference_results.tsv").read_text()
            conf_header = conf_tsv.split("\n")[0]
            self.assertIn("evaluator_source", conf_header)
            self.assertEqual(len(conf_header.split("\t")), 11)


if __name__ == "__main__":
    unittest.main()
