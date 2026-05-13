#!/usr/bin/env python3
"""
Analyze Visual Studio .sln/.csproj/.vbproj metadata.

Usage:
    python analyze_solution.py <repo_root> <out_dir>

Outputs:
    solution.json
    projects.json
    dependencies.json
    diagnostics.json
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SLN_PROJECT_RE = re.compile(
    r'Project\("\{(?P<type_guid>[^}]+)\}"\)\s*=\s*"(?P<name>[^"]+)",\s*"(?P<path>[^"]+)",\s*"\{(?P<guid>[^}]+)\}"',
    re.IGNORECASE,
)

CSHARP_GUIDS = {"FAE04EC0-301F-11D3-BF4B-00C04F79EFBC", "9A19103F-16F7-4668-BE54-9A1E7A4F7556"}
VB_GUIDS = {"F184B08F-C81C-45F6-A57F-5ABD9991F28F"}
CPP_GUIDS = {"BC8A1FFA-BEE3-4634-8014-F334798102B3"}


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def children_by_name(root: ET.Element, name: str) -> list[ET.Element]:
    return [e for e in root.iter() if strip_ns(e.tag) == name]


def text_of(elem: ET.Element | None) -> str | None:
    if elem is None or elem.text is None:
        return None
    v = elem.text.strip()
    return v if v else None


def rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def language_from_file(path: Path, type_guid: str | None = None) -> str:
    guid = (type_guid or "").upper()
    if path.suffix.lower() == ".csproj" or guid in CSHARP_GUIDS:
        return "C#"
    if path.suffix.lower() == ".vbproj" or guid in VB_GUIDS:
        return "VB.NET"
    if path.suffix.lower() == ".vcxproj" or guid in CPP_GUIDS:
        return "C++"
    return "Unknown"


def read_packages_config(path: Path, repo: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    packages = []
    try:
        root = ET.parse(path).getroot()
        for pkg in root.findall(".//package"):
            packages.append({
                "id": pkg.attrib.get("id"),
                "version": pkg.attrib.get("version"),
                "target_framework": pkg.attrib.get("targetFramework"),
                "source_file": rel(path, repo),
            })
    except Exception as exc:
        packages.append({"error": repr(exc), "source_file": rel(path, repo)})
    return packages


def parse_project(path: Path, repo: Path, sln_info: dict[str, Any] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    dependencies: list[dict[str, Any]] = []
    info = sln_info or {}
    project = {
        "name": info.get("name") or path.stem,
        "language": language_from_file(path, info.get("type_guid")),
        "project_file": rel(path, repo),
        "guid": info.get("guid"),
        "target_framework": None,
        "target_frameworks": [],
        "output_type": None,
        "is_winforms": False,
        "root_namespace": None,
        "assembly_name": None,
        "platforms": [],
        "project_references": [],
        "references": [],
        "nuget_packages": [],
    }

    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        diagnostics.append({"level": "error", "source_file": rel(path, repo), "message": f"Cannot parse project XML: {exc!r}"})
        return project, dependencies, diagnostics

    props = {strip_ns(e.tag): text_of(e) for e in root.iter() if text_of(e)}
    target = props.get("TargetFramework") or props.get("TargetFrameworkVersion")
    project["target_framework"] = target
    if props.get("TargetFrameworks"):
        project["target_frameworks"] = [x.strip() for x in props["TargetFrameworks"].split(";") if x.strip()]
    project["output_type"] = props.get("OutputType")
    project["root_namespace"] = props.get("RootNamespace")
    project["assembly_name"] = props.get("AssemblyName")
    use_winforms = props.get("UseWindowsForms")
    project["is_winforms"] = (
        (use_winforms or "").lower() == "true"
        or (project["output_type"] or "").lower() == "winexe"
        or any("System.Windows.Forms" in (text_of(e) or "") or e.attrib.get("Include") == "System.Windows.Forms" for e in children_by_name(root, "Reference"))
    )

    platforms = set()
    for pg in children_by_name(root, "PropertyGroup"):
        cond = pg.attrib.get("Condition", "")
        for platform in ["AnyCPU", "x86", "x64"]:
            if platform.lower() in cond.replace(" ", "").lower():
                platforms.add(platform)
    project["platforms"] = sorted(platforms)

    for pr in children_by_name(root, "ProjectReference"):
        include = pr.attrib.get("Include")
        item = {
            "include": include,
            "name": text_of(next((c for c in pr if strip_ns(c.tag) == "Name"), None)),
            "project": text_of(next((c for c in pr if strip_ns(c.tag) == "Project"), None)),
            "source_file": rel(path, repo),
        }
        project["project_references"].append(item)
        dependencies.append({"type": "ProjectReference", "project": project["name"], **item})

    for ref in children_by_name(root, "Reference"):
        include = ref.attrib.get("Include")
        hint = text_of(next((c for c in ref if strip_ns(c.tag) == "HintPath"), None))
        item = {"include": include, "hint_path": hint, "source_file": rel(path, repo)}
        project["references"].append(item)
        dependencies.append({"type": "Reference", "project": project["name"], **item})

    for pkg in children_by_name(root, "PackageReference"):
        item = {"id": pkg.attrib.get("Include"), "version": pkg.attrib.get("Version") or text_of(next((c for c in pkg if strip_ns(c.tag) == "Version"), None)), "source_file": rel(path, repo)}
        project["nuget_packages"].append(item)
        dependencies.append({"type": "PackageReference", "project": project["name"], **item})

    pkg_cfg = path.parent / "packages.config"
    for pkg in read_packages_config(pkg_cfg, repo):
        project["nuget_packages"].append(pkg)
        dependencies.append({"type": "packages.config", "project": project["name"], **pkg})

    return project, dependencies, diagnostics


def parse_sln(path: Path, repo: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    projects = []
    for m in SLN_PROJECT_RE.finditer(text):
        p = m.groupdict()
        if Path(p["path"]).suffix.lower() in {".csproj", ".vbproj", ".vcxproj"}:
            projects.append({
                "name": p["name"],
                "path": p["path"].replace("\\", "/"),
                "guid": p["guid"],
                "type_guid": p["type_guid"].upper(),
            })
    return {"name": path.stem, "path": rel(path, repo), "projects": projects}


def main(repo_arg: str, out_arg: str) -> int:
    repo = Path(repo_arg).resolve()
    out = Path(out_arg).resolve()
    out.mkdir(parents=True, exist_ok=True)

    diagnostics: list[dict[str, Any]] = []
    sln_files = sorted(repo.rglob("*.sln"))
    solution = {"name": repo.name, "path": None, "projects": []}
    sln_projects: dict[str, dict[str, Any]] = {}

    if sln_files:
        solution = parse_sln(sln_files[0], repo)
        for p in solution["projects"]:
            sln_projects[(repo / p["path"]).resolve().as_posix().lower()] = p
    else:
        diagnostics.append({"level": "warning", "message": "No .sln file found. Scanning project files directly."})

    project_files = sorted(list(repo.rglob("*.csproj")) + list(repo.rglob("*.vbproj")) + list(repo.rglob("*.vcxproj")))
    projects = []
    dependencies = []

    for pf in project_files:
        sln_info = sln_projects.get(pf.resolve().as_posix().lower())
        project, deps, diags = parse_project(pf, repo, sln_info)
        projects.append(project)
        dependencies.extend(deps)
        diagnostics.extend(diags)

    (out / "solution.json").write_text(json.dumps({"solution": solution}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "projects.json").write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "dependencies.json").write_text(json.dumps(dependencies, ensure_ascii=False, indent=2), encoding="utf-8")

    diag_path = out / "diagnostics.json"
    old = []
    if diag_path.exists():
        try:
            old = json.loads(diag_path.read_text(encoding="utf-8"))
        except Exception:
            old = []
    diag_path.write_text(json.dumps(old + diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote solution analysis to {out}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: analyze_solution.py <repo_root> <out_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
