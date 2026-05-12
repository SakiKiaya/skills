---
name: mitsubishi-plc-export-advisor
description: Plan what to export from Mitsubishi GX Works2/GX Works3 projects for Git version control and documentation. Use when the user asks how to export Mitsubishi PLC project data, prepare raw files, or document GX Works projects.
version: 0.2.0
---

# Mitsubishi PLC Export Advisor

## Purpose

Plan a text-based export workflow for Mitsubishi PLC projects so downstream skills can generate project structure and parameter documentation.

## Core rule

Do not assume direct parsing of proprietary GX Works project files such as `.gx3`, `.gxw`, `.gppw`, or packaged project archives. Treat GX Works as the exporter and require text or semi-structured files as input.

## Required questions when information is missing

Ask only for details that materially change the export plan:

- GX Works version: GX Developer, GX Works2, GX Works3
- PLC family: FX, Q, L, iQ-F, iQ-R
- Programming languages used: Ladder, ST, FBD, SFC, FB, Function
- Whether the user needs Git diff only, documentation only, or both

If the user does not know, provide a generic GX Works2/GX Works3 export plan.

## Recommended export folders

Create this structure in the user's repository:

```text
exports/raw/
  project_info/
  programs/
  labels/
  device_comments/
  parameters/
  module_config/
  network/
  cross_reference/
  reports/
exports/normalized/
docs/
```

## Minimum export set

For MVP documentation, request:

1. Global Label CSV
2. Local Label CSV, if local labels are used
3. Device Comment CSV
4. Program source as ST, TXT, or mnemonic CSV
5. CPU parameter report or CSV
6. Module parameter report or CSV
7. Network parameter report or CSV, if communication modules are used
8. Cross Reference CSV, if available
9. Compile/build report, if available

## Output format

Return:

1. Export checklist
2. Target folder path for each export
3. Why the export is needed
4. Which downstream skill consumes it
5. Items requiring manual confirmation

## Downstream skills

- Use `mitsubishi-plc-project-normalizer` after raw files are exported.
- Use `mitsubishi-plc-doc-generator` after normalized JSON exists.
- Use `mitsubishi-plc-parameter-explainer` for CPU/module/network parameter documentation.
- Use `mitsubishi-plc-structure-analyzer` for program tree, cross reference, and Mermaid diagrams.
