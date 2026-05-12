# Normalized Schema

## project.json

```json
{
  "project": {
    "name": null,
    "plc_series": null,
    "cpu_model": null,
    "software": null,
    "exported_at": null,
    "source_files": []
  }
}
```

## labels.json

```json
[
  {
    "name": "",
    "scope": "global|local|unknown",
    "program": null,
    "address": null,
    "data_type": null,
    "comment": null,
    "source_file": "",
    "raw": {}
  }
]
```

## devices.json

```json
[
  {
    "device": "M100",
    "comment": "",
    "source_file": "",
    "raw": {}
  }
]
```

## programs.json

```json
[
  {
    "name": "MAIN",
    "language": "ST|LADDER_MNEMONIC|TXT|UNKNOWN",
    "source_file": "",
    "calls": [],
    "devices_read": [],
    "devices_written": [],
    "raw_summary": {}
  }
]
```

## parameters.json

```json
[
  {
    "category": "cpu|module|network|unknown",
    "parameter_name": "",
    "value": "",
    "unit": null,
    "module": null,
    "station": null,
    "source_file": "",
    "raw": {}
  }
]
```
