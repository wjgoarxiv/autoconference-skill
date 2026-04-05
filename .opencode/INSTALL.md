# Installing autoconference-skill via OpenCode CLI

## Prerequisites

- [OpenCode](https://github.com/sst/opencode) installed and authenticated
- Git available on `$PATH`

## Install

```bash
# Clone the repository
git clone https://github.com/wjgoarxiv/autoconference-skill
cd autoconference-skill

# Register the skill with OpenCode
opencode skill add .
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

After installation, invoke the conference from any project:

```bash
opencode run autoconference "What are the limits of transformer scaling?"
```

For the interactive plan wizard:

```bash
opencode run autoconference:plan
```

For adversarial debate mode:

```bash
opencode run autoconference:debate "LLMs can reason"
```

## Uninstall

```bash
opencode skill remove autoconference
```
