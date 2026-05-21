#!/usr/bin/env python3
"""Build a registry from Agent Runtime evidence indexes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def list_index_paths(paths: list[str], root: str | None) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            candidate = path / "00_evidence_index.json"
            if candidate.exists():
                found.append(candidate)
        elif path.name == "00_evidence_index.json" and path.exists():
            found.append(path)

    if root:
        root_path = Path(root)
        if root_path.exists():
            found.extend(root_path.rglob("00_evidence_index.json"))

    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in found:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return sorted(deduped, key=lambda p: str(p.parent))


def value(data: dict[str, Any], section: str, key: str, default: Any = "unknown") -> Any:
    section_data = data.get(section)
    if isinstance(section_data, dict):
        candidate = section_data.get(key)
        if candidate not in (None, ""):
            return candidate
    return default


def run_id_from_path(path: Path) -> str:
    parent = path.parent
    return parent.name or str(parent)


def make_relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def build_registry(index_paths: list[Path], output_base: Path) -> dict[str, Any]:
    runs = []
    for index_path in index_paths:
        index = load_json(index_path)
        if not index:
            continue
        run_summary = index.get("run_summary") if isinstance(index.get("run_summary"), dict) else {}
        guard_summary = (
            index.get("guard_summary") if isinstance(index.get("guard_summary"), dict) else {}
        )
        decision_summary = (
            index.get("decision_summary")
            if isinstance(index.get("decision_summary"), dict)
            else {}
        )
        remote_summary = (
            index.get("remote_summary") if isinstance(index.get("remote_summary"), dict) else {}
        )
        run_dir = index_path.parent
        markdown_path = run_dir / "00_evidence_index.md"
        lab_md_path = run_dir / "05_lab_agent_runtime_report.md"
        runs.append(
            {
                "run_id": run_id_from_path(index_path),
                "run_dir": str(run_dir),
                "index_json": make_relative(index_path, output_base),
                "index_markdown": make_relative(markdown_path, output_base)
                if markdown_path.exists()
                else None,
                "lab_markdown_report": make_relative(lab_md_path, output_base)
                if lab_md_path.exists()
                else None,
                "operation_path": index.get("operation_path", "unknown"),
                "scenario_label": run_summary.get("scenario_label", "unknown"),
                "scenario_category": run_summary.get("scenario_category", "unknown"),
                "scenario_description": run_summary.get("scenario_description", "unknown"),
                "scenario_mode": run_summary.get("scenario_mode", "unknown"),
                "frames": run_summary.get("frames", "unknown"),
                "max_total_queue_depth": run_summary.get("max_total_queue_depth", "unknown"),
                "dropped_count": run_summary.get("dropped_count", "unknown"),
                "fallback_count": run_summary.get("fallback_count", "unknown"),
                "deadline_missed_count": run_summary.get("deadline_missed_count", "unknown"),
                "tegrastats_sample_count": run_summary.get(
                    "tegrastats_sample_count", "unknown"
                ),
                "producer_sources": run_summary.get("producer_sources", []),
                "producer_source_count": run_summary.get(
                    "producer_source_count", "unknown"
                ),
                "device_local_producer_count": run_summary.get(
                    "device_local_producer_count", "unknown"
                ),
                "producer_stages": run_summary.get("producer_stages", []),
                "queue_pressure_reason": run_summary.get(
                    "queue_pressure_reason", "unknown"
                ),
                "max_pressure_task": run_summary.get("max_pressure_task", "unknown"),
                "device_local_event_count": run_summary.get(
                    "device_local_event_count", "unknown"
                ),
                "producer_event_count": run_summary.get(
                    "producer_event_count", "unknown"
                ),
                "guard_verdict": guard_summary.get("guard_verdict", "unknown"),
                "severity": guard_summary.get("severity", "unknown"),
                "lab_decision": decision_summary.get("decision", "unknown"),
                "triggered_rules": decision_summary.get("triggered_rules", []),
                "remote_dispatch_status": remote_summary.get("dispatch_status")
                if remote_summary
                else None,
                "remote_selected_worker_id": remote_summary.get("selected_worker_id")
                if remote_summary
                else None,
                "remote_execution_status": remote_summary.get("remote_execution_status")
                if remote_summary
                else None,
                "fallback_final_status": remote_summary.get("fallback_final_status")
                if remote_summary
                else None,
                "remote_final_status": remote_summary.get("final_status")
                if remote_summary
                else None,
            }
        )

    return {
        "schema_version": "inferedge-agent-runtime-run-registry-v1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_count": len(runs),
        "runs": runs,
        "notes": [
            "This registry is derived from 00_evidence_index.json files.",
            "It is a run navigation layer, not a replacement for source evidence contracts.",
            "Use each run's Lab Markdown report for the human-readable deployment context.",
        ],
    }


def md_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "none"
    return str(value)


def write_markdown(registry: dict[str, Any], path: Path) -> None:
    lines = [
        "# Agent Runtime Run Registry",
        "",
        "This registry summarizes multiple Agent Runtime evidence bundles generated by the entrypoint smoke scripts.",
        "It is derived from `00_evidence_index.json` files and does not replace the source contracts.",
        "",
        f"- Run count: {registry['run_count']}",
        f"- Created at: {registry['created_at']}",
        "",
        "## Runs",
        "",
        "| Run | Operation Path | Scenario Label | Category | Mode | Frames | Queue Max | Queue Reason | Max Pressure Task | Dropped | Fallback | Deadline Missed | Tegrastats Samples | Producer Sources | Device-Local Producers | Device-Local Events | Producer Events | Producer Stages | Guard | Lab Decision | Remote |",
        "|---|---|---|---|---|---:|---:|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|---|---|",
    ]
    for run in registry["runs"]:
        index_md = run.get("index_markdown")
        run_label = f"[{run['run_id']}]({index_md})" if index_md else run["run_id"]
        lines.append(
            "| "
            + " | ".join(
                [
                    run_label,
                    md_value(run["operation_path"]),
                    md_value(run["scenario_label"]),
                    md_value(run["scenario_category"]),
                    md_value(run["scenario_mode"]),
                    md_value(run["frames"]),
                    md_value(run["max_total_queue_depth"]),
                    md_value(run["queue_pressure_reason"]),
                    md_value(run["max_pressure_task"]),
                    md_value(run["dropped_count"]),
                    md_value(run["fallback_count"]),
                    md_value(run["deadline_missed_count"]),
                    md_value(run["tegrastats_sample_count"]),
                    md_value(run["producer_sources"]),
                    md_value(run["device_local_producer_count"]),
                    md_value(run["device_local_event_count"]),
                    md_value(run["producer_event_count"]),
                    md_value(run["producer_stages"]),
                    f"{md_value(run['guard_verdict'])}/{md_value(run['severity'])}",
                    md_value(run["lab_decision"]),
                    _remote_cell(run),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Keep run bundles local or in explicit evidence docs; do not commit large generated output directories by default.",
            "- Use this registry to compare repeat smoke runs such as 96-frame, 5-minute, and remote fallback evidence.",
            "- Missing fields are preserved as `unknown` so partial run bundles can still be inspected.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _remote_cell(run: dict[str, Any]) -> str:
    dispatch = run.get("remote_dispatch_status")
    selected = run.get("remote_selected_worker_id")
    remote_status = run.get("remote_execution_status")
    fallback_status = run.get("fallback_final_status")
    if all(value in (None, "", "unknown") for value in (dispatch, selected, remote_status, fallback_status)):
        return "-"
    parts = [
        f"dispatch={dispatch}" if dispatch not in (None, "", "unknown") else None,
        f"worker={selected}" if selected not in (None, "", "unknown") else None,
        f"remote={remote_status}" if remote_status not in (None, "", "unknown") else None,
        f"fallback={fallback_status}" if fallback_status not in (None, "", "unknown") else None,
    ]
    return ", ".join(part for part in parts if part)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a registry from Agent Runtime 00_evidence_index.json files."
    )
    parser.add_argument(
        "--run-dir",
        action="append",
        default=[],
        help="Run output directory or direct 00_evidence_index.json path. Can be repeated.",
    )
    parser.add_argument(
        "--scan-root",
        help="Directory to scan recursively for 00_evidence_index.json files.",
    )
    parser.add_argument("--output-json", required=True, help="Registry JSON output path")
    parser.add_argument(
        "--output-md",
        required=True,
        help="Registry Markdown output path",
    )
    args = parser.parse_args()

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_base = output_md.parent.resolve()

    index_paths = list_index_paths(args.run_dir, args.scan_root)
    registry = build_registry(index_paths, output_base=output_base)
    output_json.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(registry, output_md)
    print(f"wrote {output_json}")
    print(f"wrote {output_md}")
    print(f"indexed runs: {registry['run_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
