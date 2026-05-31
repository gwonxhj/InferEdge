# InferEdge Portfolio Summary

InferEdge is a local-first Edge AI inference validation pipeline that turns an ONNX model into traceable build artifacts, real runtime evidence, structured evaluation, optional diagnosis, and a Lab-owned deployment decision.

## 30-Second Structure

```text
Can we deploy this model?
-> Forge -> Runtime -> Lab (+ optional AIGuard)

Can this benchmark evidence be trusted and compared?
-> InferEdgeEnv v0.1.5 comparability layer

Can deployed workloads stay stable under load?
-> InferEdgeOrchestrator operation layer
```

For a diagram-first version of this same structure, see
[InferEdge Ecosystem 1-Page Summary](ecosystem_1page.md).

Reusable first-slide / README visual:

```text
docs/assets/inferedge_ecosystem_diagram.svg
```

## Repository Roles

| Repository | One-line role | Boundary |
|---|---|---|
| InferEdge | Multi-repository entrypoint and reproducible clone/smoke map | Orchestrates review flow; does not replace individual repo contracts |
| InferEdgeForge | Build provenance and artifact handoff layer | Creates metadata/manifest evidence; does not run inference or decide deployment |
| InferEdge-Runtime | C++ execution and Lab-compatible result export layer | Runs/profiles artifacts and exports result JSON; does not own comparison policy |
| InferEdgeLab | Validation, comparison, report, API, Local Studio, and deployment decision layer | Owns `deployment_decision`; consumes evidence rather than generating build artifacts |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence layer | Adds `guard_analysis`; does not make the final deployment decision |
| InferEdgeEnv | v1-complete local-first run evidence registry and comparability checker | Records whether benchmark evidence can be trusted and compared; does not validate deployability |
| InferEdgeOrchestrator | Post-deployment runtime operation-control layer | Schedules and sheds load after deployment; does not decide whether a model should deploy |

## Core Message

The Core 4 validation path is:

- Forge preserves build identity.
- Runtime records real execution evidence.
- Lab compares, evaluates, reports, and decides.
- AIGuard optionally explains suspicious evidence.

The ecosystem extension layers stay separate:

- Env records benchmark evidence and comparability. Its `v0.1.5` release freezes this role as the v1-complete baseline.
- Orchestrator controls runtime behavior after deployment.

## Implementation Status

This status table prevents roadmap language from being read as completed
production capability.

| Capability | Status | Portfolio wording |
|---|---|---|
| Core 4 validation pipeline | Implemented | Local-first validation pipeline with provenance, Runtime evidence, Lab decision, and optional AIGuard evidence |
| Local Studio | Implemented | Browser-based local workflow for demo evidence replay, compare, decision, and AIGuard cases |
| Evaluation / contract validation | Implemented | YOLOv8 COCO subset, simplified mAP50, bbox/score/model contract evidence |
| AIGuard diagnosis cases | Implemented | Deterministic evidence for bbox collapse, score saturation, temporal instability, and baseline deviation |
| Runtime operation e2e chain | Implemented | Entrypoint smoke connects agent manifest, Runtime result, Orchestrator summary, AIGuard analysis, and Lab report |
| Orchestrator operation evidence in Lab report | Implemented | Lab surfaces AIGuard `worker_health_degradation` and `scheduler_delay_pattern` context from Orchestrator telemetry |
| Runtime Intelligence artifact gate | Implemented | Cross-repo smoke includes Lab's local-first bundle manifest/report/CI artifact gates for Orchestrator -> EdgeEnv -> AIGuard -> Lab evidence, including Lab-owned expected report marker context, EdgeEnv-preserved `operation_risk_summary` rows, Lab EdgeEnv preservation context markers, and directly gated Jetson preservation and remote fallback Lab markers |
| Producer-backed sustained workload path | Smoke/Starter | Reproducible scheduling/drop/fallback evidence, not a production scheduler |
| Jetson ONNX + `tegrastats` replay | Smoke/Starter | Device-local smoke evidence with live telemetry handoff, not decoded YOLO accuracy or thermal endurance validation |
| Remote dispatch/fallback | Smoke/Starter | Orchestrator worker-selection/fallback evidence preserved through EdgeEnv context, AIGuard warning evidence, and Lab-owned report context; not production remote execution |
| Live camera, Whisper/FastAPI sustained services, Cloudflare hardening, dashboard | Future Work | Roadmap only |

## Runtime Operation Starter Evidence Chain

The remote-dispatch/fallback path is valuable because it shows role separation
across repositories, not because it claims production remote operation.

```text
Orchestrator worker selection / fallback starter
-> EdgeEnv local registry and replay context
-> AIGuard deterministic warning evidence
-> Lab Runtime Intelligence / operation-risk report
-> Lab-owned deployment decision
```

What to emphasize in a portfolio review:

- Orchestrator records worker eligibility, selected/rejected worker reasons,
  starter execution status, fallback final status, and compact event summary.
- EdgeEnv can preserve that evidence as local registry / handoff context while
  leaving comparability and deployment decisions to their owning layers.
- AIGuard explains observed remote-dispatch failure or fallback recovery with
  deterministic evidence, not LLM root-cause guessing.
- Lab ties the evidence back to deployment risk and remains the final decision
  owner.

What not to claim:

- production SSH/HTTP remote execution
- long-lived remote worker daemon operation
- Cloudflare / secure tunnel operation
- production retry/failover infrastructure
- Kubernetes-style or cloud orchestration

Latest Runtime Intelligence gate hardening:

- Lab's CI artifact gate now verifies that the copied
  `aiguard_edgeenv_handoff_alignment.json/.md` artifacts preserve
  `lab_expected_report_markers` and
  `report_marker_context_role=lab_report_contract_context`.
- The same gate requires `aiguard_validates_expected_report_markers=false`, so
  AIGuard stays a deterministic external evidence provider while Lab remains
  the report marker and deployment decision owner.
- Lab's Runtime Intelligence artifact gate now uses the same EdgeEnv
  preservation marker vocabulary as the entrypoint evidence index:
  `Lab EdgeEnv preservation context`,
  `lab_report_preservation_context_present=True`, and
  `lab_preservation=present`.
- Lab's Runtime Intelligence report now surfaces the remote fallback starter
  label with the same entrypoint registry vocabulary:
  `Remote fallback starter evidence`, `lab=Remote fallback starter evidence`,
  and `remote_execution_recovered_by_fallback`.
- The InferEdge entrypoint `smoke_all.sh` now directly gates the Lab
  Markdown/HTML Runtime Intelligence report for that remote fallback row, so
  the cross-repo smoke fails if the Lab-owned report context disappears.
- The same entrypoint smoke now gates Lab's bundle manifest summary marker
  `expected_report_markers: remote fallback Lab context row declared`, so the
  summary artifact and generated report stay aligned on the same Lab-owned
  remote fallback row contract.
- The same entrypoint smoke now directly gates the Lab report's Jetson/device-local
  preservation labels: `identity=jetson_device_local_preservation` and
  `path=device_local_starter` in the short identity row, plus the companion
  `Jetson/device-local EdgeEnv preservation details` row with
  `sources=device_local_cli_override`. This keeps the reviewer-facing
  preservation rows aligned with the device-local evidence path without
  requiring a live Jetson for fixture smoke validation.
- EdgeEnv now preserves Orchestrator `operation_risk_summary` as supplemental
  runtime operation navigation context, and Lab surfaces that marker in the
  Runtime Intelligence Risk Summary without turning it into a comparability
  field, regression delta, or deployment decision override.
- AIGuard now emits `edgeenv_orchestrator_operation_risk_summary` as
  deterministic warning evidence, and Lab surfaces that AIGuard evidence as a
  separate Runtime Intelligence row while preserving Lab as final deployment
  decision owner.
- This is artifact contract hardening before deeper Jetson evidence capture;
  it is not a production observability or GitLab control-plane claim.

## Device-Local Sustained Validation Starter

The current runtime-operation extension is a local-first starter, not a full
production remote execution system. It lets a reviewer replay the same
contract chain with committed Orchestrator input fixtures, then replace those
fixtures with local device inputs when available.

Assuming `InferEdgeOrchestrator` is cloned next to this entrypoint repo, the
minimum committed sample inputs are:

| Workload | Sample input path | Purpose |
|---|---|---|
| Vision | `../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm` | Local image producer input |
| Voice / Command | `../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json` | FastAPI-style request burst fixture |
| Safety / Monitor | `../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json` | Resource snapshot fixture |

Replay the committed device-local starter:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local \
  --frames 8
```

Replay the same chain with the remote dispatch starter:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch \
  --output-dir /tmp/inferedge_agent_runtime_remote_dispatch \
  --frames 8
```

This adds `06_remote_dispatch_result.json` with remote worker selection
evidence, worker selection reasons, retry/fallback planning,
`remote_execution_plan`, and `remote_execution_result`. It also adds
`07_remote_dispatch_guard_analysis.json` so AIGuard can explain the remote
dispatch starter evidence. Use `--remote-execute-plan` to explicitly request
the HTTP/SSH starter execution path when a worker registry entry supports it;
the committed file-contract fixture records skipped starter evidence. This
proves the worker registry/task request/remote execution starter contract, not
production remote worker execution.

Remote fallback recovery can also be replayed with the committed
`examples/remote_fallback` fixtures. Start only the local fallback HTTP starter
worker on port `8765`, then run the entrypoint smoke with `--remote-execute-plan`
and the fallback registry/request overrides. The resulting evidence chain is:

```text
primary-http-worker connection_error
-> fallback-http-worker starter succeeds
-> AIGuard remote_execution_recovered_by_fallback
-> Lab Remote fallback starter evidence
```

This shows bounded recovery evidence propagation. It is still a starter smoke,
not production-grade remote retry control.
The matching Orchestrator source sample is tracked only as a supporting
reference in `repos.yaml`: commit
`654e0ab27b383317ec816d054b293bfa3061cf32`,
`examples/telemetry/remote_fallback_recovery_sample.json`. Core `repos.lock`
remains scoped to Forge, Runtime, Lab, and AIGuard.

The generated `00_evidence_index.json` files can be combined into a local
entrypoint navigation registry so the device-local probe/process path and
remote fallback path are reviewed side by side. This registry is only a
navigation and comparison layer; it preserves links back to the source
Orchestrator, AIGuard, Lab, and remote dispatch artifacts instead of replacing
those contracts or InferEdgeEnv's run evidence registry / comparability checker.
The registry includes `operation_path`, selected remote worker, remote execution
status, fallback final status, `production_remote_execution`, and
`operation_boundary` when those starter artifacts exist. It also surfaces the
Lab-facing remote report context such as `Remote fallback starter evidence`
beside the AIGuard marker so remote/fallback starter evidence can be traced
from the entrypoint registry back to the Lab-owned report.
For device-local input override evidence, the same index/registry path now also
shows `producer_sources`, `device_local_producer_count`, and `producer_stages`
so the override path can be reviewed without turning the registry into a new
monitoring system.
When EdgeEnv preservation evidence is present, the navigation path also records
Lab's `Runtime Intelligence EdgeEnv Preservation` section marker so reviewers
can trace the EdgeEnv run ID into the Lab-owned report context directly.
The entrypoint index and registry also preserve Lab's preservation
identity/details labels, keeping `identity=...` and `path=...` separate from
source, stage, resource, and queue markers.
The fixture-only `scripts/smoke_remote_fallback_registry_marker.sh` gate keeps
this remote fallback registry marker path reproducible without a live HTTP
worker. It builds local synthetic artifacts, regenerates `00_evidence_index.*`
and the run registry, then requires
`remote_execution_recovered_by_fallback` and
`lab=Remote fallback starter evidence` to stay visible.

The current Lab report also has a dedicated `AIGuard Orchestrator Operation
Evidence` section. It preserves `worker_health_degradation` and
`scheduler_delay_pattern` when AIGuard explains Orchestrator worker health or
scheduler-delay telemetry, including worker reason summaries and policy/drop
reason counts. This is deployment context for Lab-owned decisions, not a change
in final decision ownership.

Replay the same entrypoint with explicit local input overrides:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_inputs \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --resource-snapshot ../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json
```

If no local ONNX model should be committed but a vision-shaped probe is needed,
add `--generate-vision-detector-probe`. This creates a small detector-like ONNX
artifact inside the output directory and routes it through the same Vision
producer probe path. It is stronger than the identity probe for workflow
evidence, but it is still not full live YOLO validation.
The local validation run generated `detector_tiny.onnx`, preserved
`CPUExecutionProvider`, input shape `[1, 3, 16, 16]`, output shape `[1, 6]`,
and carried the resulting runtime reliability evidence into a Lab `blocked`
decision.
The same entrypoint path was replayed on Jetson Orin Nano with 16 frames,
max queue depth 6, dropped/fallback count 13/13, one deadline miss, and a Lab
`blocked` decision. This is device-local smoke evidence, not full live YOLO or
thermal endurance validation.
Using a real user-provided `yolov8n.onnx` probe on Jetson preserved
`CPUExecutionProvider`, input shape `[1, 3, 640, 640]`, output shape
`[1, 84, 8400]`, 16 frames, max queue depth 6, dropped/fallback count 13/13,
10 deadline misses, and a Lab `blocked` decision. This is a real ONNX model
probe through the orchestration contract chain, not decoded YOLO accuracy or
live camera validation.
The same real model probe was then replayed with live `--capture-tegrastats`:
32 frames, max queue depth 6, dropped/fallback count 29/29, 18 deadline misses,
4 parsed `tegrastats` samples, max temperature 43.937 C, max RAM 966 MB, and a
Lab `blocked` decision. This ties real ONNX model execution evidence and live
Jetson telemetry into one device-local smoke bundle, not a thermal endurance
claim.
A latest main-branch replay used the same Jetson Orin Nano 25W path with a
user-provided `yolov8n.onnx`, local image input, process resource snapshot
capture, and live `tegrastats` capture. It ran 96 frames, reached max queue
depth 6, recorded dropped/fallback count 93/93, 50 deadline misses, parsed 9
`tegrastats` samples, and preserved max temperature 39.0 C / max RAM 979 MB.
The Vision ONNX probe reported mean/p95 latency 156.43 ms / 159.629 ms, while
AIGuard reported `blocked` / `high` and Lab produced a `blocked` decision. The
Lab report also preserved Runtime operation guard evidence
(`runtime_latency_budget_overrun`, `runtime_error_classification`) and now
surfaces retryable Runtime failure-handling context through
`runtime_error_retryable`, `runtime_error_retry_hint`, and
`runtime_retryable_error_review`. AIGuard preserves the Runtime retry hint as
deterministic evidence, and Lab remains the final deployment decision owner.
This is current-main device-local ONNX probe and telemetry handoff evidence
from a longer 96-frame starter replay, not decoded YOLO accuracy, live camera,
or thermal endurance validation.
The submission-facing Lab evidence snapshot is stored in
[`Jetson Device-Local Agent Runtime Evidence Report`](evidence/jetson_device_local_agent_runtime_report.md).
The clean Jetson replay runbook uses a temporary Forge clone under `/tmp` so
dirty local Jetson Forge/Runtime worktrees do not need to be deleted or reset
for reproduction.
After the split Jetson preservation report-row gate landed, the same
device-local EdgeEnv preservation path was replayed again on Jetson Orin Nano
25W from entrypoint commit `d85be12`. The output bundle
`/tmp/inferedge_agent_runtime_jetson_edgeenv_details_20260531T080118Z`
ran 96 frames, reached max queue depth 6, recorded 93 dropped / 93 fallback
events and 50 deadline misses, parsed 9 `tegrastats` samples, preserved 99
device-local producer events, and stored EdgeEnv run
`run-20260531-080130-4b480974` with `runtime_operation_summary`. The Lab
preservation context remained present
(`lab_report_preservation_context_present=true`) and the final Lab decision was
`blocked`, which is expected runtime reliability evidence rather than a
production deployment claim.

For a minimal live local resource signal, replace `--resource-snapshot` with
`--capture-process-resource-snapshot`. This records process-level resource
evidence only; it should not be described as full Jetson thermal validation.
If a Jetson `tegrastats` log was captured separately, pass
`--tegrastats-log /path/to/tegrastats.log` to the same entrypoint smoke. The
script copies that log into the evidence bundle and routes it through
Orchestrator `tegrastats_timeline`, AIGuard, and the Lab report without
claiming full thermal endurance validation.
On Jetson, `--capture-tegrastats` can capture telemetry during the Orchestrator
sustained run and route the live captured log through the same evidence path.
This remains device-local smoke evidence, not a thermal endurance claim.

Jetson starter validation has also been checked on a Jetson Orin Nano in 25W
mode using the same `device_local` starter flow with live `tegrastats` capture.
The observed starter run used 64 frames, reached max queue depth 6, recorded
61 dropped tasks and 61 fallback events, had 0 deadline misses, parsed 4
`tegrastats` samples, and reported max temperature 39.625 C / max RAM 1783 MB.
This is useful as a portfolio evidence bridge because it shows live Jetson
resource telemetry flowing through Orchestrator -> AIGuard -> Lab, while still
remaining below the claim level of full live YOLO/Whisper/FastAPI sustained
validation.

A follow-up Jetson ONNX probe run used the same entrypoint `device_local` path
with `--vision-onnx-model`. It ran 16 frames on Jetson Orin Nano 25W,
preserved `vision_inference_backend=onnxruntime`, `CPUExecutionProvider`,
output shape `[1, 2]`, and 1.255 ms probe latency in the Orchestrator summary,
then carried `blocked` / `high` AIGuard evidence into a Lab `blocked` decision.
This is device-local ONNX Runtime probe evidence using a tiny identity model,
not full live YOLO validation.

The new `--tegrastats-log` option was then validated with a separately captured
~12 second Jetson log. The entrypoint parsed 11 `tegrastats` samples, preserved
max temperature 41.5 C and max RAM 830 MB, and carried the same device-local
ONNX probe path into AIGuard `blocked` / `high` evidence and a Lab `blocked`
decision. This is captured telemetry handoff evidence, not full thermal
endurance validation.

## What To Show First

For an external reviewer, use this order:

1. `docs/ecosystem_1page.md`.
2. This summary.
3. `docs/interview_narrative.md`.
4. `README.md`.
5. `docs/pipeline_map.md`.
6. `repos/InferEdgeLab/README.md`.
7. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`.
8. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`.
9. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`.

## What Not To Claim

- InferEdge is not a production SaaS dashboard.
- InferEdgeEnv is not the validation or deployment decision layer.
- InferEdgeOrchestrator is not the benchmark or validation layer.
- Runtime evidence is not a public leaderboard or single-score ranking.
- AIGuard is deterministic diagnosis evidence, not LLM guessing.

## Validation Entry

From this entrypoint repo:

```bash
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

For a workspace where the repositories already exist as siblings:

```bash
INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub bash scripts/smoke_all.sh
```

This cross-repo smoke includes the Runtime Intelligence artifact gate. It checks
the local-first Orchestrator -> EdgeEnv -> AIGuard -> Lab bundle/report
artifacts without treating CI, telemetry artifacts, or remote dispatch as a
production control plane.
It also runs a lightweight Agent Runtime EdgeEnv preservation smoke and gates
the `preservation_identity` / `preservation_details` labels in both the Lab
report and entrypoint evidence index.

Recent local validation record:

| Date | Command | Result | Scope |
|---|---|---|---|
| 2026-05-28 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_runtime_intelligence_marker_gate_20260528 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke still passes after Lab hardened the Runtime Intelligence bundle manifest gate for required report markers. |
| 2026-05-28 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_lab_edgeenv_marker_alignment_20260528 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke still passes after Lab documented the expected report marker contract and EdgeEnv exposed the matching producer-side `lab_bundle_alignment.expected_report_markers` metadata. |
| 2026-05-28 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_aiguard_marker_context_20260528 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke still passes after AIGuard preserved Lab report marker context as external handoff metadata without taking ownership of Lab's report gate. |
| 2026-05-29 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_aiguard_operation_risk_summary_20260529 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke still passes after AIGuard added `edgeenv_orchestrator_operation_risk_summary` and Lab surfaced it as a Lab-owned Runtime Intelligence row. |
| 2026-05-29 | Jetson `bash scripts/demo_agent_runtime_e2e.sh --device-local --frames 32 --vision-onnx-model ~/InferEdge_device_local_inputs/models/yolov8n.onnx --capture-process-resource-snapshot --capture-tegrastats --edgeenv-run-evidence` | pass | Confirms the device-local EdgeEnv preservation marker path produces `Runtime Intelligence EdgeEnv Preservation` in Lab Markdown and `lab_preservation=present` / `lab_context=present` in the local evidence registry replay. |
| 2026-05-29 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_lab_preservation_context_marker_20260529 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke passes after Lab aligned the Runtime Intelligence artifact gate with the entrypoint preservation marker vocabulary: `Lab EdgeEnv preservation context`, `lab_report_preservation_context_present=True`, and `lab_preservation=present`. |
| 2026-05-29 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_lab_remote_fallback_marker_20260529 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_marker_smoke_lab_20260529 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke passes after Lab aligned the Runtime Intelligence report row with the entrypoint remote fallback marker vocabulary: `Remote fallback starter evidence`, `lab=Remote fallback starter evidence`, and `remote_execution_recovered_by_fallback`. |
| 2026-05-29 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_lab_remote_fallback_marker_gate_20260529 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_marker_gate_20260529 bash scripts/smoke_all.sh` | pass | Confirms the InferEdge entrypoint smoke now directly gates Lab Markdown/HTML Runtime Intelligence reports for the remote fallback row markers: `Remote fallback starter evidence`, `lab=Remote fallback starter evidence`, and `remote_execution_recovered_by_fallback`. |
| 2026-05-29 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_lab_summary_marker_20260529 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_summary_marker_20260529 bash scripts/smoke_all.sh` | pass | Confirms the InferEdge entrypoint smoke now directly gates Lab's bundle manifest summary marker `expected_report_markers: remote fallback Lab context row declared` alongside the generated Lab Markdown/HTML remote fallback row. |
| 2026-05-30 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_jetson_preservation_label_gate_20260530 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_jetson_preservation_label_gate_20260530 bash scripts/smoke_all.sh` | pass | Confirms the InferEdge entrypoint smoke now directly gates Lab's Jetson/device-local preservation labels `identity=jetson_device_local_preservation` and `path=device_local_starter` alongside the existing remote fallback report markers. |
| 2026-05-30 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_jetson_preservation_details_gate_20260530 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_jetson_preservation_details_gate_20260530 bash scripts/smoke_all.sh` | pass | Confirms the InferEdge entrypoint smoke now directly gates Lab's split Jetson/device-local preservation rows: the short identity row and the companion `Jetson/device-local EdgeEnv preservation details` row with `sources=device_local_cli_override`. |
| 2026-05-31 | Jetson `bash scripts/demo_agent_runtime_e2e.sh --device-local --frames 96 --vision-onnx-model ~/InferEdge_device_local_inputs/models/yolov8n.onnx --capture-process-resource-snapshot --capture-tegrastats --edgeenv-run-evidence` | pass | Confirms latest main `d85be12` still carries the device-local ONNX + live `tegrastats` + EdgeEnv preservation path through Orchestrator -> AIGuard -> Lab after the split Jetson preservation report-row gate; Lab preservation context remained present and EdgeEnv stored `run-20260531-080130-4b480974`. |
| 2026-05-31 | `INFEREDGE_REPOS_DIR=/Users/GwonHyeokJun/Documents/GitHub INFEREDGE_AGENT_RUNTIME_EDGEENV_SMOKE_OUT=/private/tmp/inferedge_agent_runtime_edgeenv_smoke_all_gate_20260531 INFEREDGE_RUNTIME_INTELLIGENCE_SMOKE_OUT=/private/tmp/inferedge_smoke_all_agent_runtime_edgeenv_gate_20260531 INFEREDGE_REMOTE_FALLBACK_REGISTRY_SMOKE_OUT=/private/tmp/inferedge_remote_fallback_registry_agent_runtime_edgeenv_gate_20260531 bash scripts/smoke_all.sh` | pass | Confirms the cross-repo smoke now directly runs the lightweight Agent Runtime EdgeEnv preservation path and gates `preservation_identity` / `preservation_details` in the Lab report and entrypoint evidence index. |
