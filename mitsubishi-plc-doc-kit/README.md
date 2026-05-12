# Mitsubishi PLC Documentation Kit Skill

This repository contains a Claude-compatible Skill for documenting Mitsubishi PLC projects from GX Works2/GX Works3 exported files.

## Layout

```text
skills/mitsubishi-plc-doc-kit/SKILL.md
skills/mitsubishi-plc-doc-kit/references/
skills/mitsubishi-plc-doc-kit/examples/
skills/mitsubishi-plc-doc-kit/scripts/
.claude/skills/mitsubishi-plc-doc-kit/SKILL.md
```

## Gemini CLI usage

```bash
gemini -p "Read skills/mitsubishi-plc-doc-kit/SKILL.md and generate documentation from exports/raw into docs/ and exports/normalized. Follow the skill rules strictly."
```

## Claude Code usage

Copy the skill directory to your Claude skills folder or keep the included `.claude/skills` layout inside a project.

```bash
mkdir -p ~/.claude/skills
cp -r skills/mitsubishi-plc-doc-kit ~/.claude/skills/
```
