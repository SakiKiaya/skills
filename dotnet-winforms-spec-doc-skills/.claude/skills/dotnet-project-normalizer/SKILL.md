    ---
    name: dotnet-project-normalizer
    description: Normalize C# and VB.NET WinForms projects into structured JSON IR.
    version: 0.1.0
    ---


# dotnet-project-normalizer

## Purpose

Convert .NET WinForms projects into normalized JSON for downstream AI Agent analysis.

## Supported Input

- *.cs
- *.vb
- *.Designer.cs
- *.Designer.vb
- *.resx
- *.config
- *.settings

## Output

```text
exports/normalized/
  forms.json
  controls.json
  classes.json
  methods.json
  configs.json
  diagnostics.json
```

## Important Rules

- Merge Designer files with logic files.
- Preserve UI tree.
- Preserve control names.
- Preserve source_file and line_range.
- Preserve language type (C# / VB.NET).
- Do not summarize only; build reusable IR.

## Expected IR

```json
{
  "form_name": "MainForm",
  "language": "C#",
  "controls": [],
  "events": []
}
```

