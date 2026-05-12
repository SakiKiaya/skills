# Normalized JSON Schema Reference

## project.json

```json
{
  "project": {
    "name": "",
    "plc_series": "",
    "cpu_model": "",
    "software": "GX Works2 or GX Works3",
    "exported_at": "",
    "source_files": []
  }
}
```

## labels.json

```json
{
  "labels": [
    {
      "name": "",
      "scope": "global|local|unknown",
      "program": "",
      "data_type": "",
      "address": "",
      "initial_value": "",
      "comment": "",
      "source_file": "",
      "source_row": 0,
      "raw": {}
    }
  ]
}
```

## parameters.json

```json
{
  "parameters": [
    {
      "category": "cpu|module|network|io|unknown",
      "module": "",
      "parameter_name": "",
      "original_value": "",
      "interpreted_value": "",
      "comment": "",
      "source_file": "",
      "source_row": 0,
      "raw": {}
    }
  ]
}
```

## diagnostics.json

```json
{
  "diagnostics": [
    {
      "level": "info|warning|error",
      "source_file": "",
      "source_row": 0,
      "message": "",
      "raw": ""
    }
  ]
}
```
