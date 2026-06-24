#!/usr/bin/env python3
"""Validate package metadata, docs, examples, evals, and output contracts.

This script intentionally uses only the Python standard library so it can run in
fresh skill checkouts before any development dependencies are installed.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent


def package_git_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


GIT_ROOT = package_git_root()

CONFERENCE_TSV_HEADER = [
    "round",
    "researcher",
    "iteration",
    "metric_value",
    "delta",
    "delta_pct",
    "status",
    "description",
    "evaluator_source",
    "peer_review_verdict",
    "timestamp",
]
RESEARCHER_TSV_HEADER = [
    "iteration",
    "metric_value",
    "delta",
    "delta_pct",
    "status",
    "description",
    "evaluator_source",
    "timestamp",
]
REQUIRED_EVAL_CATEGORIES = {
    "routing",
    "subcommand",
    "negative",
    "user_confusion",
    "resume_retry",
    "prompt_injection",
    "install_platform",
}
SKIP_DIRS = {
    ".git",
    ".litopencode",
    ".pytest_cache",
    ".worktrees",
    ".omc",
    "__pycache__",
    "node_modules",
}


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.fail(message)

    def existing_path(self, path: str | Path, *, base: Path = ROOT) -> Path:
        return (base / path).resolve()

    def is_git_ignored(self, path: Path) -> bool:
        if GIT_ROOT != ROOT.resolve():
            return False
        try:
            rel = path.resolve().relative_to(ROOT.resolve())
        except ValueError:
            return False
        try:
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(rel)],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except FileNotFoundError:
            return False
        return result.returncode == 0

    def check_json_files(self) -> None:
        paths = [
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / "context7.json",
            ROOT / "gemini-extension.json",
            ROOT / "evals" / "evals.json",
        ]
        paths.extend((ROOT / "examples" / "sii-hydrate-generation" / "iterations").glob("*_scores.json"))
        for path in paths:
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - report all parse/read failures
                self.fail(f"invalid JSON: {path.relative_to(ROOT)}: {exc}")

    def check_manifests(self) -> None:
        plugin_path = ROOT / ".claude-plugin" / "plugin.json"
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        skills_dir = (plugin_path.parent / plugin.get("skills", "")).resolve()
        self.require(skills_dir == (ROOT / "skills").resolve(), ".claude-plugin/plugin.json skills must resolve to ./skills")
        self.require(skills_dir.exists(), ".claude-plugin/plugin.json skills path is missing")

        for manifest_name in [".claude-plugin/marketplace.json", "gemini-extension.json"]:
            manifest = json.loads((ROOT / manifest_name).read_text(encoding="utf-8"))
            for skill in manifest.get("skills", []):
                rel = skill.get("path", "")
                self.require(bool(rel), f"{manifest_name}: skill {skill.get('name')} missing path")
                self.require((ROOT / rel).exists(), f"{manifest_name}: missing skill path {rel}")

    def check_skill_frontmatter(self) -> None:
        for path in [ROOT / "SKILL.md", *sorted((ROOT / "skills").glob("*/SKILL.md"))]:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(ROOT)
            self.require(text.startswith("---\n"), f"{rel}: missing opening frontmatter fence")
            parts = text.split("---", 2)
            self.require(len(parts) >= 3, f"{rel}: missing closing frontmatter fence")
            frontmatter = parts[1]
            self.require("name:" in frontmatter, f"{rel}: missing name in frontmatter")
            self.require("description:" in frontmatter, f"{rel}: missing description in frontmatter")
            self.require("allowed-tools:" in frontmatter, f"{rel}: missing allowed-tools in frontmatter")

    def iter_markdown_files(self):
        for path in ROOT.rglob("*.md"):
            if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
                continue
            yield path

    def check_markdown_links(self) -> None:
        link_re = re.compile(r"!?(?<!\\)\[[^\]]*\]\(([^)]+)\)")
        for path in self.iter_markdown_files():
            text = path.read_text(encoding="utf-8")
            for raw in link_re.findall(text):
                target = raw.strip().split()[0]
                target = target.strip("<>")
                if not target or target.startswith("#"):
                    continue
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                target = unquote(target.split("#", 1)[0])
                if not target:
                    continue
                candidate = (path.parent / target).resolve()
                try:
                    candidate.relative_to(ROOT.resolve())
                except ValueError:
                    self.fail(f"{path.relative_to(ROOT)}: link escapes repo: {raw}")
                    continue
                self.require(candidate.exists(), f"{path.relative_to(ROOT)}: broken link {raw}")
                self.require(not self.is_git_ignored(candidate), f"{path.relative_to(ROOT)}: link targets ignored file {raw}")

    def check_examples(self) -> None:
        examples_dir = ROOT / "examples"
        for example in sorted(p for p in examples_dir.iterdir() if p.is_dir()):
            rel = example.relative_to(ROOT)
            readme = example / "README.md"
            conference = example / "conference.md"
            self.require(readme.exists(), f"{rel}: missing README.md")
            self.require(conference.exists(), f"{rel}: missing conference.md")
            if readme.exists():
                text = readme.read_text(encoding="utf-8")
                for phrase in ["Goal", "Metric", "Expected Outputs", "Verify"]:
                    self.require(phrase in text, f"{rel}/README.md: missing {phrase!r} section text")
            conf_tsv = example / "conference_results.tsv"
            if conf_tsv.exists() and not self.is_git_ignored(conf_tsv):
                header = conf_tsv.read_text(encoding="utf-8").splitlines()[0].split("\t")
                self.require(header == CONFERENCE_TSV_HEADER, f"{conf_tsv.relative_to(ROOT)}: invalid conference TSV header")
            max_conference_iteration: dict[str, int] = {}
            if conf_tsv.exists() and not self.is_git_ignored(conf_tsv):
                for row in conf_tsv.read_text(encoding="utf-8").splitlines()[1:]:
                    parts = row.split("\t")
                    if len(parts) < 4:
                        continue
                    researcher = parts[1]
                    try:
                        iteration = int(parts[2])
                    except ValueError:
                        continue
                    max_conference_iteration[researcher] = max(max_conference_iteration.get(researcher, 0), iteration)
            for tsv in sorted(example.glob("researcher_*_results.tsv")):
                if self.is_git_ignored(tsv):
                    continue
                header = tsv.read_text(encoding="utf-8").splitlines()[0].split("\t")
                self.require(header == RESEARCHER_TSV_HEADER, f"{tsv.relative_to(ROOT)}: invalid researcher TSV header")
                rows = tsv.read_text(encoding="utf-8").splitlines()[1:]
                prev_iteration: int | None = None
                max_iteration = 0
                for line_no, row in enumerate(rows, 2):
                    parts = row.split("\t")
                    if len(parts) != len(RESEARCHER_TSV_HEADER):
                        self.fail(f"{tsv.relative_to(ROOT)}:{line_no}: expected 8 columns")
                        continue
                    try:
                        iteration = int(parts[0])
                    except ValueError:
                        self.fail(f"{tsv.relative_to(ROOT)}:{line_no}: iteration is not an integer")
                        continue
                    max_iteration = max(max_iteration, iteration)
                    if prev_iteration is None or iteration <= prev_iteration:
                        self.require(iteration == 0, f"{tsv.relative_to(ROOT)}:{line_no}: round reset must start at iteration 0")
                        self.require(parts[4] == "baseline", f"{tsv.relative_to(ROOT)}:{line_no}: round reset row must be baseline")
                        self.require(parts[2] == "-", f"{tsv.relative_to(ROOT)}:{line_no}: baseline delta must be '-'")
                    prev_iteration = iteration
                researcher_id = tsv.name.split("_")[1]
                conf_max = max_conference_iteration.get(researcher_id)
                if conf_max is not None:
                    self.require(
                        max_iteration <= conf_max,
                        f"{tsv.relative_to(ROOT)}: per-researcher iteration should reset by round",
                    )
            events = example / "conference_events.jsonl"
            if events.exists() and not self.is_git_ignored(events):
                for line_no, line in enumerate(events.read_text(encoding="utf-8").splitlines(), 1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        self.fail(f"{events.relative_to(ROOT)}:{line_no}: invalid JSONL: {exc}")
                        continue
                    self.require("event" in obj, f"{events.relative_to(ROOT)}:{line_no}: missing event")
                    self.require("timestamp" in obj, f"{events.relative_to(ROOT)}:{line_no}: missing timestamp")

    def check_evals(self) -> None:
        path = ROOT / "evals" / "evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.require(isinstance(data, list) and data, "evals/evals.json must be a non-empty list")
        categories = set()
        for idx, case in enumerate(data):
            prefix = f"evals/evals.json[{idx}]"
            for key in ["category", "input", "expected_skill", "should_trigger"]:
                self.require(key in case, f"{prefix}: missing {key}")
            self.require(isinstance(case.get("should_trigger"), bool), f"{prefix}: should_trigger must be boolean")
            if "category" in case:
                categories.add(case["category"])
        missing = REQUIRED_EVAL_CATEGORIES - categories
        self.require(not missing, f"evals/evals.json missing categories: {sorted(missing)}")

    def check_docs_contract(self) -> None:
        required_paths = [
            ROOT / "references" / "results-logging.md",
            ROOT / "guide" / "self-improvement.md",
            ROOT / "evals" / "README.md",
        ]
        for path in required_paths:
            self.require(path.exists(), f"missing required contract doc: {path.relative_to(ROOT)}")

    def check_preflight_gate_contract(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        core_skill = (ROOT / "skills" / "autoconference" / "SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "assets" / "conference_template.md").read_text(encoding="utf-8")
        init_script = (ROOT / "scripts" / "init_conference.py").read_text(encoding="utf-8")

        for phrase in [
            "Mandatory Start Gate",
            "final confirmation",
            "Critic/Devil's Advocate",
            "researcher count",
        ]:
            self.require(phrase in root_skill, f"SKILL.md: missing pre-flight gate phrase {phrase!r}")

        for phrase in [
            "Start Gate: Inputs → Conditions → Final Confirm",
            "Researcher count",
            "If any required input is missing or vague",
            "Do NOT start Phase 1",
        ]:
            self.require(phrase in core_skill, f"skills/autoconference/SKILL.md: missing pre-flight gate phrase {phrase!r}")

        for phrase in ["## Pre-Flight Gate", "**Researcher count:**", "**Final confirmation:** pending", "Do not start Phase 1"]:
            self.require(phrase in template, f"assets/conference_template.md: missing pre-flight gate phrase {phrase!r}")
            self.require(phrase in init_script, f"scripts/init_conference.py: missing pre-flight gate phrase {phrase!r}")

        self.require("--devils-advocate" in init_script, "scripts/init_conference.py: missing --devils-advocate option")
        self.require("--target is required when --mode is metric" in init_script, "scripts/init_conference.py: metric mode target must be required")
        self.require("args.target.strip().lower()" in init_script, "scripts/init_conference.py: placeholder target check must normalize whitespace/case")

    def run(self) -> int:
        self.check_json_files()
        self.check_manifests()
        self.check_skill_frontmatter()
        self.check_markdown_links()
        self.check_examples()
        self.check_evals()
        self.check_docs_contract()
        self.check_preflight_gate_contract()

        if self.errors:
            for error in self.errors:
                print(f"FAIL: {error}")
            print(f"Validation failed: {len(self.errors)} issue(s)")
            return 1
        print("OK: package metadata, docs, examples, evals, and output contracts validated")
        return 0


if __name__ == "__main__":
    sys.exit(Validator().run())
