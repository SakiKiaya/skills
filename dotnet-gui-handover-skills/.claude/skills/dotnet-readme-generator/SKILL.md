---
name: dotnet-readme-generator
description: Generate enterprise-grade GUI project README.md for onboarding, maintenance, and AI Agent understanding.
version: 0.9.0
allowed-tools: Read Write Edit Bash
---

# dotnet-readme-generator

## Purpose

Generate a chunk-aware enterprise GUI project README.

This README is not a simple GitHub introduction. It is the entry point for:

- new engineer onboarding
- GUI project overview
- architecture summary
- operation guide
- maintenance guide
- AI Agent first reading

## Required Format

Read `references/README_SPEC.md`.

## Output

```text
docs/README.md
```

## Rules

- Must include Mermaid `graph TD`.
- Must include technical stack, project structure, application flow, forms, modules, configuration, common operations, and known issues.
- Must mark inferred content as `推測` or `需人工確認`.
- Must prefer `exports/analysis_chunks/` and `docs/chunks/` when available.
