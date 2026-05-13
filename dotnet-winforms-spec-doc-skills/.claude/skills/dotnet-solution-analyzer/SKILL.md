    ---
    name: dotnet-solution-analyzer
    description: Analyze .sln, .csproj, .vbproj, NuGet, platform targets, and project dependencies.
    version: 0.1.0
    ---


# dotnet-solution-analyzer

## Purpose

Analyze Visual Studio solution structure for .NET Framework / .NET WinForms projects.

Supports:

- C#
- VB.NET
- WinForms
- Class Library
- Native interop projects

## Input

- *.sln
- *.csproj
- *.vbproj
- packages.config
- Directory.Build.props
- app.config

## Output

Write:

```text
exports/normalized/
  solution.json
  projects.json
  dependencies.json

docs/
  00_solution_overview.md
  01_project_structure.md
```

## Rules

- Detect C# and VB.NET projects.
- Detect WinForms projects.
- Detect AnyCPU/x86/x64.
- Detect ProjectReference.
- Detect NuGet packages.
- Preserve original project names.
- Preserve source file paths.
- Do not invent missing metadata.

