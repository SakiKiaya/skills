# Risk Analysis Specification

## Requirements

### Requirement: Risk cross-thread UI risk shall be reviewed

The system MUST review `cross-thread UI risk` in `Forms/MainForm.vb` with evidence `invoke`.

#### Scenario: Risk cross-thread UI risk shall be reviewed

- GIVEN a maintainer modifies code near `Forms/MainForm.vb`
- THEN risk `cross-thread UI risk` MUST be considered before implementation.

**Source:** `Forms/MainForm.vb`

### Requirement: Risk cross-thread UI risk shall be reviewed

The system MUST review `cross-thread UI risk` in `Forms/MainForm.vb` with evidence `begininvoke`.

#### Scenario: Risk cross-thread UI risk shall be reviewed

- GIVEN a maintainer modifies code near `Forms/MainForm.vb`
- THEN risk `cross-thread UI risk` MUST be considered before implementation.

**Source:** `Forms/MainForm.vb`

### Requirement: Risk event leak risk shall be reviewed

The system MUST review `event leak risk` in `Forms/MainForm.vb` with evidence `addhandler`.

#### Scenario: Risk event leak risk shall be reviewed

- GIVEN a maintainer modifies code near `Forms/MainForm.vb`
- THEN risk `event leak risk` MUST be considered before implementation.

**Source:** `Forms/MainForm.vb`

### Requirement: Risk blocking UI risk shall be reviewed

The system MUST review `blocking UI risk` in `Forms/MainForm.vb` with evidence `thread.sleep`.

#### Scenario: Risk blocking UI risk shall be reviewed

- GIVEN a maintainer modifies code near `Forms/MainForm.vb`
- THEN risk `blocking UI risk` MUST be considered before implementation.

**Source:** `Forms/MainForm.vb`


## Required Risk Categories

- God Object / Giant Form
- UI and logic coupling
- static / Singleton abuse
- hardcoded configuration
- cross-thread UI update
- event leak
- circular dependency
- async deadlock
