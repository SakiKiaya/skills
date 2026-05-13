# Analysis Chunk Schema

Each chunk should include:

```json
{
  "chunk_type": "project|form|event_flow|method|dependency|config|risk|source_file|large_file_task",
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
  source_files/
  large_file_tasks/
```

## Source File Chunk

`source_file` chunks summarize one scanned source file and include file size, method count, class count, related methods, related events, and risks.

## Large File Task Chunk

`large_file_task` chunks are generated only when `source_files.json` reports `line_count > 1000`.

Each task includes:

- `source_file`
- `task_no`
- `line_range.start`
- `line_range.end`
- `context_line_range.start`
- `context_line_range.end`
- `context_before_lines`
- `context_after_lines`
- `split_reason`
- `task_strategy`
- `semantic_blocks`
- methods and events inside the line range
- related risks
- review goals

## Splitting Strategy

Large-file task splitting uses this order:

1. class-aware ranges
2. method-aware ranges inside oversized classes
3. switch-aware ranges inside oversized methods
4. line-window fallback for code that cannot be mapped to semantic blocks

Task ranges are line-based, not character-based. Raw words are not split.
