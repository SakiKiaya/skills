#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json
import re
import sys
from typing import Any

MAX_ITEMS = 300

def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def esc(v: Any) -> str:
    if v in (None, ""):
        return "N/A"
    s = str(v).replace("\n", " ").strip()
    return s[:1200] + "..." if len(s) > 1200 else s

def req(title: str, body: str, scenario: str = "", source: str = "") -> str:
    out = f"### Requirement: {title}\n\n{body.strip()}\n"
    if scenario:
        out += f"\n#### Scenario: {title}\n\n{scenario.strip()}\n"
    if source:
        out += f"\n**Source:** `{source}`\n"
    return out + "\n"

def chunks(chunks_dir: Path, folder: str):
    d = chunks_dir / folder
    if not d.exists():
        return []
    return [load(p, {}) for p in sorted(d.glob("*.json")) if p.name != "index.json"]

def chunk_doc(docs_chunks: Path, chunk: dict[str, Any]) -> str:
    ctype = chunk.get("chunk_type")
    folder = {
        "project": "projects", "form": "forms", "event_flow": "event_flows",
        "method": "methods", "dependency": "dependencies", "config": "configs", "risk": "risks"
    }.get(ctype, f"{ctype}s")
    p = docs_chunks / folder / f"{chunk.get('chunk_id')}.md"
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8", errors="replace").strip()
    text = sanitize_markdown_excerpt(text)
    return truncate_markdown(text, 1000)

def sanitize_markdown_excerpt(text: str) -> str:
    text = re.sub(
        r"```[A-Za-z0-9_-]*\n.*?\n```",
        "> Diagram or code block omitted from OpenSpec excerpt.",
        text,
        flags=re.S,
    )
    lines = []
    for line in text.splitlines():
        if line.startswith("# "):
            lines.append("### " + line[2:])
        elif line.startswith("## "):
            lines.append("#### " + line[3:])
        elif line.startswith("### "):
            lines.append("##### " + line[4:])
        else:
            lines.append(line)
    return "\n".join(lines).strip()

def truncate_markdown(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cutoff = text.rfind("\n", 0, max_chars)
    if cutoff < max_chars // 2:
        cutoff = max_chars
    return text[:cutoff].rstrip() + "\n\n> Excerpt truncated. See the full chunk document."

def main(analysis_dir: str, chunks_dir: str, docs_chunks_dir: str, openspec_dir: str) -> int:
    analysis = Path(analysis_dir)
    chunks_dir = Path(chunks_dir)
    docs_chunks = Path(docs_chunks_dir)
    out = Path(openspec_dir)

    (out / "changes").mkdir(parents=True, exist_ok=True)
    index = load(chunks_dir / "index.json", {"counts": {}})

    project_chunks = chunks(chunks_dir, "projects")
    form_chunks = chunks(chunks_dir, "forms")
    event_chunks = chunks(chunks_dir, "event_flows")
    method_chunks = chunks(chunks_dir, "methods")
    dependency_chunks = chunks(chunks_dir, "dependencies")
    config_chunks = chunks(chunks_dir, "configs")
    risk_chunks = chunks(chunks_dir, "risks")

    projects = load(analysis / "projects.json", [])
    event_flows = load(analysis / "event_flows.json", [])
    methods = load(analysis / "methods.json", [])
    config = load(analysis / "configuration.json", {"files": [], "code_references": []})
    external = load(analysis / "external_dependencies.json", [])
    workflows = load(analysis / "user_workflows.json", [])
    risks = load(analysis / "risks.json", [])

    write(out / "project.md", f"""# Enterprise GUI Project OpenSpec

## Purpose

This OpenSpec workspace describes the current structure and behavior of the analyzed .NET GUI project for AI Agent consumption.

## Source Inputs

- `exports/enterprise_analysis/`
- `exports/analysis_chunks/`
- `docs/chunks/`

## Chunk Counts

```json
{json.dumps(index.get("counts", {}), ensure_ascii=False, indent=2)}
```

## Specs

- `specs/solution-architecture/spec.md`
- `specs/ui-forms/spec.md`
- `specs/event-flow/spec.md`
- `specs/method-flow/spec.md`
- `specs/configuration/spec.md`
- `specs/external-dependencies/spec.md`
- `specs/user-workflow/spec.md`
- `specs/risk-analysis/spec.md`

## Agent Rules

- Treat confirmed source-backed items as current behavior.
- Treat `推測`, assumptions, and low-confidence items as review targets.
- Do not change behavior without creating a proposal under `openspec/changes/`.
""")

    txt = "# Solution Architecture Specification\n\n## Requirements\n\n"
    items = project_chunks or [{"data": {"project": p}, "source_refs": []} for p in projects]
    for c in items[:MAX_ITEMS]:
        p = (c.get("data") or {}).get("project", {})
        name = p.get("name") or c.get("title")
        txt += req(
            f"Project {esc(name)} shall be documented",
            f"The system SHALL include project `{esc(name)}` in the architecture inventory with responsibility `{esc(p.get('responsibility_inference') or '需人工確認')}`.",
            f"- GIVEN an AI Agent reviews project `{esc(name)}`\n- THEN it MUST inspect related project and dependency chunks before modifying module behavior.",
            ", ".join(c.get("source_refs") or [])
        )
    txt += "\n## Assumptions\n\n- Layer and responsibility inference based on names or references MUST be treated as `推測` until verified.\n"
    write(out / "specs/solution-architecture/spec.md", txt)

    txt = "# UI Forms Specification\n\n## Requirements\n\n"
    for c in form_chunks[:MAX_ITEMS]:
        data = c.get("data") or {}
        form = data.get("form_name") or c.get("title")
        txt += req(
            f"Form {esc(form)} shall be documented",
            f"The system SHALL document `{esc(form)}` as a GUI surface with detected events and handler methods.",
            f"- GIVEN the user interacts with `{esc(form)}`\n- THEN event entries and handler methods SHALL be reviewed before UI behavior changes.",
            ", ".join(c.get("source_refs") or [])
        )
        summary = chunk_doc(docs_chunks, c)
        if summary:
            txt += f"\n**Chunk Summary:**\n\n{summary}\n\n"
    if not form_chunks:
        txt += "No form chunks were found. Generate analysis chunks first.\n"
    txt += "\n## Assumptions\n\n- Form responsibility summaries may be inferred from filenames, controls, and event handlers.\n"
    write(out / "specs/ui-forms/spec.md", txt)

    txt = "# Event Flow Specification\n\n## Requirements\n\n"
    items = event_chunks or [{"data": {"event_flow": f}, "source_refs": []} for f in event_flows]
    for c in items[:MAX_ITEMS]:
        f = (c.get("data") or {}).get("event_flow", {})
        entry = f.get("entry") or c.get("title")
        handler = f.get("handler")
        chain = f.get("call_chain")
        txt += req(
            f"{esc(entry)} shall invoke {esc(handler)}",
            f"The system SHALL route `{esc(entry)}` to handler `{esc(handler)}`.",
            f"- GIVEN the GUI event `{esc(entry)}` occurs\n- THEN handler `{esc(handler)}` SHALL execute\n- AND the candidate call chain SHALL be reviewed: `{esc(chain)}`",
            ", ".join(c.get("source_refs") or [])
        )
        summary = chunk_doc(docs_chunks, c)
        if summary:
            txt += f"\n**Chunk Summary:**\n\n{summary}\n\n"
    txt += "\n## Safety Notes\n\n- Timer, async, BackgroundWorker, and device-control event flows MUST be reviewed for re-entry, blocking calls, timeout handling, and UI thread safety.\n"
    write(out / "specs/event-flow/spec.md", txt)

    txt = "# Method Flow Specification\n\n## Requirements\n\n"
    items = method_chunks or [{"data": {"method": m}, "source_refs": []} for m in methods]
    for c in items[:MAX_ITEMS]:
        data = c.get("data") or {}
        m = data.get("method", {})
        purpose = (data.get("purpose_analysis") or [{}])[0]
        name = m.get("name") or c.get("title")
        txt += req(
            f"Method {esc(name)} shall have impact information",
            f"The method `{esc(name)}` SHALL be documented with callers `{esc(m.get('called_by'))}`, callees `{esc(m.get('calls'))}`, inferred purpose `{esc(purpose.get('inferred_purpose'))}`, and side effects `{esc(purpose.get('side_effects') or m.get('side_effects'))}`.",
            f"- WHEN an AI Agent modifies `{esc(name)}`\n- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.",
            ", ".join(c.get("source_refs") or [])
        )
    txt += "\n## Modification Rule\n\n- AI Agents MUST review method callers and callees before changing method behavior.\n"
    write(out / "specs/method-flow/spec.md", txt)

    txt = "# Configuration Specification\n\n## Requirements\n\n"
    if config_chunks:
        for c in config_chunks[:MAX_ITEMS]:
            d = c.get("data") or {}
            source = d.get("path") or d.get("source") or d.get("expression") or c.get("title")
            txt += req(
                f"Configuration source {esc(source)} shall be tracked",
                f"The system SHALL track configuration source or usage `{esc(source)}` as part of runtime behavior.",
                f"- GIVEN deployment or environment changes\n- THEN `{esc(source)}` MUST be reviewed for path, environment, registry, or machine-specific dependencies.",
                ", ".join(c.get("source_refs") or [])
            )
    else:
        for f in (config.get("files") or [])[:MAX_ITEMS]:
            txt += req(f"Configuration file {esc(f.get('path'))} shall be tracked", f"The system SHALL document configuration file `{esc(f.get('path'))}`.")
        for r in (config.get("code_references") or [])[:MAX_ITEMS]:
            txt += req(f"Configuration reference {esc(r.get('source'))}:{esc(r.get('line'))} shall be tracked", f"The system SHALL document in-code configuration reference `{esc(r.get('expression'))}`.")
    txt += "\n## Exclusions\n\n- Skill-generated `.claude/`, `exports/`, `docs/`, and `openspec/` outputs are not application runtime configuration.\n"
    write(out / "specs/configuration/spec.md", txt)

    txt = "# External Dependencies Specification\n\n## Requirements\n\n"
    if dependency_chunks:
        for c in dependency_chunks[:MAX_ITEMS]:
            d = c.get("data") or {}
            name = d.get("dependency_type") or d.get("name") or d.get("target") or c.get("title")
            txt += req(
                f"Dependency {esc(name)} shall be reviewed",
                f"The system SHALL document dependency `{esc(name)}` with its purpose and deployment risk.",
                f"- GIVEN the system is built or deployed\n- THEN dependency `{esc(name)}` MUST be verified for version, runtime availability, x86/x64 compatibility, and initialization failure behavior.",
                ", ".join(c.get("source_refs") or [])
            )
    else:
        for e in external[:MAX_ITEMS]:
            txt += req(f"Dependency {esc(e.get('dependency_type') or e.get('name'))} shall be reviewed", f"The system SHALL review dependency `{esc(e)}` for initialization and deployment risk.")
    write(out / "specs/external-dependencies/spec.md", txt)

    txt = "# User Workflow Specification\n\n## Requirements\n\n"
    if form_chunks or event_chunks:
        for c in (form_chunks[:100] + event_chunks[:200]):
            txt += req(
                f"Workflow chunk {esc(c.get('title'))} shall be reviewable",
                f"The system SHALL make `{esc(c.get('title'))}` available as a workflow or UI-behavior review unit.",
                f"- GIVEN a maintainer reviews GUI behavior\n- THEN chunk `{esc(c.get('chunk_id'))}` MUST provide source references and related chunks."
            )
    else:
        for w in workflows[:MAX_ITEMS]:
            txt += req(
                f"Workflow {esc(w.get('workflow'))} shall be documented",
                f"The system SHALL document workflow `{esc(w.get('workflow'))}` with steps `{esc(w.get('steps'))}`.",
                f"- GIVEN the user performs `{esc(w.get('workflow'))}`\n- THEN success path is `{esc(w.get('success_path'))}`\n- AND failure path is `{esc(w.get('failure_path'))}`"
            )
    write(out / "specs/user-workflow/spec.md", txt)

    txt = "# Risk Analysis Specification\n\n## Requirements\n\n"
    if risk_chunks:
        for c in risk_chunks[:MAX_ITEMS]:
            r = c.get("data") or {}
            txt += req(
                f"Risk {esc(r.get('risk_type'))} shall be reviewed",
                f"The system MUST review `{esc(r.get('risk_type'))}` in `{esc(r.get('source'))}` with evidence `{esc(r.get('evidence'))}`.",
                f"- GIVEN a maintainer modifies code near `{esc(r.get('source'))}`\n- THEN risk `{esc(r.get('risk_type'))}` MUST be considered before implementation.",
                ", ".join(c.get("source_refs") or [])
            )
    else:
        for r in risks[:MAX_ITEMS]:
            txt += req(f"Risk {esc(r.get('risk_type'))} shall be reviewed", f"The system MUST review `{esc(r.get('risk_type'))}` in `{esc(r.get('source'))}` with evidence `{esc(r.get('evidence'))}`.")
    txt += "\n## Required Risk Categories\n\n- God Object / Giant Form\n- UI and logic coupling\n- static / Singleton abuse\n- hardcoded configuration\n- cross-thread UI update\n- event leak\n- circular dependency\n- async deadlock\n"
    write(out / "specs/risk-analysis/spec.md", txt)

    print(f"Wrote OpenSpec files to {out}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: generate_openspec.py <analysis_dir> <analysis_chunks_dir> <docs_chunks_dir> <openspec_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
