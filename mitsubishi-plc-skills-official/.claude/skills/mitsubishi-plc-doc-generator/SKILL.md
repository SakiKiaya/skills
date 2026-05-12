---
name: mitsubishi-plc-doc-generator
description: Generate Markdown documentation for Mitsubishi PLC projects from normalized JSON. Use after exports/normalized exists and the user wants project overview, structure, labels, devices, parameters, or GitHub-style docs.
version: 0.2.0
allowed-tools: Read Write Edit Bash
---

# Mitsubishi PLC Doc Generator

## Purpose

Generate GitHub-style Markdown documentation from normalized Mitsubishi PLC JSON files.

## Input

Read:

```text
exports/normalized/
  project.json
  programs.json
  labels.json
  devices.json
  parameters.json
  modules.json
  networks.json
  cross_reference.json
  diagnostics.json
```

## Output

Write:

```text
docs/
  README.md
  00_project_overview.md
  01_system_configuration.md
  02_cpu_parameters.md
  03_module_parameters.md
  04_network_parameters.md
  05_program_structure.md
  06_labels.md
  07_device_comments.md
  08_alarm_list.md
  09_cross_reference.md
  10_diagnostics.md
```

## Rules

1. Do not invent missing values.
2. Use `N/A` when a field is absent.
3. If meaning is inferred from name/comment, label it as `推測`.
4. Prefer device comments and label comments over language model guesses.
5. Preserve source file paths in tables where useful.
6. Generate Mermaid diagrams only from known relationships.
7. Put parse warnings and missing data in `10_diagnostics.md`.

## Script

A starter script is included:

```bash
python .claude/skills/mitsubishi-plc-doc-generator/scripts/generate_docs.py exports/normalized docs
```

## References

- See `references/doc_template.md` for document layout.
