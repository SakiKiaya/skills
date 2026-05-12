# Skill: mitsubishi-plc-doc-kit

## Purpose
A comprehensive toolkit for generating documentation from Mitsubishi PLC projects exported from GX Works2/GX Works3. This kit provides skills to parse exported text files, normalize data, and generate GitHub-style Markdown documentation.

## When to use
When working with Mitsubishi PLC projects and need to:
- Generate version-controlled documentation
- Analyze project structure and parameters
- Create cross-references and dependency graphs
- Document CPU/module/network configurations
- Parse exported CSV, XML, ST, mnemonic files

## Components

### 1. mitsubishi-plc-export-advisor
Advises on exporting data from GX Works2/GX Works3 for documentation purposes.

### 2. mitsubishi-plc-project-normalizer
Parses exported CSV/TXT/XML/ST/mnemonic files and converts them to normalized JSON structures.

### 3. mitsubishi-plc-doc-generator
Generates comprehensive Markdown documentation from normalized JSON data.

### 4. mitsubishi-plc-parameter-explainer
Provides detailed explanations of CPU, module, and network parameters.

### 5. mitsubishi-plc-structure-analyzer
Analyzes program structure, dependencies, and generates Mermaid diagrams.

## Input Requirements
- Exported text files from GX Works (CSV, XML, ST, mnemonic, reports)
- PLC series information (FX, Q, L, iQ-F, iQ-R)
- Software version (GX Developer, GX Works2, GX Works3)

## Output
- Normalized JSON data structures
- Markdown documentation files
- Mermaid diagrams for structure visualization
- Parameter explanations with impact analysis

## Rules
- Do not attempt to directly parse proprietary .gx3/.gxw project files
- Work only with exported text/CSV/XML/ST data
- Preserve original field names and add standardized fields
- Mark uncertain information as "estimated" or "requires manual verification"
- Generate documentation that can be version-controlled with Git

## Workflow
1. Export data from GX Works using export-advisor guidance
2. Normalize exported files to JSON
3. Generate documentation and diagrams
4. Review and commit to Git for version control

## Limitations
- Cannot directly read Mitsubishi proprietary project formats
- Relies on GX Works export capabilities
- Parameter explanations based on available documentation
- Structure analysis limited to exported data scope