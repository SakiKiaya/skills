    ---
    name: dotnet-docs-generator
    description: Generate human-readable architecture and onboarding documentation.
    version: 0.1.0
    ---


# dotnet-docs-generator

## Purpose

Generate human-readable technical documentation for new engineers and maintainers.

## Output

```text
docs/
  README.md
  00_solution_overview.md
  01_project_structure.md
  02_architecture.md
  03_forms_ui_structure.md
  04_event_flow.md
  05_class_method_reference.md
  06_configuration.md
  07_dependencies.md
  10_learning_path_for_new_engineers.md
```

## Documentation Goals

- Lower onboarding cost.
- Explain architecture clearly.
- Explain Forms and UserControls.
- Explain event flow.
- Explain dependencies and configuration.
- Explain build and deployment process.

## Rules

- Prefer tables over large paragraphs.
- Generate Mermaid diagrams.
- Include source file references.
- Separate confirmed behavior from assumptions.
- Explain why important modules exist.

