---
name: dotnet-architecture-doc-generator
description: Generate detailed architecture documentation with block diagrams and module responsibility allocation for .NET WinForms projects.
version: 0.6.0
allowed-tools: Read Write Edit Bash
---

# dotnet-architecture-doc-generator

## Purpose

Generate a detailed `docs/02_architecture.md` document.

## Output Requirements

- Full block architecture diagram
- Project/module reference diagram
- External dependency diagram
- Module responsibility table
- Layer assignment table
- Device/backend interaction overview
- Review notes and assumptions

## Rules

- Use Mermaid flowchart diagrams.
- Show project references and assembly/package references separately.
- Mark naming-based inference as `推測`.
- Do not invent module responsibilities without evidence.
