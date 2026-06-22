# Installing autoconference-skill via Codex CLI

## Prerequisites

- [Codex CLI](https://github.com/openai/codex) installed and authenticated
- Git available on `$PATH`

## Install

```bash
# Clone the repository
git clone https://github.com/wjgoarxiv/autoconference-skill
cd autoconference-skill

# Register the skill with Codex
codex skill install .
```

## Skill directory

Keep the repository layout intact. The root router dispatches into `skills/`, and helper scripts live in `scripts/`:

| File | Purpose |
|------|---------|
| `SKILL.md` | Root router and command table |
| `skills/*/SKILL.md` | Command-specific protocols |
| `references/` | Shared output contracts and agent prompts |
| `scripts/autoconference-loop.sh` | Core conference loop |
| `scripts/init_conference.py` | Pre-flight setup wizard |
| `scripts/check_conference.sh` | Status / checkpoint checker |
| `scripts/validate_package.py` | Zero-dependency package/doc/eval validator |
| `scripts/style_presets.py` | Output style configuration |

## Usage

After installation, invoke via Codex:

```bash
codex run autoconference "What are the limits of transformer scaling?"
```

For the full 8-step setup wizard:

```bash
codex run autoconference:plan
```

## Uninstall

```bash
codex skill remove autoconference
```
