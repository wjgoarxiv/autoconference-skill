# Eval Coverage

`evals/evals.json` contains lightweight routing and safety scenarios for this skill suite. These are not model-scored automatically in this repo; they are structured cases that downstream skill evaluators can load.

## Required Fields

| Field | Meaning |
|-------|---------|
| `category` | Scenario family validated by `scripts/validate_package.py` |
| `input` | User prompt to route or reject |
| `expected_skill` | Expected skill or alternative skill |
| `should_trigger` | Whether this skill suite should trigger |
| `note` | Optional rationale or safety expectation |

## Required Categories

- `routing`
- `subcommand`
- `negative`
- `user_confusion`
- `resume_retry`
- `prompt_injection`
- `install_platform`

Run `python scripts/validate_package.py` from the repository root to confirm coverage.
