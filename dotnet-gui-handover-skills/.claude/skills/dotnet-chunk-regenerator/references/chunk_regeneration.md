# Chunk Regeneration Strategy

## Supported chunk types

- project
- form
- event_flow
- method
- dependency
- config
- risk

## Output pattern

```text
docs/chunks/<chunk_type>s/<chunk_id>.md
```

## Purpose

This enables high-quality incremental documentation:

- Re-run only one Form
- Re-run only one Project
- Re-run only one Event Flow
- Re-run only one Method
- Review generated chunk docs before merging into final 01-09 docs
