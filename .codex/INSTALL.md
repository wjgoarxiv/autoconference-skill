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

All runnable components live in `scripts/`:

| File | Purpose |
|------|---------|
| `scripts/autoconference-loop.sh` | Core conference loop |
| `scripts/init_conference.py` | Pre-flight setup wizard |
| `scripts/check_conference.sh` | Status / checkpoint checker |
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
