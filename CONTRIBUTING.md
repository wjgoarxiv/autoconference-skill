# Contributing to autoconference-skill

Contributions are welcome — bug fixes, new templates, new examples, documentation improvements, and new subcommands.

---

## How to Contribute

1. **Fork** the repository on GitHub.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the conventions below.
4. **Test** your changes locally (see [Running Tests](#running-tests)).
5. **Commit** with a conventional commit message (see [Commit Messages](#commit-messages)).
6. **Push** your branch and open a pull request against `main`.

---

## Development Setup

```bash
git clone https://github.com/wjgoarxiv/autoconference-skill.git
cd autoconference-skill

# Python 3.8+ required. No external dependencies for core scripts.
python --version

# Optional: install dev tools
pip install black isort pytest
```

---

## Code Style

**Python:**
- Formatter: `black` (default settings, line length 88)
- Import order: `isort` (black-compatible profile)
- Run before committing:
  ```bash
  black scripts/
  isort scripts/
  ```

**Markdown:**
- Match the heading structure and table formatting of existing files.
- Use `**bold**` for field names in tables, backticks for code/filenames.
- No trailing spaces.

---

## Adding a New Subcommand

Subcommands live under `skills/<name>/`. Each subcommand needs:

1. **`skills/<name>/SKILL.md`** — the skill definition that the agent reads. Follow the structure of `SKILL.md` at the root. Include:
   - Purpose and when to use
   - Input format
   - Step-by-step execution protocol
   - Output format

2. **`scripts/<name>.py`** (if scaffolding is needed) — a stdlib-only Python script for initialization or utilities. No external dependencies.

3. **Tests** — add at least one test to `tests/` covering the happy path and one edge case.

4. **Update `README.md`** — add a row to the Templates or Configuration tables if applicable.

---

## Adding a New Template

Templates live under `templates/`. Each template is a `conference.md` pre-configured for a specific use case.

1. Create `templates/<name>.md`. Follow the structure of existing templates (`research-synthesis.md`, `debate-mode.md`, etc.).
2. Required sections: `Goal`, `Mode`, `Success Criteria`, `Researchers`, `Search Space`, `Search Space Partitioning`, `Constraints`, `Current Approach`, `Shared Knowledge`, `Conference Log`.
3. Use `{placeholders}` for values the user must fill in.
4. Add a brief description comment at the top (`> **Template: Name** — one-line description`).
5. Add a row to the Templates table in `README.md`.

---

## Adding a New Example

Examples live under `examples/<name>/`. An example should demonstrate a real, runnable conference.

1. Create `examples/<name>/` containing at minimum:
   - `conference.md` — the filled-in config used for the run
   - `README.md` — brief description, how to reproduce, what the output shows
2. Optionally include output artifacts: `conference_results.tsv`, `synthesis.md`, `final_report.md`, plots.
3. Do **not** commit large binary files. Plots/images should be under 500KB each.
4. Add a row to the examples section in the main `README.md` if appropriate.

---

## Running Tests

```bash
pytest tests/
```

Tests use stdlib only (`unittest`). When adding a test:
- Mirror the existing style in `tests/test_init_conference.py`.
- Test file naming: `tests/test_<module>.py`.
- Each test function name should describe what it checks: `test_<scenario>_<expected_outcome>`.

---

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

**Types:**

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Build, config, dependency changes |
| `test` | Adding or updating tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |

**Examples:**
```
feat(templates): add debate-mode template
fix(scripts): handle missing --target flag gracefully
docs(readme): add comparison table for team mode vs autoconference
test(init_conference): add test for qualitative mode scaffold
```

Scope is optional but recommended. Keep the description under 72 characters. No period at the end.

---

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR.
- Reference any related issue in the PR description.
- Ensure `pytest tests/` passes before opening the PR.
- Templates and examples do not require tests, but should be manually verified to load without errors in your target agent tool.
