---
name: dotnet-configuration-analyzer
description: Analyze real project configuration files and in-code configuration paths while ignoring generated skill intermediate files.
version: 0.6.0
allowed-tools: Read Write Edit Bash
---

# dotnet-configuration-analyzer

## Purpose

Analyze configuration sources that are meaningful to the target .NET / WinForms project.

This skill intentionally ignores generated analysis artifacts:

- `.claude/`
- `exports/`
- `docs/`
- `openspec/`

## Outputs

```text
exports/normalized/config_sources.json
docs/06_configuration.md
```

## Focus

- `App.config` / `app.config`
- `*.exe.config` / `*.dll.config`
- `Properties/Settings.settings`
- `My Project/Settings.settings`
- `Settings/`, `Config/`, `Configuration/`
- in-code config references such as `ConfigurationManager.AppSettings`, `Settings.Default`, `My.Settings`, `File.ReadAllText`, `XDocument.Load`, `JsonConvert.DeserializeObject`

## Rules

- Do not document skill-generated intermediate files as application settings.
- Preserve source file and line number.
- Separate confirmed config files from inferred config path candidates.
