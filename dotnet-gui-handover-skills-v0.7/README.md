# dotnet-gui-handover-skills v0.7

Enterprise-grade .NET GUI reverse engineering and handover documentation Skills.

## Goal

This package upgrades the previous WinForms-focused analyzers into an enterprise GUI handover documentation framework.

Supported targets:

- WinForms
- WPF
- Avalonia
- MAUI
- C#
- VB.NET

## Output Documents

```text
docs/
  01_solution_structure.md
  02_architecture.md
  03_project_dependencies.md
  04_event_flow.md
  05_method_flow.md
  06_configuration.md
  07_user_workflow.md
  08_external_dependencies.md
  09_risk_analysis.md
```

## Output Specs

```text
openspec/
  project.md
  specs/
    solution-architecture/spec.md
    event-flow/spec.md
    method-flow/spec.md
    configuration/spec.md
    external-dependencies/spec.md
    user-workflow/spec.md
    risk-analysis/spec.md
```

## Quick Start

From this package:

```bash
python run_enterprise_analysis.py /path/to/target/repo
```

Or from target repo after copying `.claude/skills`:

```bash
python .claude/skills/dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py . exports/enterprise_analysis
python .claude/skills/dotnet-enterprise-doc-generator/scripts/generate_enterprise_docs.py exports/enterprise_analysis docs
python .claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py exports/enterprise_analysis openspec
```

## Important

This is static analysis. All inferred behavior is marked as candidate data and should be reviewed by engineers.
