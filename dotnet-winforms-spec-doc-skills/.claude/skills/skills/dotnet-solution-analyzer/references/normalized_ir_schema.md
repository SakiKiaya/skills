
# Normalized IR Schema

## exports/normalized/solution.json

```json
{
  "solution": {
    "name": "SolutionName",
    "path": "Project.sln",
    "projects": []
  }
}
```

## exports/normalized/projects.json

```json
[
  {
    "name": "ProjectName",
    "language": "C# | VB.NET | C++ | Unknown",
    "project_file": "src/App/App.csproj",
    "target_framework": ".NET Framework 4.8",
    "output_type": "WinExe",
    "is_winforms": true,
    "root_namespace": "",
    "assembly_name": "",
    "platforms": ["AnyCPU", "x86", "x64"],
    "project_references": [],
    "references": [],
    "nuget_packages": []
  }
]
```

## exports/normalized/forms.json

```json
[
  {
    "form_name": "MainForm",
    "namespace": "App.UI",
    "language": "C#",
    "logic_file": "MainForm.cs",
    "designer_file": "MainForm.Designer.cs",
    "resx_file": "MainForm.resx",
    "controls": [],
    "events": []
  }
]
```

## exports/normalized/controls.json

```json
[
  {
    "form": "MainForm",
    "name": "btnStart",
    "type": "System.Windows.Forms.Button",
    "parent": "panelTop",
    "text": "Start",
    "events": {
      "Click": "btnStart_Click"
    },
    "source_file": "MainForm.Designer.cs"
  }
]
```

## exports/normalized/classes.json / methods.json

```json
[
  {
    "name": "MainForm",
    "namespace": "App.UI",
    "language": "C#",
    "kind": "class",
    "source_file": "MainForm.cs",
    "line_range": [10, 300]
  }
]
```
