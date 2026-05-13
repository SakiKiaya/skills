# Analysis Chunk Schema

Each chunk should include:

```json
{
  "chunk_type": "project|form|event_flow|method|dependency|config|risk",
  "chunk_id": "stable-id",
  "title": "Human readable title",
  "summary": "",
  "source_refs": [],
  "data": {},
  "related_chunks": []
}
```

## Folder Layout

```text
exports/analysis_chunks/
  index.json
  projects/
  forms/
  event_flows/
  methods/
  dependencies/
  configs/
  risks/
```
