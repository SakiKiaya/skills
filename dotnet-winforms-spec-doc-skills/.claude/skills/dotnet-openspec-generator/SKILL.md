    ---
    name: dotnet-openspec-generator
    description: Generate OpenSpec-compatible specifications for AI Agents.
    version: 0.1.0
    ---


# dotnet-openspec-generator

## Purpose

Generate OpenSpec-compatible specifications from normalized project IR.

## Output

```text
openspec/
  project.md
  specs/
    solution-architecture/spec.md
    ui-forms/spec.md
    business-logic/spec.md
    dependencies/spec.md
```

## Spec Rules

- Use SHALL / MUST wording.
- Include Scenario sections.
- Separate assumptions from confirmed behavior.
- Do not convert guesses into requirements.
- Preserve source references.

## Example

```markdown
# UI Forms Specification

## Requirements

### Requirement: Start inspection flow

The system SHALL start image acquisition when the operator clicks the Start button.

#### Scenario: Operator starts inspection

- GIVEN the MainForm is loaded
- WHEN the operator clicks btnStart
- THEN the system SHALL call CameraManager.StartGrab
```

