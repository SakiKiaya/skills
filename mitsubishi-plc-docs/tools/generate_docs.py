#!/usr/bin/env python3
"""
Mitsubishi PLC Documentation Generator

This script generates Markdown documentation from normalized JSON data.
"""

import json
from pathlib import Path

def generate_overview(project_data):
    """Generate project overview"""
    md = f"# Project Overview\n\n"
    md += f"**Project Name:** {project_data.get('name', 'N/A')}\n\n"
    md += f"**PLC Series:** {project_data.get('plc_series', 'N/A')}\n\n"
    md += f"**CPU Model:** {project_data.get('cpu_model', 'N/A')}\n\n"
    md += f"**Software:** {project_data.get('software', 'N/A')}\n\n"
    md += f"**Exported At:** {project_data.get('exported_at', 'N/A')}\n\n"
    return md

def generate_labels(labels_data):
    """Generate labels documentation"""
    md = "# Labels\n\n"
    md += "| Name | Address | Data Type | Scope | Comment |\n"
    md += "|------|---------|-----------|-------|--------|\n"
    for label in labels_data:
        md += f"| {label.get('name', 'N/A')} | {label.get('address', 'N/A')} | {label.get('data_type', 'N/A')} | {label.get('scope', 'N/A')} | {label.get('comment', 'N/A')} |\n"
    return md

def main():
    normalized_dir = Path('exports/normalized')
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    # Load data
    with open(normalized_dir / 'project.json', 'r', encoding='utf-8') as f:
        project = json.load(f)

    with open(normalized_dir / 'labels.json', 'r', encoding='utf-8') as f:
        labels = json.load(f)

    # Generate docs
    overview = generate_overview(project)
    with open(docs_dir / '00_project_overview.md', 'w', encoding='utf-8') as f:
        f.write(overview)

    labels_doc = generate_labels(labels)
    with open(docs_dir / '06_labels.md', 'w', encoding='utf-8') as f:
        f.write(labels_doc)

    print("Documentation generation complete!")

if __name__ == '__main__':
    main()