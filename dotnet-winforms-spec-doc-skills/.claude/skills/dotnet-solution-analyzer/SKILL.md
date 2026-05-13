---
name: dotnet-solution-analyzer
description: Analyze Visual Studio .sln, .csproj, .vbproj, NuGet packages, references, target frameworks, WinForms flags, and project dependencies for C# and VB.NET projects.
version: 0.2.0
allowed-tools: Read Write Edit Bash
---

# dotnet-solution-analyzer

## Purpose

Analyze Visual Studio solution and project metadata for .NET Framework / .NET WinForms repositories.

## Input

- `*.sln`
- `*.csproj`
- `*.vbproj`
- `packages.config`
- `Directory.Build.props`
- `app.config`

## Output

```text
exports/normalized/
  solution.json
  projects.json
  dependencies.json
  diagnostics.json

docs/
  00_solution_overview.md
  01_project_structure.md
```

## Script

Run from repository root:

```bash
python .claude/skills/dotnet-solution-analyzer/scripts/analyze_solution.py . exports/normalized
```

## Rules

- Detect C# and VB.NET projects.
- Detect WinForms projects.
- Detect `.NET Framework` and SDK-style target frameworks when possible.
- Detect AnyCPU/x86/x64 from project configuration.
- Detect ProjectReference.
- Detect NuGet packages from both `packages.config` and `PackageReference`.
- Preserve original project names and source file paths.
- Do not invent missing metadata.
