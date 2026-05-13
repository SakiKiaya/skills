# Configuration Specification

## Requirements

### Requirement: Configuration source App.config shall be tracked

The system SHALL track configuration source or usage `App.config` as part of runtime behavior.

#### Scenario: Configuration source App.config shall be tracked

- GIVEN deployment or environment changes
- THEN `App.config` MUST be reviewed for path, environment, registry, or machine-specific dependencies.

**Source:** `App.config`

### Requirement: Configuration source Forms/MainForm.vb shall be tracked

The system SHALL track configuration source or usage `Forms/MainForm.vb` as part of runtime behavior.

#### Scenario: Configuration source Forms/MainForm.vb shall be tracked

- GIVEN deployment or environment changes
- THEN `Forms/MainForm.vb` MUST be reviewed for path, environment, registry, or machine-specific dependencies.

**Source:** `Forms/MainForm.vb`

### Requirement: Configuration source Forms/MainForm.vb shall be tracked

The system SHALL track configuration source or usage `Forms/MainForm.vb` as part of runtime behavior.

#### Scenario: Configuration source Forms/MainForm.vb shall be tracked

- GIVEN deployment or environment changes
- THEN `Forms/MainForm.vb` MUST be reviewed for path, environment, registry, or machine-specific dependencies.

**Source:** `Forms/MainForm.vb`


## Exclusions

- Skill-generated `.claude/`, `exports/`, `docs/`, and `openspec/` outputs are not application runtime configuration.
