from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
RUNTIME_INTELLIGENCE_ARTIFACT_ORDER = [
    "examples/regression/fixture_matrix.json",
    "runtime_intelligence_bundle_manifest_gate_summary.md",
    "edgeenv_runtime_regression.md",
    "edgeenv_runtime_regression.html",
    "runtime_anomaly_summary.md",
    "runtime_anomaly_summary.html",
    "runtime_anomaly_gate_summary.md",
    "runtime_intelligence_ci_artifact_gate_summary.md",
    "aiguard_edgeenv_handoff_alignment.json",
    "aiguard_edgeenv_handoff_alignment.md",
]
RUNTIME_INTELLIGENCE_SMOKE_GATE_ORDER = [
    "EdgeEnv regression replay fixture matrix gate",
    "Lab Runtime Intelligence artifact smoke",
    "Lab Runtime Intelligence report marker gate",
]
JETSON_SHORT_REPLAY_MEAN_MS = "155.86"
JETSON_SHORT_REPLAY_P95_MS = "156.877"
JETSON_SHORT_REPLAY_MAX_TEMP_C = "45.5"
JETSON_SHORT_REPLAY_MAX_RAM_MB = "1000"
JETSON_SUSTAINED_REPLAY_MEAN_MS = "152.77"
JETSON_SUSTAINED_REPLAY_P95_MS = "156.948"
JETSON_SUSTAINED_REPLAY_MAX_TEMP_C = "50.375"
JETSON_SUSTAINED_REPLAY_MAX_RAM_MB = "1038"


def load_script_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def assert_markers_in_order(
    text: str, markers: list[str], *, label: str
) -> None:
    previous_index = -1
    previous_marker = "<start>"
    for marker in markers:
        current_index = text.find(marker, previous_index + 1)
        assert current_index != -1, (
            f"{label}: expected marker {marker!r} after "
            f"{previous_marker!r} at offset {previous_index}"
        )
        previous_index = current_index
        previous_marker = marker


def assert_jetson_p95_evidence_terms(text: str) -> None:
    assert (
        f"96 frames, {JETSON_SHORT_REPLAY_MEAN_MS} ms mean, "
        f"{JETSON_SHORT_REPLAY_P95_MS} ms p95"
    ) in text
    assert (
        f"Vision mean {JETSON_SUSTAINED_REPLAY_MEAN_MS} ms, "
        f"p95 {JETSON_SUSTAINED_REPLAY_P95_MS} ms"
    ) in text


def assert_jetson_max_resource_evidence_terms(text: str) -> None:
    assert (
        f"max {JETSON_SHORT_REPLAY_MAX_TEMP_C} C / "
        f"{JETSON_SHORT_REPLAY_MAX_RAM_MB} MB"
    ) in text
    assert (
        f"max {JETSON_SUSTAINED_REPLAY_MAX_TEMP_C} C / "
        f"{JETSON_SUSTAINED_REPLAY_MAX_RAM_MB} MB"
    ) in text


def assert_jetson_comma_resource_evidence_terms(text: str) -> None:
    assert (
        f"{JETSON_SHORT_REPLAY_MAX_TEMP_C} C, "
        f"{JETSON_SHORT_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text
    assert (
        f"{JETSON_SUSTAINED_REPLAY_MAX_TEMP_C} C, "
        f"{JETSON_SUSTAINED_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text


def assert_readme_top_jetson_p95_evidence_terms(text: str) -> None:
    assert (
        "Real device replay | Jetson Orin Nano ONNX replay: "
        f"{JETSON_SHORT_REPLAY_MEAN_MS} ms mean, "
        f"{JETSON_SHORT_REPLAY_P95_MS} ms p95, "
        f"{JETSON_SHORT_REPLAY_MAX_TEMP_C} C, "
        f"{JETSON_SHORT_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text
    assert (
        "Sustained operation smoke | 5-minute-class Jetson replay: "
        f"3600 frames, {JETSON_SUSTAINED_REPLAY_MEAN_MS} ms mean, "
        f"{JETSON_SUSTAINED_REPLAY_P95_MS} ms p95, "
        f"{JETSON_SUSTAINED_REPLAY_MAX_TEMP_C} C, "
        f"{JETSON_SUSTAINED_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text


def assert_korean_readme_jetson_p95_evidence_terms(text: str) -> None:
    assert (
        f"Jetson device-local replay | 96 frames, {JETSON_SHORT_REPLAY_MEAN_MS} "
        f"ms mean, {JETSON_SHORT_REPLAY_P95_MS} ms p95, "
        f"max {JETSON_SHORT_REPLAY_MAX_TEMP_C} C / "
        f"{JETSON_SHORT_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text
    assert (
        "Jetson 5-minute-class sustained replay | 3600 frames, "
        f"Vision mean {JETSON_SUSTAINED_REPLAY_MEAN_MS} ms, "
        f"p95 {JETSON_SUSTAINED_REPLAY_P95_MS} ms, "
        f"max {JETSON_SUSTAINED_REPLAY_MAX_TEMP_C} C / "
        f"{JETSON_SUSTAINED_REPLAY_MAX_RAM_MB} MB RAM"
    ) in text


def assert_readme_quick_scan_snapshot_terms(text: str) -> None:
    assert "Jetson operation-summary quick-scan registry" in text
    assert "linked metric snapshots" in text or "연결된 metric snapshot" in text
    assert f"`{JETSON_SHORT_REPLAY_MEAN_MS}` / `{JETSON_SHORT_REPLAY_P95_MS}` ms" in text
    assert (
        f"`{JETSON_SHORT_REPLAY_MAX_TEMP_C} C` / "
        f"`{JETSON_SHORT_REPLAY_MAX_RAM_MB} MB`"
    ) in text
    assert (
        f"`{JETSON_SUSTAINED_REPLAY_MEAN_MS}` / "
        f"`{JETSON_SUSTAINED_REPLAY_P95_MS}` ms"
    ) in text
    assert (
        f"`{JETSON_SUSTAINED_REPLAY_MAX_TEMP_C} C` / "
        f"`{JETSON_SUSTAINED_REPLAY_MAX_RAM_MB} MB`"
    ) in text


def assert_linked_quick_scan_snapshot_context(text: str) -> None:
    assert "linked metric snapshot" in text or "연결된 metric snapshot" in text
    assert_short_jetson_source_values(text)
    assert_sustained_jetson_source_values(text)


def assert_jetson_reviewer_navigation_terms(
    text: str,
    *,
    representative_marker: str,
    resource_style: str,
    extra_markers: tuple[str, ...] = (),
    require_metric_owner_boundary: bool = False,
) -> None:
    normalized_lower = text.lower()

    assert representative_marker.lower() in normalized_lower
    assert "latest registry" in normalized_lower
    assert "quick-scan navigation" in normalized_lower
    assert "operation quick scan summary" in normalized_lower
    assert_jetson_p95_evidence_terms(text)
    if resource_style == "comma":
        assert_jetson_comma_resource_evidence_terms(text)
    elif resource_style == "max":
        assert_jetson_max_resource_evidence_terms(text)
    else:
        raise AssertionError(f"unsupported Jetson resource style: {resource_style}")
    assert_linked_quick_scan_snapshot_context(text)
    if require_metric_owner_boundary:
        assert "metric record owner" in normalized_lower
    for marker in extra_markers:
        assert marker in text
    assert "queue/deadline/fallback pressure" in text
    assert "production runtime operation proof" in text


def assert_short_jetson_source_values(text: str) -> None:
    assert JETSON_SHORT_REPLAY_MEAN_MS in text
    assert JETSON_SHORT_REPLAY_P95_MS in text
    assert JETSON_SHORT_REPLAY_MAX_TEMP_C in text
    assert JETSON_SHORT_REPLAY_MAX_RAM_MB in text


def assert_sustained_jetson_source_values(text: str) -> None:
    assert JETSON_SUSTAINED_REPLAY_MEAN_MS in text
    assert JETSON_SUSTAINED_REPLAY_P95_MS in text
    assert JETSON_SUSTAINED_REPLAY_MAX_TEMP_C in text
    assert JETSON_SUSTAINED_REPLAY_MAX_RAM_MB in text


def section_by_heading(text: str, heading: str) -> str:
    start = text.find(heading)
    assert start != -1, f"expected section heading {heading!r}"
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


def local_link_target(target: str) -> str | None:
    target = normalized_link_target(target)
    if target.startswith(("http://", "https://", "mailto:")):
        return None
    path_without_fragment = target.split("#", 1)[0]
    if not path_without_fragment:
        return None
    return path_without_fragment


def normalized_link_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        return target[1:-1]
    return target


def github_heading_slug(heading: str) -> str:
    slug_chars = []
    for char in heading.strip().lower():
        if char.isalnum():
            slug_chars.append(char)
        elif char.isspace() or char == "-":
            slug_chars.append("-")
    return re.sub(r"-+", "-", "".join(slug_chars)).strip("-")


def markdown_heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in text.splitlines():
        match = MARKDOWN_HEADING_RE.match(line)
        if not match:
            continue

        base_slug = github_heading_slug(match.group(2))
        if not base_slug:
            continue
        count = counts.get(base_slug, 0)
        counts[base_slug] = count + 1
        anchors.add(base_slug if count == 0 else f"{base_slug}-{count}")
    return anchors


def assert_local_links_exist(doc_path: str, section_heading: str) -> None:
    source_path = ROOT / doc_path
    section = section_by_heading(
        source_path.read_text(encoding="utf-8"), section_heading
    )
    links = [
        link
        for link in (
            local_link_target(match.group(1))
            for match in MARKDOWN_LINK_RE.finditer(section)
        )
        if link is not None
    ]

    assert links, f"{doc_path}: expected local reviewer path links"
    for link in links:
        target_path = source_path.parent / link
        assert target_path.exists(), (
            f"{doc_path} {section_heading}: missing local link target "
            f"{link!r} -> {target_path}"
        )


def assert_local_markdown_link_fragments_exist(
    doc_path: str, section_heading: str
) -> None:
    source_path = ROOT / doc_path
    section = section_by_heading(
        source_path.read_text(encoding="utf-8"), section_heading
    )
    checked_fragments = []
    for match in MARKDOWN_LINK_RE.finditer(section):
        target = normalized_link_target(match.group(1))
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if "#" not in target:
            continue
        link_path, fragment = target.split("#", 1)
        if not fragment:
            continue

        target_path = source_path if not link_path else source_path.parent / link_path
        if target_path.suffix.lower() != ".md":
            continue

        anchors = markdown_heading_anchors(target_path.read_text(encoding="utf-8"))
        checked_fragments.append(target)
        assert fragment in anchors, (
            f"{doc_path} {section_heading}: missing heading anchor "
            f"#{fragment!r} in {target_path}"
        )

    assert checked_fragments, (
        f"{doc_path} {section_heading}: expected local Markdown anchor links"
    )


def markdown_docs() -> list[Path]:
    return sorted(
        path
        for path in [
            ROOT / "README.md",
            ROOT / "README.ko.md",
            *ROOT.glob("docs/**/*.md"),
        ]
        if path.exists()
    )


def markdown_links(text: str) -> list[str]:
    links: list[str] = []
    in_code_block = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        links.extend(match.group(1) for match in MARKDOWN_LINK_RE.finditer(line))
    return links


def test_repo_local_markdown_links_are_resolvable() -> None:
    checked_links = []
    checked_fragments = []

    for source_path in markdown_docs():
        source_text = source_path.read_text(encoding="utf-8")
        for raw_target in markdown_links(source_text):
            target = normalized_link_target(raw_target)
            if target.startswith(("http://", "https://", "mailto:")):
                continue

            link_path, _, fragment = target.partition("#")
            if not link_path and not fragment:
                continue

            target_path = (
                source_path if not link_path else source_path.parent / link_path
            )
            checked_links.append(f"{source_path.relative_to(ROOT)} -> {target}")
            assert target_path.exists(), (
                f"{source_path.relative_to(ROOT)}: missing local link target "
                f"{target!r} -> {target_path}"
            )

            if fragment and target_path.suffix.lower() == ".md":
                anchors = markdown_heading_anchors(
                    target_path.read_text(encoding="utf-8")
                )
                checked_fragments.append(
                    f"{source_path.relative_to(ROOT)} -> {target}"
                )
                assert fragment in anchors, (
                    f"{source_path.relative_to(ROOT)}: missing heading anchor "
                    f"#{fragment!r} in {target_path}"
                )

    assert checked_links, "expected repo-local Markdown links to validate"
    assert checked_fragments, "expected repo-local Markdown anchor links to validate"


def test_marker_order_helper_reports_context_for_missing_marker() -> None:
    try:
        assert_markers_in_order(
            "alpha beta",
            ["alpha", "gamma"],
            label="sample reviewer path",
        )
    except AssertionError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing marker assertion")

    assert "sample reviewer path" in message
    assert "'gamma'" in message
    assert "'alpha'" in message


def test_local_link_helper_reports_missing_section() -> None:
    try:
        assert_local_links_exist("README.md", "## Missing Section")
    except AssertionError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing section lookup failure")

    assert "## Missing Section" in message


def test_markdown_heading_anchor_helper_handles_reviewer_headings() -> None:
    anchors = markdown_heading_anchors(
        "\n".join(
            [
                "# Demo",
                "### Latest Jetson Quick-Scan Registry",
                "## 최근 Jetson quick-scan marker 재현",
            ]
        )
    )

    assert "latest-jetson-quick-scan-registry" in anchors
    assert "최근-jetson-quick-scan-marker-재현" in anchors


def test_cross_repo_smoke_runs_runtime_intelligence_artifact_gate() -> None:
    smoke_script = (ROOT / "scripts" / "smoke_all.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )
    demo_doc_ko = (ROOT / "docs" / "agent_runtime_e2e_demo.ko.md").read_text(
        encoding="utf-8"
    )

    assert "Lab Runtime Intelligence artifact smoke" in smoke_script
    assert "scripts/smoke_runtime_intelligence_chain.sh --output-dir" in smoke_script
    assert "INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT" in smoke_script
    assert "EdgeEnv regression replay fixture matrix gate" in smoke_script
    assert "examples/regression/fixture_matrix.json" in smoke_script
    assert "edgeenv-regression-replay-fixture-matrix-v1" in smoke_script
    assert "same_condition_regression" in smoke_script
    assert "runtime_comparison_blocked" in smoke_script
    assert "target_comparison_blocked" in smoke_script
    assert "protocol_mismatch_blocked" in smoke_script
    assert "telemetry_gap_same_condition" in smoke_script
    assert "replay_sequence_context" in smoke_script
    assert "regression_delta_allowed" in smoke_script
    assert "not_a_deployment_decision" in smoke_script
    assert "not_a_guard_analysis" in smoke_script
    assert "not_production_monitoring" in smoke_script
    assert "Agent Runtime EdgeEnv preservation identity/details smoke" in smoke_script
    assert "INFEREDGE_AGENT_RUNTIME_EDGEENV_SMOKE_OUT" in smoke_script
    assert "demo_agent_runtime_e2e.sh\" --device-local --edgeenv-run-evidence" in smoke_script
    assert "Agent Runtime EdgeEnv preservation marker gate" in smoke_script
    assert "agent_edgeenv_lab_markers=(" in smoke_script
    assert "agent_edgeenv_index_common_markers=(" in smoke_script
    assert "agent_edgeenv_index_json_markers=(" in smoke_script
    assert "agent_edgeenv_index_md_markers=(" in smoke_script
    assert (
        'require_markers "$index_json" "${agent_edgeenv_index_common_markers[@]}"'
        in smoke_script
    )
    assert (
        'require_markers "$index_md" "${agent_edgeenv_index_common_markers[@]}"'
        in smoke_script
    )
    assert "preservation_identity_label" in smoke_script
    assert "preservation_details_label" in smoke_script
    assert "Runtime operation summary" in smoke_script
    assert "Queue pressure reasons:" in smoke_script
    assert "fallback_count" in smoke_script
    assert "deadline_missed_count" in smoke_script
    assert "max_total_queue_depth" in smoke_script
    assert "queue_pressure_reason" in smoke_script
    assert "queue=queue_backlog_threshold_exceeded" in smoke_script
    assert "queue_backlog_threshold_exceeded" in smoke_script
    assert "duration_class" in smoke_script
    assert "duration_label" in smoke_script
    assert "Reviewer Duration Label" in smoke_script
    assert "Duration label" in smoke_script
    assert "Duration class" in smoke_script
    assert "Duration source" in smoke_script
    assert "Duration scope label" in smoke_script
    assert "quick_starter_smoke" in smoke_script
    assert "quick starter smoke (8 frames)" in smoke_script
    assert "duration_source" in smoke_script
    assert "entrypoint_requested_frames" in smoke_script
    assert "duration_scope_label" in smoke_script
    assert "source=entrypoint_requested_frames" in smoke_script
    assert "lab_report_operation_quick_scan_focus_marker" in smoke_script
    assert "operation_summary: mode=device_local_starter" in smoke_script
    assert "operation_summary: mode=timeout_threshold_exceeded" in smoke_script
    assert "Lab Runtime Intelligence report marker gate" in smoke_script
    assert "require_markers()" in smoke_script
    assert "runtime_report_gate_markers=(" in smoke_script
    assert "runtime_summary_common_markers=(" in smoke_script
    assert (
        'require_markers "$gate_summary" "${runtime_report_gate_markers[@]}"'
        in smoke_script
    )
    assert (
        'require_markers "$ci_summary" "${runtime_report_gate_markers[@]}"'
        in smoke_script
    )
    assert (
        'require_markers "$summary_md" "${runtime_summary_common_markers[@]}"'
        in smoke_script
    )
    assert (
        'require_markers "$summary_html" "${runtime_summary_common_markers[@]}"'
        in smoke_script
    )
    assert "runtime_intelligence_bundle_manifest_gate_summary.md" in smoke_script
    assert "expected_report_markers: remote fallback Lab context row declared" in smoke_script
    assert "aiguard_raw_context: max_total_queue_depth traceability preserved" in smoke_script
    assert (
        "reviewer_path_gate: README/ecosystem reviewer path gate context declared"
        in smoke_script
    )
    assert (
        "reviewer_path_local_links: local reviewer path link gate context preserved"
        in smoke_script
    )
    assert (
        "reviewer_path_anchor_fragments: reviewer path anchor gate context preserved"
        in smoke_script
    )
    assert "runtime_anomaly_gate_summary.md" in smoke_script
    assert "runtime_intelligence_ci_artifact_gate_summary.md" in smoke_script
    assert "Validated Duration Traceability" in smoke_script
    assert "duration_handoff_alignment: EdgeEnv/AIGuard report context preserved" in smoke_script
    assert "duration_source: source=entrypoint_requested_frames" in smoke_script
    assert "duration_scope_label: scope_label=source=entrypoint_requested_frames" in smoke_script
    assert "duration_label: short 96-frame-class replay (96 frames)" in smoke_script
    assert "Validated Reviewer Focus" in smoke_script
    assert "reviewer_focus_operation_quick_scan: Reviewer Focus / Operation quick scan marker validated" in smoke_script
    assert (
        "reviewer_focus_operation_quick_scan_raw_marker: raw marker preserved in Lab report"
        in smoke_script
    )
    assert "Validated Review Path" in smoke_script
    assert "review_path_section: short Review Path section rendered" in smoke_script
    assert "review_path_fast_path: readable Review Path fast path rendered" in smoke_script
    assert "review_path: Reviewer Focus -> Detailed Evidence Rows guidance validated" in smoke_script
    assert (
        "review_path_scope: comparable regression / telemetry replay / operation evidence preserved"
        in smoke_script
    )
    assert (
        "review_path_artifact_gate_summary: artifact gate summary reference row validated"
        in smoke_script
    )
    assert "runtime_anomaly_summary.md" in smoke_script
    assert "runtime_anomaly_summary.html" in smoke_script
    assert "Jetson/device-local EdgeEnv preservation run" in smoke_script
    assert "Jetson/device-local EdgeEnv preservation details" in smoke_script
    assert "identity=jetson_device_local_preservation" in smoke_script
    assert "path=device_local_starter" in smoke_script
    assert "sources=device_local_cli_override" in smoke_script
    assert "Runtime replay duration scope" in smoke_script
    assert "short 96-frame-class replay (96 frames)" in smoke_script
    assert "class=short_96_frame_class, frames=96" in smoke_script
    assert "scope_label=source=entrypoint_requested_frames" in smoke_script
    assert "Orchestrator queue/deadline/fallback markers" in smoke_script
    assert "Operation quick scan" in smoke_script
    assert "Reviewer operation quick scan" in smoke_script
    assert "raw_marker=reviewer_focus_operation_quick_scan" in smoke_script
    assert "queue_pressure_reason=queue_backlog_threshold_exceeded" in smoke_script
    assert "max_total_queue_depth=7" in smoke_script
    assert "deadline_missed_count=2" in smoke_script
    assert "fallback_count=1" in smoke_script
    assert "lab=Remote fallback starter evidence; evidence=remote_execution_recovered_by_fallback" in smoke_script
    assert "smoke_remote_fallback_registry_marker.sh" in smoke_script
    assert "INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT" in smoke_script
    assert "Operation quick-scan registry summary smoke" in smoke_script
    assert "smoke_quick_scan_registry_summary.sh" in smoke_script
    assert "INFEREDGE_QUICK_SCAN_REGISTRY_SMOKE_OUT" in smoke_script
    assert "Lab's local-first Runtime Intelligence artifact" in readme
    assert "remote-dispatch boundary rows" in readme
    assert "Reviewer path" in readme
    assert "What to inspect" in readme
    assert "runtime_intelligence_bundle_manifest_gate_summary.md" in readme
    assert "EdgeEnv `examples/regression/fixture_matrix.json`" in readme
    assert "telemetry-gap" in readme
    assert "replay-sequence fixtures" in readme
    assert "Runtime Intelligence Risk Summary" in readme
    assert "duration traceability" in readme
    assert "Lab `Review Path` section" in readme
    assert "Validated Review Path" in readme
    assert (
        "Detailed marker vocabulary lives in the Agent Runtime E2E demo docs"
        in readme
    )
    assert "shared reviewer marker gates" in readme
    assert "generated `00_evidence_index.*`" in readme
    assert "without expanding the README's detailed marker vocabulary" in readme
    assert "README -> Lab report -> gate summary reading order" in readme
    assert "short Review Path section" not in readme
    assert "artifact gate summary reference row" not in readme
    assert "Operation Quick Scan Summary" in readme
    assert "max_total_queue_depth" in readme
    assert "raw_marker=reviewer_focus_operation_quick_scan" in readme
    assert "queue pressure" in readme

    for doc_text in (demo_doc, demo_doc_ko):
        assert "shared marker" in doc_text or "공통 marker" in doc_text
        assert (
            "same reviewer marker vocabulary" in doc_text
            or "같은 reviewer marker vocabulary" in doc_text
        )
        assert "Format-specific" in doc_text or "format-specific" in doc_text
        assert "drift" in doc_text
        assert "review_path_section: short Review Path section rendered" in doc_text
        assert "review_path_fast_path: readable Review Path fast path rendered" in doc_text
        assert (
            "review_path_artifact_gate_summary: artifact gate summary reference row validated"
            in doc_text
        )


def test_runtime_intelligence_demo_docs_preserve_artifact_and_gate_order() -> None:
    smoke_script = (ROOT / "scripts" / "smoke_all.sh").read_text(
        encoding="utf-8"
    )
    doc_sections = [
        (
            "docs/agent_runtime_e2e_demo.md",
            "## Smoke Gate Split",
            "English Runtime Intelligence artifact output list",
        ),
        (
            "docs/agent_runtime_e2e_demo.ko.md",
            "## Runtime Intelligence artifact smoke와의 차이",
            "Korean Runtime Intelligence artifact output list",
        ),
    ]

    for doc_path, heading, label in doc_sections:
        section = section_by_heading(
            (ROOT / doc_path).read_text(encoding="utf-8"), heading
        )
        assert_markers_in_order(
            section,
            RUNTIME_INTELLIGENCE_ARTIFACT_ORDER,
            label=label,
        )

    assert_markers_in_order(
        smoke_script,
        RUNTIME_INTELLIGENCE_SMOKE_GATE_ORDER,
        label="scripts/smoke_all.sh Runtime Intelligence gate order",
    )


def test_remote_fallback_registry_marker_smoke_is_fixture_only() -> None:
    script = (ROOT / "scripts" / "smoke_remote_fallback_registry_marker.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )
    korean_demo_doc = (
        ROOT / "docs" / "agent_runtime_e2e_demo.ko.md"
    ).read_text(encoding="utf-8")
    normalized_demo_doc = " ".join(demo_doc.split())

    assert "fixture-only remote fallback evidence bundle" in script
    assert "build_agent_runtime_evidence_index.py" in script
    assert "build_agent_runtime_run_registry.py" in script
    assert "remote_execution_recovered_by_fallback" in script
    assert "lab=Remote fallback starter evidence" in script
    assert "production_remote_execution=False" in script
    assert "local HTTP fallback worker" in readme
    for text in (portfolio, demo_doc):
        assert "smoke_remote_fallback_registry_marker.sh" in text
        assert "lab=Remote fallback starter evidence" in text
    assert "Duration Comparison Summary" in demo_doc
    assert "Duration source" in demo_doc
    assert "Duration scope label" in demo_doc
    assert "source=entrypoint_requested_frames" in demo_doc
    assert "Duration Sources" in demo_doc
    assert "entrypoint-requested replay scope" in demo_doc
    assert "live production runtime duration claim" in normalized_demo_doc
    assert "Remote fallback registry marker smoke" in korean_demo_doc
    assert "Duration source" in korean_demo_doc
    assert "Duration scope label" in korean_demo_doc
    assert "source=entrypoint_requested_frames" in korean_demo_doc
    assert "Duration Sources" in korean_demo_doc
    assert "production remote execution" in korean_demo_doc
    assert "source=entrypoint_requested_frames" in script
    assert "reviewer navigation context" in script
    assert "do not make the index a Lab report owner" in script
    assert "not as a new source contract" in script
    assert "Duration Sources" in script


def test_quick_scan_registry_summary_smoke_is_fixture_only() -> None:
    script = (ROOT / "scripts" / "smoke_quick_scan_registry_summary.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )
    korean_demo_doc = (
        ROOT / "docs" / "agent_runtime_e2e_demo.ko.md"
    ).read_text(encoding="utf-8")
    interview = (ROOT / "docs" / "interview_narrative.md").read_text(
        encoding="utf-8"
    )

    assert "fixture-only device-local EdgeEnv preservation bundle" in script
    assert "build_agent_runtime_evidence_index.py" in script
    assert "build_agent_runtime_run_registry.py" in script
    assert "Operation Quick Scan Summary" in script
    assert "Raw Marker" in script
    assert "Raw Marker Label" in script
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker" in script
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker_label" in script
    assert "reviewer_focus_operation_quick_scan" in script
    assert "raw_marker=reviewer_focus_operation_quick_scan" in script
    assert "Reviewer operation quick scan" in script
    assert "queue_pressure_reason=queue_backlog_threshold_exceeded" in script
    assert "max_total_queue_depth=6" in script
    assert "deadline_missed_count=50" in script
    assert "fallback_count=93" in script
    assert "operation_summary: mode=device_local_starter" in script
    assert "operation_summary: mode=timeout_threshold_exceeded" in script
    assert "reviewer navigation metadata" in script
    assert "does not make this registry a Lab report owner" in script
    assert "Operation Quick Scan Summary must appear before ## Runs" in script
    assert "Quick-scan registry summary smoke: pass" in script
    assert "reviewer navigation context" in script
    assert "do not make the index a Lab report owner" in script
    assert "not as a new source contract" in script
    assert "raw quick-scan marker labels appear" in script
    assert "reviewer-navigation bug" in script
    assert "raw marker labels leak" in demo_doc
    assert "Raw Marker Label" in demo_doc
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker" in demo_doc
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker_label" in demo_doc
    assert "compact `Operation Quick Scan Summary`에 새면 안 되고" in korean_demo_doc
    assert "Raw Marker Label" in korean_demo_doc
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker" in korean_demo_doc
    assert "edgeenv_lab_report_operation_quick_scan_raw_marker_label" in korean_demo_doc
    for text in (readme, portfolio, interview):
        assert "Operation Quick Scan Summary" in text
        assert "quick-scan registry" in text


def test_jetson_5min_html_preserves_latest_registry_context() -> None:
    html = (
        ROOT / "docs" / "evidence" / "jetson_device_local_5min_sustained_report.html"
    ).read_text(encoding="utf-8")
    normalized_html = " ".join(html.split())

    assert "<h2>Relationship To Latest Registry</h2>" in html
    assert "representative 5-minute-class Jetson metric snapshot" in normalized_html
    assert "latest reviewer navigation record" in normalized_html
    assert "../agent_runtime_e2e_demo.md#latest-jetson-quick-scan-registry" in html
    assert "c04abc9" in html
    assert (
        "/tmp/inferedge_agent_runtime_jetson_sustained_5min_operation_summary_latest_20260609T121700Z"
        in html
    )
    assert (
        "/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.md"
        in html
    )
    assert (
        "/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.json"
        in html
    )
    assert "run-20260609-122009-c17a030b" in html
    assert "5-minute-class sustained replay (3600 frames)" in html
    assert "operation_summary: mode=device_local_starter" in html
    assert "operation_summary: mode=timeout_threshold_exceeded" in html
    assert "one navigation table" in normalized_html
    assert "thermal endurance validation" in normalized_html
    assert "replace this report's metric snapshot" in normalized_html
    assert "make the registry a Lab report owner" in normalized_html


def test_jetson_evidence_terms_align_snapshot_registry_navigation() -> None:
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )
    korean_demo_doc = (
        ROOT / "docs" / "agent_runtime_e2e_demo.ko.md"
    ).read_text(encoding="utf-8")
    evidence_docs = [
        ROOT / "docs" / "evidence" / "jetson_device_local_agent_runtime_report.md",
        ROOT / "docs" / "evidence" / "jetson_device_local_5min_sustained_report.md",
        ROOT / "docs" / "evidence" / "jetson_device_local_agent_runtime_report.ko.md",
        ROOT
        / "docs"
        / "evidence"
        / "jetson_device_local_5min_sustained_report.ko.md",
    ]

    for text in (demo_doc, korean_demo_doc):
        assert "Representative snapshot" in text
        assert "Latest registry" in text
        assert "Quick-scan navigation" in text
        assert "Duration Comparison Summary" in text
        assert "Operation Quick Scan Summary" in text
        assert "reviewer navigation metadata" in text
        assert "production runtime operation proof" in text

    for path in evidence_docs:
        text = path.read_text(encoding="utf-8")
        assert "representative snapshot" in text
        assert "latest registry" in text
        assert "quick-scan navigation" in text
        assert "Relationship To Latest Registry" in text or "최신 registry와의 관계" in text
        assert "metric snapshot" in text or "metric record" in text

    for path in (
        ROOT / "docs" / "evidence" / "jetson_device_local_agent_runtime_report.md",
        ROOT / "docs" / "evidence" / "jetson_device_local_agent_runtime_report.ko.md",
    ):
        assert_short_jetson_source_values(path.read_text(encoding="utf-8"))

    for path in (
        ROOT / "docs" / "evidence" / "jetson_device_local_5min_sustained_report.md",
        ROOT
        / "docs"
        / "evidence"
        / "jetson_device_local_5min_sustained_report.ko.md",
        ROOT
        / "docs"
        / "evidence"
        / "jetson_device_local_5min_sustained_report.html",
    ):
        assert_sustained_jetson_source_values(path.read_text(encoding="utf-8"))


def test_latest_jetson_quick_scan_registry_preserves_snapshot_values() -> None:
    doc_sections = [
        (
            ROOT / "docs" / "agent_runtime_e2e_demo.md",
            "### Latest Jetson Quick-Scan Registry",
            "Linked metric snapshots",
        ),
        (
            ROOT / "docs" / "agent_runtime_e2e_demo.ko.md",
            "## 최근 Jetson quick-scan marker 재현",
            "연결된 metric snapshot",
        ),
    ]

    for path, heading, snapshot_label in doc_sections:
        section = section_by_heading(path.read_text(encoding="utf-8"), heading)

        assert snapshot_label in section
        assert "Operation Quick Scan Summary" in section
        assert "metric record" in section
        assert "production runtime operation proof" in section
        assert "Lab report owner" in section
        assert "EdgeEnv comparability gate" in section
        assert "deployment decision" in section
        assert "Raw Marker" in section
        assert "raw marker label" in section
        assert "detailed `## Runs`" in section
        assert_short_jetson_source_values(section)
        assert_sustained_jetson_source_values(section)


def test_interview_narrative_uses_jetson_evidence_terms() -> None:
    interview = (ROOT / "docs" / "interview_narrative.md").read_text(
        encoding="utf-8"
    )
    korean_interview = (ROOT / "docs" / "interview_narrative.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (interview, korean_interview):
        normalized_text = " ".join(text.split())
        assert_jetson_reviewer_navigation_terms(
            normalized_text,
            representative_marker="Representative snapshot",
            resource_style="comma",
            extra_markers=("submission-facing metric snapshot",),
        )
        assert (
            "shared reviewer marker-gate" in normalized_text
            or "공통 reviewer marker-gate" in normalized_text
        )
        assert "generated `00_evidence_index.*`" in normalized_text
        assert "Agent Runtime E2E Demo" in normalized_text
        assert (
            "detailed marker vocabulary owner" in normalized_text
            or "세부 marker vocabulary owner" in normalized_text
        )


def test_portfolio_summary_uses_jetson_evidence_terms() -> None:
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )
    korean_portfolio = (ROOT / "docs" / "portfolio_summary.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (portfolio, korean_portfolio):
        normalized_text = " ".join(text.split())
        assert_jetson_reviewer_navigation_terms(
            normalized_text,
            representative_marker="representative snapshot",
            resource_style="max",
        )
        assert "shared reviewer marker" in text or "공통 reviewer marker" in text
        assert "generated `00_evidence_index.*`" in normalized_text
        assert "detailed marker vocabulary owner" in text or "세부 marker vocabulary owner" in text


def test_ecosystem_1page_uses_jetson_evidence_terms() -> None:
    ecosystem = (ROOT / "docs" / "ecosystem_1page.md").read_text(
        encoding="utf-8"
    )
    korean_ecosystem = (ROOT / "docs" / "ecosystem_1page.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (ecosystem, korean_ecosystem):
        normalized_text = " ".join(text.split())
        assert_jetson_reviewer_navigation_terms(
            normalized_text,
            representative_marker="representative snapshot",
            resource_style="max",
            extra_markers=("submission-facing metric report",),
        )


def test_pipeline_map_uses_jetson_evidence_terms() -> None:
    pipeline = (ROOT / "docs" / "pipeline_map.md").read_text(encoding="utf-8")
    korean_pipeline = (ROOT / "docs" / "pipeline_map.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (pipeline, korean_pipeline):
        normalized_text = " ".join(text.split())
        assert_jetson_reviewer_navigation_terms(
            normalized_text,
            representative_marker="representative snapshot",
            resource_style="max",
            extra_markers=("submission-facing metric", "local reviewer navigation"),
            require_metric_owner_boundary=True,
        )
        assert "generated `00_evidence_index.*`" in normalized_text
        assert "marker-gate" in normalized_text
        assert "contract-boundary view" in normalized_text
        assert "detailed marker vocabulary owner" in normalized_text or "세부 marker vocabulary owner" in normalized_text


def test_jetson_readiness_preflight_is_not_evidence() -> None:
    script = (ROOT / "scripts" / "check_jetson_sustained_readiness.sh").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "scripts" / "demo_jetson_5min_sustained.sh").read_text(
        encoding="utf-8"
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    assert "ssh" in script
    assert "ConnectTimeout" in script
    assert "tegrastats=available" in script
    assert "clean_forge_repo=available" in script
    assert "vision_onnx_model=available" in script
    assert "edgeenv_repo=available" in script
    assert "edgeenv_cli=available" in script
    assert "miniconda3/envs/yolo_env/bin/python" in script
    assert "--edgeenv-run-evidence" in script
    assert "This preflight does not create evidence" in script
    assert "INFEREDGE_ENV_REPO" in runner
    assert "--edgeenv-run-evidence" in runner
    for text in (readme, demo_doc):
        assert "check_jetson_sustained_readiness.sh" in text
        assert "does not" in text
        assert "new evidence" in text
        assert "--edgeenv-run-evidence" in text


def test_entrypoint_lab_report_can_use_local_lab_module() -> None:
    script = (ROOT / "scripts" / "demo_agent_runtime_e2e.sh").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    assert "PYTHONPATH=\"$LAB_REPO${PYTHONPATH:+:$PYTHONPATH}\"" in script
    assert "-m inferedgelab.cli" in script
    assert "--edgeenv-run-show" in script
    assert "Runtime Intelligence EdgeEnv Preservation" in script
    assert "python -m inferedgelab.cli" in demo_doc


def test_runtime_intelligence_status_preserves_local_first_boundary() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    portfolio = (ROOT / "docs" / "portfolio_summary.md").read_text(
        encoding="utf-8"
    )
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )

    for text in (readme, portfolio):
        assert "Runtime Intelligence artifact gate" in text
        assert "Orchestrator -> EdgeEnv -> AIGuard -> Lab" in text
        assert "Runtime Intelligence Risk Summary" in text
        assert "Operation Quick Scan Summary" in text
        assert "lab_preservation=present" in text
        assert "identity=jetson_device_local_preservation" in text
        assert "raw_marker=reviewer_focus_operation_quick_scan" in text
        assert "max_total_queue_depth" in text
        assert "fallback count" in text
        assert "deadline miss" in text
        assert "Remote fallback starter evidence" in text

    assert "Production observability platform or GitLab control plane" in readme
    assert "production control plane" in portfolio
    for text in (demo_doc,):
        assert "Validated Duration Traceability" in text
        assert "Validated Reviewer Focus" in text
        assert "reviewer_focus_operation_quick_scan" in text
        assert "runtime_intelligence_ci_artifact_gate_summary.md" in text
        assert "lab_expected_report_markers" in text
        assert "lab_report_contract_context" in text
        assert "aiguard_validates_expected_report_markers=false" in text
    assert "EdgeEnv/AIGuard duration handoff alignment" in portfolio
    assert "duration_handoff_alignment_20260601" in portfolio
    assert "EdgeEnv `de64d50` and AIGuard `7289899`" in portfolio


def test_readme_language_selector_links_to_korean_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    korean_readme = (ROOT / "README.ko.md").read_text(encoding="utf-8")

    assert readme.startswith("# InferEdge\n\nLanguage: English | [한국어](README.ko.md)")
    assert korean_readme.startswith("# InferEdge\n\n언어: [English](README.md) | 한국어")
    assert_readme_top_jetson_p95_evidence_terms(readme)
    assert_readme_quick_scan_snapshot_terms(readme)
    assert "대표 README와 가장 최신 상세 설명" in korean_readme
    assert "[English README](README.md)" in korean_readme
    assert "Lab-owned deployment decision" in korean_readme
    assert "production SaaS dashboard" in korean_readme
    assert "production observability platform" in korean_readme
    assert "Kubernetes-style orchestration" in korean_readme
    assert "AIGuard 또는 Orchestrator의 최종 deployment decision ownership" in korean_readme
    assert "[InferEdge 생태계 1페이지 요약](docs/ecosystem_1page.ko.md)" in korean_readme
    assert "[포트폴리오 요약](docs/portfolio_summary.ko.md)" in korean_readme
    assert "[파이프라인 맵](docs/pipeline_map.ko.md)" in korean_readme
    assert "[Agent Runtime E2E Demo](docs/agent_runtime_e2e_demo.ko.md)" in korean_readme
    assert "공통 reviewer marker gate" in korean_readme
    assert "generated `00_evidence_index.*`" in korean_readme
    assert "README에는 세부 marker vocabulary를 늘리지 않고" in korean_readme
    assert_korean_readme_jetson_p95_evidence_terms(korean_readme)
    assert_readme_quick_scan_snapshot_terms(korean_readme)
    assert (
        "[Jetson 디바이스 로컬 evidence quick guide]"
        "(docs/evidence/jetson_device_local_agent_runtime_report.ko.md)"
        in korean_readme
    )
    assert (
        "[Jetson 5분급 sustained evidence quick guide]"
        "(docs/evidence/jetson_device_local_5min_sustained_report.ko.md)"
        in korean_readme
    )


def test_publish_readiness_preserves_safe_branch_boundary() -> None:
    script = (ROOT / "scripts" / "check_publish_ready.sh").read_text(
        encoding="utf-8"
    )
    publish_doc = (ROOT / "docs" / "publish_inferedge.md").read_text(
        encoding="utf-8"
    )
    normalized_publish_doc = " ".join(publish_doc.split())
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    korean_readme = (ROOT / "README.ko.md").read_text(encoding="utf-8")

    assert "InferEdge publish readiness" in script
    assert "check_origin_branch_state" in script
    assert "Origin branch state: unrelated-history" in script
    assert "do not force push" in script
    assert "Upstream status: different branch" in script
    assert "git push -u origin $branch_name" in script
    assert "print_local_main_safety" in script
    assert "Local main safety: upstream matches origin/main" in script
    assert "Local main safety: review before publishing" in script
    assert "start review work from origin/main" in script
    assert "origin remote placeholder detection" in script
    assert "local main checkout safety" in script
    assert "--allow-dirty" in script
    assert "--allow-missing-remote" in script
    assert "--allow-placeholder-remote" in script
    assert "--skip-remote-check" in script

    assert "public InferEdge ecosystem entrypoint" in publish_doc
    assert "Do not force push" in publish_doc
    assert "Origin branch state: unrelated-history" in publish_doc
    assert "Upstream status: different branch" in publish_doc
    assert "Local main safety: review before publishing" in publish_doc
    assert "local `main` checkout safety" in publish_doc
    assert "Do not push local `main` directly" in publish_doc
    assert "`origin` remote placeholder detection" in publish_doc
    assert "whitespace and patch sanity check" in publish_doc
    assert "git diff --check" in publish_doc
    assert "After staging files" in publish_doc
    assert "staged patch before" in publish_doc
    assert "git diff --cached --check" in publish_doc
    assert "Local Checkout Safety" in publish_doc
    assert "If local `main` has unrelated" in publish_doc
    assert "history, do not use it as the base for new work" in publish_doc
    assert (
        "Treat that as a prompt to stop and start from `origin/main`"
        in normalized_publish_doc
    )
    assert "origin/main` as the source of truth" in publish_doc
    assert "After PR Merge" in publish_doc
    assert "Bundled PR Merge Step" in publish_doc
    assert "PR creation, and PR merge as one execution step" in publish_doc
    assert "Do not commit, push, open a PR, or merge" in publish_doc
    assert "verify the changed file list" in publish_doc
    assert "the pull request is mergeable" in publish_doc
    assert "Use this PR merge gate inside the bundled step" in publish_doc
    assert "PR changed-file list matches the local diff scope" in publish_doc
    assert "not a draft" in publish_doc
    assert "commit status checks have no failures" in publish_doc
    assert "no failing GitHub statuses were reported" in publish_doc
    assert "expected head SHA" in publish_doc
    assert "The PR body should include" in publish_doc
    assert "`Summary` and `Tests` section" in publish_doc
    assert "exact validation commands that passed" in publish_doc
    assert "GitHub Auth Fallback" in publish_doc
    assert "Use the GitHub connector/app" in publish_doc
    assert "`gh` CLI is a fallback path" in publish_doc
    assert "gh auth status" in publish_doc
    assert "invalid token" in publish_doc
    assert "gh auth login -h github.com" in publish_doc
    assert "note that in the PR body" in publish_doc
    assert "Final Status Check" in publish_doc
    assert "git status --short --branch" in publish_doc
    assert "git diff --stat" in publish_doc
    assert "git diff --cached --stat" in publish_doc
    assert "If any unexpected file appears" in publish_doc
    assert "git log --oneline -3 origin/main" in publish_doc
    assert "not run `git pull` into a stale or unrelated local `main`" in publish_doc
    assert "git merge --ff-only origin/main" in publish_doc
    assert "fatal: refusing to merge unrelated histories" in publish_doc
    assert "Do not retry with" in publish_doc
    assert "`--allow-unrelated-histories`" in publish_doc
    assert "force reset" in publish_doc
    assert "create a fresh branch from" in publish_doc
    assert "Optional Branch Cleanup" in publish_doc
    assert "Never delete `main`" in publish_doc
    assert "make a cleanup inventory" in publish_doc
    assert "not a deletion list" in publish_doc
    assert "bash scripts/audit_branch_cleanup.sh --fetch" in publish_doc
    assert "matching `origin/codex/*` remote branches" in normalized_publish_doc
    assert "cleanup inventory only" in publish_doc
    assert "regular merge ancestry" in publish_doc
    assert "not sufficient for squash-merged pull requests" in normalized_publish_doc
    assert "zero regular-merge ancestry entries" in publish_doc
    assert (
        "does not mean there are zero squash-merged PR branches"
        in normalized_publish_doc
    )
    assert "PR merged state as the deciding evidence" in publish_doc
    assert "merged PR confirmation checklist" in publish_doc
    assert "Match the branch name to its GitHub pull request" in publish_doc
    assert "closed as merged, not merely closed" in publish_doc
    assert "merge commit is visible on the current `origin/main`" in publish_doc
    assert (
        "no longer needed for review, audit, or comparing local logs"
        in normalized_publish_doc
    )
    assert "Keep the branch when any of those checks is uncertain" in publish_doc
    assert "only proves regular merge ancestry" in normalized_publish_doc
    assert "Squash-merged branches may not appear" in publish_doc
    assert "do not delete the branch based on `--merged` alone" in publish_doc
    assert "Verify the PR is" in publish_doc
    assert "closed as merged" in publish_doc
    assert "local `gh` token is invalid" in publish_doc
    assert "GitHub connector/app" in publish_doc
    assert "GitHub PR page" in publish_doc
    assert "git push origin --delete codex/<merged-topic>" in publish_doc
    assert "`--allow-dirty`" in publish_doc
    assert "`--allow-missing-remote`" in publish_doc
    assert "`--allow-placeholder-remote`" in publish_doc
    assert "`--skip-remote-check`" in publish_doc
    assert "diagnostic" in publish_doc
    assert "escape hatches" in publish_doc
    assert "Do not use them for normal branch publish" in publish_doc
    assert "bypass the blocked-state evidence" in publish_doc
    assert "git switch -c codex/<topic> origin/main" in publish_doc
    assert "git switch -c codex/<next-task> origin/main" in publish_doc
    assert "git push -u origin codex/<topic>" in publish_doc
    assert "Jetson hardware is not required" in publish_doc

    assert_markers_in_order(
        section_by_heading(publish_doc, "## Pre-publish Checks"),
        [
            "python -m pytest -q",
            "git diff --check",
            "git diff --cached --check",
            "bash scripts/smoke_all.sh",
            "bash scripts/check_publish_ready.sh",
        ],
        label="docs/publish_inferedge.md pre-publish command order",
    )
    assert_markers_in_order(
        section_by_heading(publish_doc, "## Safe Branch Publish"),
        [
            "git fetch origin main",
            "git switch -c codex/<topic> origin/main",
            "git diff --check",
            "python -m pytest -q",
            "bash scripts/check_publish_ready.sh",
            "git push -u origin codex/<topic>",
        ],
        label="docs/publish_inferedge.md safe branch publish command order",
    )
    assert_markers_in_order(
        section_by_heading(publish_doc, "## Final Status Check"),
        [
            "git status --short --branch",
            "git diff --stat",
            "git diff --cached --stat",
        ],
        label="docs/publish_inferedge.md final status command order",
    )

    assert "scripts/check_publish_ready.sh" in readme
    assert "docs/publish_inferedge.md" in readme
    assert "Do not" in readme
    assert "force push" in readme
    assert "public `main`" in readme
    assert "bundled PR merge step" in readme
    assert "PR changed-file/status gate" in readme
    assert "PR `Summary` / `Tests` recording" in readme
    assert "final status check" in readme
    assert "local checkout safety" in readme
    assert "optional branch cleanup" in readme
    assert "diagnostic escape-hatch flags" in readme
    assert "scripts/check_publish_ready.sh" in korean_readme
    assert "docs/publish_inferedge.md" in korean_readme
    assert "PR 생성과 merge까지 한 단계" in korean_readme
    assert "PR changed-file/status gate" in korean_readme
    assert "PR `Summary` / `Tests` 기록" in korean_readme
    assert "최종 상태 확인" in korean_readme
    assert "local checkout" in korean_readme
    assert "safety" in korean_readme
    assert "optional branch cleanup" in korean_readme
    assert "diagnostic escape-hatch flag" in korean_readme
    assert "force push하지 않습니다" in korean_readme


def test_publish_readiness_help_output_lists_safety_boundaries() -> None:
    result = subprocess.run(
        ["bash", "scripts/check_publish_ready.sh", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = result.stdout

    assert "Usage:" in output
    assert "bash scripts/check_publish_ready.sh [options]" in output
    assert "--allow-dirty" in output
    assert "--allow-missing-remote" in output
    assert "--allow-placeholder-remote" in output
    assert "--skip-remote-check" in output
    assert "origin remote placeholder detection" in output
    assert "origin branch fast-forward safety" in output
    assert "suggested push command" in output
    assert result.stderr == ""


def test_branch_cleanup_audit_script_is_inventory_only() -> None:
    script = (ROOT / "scripts" / "audit_branch_cleanup.sh").read_text(
        encoding="utf-8"
    )
    result = subprocess.run(
        ["bash", "scripts/audit_branch_cleanup.sh", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = result.stdout
    normalized_output = " ".join(output.split())

    assert "InferEdge branch cleanup audit" in script
    assert "CURRENT_BRANCH=\"$(git branch --show-current)\"" in script
    assert "(current; do not delete while checked out)" in script
    assert "Remote cleanup inventory" in script
    assert "git branch -r --list" in script
    assert "origin/$BRANCH_PATTERN" in script
    assert "Cleanup audit summary" in script
    assert "Local inventory entries" in script
    assert "Remote inventory entries" in script
    assert "Regular-merge ancestry entries" in script
    assert "does not mean zero squash-merged PR branches" in script
    assert "git fetch origin main" in script
    assert "git branch --list" in script
    assert "git branch --merged origin/main" in script
    assert "git branch -d" not in script
    assert "git branch -D" not in script
    assert "git push origin --delete" not in script
    assert "not a deletion list" in script
    assert "Do not delete the current checked-out branch" in script
    assert "Remote inventory entries are branch refs to inspect" in script
    assert "Squash-merged branches may not appear" in script
    assert "Verify the PR is closed as merged" in script
    assert "GitHub connector/app" in script

    assert "bash scripts/audit_branch_cleanup.sh [options]" in output
    assert "--fetch" in output
    assert "--branch-pattern <glob>" in output
    assert "Matching origin/<glob> remote branches" in normalized_output
    assert "It never deletes local or remote branches" in normalized_output
    assert result.stderr == ""


def test_cross_repo_role_boundary_matrix_preserves_canonical_ownership() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    korean_readme = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    ecosystem = (ROOT / "docs" / "ecosystem_1page.md").read_text(
        encoding="utf-8"
    )
    ecosystem_ko = (ROOT / "docs" / "ecosystem_1page.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (readme, korean_readme):
        lower_text = text.lower()
        assert "Cross-Repo" in text
        assert "production saas" in lower_text
        assert "cloud control plane" in text
        assert "generic monitoring" in text
        assert "InferEdgeForge" in text
        assert "build provenance / handoff owner" in lower_text
        assert "InferEdge-Runtime" in text
        assert "execution / result evidence owner" in lower_text
        assert "Lab-compatible `result.json`" in text
        assert "InferEdgeLab" in text
        assert "deployment decision owner" in text
        assert "InferEdgeAIGuard" in text
        assert "optional deterministic diagnosis evidence provider" in lower_text
        assert "`guard_analysis`" in text
        assert "InferEdgeEnv" in text
        assert "runtime regression owner" in text
        assert "general monitoring SaaS" in text
        assert "InferEdgeOrchestrator" in text
        assert "runtime operation context provider" in lower_text
        assert "Kubernetes replacement" in text
        assert "completed production scheduler" in text

    for text in (ecosystem, ecosystem_ko):
        lower_text = text.lower()
        assert "Canonical Ownership Matrix" in text
        assert "build provenance / handoff evidence" in lower_text
        assert "runtime health and telemetry seed evidence" in text
        assert "Lab-owned deployment decision" in text
        assert "optional deterministic diagnosis" in lower_text
        assert "runtime regression report" in text
        assert "runtime operation context" in lower_text
        assert "general monitoring SaaS" in text
        assert "cloud orchestration platform" in text
        assert "completed production scheduler" in text


def test_core_docs_language_selectors_link_to_korean_guides() -> None:
    doc_pairs = [
        ("docs/ecosystem_1page.md", "docs/ecosystem_1page.ko.md"),
        ("docs/portfolio_summary.md", "docs/portfolio_summary.ko.md"),
        ("docs/pipeline_map.md", "docs/pipeline_map.ko.md"),
        ("docs/agent_runtime_e2e_demo.md", "docs/agent_runtime_e2e_demo.ko.md"),
        (
            "docs/evidence/jetson_device_local_agent_runtime_report.md",
            "docs/evidence/jetson_device_local_agent_runtime_report.ko.md",
        ),
        (
            "docs/evidence/jetson_device_local_5min_sustained_report.md",
            "docs/evidence/jetson_device_local_5min_sustained_report.ko.md",
        ),
    ]

    for english_path, korean_path in doc_pairs:
        english = (ROOT / english_path).read_text(encoding="utf-8")
        korean = (ROOT / korean_path).read_text(encoding="utf-8")
        english_name = Path(english_path).name
        korean_name = Path(korean_path).name

        assert f"Language: English | [한국어]({korean_name})" in english
        assert f"언어: [English]({english_name}) | 한국어" in korean
        assert "대표/canonical 문서" in korean
        assert "Lab-owned deployment decision" in korean
        assert "production" in korean

    ecosystem_ko = (ROOT / "docs" / "ecosystem_1page.ko.md").read_text(
        encoding="utf-8"
    )
    portfolio_ko = (ROOT / "docs" / "portfolio_summary.ko.md").read_text(
        encoding="utf-8"
    )
    pipeline_ko = (ROOT / "docs" / "pipeline_map.ko.md").read_text(
        encoding="utf-8"
    )

    assert "[포트폴리오 요약](portfolio_summary.ko.md)" in ecosystem_ko
    assert "[파이프라인 맵](pipeline_map.ko.md)" in ecosystem_ko
    assert "Runtime Intelligence artifact gate" in portfolio_ko
    assert "Core 4 validation contract" in pipeline_ko
    assert "AIGuard `guard_analysis`" in pipeline_ko


def test_entrypoint_reviewer_path_preserves_doc_order() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    korean_readme = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    ecosystem = (ROOT / "docs" / "ecosystem_1page.md").read_text(
        encoding="utf-8"
    )
    korean_ecosystem = (ROOT / "docs" / "ecosystem_1page.ko.md").read_text(
        encoding="utf-8"
    )

    assert "## Docs & Review Path" in readme
    assert "## 먼저 볼 문서" in korean_readme
    assert "## Reviewer Path" in ecosystem
    assert "## Reviewer Path" in korean_ecosystem
    assert (
        "Agent Runtime / Runtime Operation smoke details and shared marker-gate owner"
        in readme
    )
    assert "Runtime Operation / Agent Runtime smoke 흐름과 공통 marker-gate 상세 owner" in korean_readme

    assert_markers_in_order(
        readme,
        [
            "docs/ecosystem_1page.md",
            "docs/portfolio_summary.md",
            "docs/pipeline_map.md",
            "docs/final_submission_rehearsal.md",
            "docs/publish_inferedge.md",
            "docs/agent_runtime_e2e_demo.md",
            "docs/agent_runtime_e2e_demo.md#latest-jetson-quick-scan-registry",
            "docs/interview_narrative.md",
            "docs/evidence/jetson_device_local_agent_runtime_report.md",
            "docs/evidence/jetson_device_local_5min_sustained_report.md",
        ],
        label="README Docs & Review Path",
    )
    assert_markers_in_order(
        korean_readme,
        [
            "docs/ecosystem_1page.ko.md",
            "docs/portfolio_summary.ko.md",
            "docs/pipeline_map.ko.md",
            "docs/final_submission_rehearsal.md",
            "docs/publish_inferedge.md",
            "docs/agent_runtime_e2e_demo.ko.md",
            "docs/agent_runtime_e2e_demo.ko.md#최근-jetson-quick-scan-marker-재현",
            "docs/interview_narrative.ko.md",
            "docs/evidence/jetson_device_local_agent_runtime_report.ko.md",
            "docs/evidence/jetson_device_local_5min_sustained_report.ko.md",
            "docs/evidence/jetson_device_local_5min_sustained_report.html",
        ],
        label="README.ko 먼저 볼 문서",
    )
    assert_markers_in_order(
        ecosystem,
        [
            "[Portfolio Summary](portfolio_summary.md)",
            "[Pipeline Map](pipeline_map.md)",
            "[Agent Runtime E2E Demo](agent_runtime_e2e_demo.md)",
            "[Interview Narrative](interview_narrative.md)",
            "bash scripts/clone_all.sh --locked",
            "bash scripts/smoke_all.sh",
        ],
        label="ecosystem_1page Reviewer Path",
    )
    assert_markers_in_order(
        korean_ecosystem,
        [
            "[포트폴리오 요약](portfolio_summary.ko.md)",
            "[파이프라인 맵](pipeline_map.ko.md)",
            "[Agent Runtime E2E Demo](agent_runtime_e2e_demo.ko.md)",
            "[인터뷰 내러티브](interview_narrative.ko.md)",
            "[InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md)",
        ],
        label="ecosystem_1page.ko Reviewer Path",
    )

    for text in (readme, korean_readme, ecosystem, korean_ecosystem):
        normalized_text = " ".join(text.split())
        assert "Lab-owned deployment decision" in normalized_text
        assert "production observability" in normalized_text
        assert "cloud control plane" in normalized_text
    assert "shared reviewer marker-gate details" in ecosystem
    assert "generated `00_evidence_index.*`" in " ".join(ecosystem.split())
    assert "공통 reviewer marker-gate 상세" in " ".join(korean_ecosystem.split())
    assert "generated `00_evidence_index.*`" in " ".join(korean_ecosystem.split())


def test_entrypoint_reviewer_path_local_links_exist() -> None:
    for doc_path, section_heading in [
        ("README.md", "## Docs & Review Path"),
        ("README.ko.md", "## 먼저 볼 문서"),
        ("docs/ecosystem_1page.md", "## Reviewer Path"),
        ("docs/ecosystem_1page.ko.md", "## Reviewer Path"),
    ]:
        assert_local_links_exist(doc_path, section_heading)


def test_entrypoint_reviewer_path_anchor_fragments_exist() -> None:
    for doc_path, section_heading in [
        ("README.md", "## Docs & Review Path"),
        ("README.ko.md", "## 먼저 볼 문서"),
    ]:
        assert_local_markdown_link_fragments_exist(doc_path, section_heading)


def test_final_submission_rehearsal_preserves_current_reviewer_delta() -> None:
    rehearsal = (ROOT / "docs" / "final_submission_rehearsal.md").read_text(
        encoding="utf-8"
    )
    delta = section_by_heading(rehearsal, "## Current Reviewer Path Delta")
    normalized_delta = " ".join(delta.split())

    assert "historical clean-clone record from 2026-05-14" in delta
    assert "does not claim a new clean-clone run" in normalized_delta
    assert "Runtime Intelligence artifact gate" in delta
    assert "Operation quick-scan registry" in delta
    assert "Shared reviewer marker-gate details" in delta
    assert "Runtime operation / Jetson evidence snapshot" in delta
    assert "Safe publish and PR path" in delta
    assert "copied CI artifact summaries" in delta
    assert "generated `00_evidence_index.*` artifacts" in delta
    assert "detailed marker vocabulary owner" in delta
    assert "not production observability or a GitLab control plane" in delta
    assert "not a Lab report owner or production runtime proof" in delta
    assert "live Jetson execution is not implied" in delta
    assert "do not force push over public `main`" in delta
    assert_markers_in_order(
        delta,
        [
            "Start with `README.md`",
            "Follow `## Docs & Review Path`",
            "Use this rehearsal for the clean-clone baseline",
            "Use `docs/agent_runtime_e2e_demo.md`",
            "Use `docs/publish_inferedge.md`",
        ],
        label="final submission rehearsal current reviewer order",
    )


def test_cross_repo_quick_guide_path_preserves_lifecycle_order() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    ecosystem = (ROOT / "docs" / "ecosystem_1page.md").read_text(
        encoding="utf-8"
    )
    ecosystem_ko = (ROOT / "docs" / "ecosystem_1page.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (readme, readme_ko, ecosystem, ecosystem_ko):
        normalized_text = " ".join(text.split())
        assert "Cross-Repo Quick Guide Path" in text
        assert "Validation -> Evidence -> Operation Control" in normalized_text
        assert "agent_manifest_contract.ko.md" in text
        assert "agent_runtime_result_contract.ko.md" in text
        assert "InferEdgeLab/blob/main/README.ko.md" in text
        assert "detector_validation_matrix.ko.md" in text
        assert "runtime-regression-monitor.md" in text
        assert "operation_control.ko.md" in text
        assert "production SaaS" in text
        assert "cloud control plane" in text

    assert readme.index("agent_manifest_contract.ko.md") < readme.index(
        "agent_runtime_result_contract.ko.md"
    )
    assert readme.index("agent_runtime_result_contract.ko.md") < readme.index(
        "InferEdgeLab/blob/main/README.ko.md"
    )
    assert readme.index("detector_validation_matrix.ko.md") < readme.index(
        "runtime-regression-monitor.md"
    )
    assert readme.index("runtime-regression-monitor.md") < readme.index(
        "operation_control.ko.md"
    )
    assert (
        "Lab remains the final deployment decision owner"
        in " ".join(readme.split())
    )
    assert "최종 deployment decision owner는 Lab" in " ".join(readme_ko.split())


def test_agent_runtime_korean_guide_preserves_execution_boundaries() -> None:
    korean_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.ko.md").read_text(
        encoding="utf-8"
    )

    assert "Jetson 필요 여부" in korean_doc
    assert "필요 없음" in korean_doc
    assert "필요함" in korean_doc
    for command in [
        "bash scripts/demo_agent_runtime_e2e.sh",
        "--device-local",
        "--remote-dispatch",
        "--edgeenv-run-evidence",
        "--capture-tegrastats",
        "bash scripts/demo_jetson_5min_sustained.sh",
        "bash scripts/check_jetson_sustained_readiness.sh",
    ]:
        assert command in korean_doc

    for marker in [
        "Lab-owned deployment decision",
        "production observability",
        "GitLab control plane",
        "production remote execution",
        "sustained thermal endurance validation",
        "universal AI OS claims",
    ]:
        assert marker in korean_doc


def test_agent_runtime_demo_records_latest_jetson_reviewer_focus_validation() -> None:
    demo_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.md").read_text(
        encoding="utf-8"
    )
    korean_doc = (ROOT / "docs" / "agent_runtime_e2e_demo.ko.md").read_text(
        encoding="utf-8"
    )

    for text in (demo_doc, korean_doc):
        assert "20260608T232814Z" in text
        assert "06e4ab9" in text
        assert "3a7a464" in text
        assert "inferedge_agent_runtime_jetson_reviewer_focus_96_20260608T232814Z" in text
        assert (
            "inferedgelab_runtime_intelligence_reviewer_focus_jetson_20260608T232927Z"
            in text
        )
        assert (
            "inferedge_agent_runtime_jetson_reviewer_focus_96_registry_20260608T232814Z.md"
            in text
        )
        assert "Validated Reviewer Focus" in text
        assert "reviewer_focus_operation_quick_scan" in text
        assert "Runtime Intelligence EdgeEnv Preservation" in text
        assert "Operation Quick Scan Summary" in text
        assert "run-20260608-232827-e584af13" in text
        assert "yolo_env" in text
        assert "contract change" in text or "contract 변경" in text
        assert (
            "starter-only boundary" in text
            or "device-local starter를 production operation으로" in text
        )
        assert "d38df87" in text
        assert "inferedge_agent_runtime_jetson_sustained_5min_reviewer_focus_20260609T001057Z" in text
        assert (
            "inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.md"
            in text
        )
        assert (
            "inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.json"
            in text
        )
        assert "run-20260609-001553-51217d1d" in text
        assert "5-minute-class sustained replay (3600 frames)" in text
        assert "6 / 3597 / 3597 / 1802" in text
        assert "281" in text
        assert "Reviewer operation quick scan" in text
        assert "lab_preservation=present" in text


def test_internal_docs_provide_matching_korean_link_labels() -> None:
    link_pairs = [
        (
            "README.md",
            "InferEdge Ecosystem 1-Page Summary",
            "InferEdge 생태계 1페이지 요약",
            "docs/ecosystem_1page.md",
            "docs/ecosystem_1page.ko.md",
        ),
        (
            "README.md",
            "`docs/agent_runtime_e2e_demo.md`",
            "에이전트 런타임 e2e 데모 문서",
            "docs/agent_runtime_e2e_demo.md#smoke-gate-split",
            "docs/agent_runtime_e2e_demo.ko.md",
        ),
        (
            "README.md",
            "`docs/agent_runtime_e2e_demo.md`",
            "에이전트 런타임 e2e 데모 문서",
            "docs/agent_runtime_e2e_demo.md",
            "docs/agent_runtime_e2e_demo.ko.md",
        ),
        (
            "README.md",
            "`Clean Jetson Replay Runbook`",
            "클린 Jetson 재현 런북",
            "docs/agent_runtime_e2e_demo.md#clean-jetson-replay-runbook",
            "docs/agent_runtime_e2e_demo.ko.md",
        ),
        (
            "README.md",
            "`Jetson Device-Local Agent Runtime Evidence Report`",
            "Jetson 디바이스 로컬 에이전트 런타임 증거 보고서",
            "docs/evidence/jetson_device_local_agent_runtime_report.md",
            "docs/evidence/jetson_device_local_agent_runtime_report.ko.md",
        ),
        (
            "README.md",
            "`Jetson Device-Local 5-Minute Sustained Smoke Report`",
            "Jetson 디바이스 로컬 5분급 지속 스모크 보고서",
            "docs/evidence/jetson_device_local_5min_sustained_report.md",
            "docs/evidence/jetson_device_local_5min_sustained_report.ko.md",
        ),
        (
            "README.md",
            "`Snapshot HTML report`",
            "대표 스냅샷 HTML 보고서",
            "docs/evidence/jetson_device_local_5min_sustained_report.html",
            "docs/evidence/jetson_device_local_5min_sustained_report.html",
        ),
        (
            "docs/portfolio_summary.md",
            "InferEdge Ecosystem 1-Page Summary",
            "InferEdge 생태계 1페이지 요약",
            "ecosystem_1page.md",
            "ecosystem_1page.ko.md",
        ),
        (
            "docs/portfolio_summary.md",
            "`Jetson Device-Local Agent Runtime Evidence Report`",
            "Jetson 디바이스 로컬 에이전트 런타임 증거 보고서",
            "evidence/jetson_device_local_agent_runtime_report.md",
            "evidence/jetson_device_local_agent_runtime_report.ko.md",
        ),
        (
            "docs/portfolio_summary.md",
            "`Jetson Device-Local 5-Minute Sustained Smoke Report`",
            "Jetson 디바이스 로컬 5분급 지속 스모크 보고서",
            "evidence/jetson_device_local_5min_sustained_report.md",
            "evidence/jetson_device_local_5min_sustained_report.ko.md",
        ),
        (
            "docs/pipeline_map.md",
            "Ecosystem 1-Page Summary",
            "생태계 1페이지 요약",
            "ecosystem_1page.md",
            "ecosystem_1page.ko.md",
        ),
        (
            "docs/ecosystem_1page.md",
            "Portfolio Summary",
            "포트폴리오 요약",
            "portfolio_summary.md",
            "portfolio_summary.ko.md",
        ),
        (
            "docs/ecosystem_1page.md",
            "Pipeline Map",
            "파이프라인 맵",
            "pipeline_map.md",
            "pipeline_map.ko.md",
        ),
        (
            "docs/agent_runtime_e2e_demo.md",
            "`Jetson Device-Local Agent Runtime Evidence Report`",
            "Jetson 디바이스 로컬 에이전트 런타임 증거 보고서",
            "evidence/jetson_device_local_agent_runtime_report.md",
            "evidence/jetson_device_local_agent_runtime_report.ko.md",
        ),
        (
            "docs/agent_runtime_e2e_demo.md",
            "`Jetson Device-Local 5-Minute Sustained Smoke Report`",
            "Jetson 디바이스 로컬 5분급 지속 스모크 보고서",
            "evidence/jetson_device_local_5min_sustained_report.md",
            "evidence/jetson_device_local_5min_sustained_report.ko.md",
        ),
        (
            "docs/agent_runtime_e2e_demo.md",
            "`Snapshot HTML report`",
            "대표 스냅샷 HTML 보고서",
            "evidence/jetson_device_local_5min_sustained_report.html",
            "evidence/jetson_device_local_5min_sustained_report.html",
        ),
    ]

    for (
        relative_path,
        english_label,
        korean_label,
        english_target,
        korean_target,
    ) in link_pairs:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert f"[{english_label}]({english_target})" in text
        assert f"[한국어: {korean_label}]({korean_target})" in text


def test_evidence_index_preserves_device_local_override_producers(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "02_runtime_result_agent.json",
        {
            "runtime_operation_summary": {
                "schema_version": "inferedge-runtime-operation-summary-v1",
                "health_reason": "timeout_threshold_exceeded",
                "recommended_action": "review_latency_budget_or_degrade",
                "risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
                "evidence_gaps": ["thermal_memory_evidence_missing"],
            }
        },
    )
    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_description": "Device-local starter",
                "scenario_mode": "device_local",
                "observed_runtime_signals": {
                    "executed_count": 7,
                    "dropped_count": 1,
                    "fallback_count": 1,
                    "deadline_missed_count": 0,
                    "max_total_queue_depth": 5,
                    "policy_decision_count": 1,
                    "producer_source_count": 7,
                    "device_local_producer_count": 7,
                    "producer_sources": [
                        "resource_snapshot_fixture",
                        "image_file",
                        "fastapi_request_fixture",
                    ],
                    "tegrastats_sample_count": 1,
                },
                "workload_profiles": [
                    {
                        "agent_id": "vision_agent",
                        "producer_stage": "device_local_cli_override",
                    },
                    {
                        "agent_id": "voice_command_agent",
                        "producer_stage": "device_local_cli_override",
                    },
                ],
            },
            "queue_state_summary": {
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
            },
            "operation_risk_summary": {
                "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
                "primary_health_reason": "worker_health_degraded",
                "device_local_event_count": 7,
                "producer_event_count": 7,
                "not_a_deployment_decision": True,
            },
            "runtime_event_summary": {
                "device_local_event_count": 7,
                "producer_event_count": 7,
            },
        },
    )
    write_json(
        tmp_path / "04_aiguard_guard_analysis.json",
        {
            "guard_verdict": "blocked",
            "severity": "high",
            "evidence": [{"type": "profiled_workload_pressure"}],
        },
    )
    write_json(
        tmp_path / "05_lab_agent_runtime_report.json",
        {
            "agent_runtime_summary": {
                "edgeenv_preservation_context": {
                    "run_id": "run-edgeenv-runtime-operation",
                    "runtime_operation_decision_owner": "lab",
                    "comparability_role": "supplemental_evidence_not_gate",
                }
            },
            "agent_deployment_decision": {
                "decision": "blocked",
                "triggered_rules": ["sustained_overload_review"],
            }
        },
    )
    (tmp_path / "05_lab_agent_runtime_report.md").write_text(
        "\n".join(
            [
                "# Agent Runtime Reliability Report",
                "",
                "## Runtime Intelligence EdgeEnv Preservation",
                "",
                "| Field | Value |",
                "|---|---|",
                "| edgeenv_run_id | run-edgeenv-runtime-operation |",
                "| comparability_role | supplemental_evidence_not_gate |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_json(
        tmp_path / "08_edgeenv_run_show.json",
        {
            "schema_version": "edgeenv.result.v1",
            "run_id": "run-edgeenv-runtime-operation",
            "result_path": "/tmp/.edgeenv/runs/run-edgeenv-runtime-operation/result.json",
            "runtime_operation_summary": {
                "schema_version": "inferedge-runtime-operation-summary-v1",
                "health_reason": "timeout_threshold_exceeded",
                "recommended_action": "review_latency_budget_or_degrade",
                "risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
            },
            "runtime_operation_summary_label": (
                "operation_summary: mode=timeout_threshold_exceeded, "
                "max_queue=n/a, queue_pressure=n/a, deadline_missed=n/a, "
                "fallback=n/a, dropped=n/a"
            ),
        },
    )

    index = index_module.build_summary(tmp_path, requested_frames="4")

    run_summary = index["run_summary"]
    edgeenv_summary = index["edgeenv_summary"]
    assert index["operation_path"] == "device_local_starter"
    assert run_summary["producer_sources"] == [
        "resource_snapshot_fixture",
        "image_file",
        "fastapi_request_fixture",
    ]
    assert run_summary["duration_class"] == "quick_starter_smoke"
    assert run_summary["duration_label"] == "quick starter smoke (4 frames)"
    assert run_summary["duration_source"] == "entrypoint_requested_frames"
    assert run_summary["duration_scope_label"] == (
        "source=entrypoint_requested_frames, "
        "label=quick starter smoke (4 frames), "
        "class=quick_starter_smoke, frames=4"
    )
    assert run_summary["producer_source_count"] == 7
    assert run_summary["device_local_producer_count"] == 7
    assert run_summary["producer_stages"] == ["device_local_cli_override"]
    assert run_summary["queue_pressure_reason"] == (
        "max_total_queue_depth_exceeded_overload_threshold"
    )
    assert run_summary["max_pressure_task"] == "vision_agent"
    assert run_summary["device_local_event_count"] == 7
    assert run_summary["producer_event_count"] == 7
    assert run_summary["runtime_operation_health_reason"] == (
        "timeout_threshold_exceeded"
    )
    assert run_summary["runtime_operation_recommended_action"] == (
        "review_latency_budget_or_degrade"
    )
    assert run_summary["runtime_operation_risk_labels"] == [
        "runtime_timeout_observed",
        "latency_budget_exceeded",
    ]
    assert run_summary["runtime_operation_evidence_gaps"] == [
        "thermal_memory_evidence_missing"
    ]
    assert edgeenv_summary["run_id"] == "run-edgeenv-runtime-operation"
    assert edgeenv_summary["has_runtime_operation_summary"] is True
    assert edgeenv_summary["runtime_operation_schema_version"] == (
        "inferedge-runtime-operation-summary-v1"
    )
    assert edgeenv_summary["edgeenv_runtime_operation_summary_label"] == (
        "operation_summary: mode=timeout_threshold_exceeded, max_queue=n/a, "
        "queue_pressure=n/a, deadline_missed=n/a, fallback=n/a, dropped=n/a"
    )
    assert edgeenv_summary["operation_summary_label"] == (
        "operation_summary: mode=device_local_starter, max_queue=5, "
        "queue_pressure=max_total_queue_depth_exceeded_overload_threshold, "
        "deadline_missed=0, fallback=1, dropped=1"
    )
    assert edgeenv_summary["lab_report_operation_summary_label"] == (
        edgeenv_summary["operation_summary_label"]
    )
    assert edgeenv_summary["comparability_role"] == "supplemental_evidence_not_gate"
    assert edgeenv_summary["lab_report_marker"] == (
        "Runtime Intelligence EdgeEnv Preservation"
    )
    assert edgeenv_summary["lab_report_preservation_section_present"] is True
    assert edgeenv_summary["lab_report_preservation_context_present"] is True
    assert edgeenv_summary["lab_report_preservation_run_id"] == (
        "run-edgeenv-runtime-operation"
    )
    assert edgeenv_summary["lab_report_decision_owner"] == "lab"
    assert edgeenv_summary["preservation_identity_label"] == (
        "identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert edgeenv_summary["preservation_details_label"] == (
        "sources=resource_snapshot_fixture+image_file+fastapi_request_fixture, "
        "stages=device_local_cli_override, device_local_events=7, "
        "resource=resource_snapshot_fixture+tegrastats_timeline, "
        "queue=max_total_queue_depth_exceeded_overload_threshold"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_focus_marker"] == (
        "Operation quick scan"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_marker"] == (
        "Reviewer operation quick scan"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_rendered_label"] == (
        "rendered_label=Reviewer operation quick scan"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_raw_marker"] == (
        "reviewer_focus_operation_quick_scan"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_raw_marker_label"] == (
        "raw_marker=reviewer_focus_operation_quick_scan"
    )
    assert edgeenv_summary["lab_report_operation_quick_scan_label"] == (
        "queue_pressure_reason=max_total_queue_depth_exceeded_overload_threshold; "
        "max_total_queue_depth=5; deadline_missed_count=0; fallback_count=1; "
        "preservation=identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert "Operation quick scan" in edgeenv_summary[
        "lab_expected_report_markers"
    ]
    assert "Reviewer operation quick scan" in edgeenv_summary[
        "lab_expected_report_markers"
    ]
    assert "raw_marker=reviewer_focus_operation_quick_scan" in edgeenv_summary[
        "lab_expected_report_markers"
    ]
    assert edgeenv_summary["lab_report_marker_context_role"] == (
        "lab_report_contract_context"
    )
    assert edgeenv_summary["aiguard_validates_expected_report_markers"] is False

    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "lab_report_marker" in markdown
    assert "Runtime Intelligence EdgeEnv Preservation" in markdown
    assert "preservation_identity" in markdown
    assert "identity=jetson_device_local_preservation" in markdown
    assert "preservation_details" in markdown
    assert "sources=resource_snapshot_fixture+image_file+fastapi_request_fixture" in markdown
    assert "duration_class" in markdown
    assert "quick_starter_smoke" in markdown
    assert "duration_source" in markdown
    assert "entrypoint_requested_frames" in markdown
    assert "duration_scope_label" in markdown
    assert "lab_report_preservation_section_present" in markdown
    assert "lab_report_preservation_run_id" in markdown
    assert "edgeenv_runtime_operation_summary_label" in markdown
    assert "operation_summary: mode=timeout_threshold_exceeded" in markdown
    assert "operation_summary_label" in markdown
    assert "lab_report_operation_summary_label" in markdown
    assert "operation_summary: mode=device_local_starter" in markdown
    assert "lab_report_operation_quick_scan_focus_marker" in markdown
    assert "Operation quick scan" in markdown
    assert "lab_report_operation_quick_scan_marker" in markdown
    assert "Reviewer operation quick scan" in markdown
    assert "lab_report_operation_quick_scan_rendered_label" in markdown
    assert "rendered_label=Reviewer operation quick scan" in markdown
    assert "lab_report_operation_quick_scan_raw_marker" in markdown
    assert "lab_report_operation_quick_scan_raw_marker_label" in markdown
    assert "raw_marker=reviewer_focus_operation_quick_scan" in markdown
    assert "lab_report_operation_quick_scan_label" in markdown
    assert "lab_expected_report_markers" in markdown
    assert "lab_report_contract_context" in markdown
    assert "aiguard_validates_expected_report_markers" in markdown
    assert "reviewer navigation context" in markdown
    assert "do not make the index a Lab report owner" in markdown
    assert "make AIGuard validate Lab report marker contracts" in markdown
    assert "Raw quick-scan marker labels are preserved here for traceability" in markdown
    assert "not as a new source contract" in markdown


def test_evidence_index_labels_runtime_duration_classes(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_duration",
        "scripts/build_agent_runtime_evidence_index.py",
    )

    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_mode": "device_local",
                "observed_runtime_signals": {},
            }
        },
    )

    quick_index = index_module.build_summary(tmp_path, requested_frames="8")
    assert quick_index["run_summary"]["duration_class"] == "quick_starter_smoke"
    assert quick_index["run_summary"]["duration_label"] == (
        "quick starter smoke (8 frames)"
    )
    assert quick_index["run_summary"]["duration_source"] == (
        "entrypoint_requested_frames"
    )
    assert quick_index["run_summary"]["duration_scope_label"] == (
        "source=entrypoint_requested_frames, "
        "label=quick starter smoke (8 frames), "
        "class=quick_starter_smoke, frames=8"
    )
    quick_md_path = tmp_path / "quick_duration_index.md"
    index_module.write_markdown(quick_index, quick_md_path)
    quick_markdown = quick_md_path.read_text(encoding="utf-8")
    assert "## Reviewer Duration Label" in quick_markdown
    assert "| Duration label | quick starter smoke (8 frames) |" in quick_markdown
    assert "| Duration class | quick_starter_smoke |" in quick_markdown
    assert "| Duration source | entrypoint_requested_frames |" in quick_markdown
    assert (
        "| Duration scope label | source=entrypoint_requested_frames, "
        "label=quick starter smoke (8 frames), class=quick_starter_smoke, frames=8 |"
        in quick_markdown
    )

    short_index = index_module.build_summary(tmp_path, requested_frames="96")
    assert short_index["run_summary"]["duration_class"] == "short_96_frame_class"
    assert short_index["run_summary"]["duration_label"] == (
        "short 96-frame-class replay (96 frames)"
    )
    short_md_path = tmp_path / "short_duration_index.md"
    index_module.write_markdown(short_index, short_md_path)
    short_markdown = short_md_path.read_text(encoding="utf-8")
    assert "| Duration label | short 96-frame-class replay (96 frames) |" in short_markdown
    assert "| Duration class | short_96_frame_class |" in short_markdown
    assert "| Duration source | entrypoint_requested_frames |" in short_markdown

    five_min_index = index_module.build_summary(tmp_path, requested_frames="3600")
    assert five_min_index["run_summary"]["duration_class"] == (
        "5_minute_class_sustained"
    )
    assert five_min_index["run_summary"]["duration_label"] == (
        "5-minute-class sustained replay (3600 frames)"
    )
    five_min_md_path = tmp_path / "five_min_duration_index.md"
    index_module.write_markdown(five_min_index, five_min_md_path)
    five_min_markdown = five_min_md_path.read_text(encoding="utf-8")
    assert (
        "| Duration label | 5-minute-class sustained replay (3600 frames) |"
        in five_min_markdown
    )
    assert "| Duration class | 5_minute_class_sustained |" in five_min_markdown
    assert "| Duration source | entrypoint_requested_frames |" in five_min_markdown


def test_evidence_index_preserves_orchestrator_duration_source(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_duration_source",
        "scripts/build_agent_runtime_evidence_index.py",
    )

    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_mode": "device_local",
                "frames": 96,
            }
        },
    )

    index = index_module.build_summary(tmp_path)
    run_summary = index["run_summary"]
    assert run_summary["frames"] == 96
    assert run_summary["duration_class"] == "short_96_frame_class"
    assert run_summary["duration_label"] == (
        "short 96-frame-class replay (96 frames)"
    )
    assert run_summary["duration_source"] == (
        "orchestrator.multi_workload_sustained_summary.frames"
    )
    assert run_summary["duration_scope_label"] == (
        "source=orchestrator.multi_workload_sustained_summary.frames, "
        "label=short 96-frame-class replay (96 frames), "
        "class=short_96_frame_class, frames=96"
    )


def test_evidence_index_uses_derived_operation_risk_summary(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_operation_risk",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "03_orchestration_summary.json",
        {
            "multi_workload_sustained_summary": {
                "scenario_mode": "device_local",
                "observed_runtime_signals": {
                    "device_local_producer_count": 9,
                    "producer_source_count": 9,
                },
            },
            "operation_risk_summary": {
                "schema_version": "inferedge-entrypoint-operation-risk-summary-v1",
                "queue_pressure_reason": "queue_backlog_threshold_exceeded",
                "max_pressure_task": "vision_agent",
                "device_local_event_count": 9,
                "producer_event_count": 9,
                "not_a_deployment_decision": True,
            },
        },
    )

    index = index_module.build_summary(tmp_path, requested_frames="9")
    run_summary = index["run_summary"]

    assert run_summary["queue_pressure_reason"] == "queue_backlog_threshold_exceeded"
    assert run_summary["duration_class"] == "quick_starter_smoke"
    assert run_summary["max_pressure_task"] == "vision_agent"
    assert run_summary["device_local_event_count"] == 9
    assert run_summary["producer_event_count"] == 9


def test_run_registry_surfaces_device_local_override_producers(tmp_path: Path) -> None:
    registry_module = load_script_module(
        "build_agent_runtime_run_registry",
        "scripts/build_agent_runtime_run_registry.py",
    )
    run_dir = tmp_path / "device_local_override"
    run_dir.mkdir()
    write_json(
        run_dir / "00_evidence_index.json",
        {
            "operation_path": "device_local_starter",
            "run_summary": {
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_description": "Device-local starter",
                "scenario_mode": "device_local",
                "frames": "4",
                "duration_class": "quick_starter_smoke",
                "duration_label": "quick starter smoke (4 frames)",
                "duration_source": "entrypoint_requested_frames",
                "duration_scope_label": (
                    "source=entrypoint_requested_frames, "
                    "label=quick starter smoke (4 frames), "
                    "class=quick_starter_smoke, frames=4"
                ),
                "max_total_queue_depth": 5,
                "dropped_count": 1,
                "fallback_count": 1,
                "deadline_missed_count": 0,
                "tegrastats_sample_count": 1,
                "producer_sources": [
                    "image_file",
                    "fastapi_request_fixture",
                    "resource_snapshot_fixture",
                ],
                "producer_source_count": 7,
                "device_local_producer_count": 7,
                "device_local_event_count": 7,
                "producer_event_count": 7,
                "producer_stages": ["device_local_cli_override"],
                "runtime_operation_health_reason": "timeout_threshold_exceeded",
                "runtime_operation_recommended_action": (
                    "review_latency_budget_or_degrade"
                ),
                "runtime_operation_risk_labels": [
                    "runtime_timeout_observed",
                    "latency_budget_exceeded",
                ],
                "queue_pressure_reason": (
                    "max_total_queue_depth_exceeded_overload_threshold"
                ),
                "max_pressure_task": "vision_agent",
            },
            "guard_summary": {"guard_verdict": "blocked", "severity": "high"},
            "decision_summary": {
                "decision": "blocked",
                "triggered_rules": ["sustained_overload_review"],
            },
            "edgeenv_summary": {
                "run_id": "run-edgeenv-runtime-operation",
                "has_runtime_operation_summary": True,
                "runtime_operation_health_reason": "timeout_threshold_exceeded",
                "lab_report_marker": "Runtime Intelligence EdgeEnv Preservation",
                "lab_report_operation_quick_scan_marker": (
                    "Reviewer operation quick scan"
                ),
                "lab_report_operation_quick_scan_label": (
                    "queue_pressure_reason="
                    "max_total_queue_depth_exceeded_overload_threshold; "
                    "max_total_queue_depth=5; deadline_missed_count=0; "
                    "fallback_count=1; preservation="
                    "identity=jetson_device_local_preservation, "
                    "path=device_local_starter, "
                    "run=run-edgeenv-runtime-operation"
                ),
                "edgeenv_runtime_operation_summary_label": (
                    "operation_summary: mode=timeout_threshold_exceeded, "
                    "max_queue=n/a, queue_pressure=n/a, deadline_missed=n/a, "
                    "fallback=n/a, dropped=n/a"
                ),
                "operation_summary_label": (
                    "operation_summary: mode=device_local_starter, max_queue=5, "
                    "queue_pressure=max_total_queue_depth_exceeded_overload_threshold, "
                    "deadline_missed=0, fallback=1, dropped=1"
                ),
                "lab_report_operation_summary_label": (
                    "operation_summary: mode=device_local_starter, max_queue=5, "
                    "queue_pressure=max_total_queue_depth_exceeded_overload_threshold, "
                    "deadline_missed=0, fallback=1, dropped=1"
                ),
                "preservation_identity_label": (
                    "identity=jetson_device_local_preservation, "
                    "path=device_local_starter, run=run-edgeenv-runtime-operation"
                ),
                "preservation_details_label": (
                    "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture, "
                    "stages=device_local_cli_override, device_local_events=7, "
                    "resource=resource_snapshot_fixture+tegrastats_timeline, "
                    "queue=max_total_queue_depth_exceeded_overload_threshold"
                ),
                "lab_report_preservation_section_present": True,
                "lab_report_preservation_context_present": True,
            },
        },
    )

    registry = registry_module.build_registry(
        [run_dir / "00_evidence_index.json"],
        output_base=tmp_path,
    )

    run = registry["runs"][0]
    assert run["producer_sources"] == [
        "image_file",
        "fastapi_request_fixture",
        "resource_snapshot_fixture",
    ]
    assert run["duration_class"] == "quick_starter_smoke"
    assert run["duration_label"] == "quick starter smoke (4 frames)"
    assert run["duration_source"] == "entrypoint_requested_frames"
    assert run["duration_scope_label"] == (
        "source=entrypoint_requested_frames, "
        "label=quick starter smoke (4 frames), "
        "class=quick_starter_smoke, frames=4"
    )
    assert run["producer_source_count"] == 7
    assert run["device_local_producer_count"] == 7
    assert run["producer_stages"] == ["device_local_cli_override"]
    assert run["queue_pressure_reason"] == (
        "max_total_queue_depth_exceeded_overload_threshold"
    )
    assert run["max_pressure_task"] == "vision_agent"
    assert run["device_local_event_count"] == 7
    assert run["producer_event_count"] == 7
    assert run["runtime_operation_health_reason"] == "timeout_threshold_exceeded"
    assert run["runtime_operation_recommended_action"] == (
        "review_latency_budget_or_degrade"
    )
    assert run["runtime_operation_risk_labels"] == [
        "runtime_timeout_observed",
        "latency_budget_exceeded",
    ]
    assert run["edgeenv_run_id"] == "run-edgeenv-runtime-operation"
    assert run["edgeenv_has_runtime_operation_summary"] is True
    assert run["edgeenv_runtime_operation_health_reason"] == (
        "timeout_threshold_exceeded"
    )
    assert run["edgeenv_runtime_operation_summary_label"] == (
        "operation_summary: mode=timeout_threshold_exceeded, max_queue=n/a, "
        "queue_pressure=n/a, deadline_missed=n/a, fallback=n/a, dropped=n/a"
    )
    assert run["edgeenv_operation_summary_label"] == (
        "operation_summary: mode=device_local_starter, max_queue=5, "
        "queue_pressure=max_total_queue_depth_exceeded_overload_threshold, "
        "deadline_missed=0, fallback=1, dropped=1"
    )
    assert run["edgeenv_lab_report_operation_summary_label"] == (
        run["edgeenv_operation_summary_label"]
    )
    assert run["edgeenv_lab_report_marker"] == (
        "Runtime Intelligence EdgeEnv Preservation"
    )
    assert run["edgeenv_lab_report_operation_quick_scan_marker"] == (
        "Reviewer operation quick scan"
    )
    assert run["edgeenv_lab_report_operation_quick_scan_raw_marker"] == (
        "reviewer_focus_operation_quick_scan"
    )
    assert run["edgeenv_lab_report_operation_quick_scan_raw_marker_label"] == (
        "raw_marker=reviewer_focus_operation_quick_scan"
    )
    assert run["edgeenv_lab_report_operation_quick_scan_label"] == (
        "queue_pressure_reason=max_total_queue_depth_exceeded_overload_threshold; "
        "max_total_queue_depth=5; deadline_missed_count=0; fallback_count=1; "
        "preservation=identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert run["edgeenv_preservation_identity_label"] == (
        "identity=jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation"
    )
    assert run["edgeenv_preservation_details_label"].startswith(
        "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture"
    )
    assert run["edgeenv_lab_preservation_section_present"] is True
    assert run["edgeenv_lab_preservation_context_present"] is True

    md_path = tmp_path / "agent_runtime_registry.md"
    registry_module.write_markdown(registry, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "Operation Quick Scan Raw Marker" in markdown
    assert "Operation Quick Scan Raw Marker Label" in markdown
    assert "reviewer_focus_operation_quick_scan" in markdown
    assert "raw_marker=reviewer_focus_operation_quick_scan" in markdown
    assert "lab_preservation=present" in markdown
    assert "lab_context=present" in markdown
    assert "Operation Quick Scan" in markdown
    assert "Reviewer operation quick scan" in markdown
    assert (
        "queue_pressure_reason=max_total_queue_depth_exceeded_overload_threshold"
        in markdown
    )
    assert "identity=jetson_device_local_preservation" in markdown
    assert "sources=image_file+fastapi_request_fixture+resource_snapshot_fixture" in markdown
    assert "quick_starter_smoke" in markdown
    assert "quick starter smoke (4 frames)" in markdown
    assert "entrypoint_requested_frames" in markdown
    assert "source=entrypoint_requested_frames" in markdown
    assert "## Duration Comparison Summary" in markdown
    assert "## Operation Quick Scan Summary" in markdown
    assert markdown.index("## Operation Quick Scan Summary") < markdown.index(
        "## Runs"
    )
    assert "Duration Label" in markdown
    assert "Duration Sources" in markdown
    assert "Quick Scan" in markdown
    assert "Queue Max" in markdown
    assert "Deadline Missed" in markdown
    assert "Operation Summary" in markdown
    summary_block = markdown[
        markdown.index("## Operation Quick Scan Summary") : markdown.index("## Runs")
    ]
    runs_block = markdown[markdown.index("## Runs") :]
    assert "Raw Marker" not in summary_block
    assert "raw_marker=reviewer_focus_operation_quick_scan" not in summary_block
    assert "Reviewer operation quick scan:" not in summary_block
    assert (
        "| device_local_override | quick starter smoke (4 frames) | 4 | "
        "device_local_starter | operation_summary: mode=device_local_starter, "
        "max_queue=5, "
        "queue_pressure=max_total_queue_depth_exceeded_overload_threshold, "
        "deadline_missed=0, fallback=1, dropped=1 | "
        "max_total_queue_depth_exceeded_overload_threshold | "
        "5 | 0 | 1 | jetson_device_local_preservation, "
        "path=device_local_starter, run=run-edgeenv-runtime-operation | "
        "blocked | blocked/high |"
    ) in summary_block
    assert "operation_summary: mode=timeout_threshold_exceeded" in runs_block
    assert "operation_summary: mode=device_local_starter" in runs_block
    assert "raw_marker=reviewer_focus_operation_quick_scan" in runs_block
    assert "Reviewer operation quick scan:" in runs_block
    assert "reviewer-facing navigation metadata" in markdown
    assert "Lab report marker context" in markdown
    assert "raw quick-scan marker labels appear" in markdown
    assert "reviewer-navigation bug" in markdown
    assert "detailed rows and JSON traceability fields" in markdown
    assert "does not make this registry a Lab report owner" in markdown


def test_run_registry_summarizes_duration_comparison_before_runs(tmp_path: Path) -> None:
    registry_module = load_script_module(
        "build_agent_runtime_run_registry_duration_summary",
        "scripts/build_agent_runtime_run_registry.py",
    )
    short_dir = tmp_path / "jetson_96"
    sustained_dir = tmp_path / "jetson_5min"
    short_dir.mkdir()
    sustained_dir.mkdir()
    write_json(
        short_dir / "00_evidence_index.json",
        {
            "operation_path": "device_local_starter",
            "run_summary": {
                "frames": "96",
                "duration_class": "short_96_frame_class",
                "duration_label": "short 96-frame-class replay (96 frames)",
                "duration_source": "entrypoint_requested_frames",
                "duration_scope_label": (
                    "source=entrypoint_requested_frames, "
                    "label=short 96-frame-class replay (96 frames), "
                    "class=short_96_frame_class, frames=96"
                ),
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_mode": "device_local",
            },
            "guard_summary": {"guard_verdict": "pass", "severity": "low"},
            "decision_summary": {"decision": "review"},
        },
    )
    write_json(
        sustained_dir / "00_evidence_index.json",
        {
            "operation_path": "device_local_starter",
            "run_summary": {
                "frames": "3600",
                "duration_class": "5_minute_class_sustained",
                "duration_label": "5-minute-class sustained replay (3600 frames)",
                "duration_source": (
                    "orchestrator.multi_workload_sustained_summary.frames"
                ),
                "duration_scope_label": (
                    "source=orchestrator.multi_workload_sustained_summary.frames, "
                    "label=5-minute-class sustained replay (3600 frames), "
                    "class=5_minute_class_sustained, frames=3600"
                ),
                "scenario_label": "device_local_sustained_starter",
                "scenario_category": "device_local",
                "scenario_mode": "device_local",
            },
            "guard_summary": {"guard_verdict": "blocked", "severity": "high"},
            "decision_summary": {"decision": "blocked"},
        },
    )

    registry = registry_module.build_registry(
        [
            short_dir / "00_evidence_index.json",
            sustained_dir / "00_evidence_index.json",
        ],
        output_base=tmp_path,
    )
    md_path = tmp_path / "agent_runtime_registry.md"
    registry_module.write_markdown(registry, md_path)
    markdown = md_path.read_text(encoding="utf-8")

    assert markdown.index("## Duration Comparison Summary") < markdown.index("## Runs")
    assert markdown.index("## Operation Quick Scan Summary") < markdown.index(
        "## Runs"
    )
    assert "No operation quick-scan marker context was found" in markdown
    assert (
        "| short 96-frame-class replay (96 frames) | short_96_frame_class | 1 | "
        "96 | entrypoint_requested_frames | device_local_starter | review | pass/low |"
    ) in markdown
    assert (
        "| 5-minute-class sustained replay (3600 frames) | "
        "5_minute_class_sustained | 1 | 3600 | "
        "orchestrator.multi_workload_sustained_summary.frames | device_local_starter | "
        "blocked | blocked/high |"
    ) in markdown
    assert "source=entrypoint_requested_frames" in markdown
    assert "source=orchestrator.multi_workload_sustained_summary.frames" in markdown


def test_evidence_index_preserves_remote_dispatch_boundary(tmp_path: Path) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_boundary",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "decision_reason": "selected online worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": False,
                "production_remote_execution": False,
                "transport": "http",
                "status": "failed",
                "error_category": "connection_error",
            },
            "fallback_execution_result": {
                "final_status": "succeeded",
                "attempts": [
                    {
                        "selected_worker_id": "fallback-http-worker",
                        "status": "succeeded",
                        "production_remote_execution": False,
                    }
                ],
            },
            "remote_operation_summary": {
                "execution_requested": True,
                "execution_performed": True,
                "remote_execution_status": "failed",
                "remote_error_category": "connection_error",
                "fallback_final_status": "succeeded",
                "final_status": "succeeded",
                "production_remote_execution": False,
                "evidence_role": (
                    "remote_worker_selection_and_starter_execution_evidence"
                ),
            },
            "remote_runtime_event_summary": {
                "event_count": 4,
                "runtime_event_count": 4,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
            "downstream_expectation": {
                "aiguard_evidence_type": "remote_execution_recovered_by_fallback",
                "lab_report_context": "Remote fallback starter evidence",
            },
        },
    )

    index = index_module.build_summary(tmp_path)

    remote = index["remote_summary"]
    assert index["operation_path"] == "remote_dispatch_with_fallback"
    assert remote["dispatch_status"] == "accepted"
    assert remote["selected_worker_id"] == "primary-http-worker"
    assert remote["remote_execution_status"] == "failed"
    assert remote["remote_error_category"] == "connection_error"
    assert remote["fallback_final_status"] == "succeeded"
    assert remote["final_status"] == "succeeded"
    assert remote["production_remote_execution"] is False
    assert remote["remote_event_count"] == 4
    assert remote["remote_runtime_event_count"] == 4
    assert remote["remote_event_summary_role"] == (
        "remote_dispatch_runtime_event_compact_summary"
    )
    assert remote["operation_boundary"] == (
        "remote dispatch starter evidence only"
    )
    assert remote["downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert remote["downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )


def test_evidence_index_markdown_surfaces_remote_dispatch_boundary(
    tmp_path: Path,
) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_boundary_md",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "decision_reason": "selected online worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": False,
                "production_remote_execution": False,
                "status": "failed",
            },
            "remote_runtime_event_summary": {
                "event_count": 2,
                "runtime_event_count": 2,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
        },
    )

    index = index_module.build_summary(tmp_path)
    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")

    assert "remote_event_summary_role" in markdown
    assert "remote_dispatch_runtime_event_compact_summary" in markdown
    assert "operation_boundary" in markdown
    assert "remote dispatch starter evidence only" in markdown
    assert "production_remote_execution" in markdown


def test_evidence_index_derives_remote_dispatch_lab_context_from_outputs(
    tmp_path: Path,
) -> None:
    index_module = load_script_module(
        "build_agent_runtime_evidence_index_remote_lab_context",
        "scripts/build_agent_runtime_evidence_index.py",
    )
    write_json(
        tmp_path / "06_remote_dispatch_result.json",
        {
            "dispatch_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
            },
            "remote_execution_result": {
                "execution_requested": True,
                "execution_performed": True,
                "production_remote_execution": False,
                "status": "failed",
                "error_category": "connection_error",
            },
            "fallback_execution_result": {
                "final_status": "succeeded",
                "production_remote_execution": False,
            },
            "remote_runtime_event_summary": {
                "event_count": 4,
                "runtime_event_count": 4,
                "production_remote_execution": False,
                "evidence_role": "remote_dispatch_runtime_event_compact_summary",
                "operation_boundary": "remote dispatch starter evidence only",
            },
        },
    )
    write_json(
        tmp_path / "07_remote_dispatch_guard_analysis.json",
        {
            "evidence": [
                {"type": "remote_execution_failed"},
                {"type": "remote_execution_recovered_by_fallback"},
            ],
        },
    )
    (tmp_path / "05_lab_agent_runtime_report.md").write_text(
        "Remote fallback starter evidence:\n",
        encoding="utf-8",
    )

    index = index_module.build_summary(tmp_path)
    remote = index["remote_summary"]

    assert remote["downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert remote["downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )

    md_path = tmp_path / "00_evidence_index.md"
    index_module.write_markdown(index, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "remote_execution_recovered_by_fallback" in markdown
    assert "Remote fallback starter evidence" in markdown


def test_run_registry_surfaces_remote_dispatch_boundary(tmp_path: Path) -> None:
    registry_module = load_script_module(
        "build_agent_runtime_run_registry_remote_boundary",
        "scripts/build_agent_runtime_run_registry.py",
    )
    run_dir = tmp_path / "remote_fallback"
    run_dir.mkdir()
    write_json(
        run_dir / "00_evidence_index.json",
        {
            "operation_path": "remote_dispatch_with_fallback",
            "run_summary": {
                "scenario_label": "remote_dispatch_fallback_starter",
            },
            "guard_summary": {
                "guard_verdict": "review_required",
                "severity": "medium",
            },
            "decision_summary": {
                "decision": "review",
                "triggered_rules": ["remote_fallback_starter_review"],
            },
            "remote_summary": {
                "dispatch_status": "accepted",
                "selected_worker_id": "primary-http-worker",
                "remote_execution_status": "failed",
                "fallback_final_status": "succeeded",
                "final_status": "succeeded",
                "production_remote_execution": False,
                "operation_boundary": "remote dispatch starter evidence only",
                "remote_event_summary_role": (
                    "remote_dispatch_runtime_event_compact_summary"
                ),
                "remote_event_count": 4,
                "remote_runtime_event_count": 4,
                "downstream_aiguard_evidence_type": (
                    "remote_execution_recovered_by_fallback"
                ),
                "downstream_lab_report_context": (
                    "Remote fallback starter evidence"
                ),
            },
        },
    )

    registry = registry_module.build_registry(
        [run_dir / "00_evidence_index.json"],
        output_base=tmp_path,
    )

    run = registry["runs"][0]
    assert run["operation_path"] == "remote_dispatch_with_fallback"
    assert run["remote_dispatch_status"] == "accepted"
    assert run["remote_selected_worker_id"] == "primary-http-worker"
    assert run["remote_execution_status"] == "failed"
    assert run["fallback_final_status"] == "succeeded"
    assert run["remote_final_status"] == "succeeded"
    assert run["remote_production_remote_execution"] is False
    assert run["remote_operation_boundary"] == (
        "remote dispatch starter evidence only"
    )
    assert run["remote_event_summary_role"] == (
        "remote_dispatch_runtime_event_compact_summary"
    )
    assert run["remote_event_count"] == 4
    assert run["remote_runtime_event_count"] == 4
    assert run["remote_downstream_aiguard_evidence_type"] == (
        "remote_execution_recovered_by_fallback"
    )
    assert run["remote_downstream_lab_report_context"] == (
        "Remote fallback starter evidence"
    )

    md_path = tmp_path / "agent_runtime_registry.md"
    registry_module.write_markdown(registry, md_path)
    markdown = md_path.read_text(encoding="utf-8")
    assert "lab=Remote fallback starter evidence" in markdown
