# InferEdge

Multi-repository entrypoint for the InferEdge local-first Edge AI inference validation pipeline.

InferEdge is not a benchmark-only script and not a production SaaS dashboard.
It is a contract/preset based validation workflow that connects build
provenance, real Runtime execution, validation evidence, optional deterministic
diagnosis evidence, and Lab-owned deployment decisions.

The ecosystem is organized by lifecycle questions:

```text
Can we deploy this model?                         -> InferEdge validation layer
Can this benchmark evidence be trusted and compared? -> InferEdgeEnv comparability layer
Can deployed workloads stay stable under load?   -> InferEdgeOrchestrator operation layer
```

![InferEdge ecosystem lifecycle diagram](docs/assets/inferedge_ecosystem_diagram.svg)

```text
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio
```

## Repositories

| Repository | Role | URL |
|---|---|---|
| InferEdgeForge | Build provenance, metadata, manifest, artifact handoff | https://github.com/gwonxhj/InferEdgeForge |
| InferEdge-Runtime | C++ execution, Lab-compatible result JSON, Jetson evidence reports | https://github.com/gwonxhj/InferEdge-Runtime |
| InferEdgeLab | Compare/evaluate/report/API/Local Studio/deployment decision owner | https://github.com/gwonxhj/InferEdgeLab |
| InferEdgeAIGuard | Optional deterministic diagnosis evidence provider | https://github.com/gwonxhj/InferEdgeAIGuard |

## Ecosystem Extension Layers

These repositories extend the lifecycle beyond the pinned Core 4 validation
message without replacing Forge, Runtime, Lab, or AIGuard.

| Repository | Role | URL |
|---|---|---|
| InferEdgeEnv | v0.1.5 v1-complete comparability layer: local run evidence registry and benchmark evidence trust/comparison judgement | https://github.com/gwonxhj/InferEdgeEnv |
| InferEdgeOrchestrator | Operation layer after deployment validation: scheduling, overload control, and runtime telemetry | https://github.com/gwonxhj/InferEdgeOrchestrator |

`repos.lock` intentionally remains scoped to the Core 4 validation pipeline
that `clone_all.sh` and `update_all.sh` manage. For runtime-operation starter
evidence, `repos.yaml` records the supporting Orchestrator reference currently
used for the bounded remote fallback recovery sample:
`654e0ab27b383317ec816d054b293bfa3061cf32` with
`examples/telemetry/remote_fallback_recovery_sample.json`.

## Real-Device Evidence

[Jetson Orin Nano Internal Lab](https://github.com/gwonxhj/jetson-orin-nano-internal-lab)
provides hardware-level runtime evidence, including TensorRT, ONNX Runtime,
YOLO, Whisper, FastAPI serving, telemetry logs, sustained multi-workload
interaction evidence, and InferEdge-compatible handoff artifacts.

For the submission-ready diagram and layer split, start with
[InferEdge Ecosystem 1-Page Summary](docs/ecosystem_1page.md).

## Implementation Status

Not every roadmap item is at the same maturity level. Use this table as the
submission boundary.

| Area | Status | What is implemented | Do not claim |
|---|---|---|---|
| Core Forge -> Runtime -> Lab -> optional AIGuard validation pipeline | Implemented | Build provenance, Runtime result evidence, Lab compare/report/decision, and optional deterministic AIGuard evidence | Production SaaS readiness |
| Local Studio demo evidence replay | Implemented | Local browser workflow for demo evidence, compare, decision, and AIGuard cases | Cloud dashboard or multi-user workspace |
| YOLOv8 COCO subset / model contract validation | Implemented | Subset evaluation plus bbox/score/contract validation | Full COCO benchmark or automatic evaluation for every model |
| AIGuard diagnosis cases | Implemented | Deterministic bbox, score, baseline, and temporal evidence | LLM root-cause inference |
| Orchestrator producer-backed and device-local smoke | Smoke/Starter | Queue depth, drop/fallback, policy reason, Lab operation context | Production scheduler or long-running worker daemon |
| Runtime Intelligence artifact gate | Implemented | Cross-repo smoke runs Lab's local-first bundle manifest/report/CI artifact gates for Orchestrator -> EdgeEnv -> AIGuard -> Lab evidence, including EdgeEnv-preserved `operation_risk_summary`, Lab EdgeEnv preservation context markers, and directly gated Jetson preservation and remote fallback Lab markers | Production observability platform or GitLab control plane |
| Jetson ONNX + `tegrastats` replay | Smoke/Starter | Device-local ONNX probe and live telemetry handoff through Orchestrator, AIGuard, and Lab | Decoded YOLO accuracy, live camera, Whisper/FastAPI service execution, or thermal endurance validation |
| Runtime retryable failure-handling evidence | Smoke/Starter | Runtime `retryable` / `retry_hint` context is preserved by AIGuard and surfaced in the Lab runtime operation report | Production request cancellation, automatic retry control, or worker daemon behavior |
| Remote dispatch / fallback starter | Smoke/Starter | Orchestrator file-based worker selection, bounded fallback evidence, EdgeEnv preservation context, AIGuard deterministic warning evidence, and Lab-owned report context | Production remote execution, secure multi-device orchestration, or cloud control plane |
| Cloudflare / dashboard / production worker services | Future Work | Documented direction only | Completed remote operation platform |

The Runtime Intelligence artifact gate directly checks Lab report markers for
Jetson/device-local preservation and remote fallback context. The gated
Jetson/device-local labels include `identity=jetson_device_local_preservation`
and `path=device_local_starter` in the short identity row, plus
`Jetson/device-local EdgeEnv preservation details` with
`sources=device_local_cli_override` in the companion details row. This keeps the
reviewer-facing report aligned with fixture-based cross-repo smoke evidence
without requiring a live Jetson for this gate.

## Runtime Operation Starter Evidence Chain

The current remote-dispatch path is intentionally a starter evidence chain, not
production remote execution.

```text
Orchestrator remote dispatch starter
-> EdgeEnv local evidence preservation context
-> AIGuard deterministic remote-dispatch warning evidence
-> Lab Runtime Intelligence / operation-risk report context
-> Lab-owned deployment decision
```

Repository boundaries stay fixed:

- Orchestrator records worker selection, skipped/failed starter execution,
  fallback status, compact runtime event summaries, and
  `operation_boundary=remote dispatch starter evidence only`.
- EdgeEnv may preserve the operation context in local registry / replay /
  handoff evidence, but it does not confirm remote execution or own operation
  control.
- AIGuard may emit deterministic evidence such as
  `remote_execution_recovered_by_fallback`, but it does not decide deployment.
- Lab remains the final report and deployment decision owner.
- The entrypoint smoke gate verifies that downstream AIGuard, Lab, and
  `00_evidence_index.*` artifacts preserve the
  `remote_dispatch_runtime_event_compact_summary` role,
  `operation_boundary`, and `production_remote_execution=false` boundary.

Do not describe this path as production SSH/HTTP execution, long-lived worker
operation, secure tunnel operation, retry/failover infrastructure, or cloud
orchestration.

## Quick Start

Clone this entrypoint repo first:

```bash
git clone https://github.com/gwonxhj/InferEdge.git
cd InferEdge
```

Clone all pipeline repositories:

```bash
bash scripts/clone_all.sh --locked
```

This creates:

```text
repos/
├─ InferEdgeForge
├─ InferEdge-Runtime
├─ InferEdgeLab
└─ InferEdgeAIGuard
```

Run the portfolio smoke checks:

```bash
bash scripts/smoke_all.sh
```

The cross-repo smoke also runs a lightweight Agent Runtime EdgeEnv preservation
identity/details smoke and Lab's local-first Runtime Intelligence artifact
chain gate. The Agent Runtime smoke checks that `preservation_identity` /
`preservation_details` remain visible in the Lab report and entrypoint evidence
index and that the generated index keeps the additive `duration_class` /
`duration_label` navigation fields. The Runtime Intelligence gate verifies the
committed Orchestrator -> EdgeEnv -> AIGuard -> Lab report bundle, including
the Runtime Intelligence Risk Summary and remote-dispatch boundary rows,
without treating GitLab,
telemetry artifacts, or remote dispatch as a production control plane. The
current chain also keeps the compact Orchestrator `operation_risk_summary`
marker as EdgeEnv-preserved navigation context and surfaces it as a Lab-owned
report row; it is not an EdgeEnv regression delta, comparability field, or
deployment decision override. AIGuard now also emits
`edgeenv_orchestrator_operation_risk_summary` as deterministic warning evidence,
and Lab renders that evidence as a separate Runtime Intelligence row while
keeping Lab as the final deployment decision owner. For the generated artifact list and the split between
operation-smoke and Runtime Intelligence smoke gates, see
[`docs/agent_runtime_e2e_demo.md`](docs/agent_runtime_e2e_demo.md#smoke-gate-split).
The current Lab gate also checks the copied AIGuard/EdgeEnv handoff alignment
artifact for Lab-owned expected report marker context. In practice,
`lab_expected_report_markers` must match the Runtime Intelligence report
markers, `report_marker_context_role` must stay
`lab_report_contract_context`, and
`aiguard_validates_expected_report_markers=false` must be preserved. This is a
CI artifact contract check for reviewer evidence; it does not make AIGuard or
CI the report owner.
The latest gate also aligns the entrypoint evidence-index vocabulary with the
Lab Runtime Intelligence report by requiring `Lab EdgeEnv preservation context`
and `lab_report_preservation_context_present=True` / `lab_preservation=present`
markers in the Lab-owned artifact chain.

Run the Reliable Edge Agent Runtime extension smoke when the supporting
Orchestrator repo is available in the same workspace:

```bash
bash scripts/demo_agent_runtime_e2e.sh

# Optional: run the explicit device_local starter path.
bash scripts/demo_agent_runtime_e2e.sh --device-local

# Optional: replace the device-local starter fixtures with local inputs.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --capture-process-resource-snapshot

# Optional: add a lightweight ONNX Runtime probe to the Vision producer.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx

# Optional: generate a tiny detector-like ONNX probe model locally.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --generate-vision-detector-probe

# Optional: route a captured Jetson tegrastats log through the same timeline.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --tegrastats-log /path/to/tegrastats.log

# Optional: capture Jetson tegrastats during the Orchestrator sustained run.
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx \
  --capture-tegrastats

# Optional: also replay the file-based remote worker selection starter.
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch

# Optional: explicitly request HTTP/SSH starter execution when the selected
# worker registry entry supports it. File-contract workers are recorded as
# skipped starter evidence.
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch --remote-execute-plan

# Optional: preserve Runtime operation summary through EdgeEnv's local registry.
bash scripts/demo_agent_runtime_e2e.sh --device-local --edgeenv-run-evidence

# Optional: reproduce primary failure followed by bounded fallback recovery.
# Terminal A:
python3 ../InferEdgeOrchestrator/scripts/remote_http_worker.py \
  --host 127.0.0.1 \
  --port 8765 \
  --worker-id fallback-http-worker

# Terminal B:
bash scripts/demo_agent_runtime_e2e.sh \
  --output-dir /tmp/inferedge_agent_runtime_fallback_e2e \
  --frames 8 \
  --remote-dispatch \
  --remote-execute-plan \
  --remote-timeout-sec 1 \
  --remote-worker-registry examples/remote_fallback/remote_worker_registry_fallback.json \
  --remote-task-request examples/remote_fallback/remote_task_request_fallback.json
```

This reproduces the file-based chain from `agent_manifest` to Runtime
`result.agent`, Orchestrator scheduling evidence, AIGuard runtime reliability
analysis, and the Lab-owned Agent Runtime Reliability report.
Each run also writes `00_evidence_index.md` and `00_evidence_index.json` in the
output bundle so the generated Orchestrator, AIGuard, Lab, telemetry, and
optional remote-dispatch artifacts are easy to navigate without changing the
source evidence contracts. The index preserves Orchestrator scenario label,
category, mode, and an additive `duration_class` / `duration_label` so repeated
smoke runs can be grouped by intent and quickly distinguished as short
96-frame-class replay, 5-minute-class sustained replay, or quick starter smoke
without changing the source contracts. It also records an `operation_path` and,
when present, remote dispatch starter status, selected worker, remote execution
status, fallback final status, `production_remote_execution`, and
`operation_boundary` so device-local and remote/fallback runs can be compared
in one registry table without turning starter evidence into production remote
operation proof. The registry also preserves the Lab-facing remote report
context, such as `Remote fallback starter evidence`, beside the AIGuard marker
so the entrypoint registry and Lab report stay easy to cross-check.
When present, EdgeEnv evidence status is also recorded so reviewers can see
that Runtime operation summary was preserved in the local registry/artifact
flow without making it a deployment decision or comparability gate.
The same index/registry path also records whether Lab rendered the
`Runtime Intelligence EdgeEnv Preservation` section, so a reviewer can identify
the Lab-owned preservation context without opening every report first.
It now also carries the same preservation identity/details labels as the Lab
Agent Runtime report, keeping the run/path identity separate from producer,
resource, and queue navigation markers.
For device-local override runs, the index and registry also surface
`producer_sources`, `device_local_producer_count`, and `producer_stages` so a
reviewer can tell whether the bundle used committed starter fixtures or runtime
input overrides without opening the full Orchestrator JSON first.
For repeat Jetson bundles, the same table makes the short 96-frame replay and
5-minute-class sustained replay visible without treating either as thermal
endurance validation.
When comparing repeated entrypoint smoke runs, build a local navigation
registry from the generated indexes:

```bash
python3 scripts/build_agent_runtime_run_registry.py \
  --scan-root /tmp \
  --output-json /tmp/inferedge_agent_runtime_registry.json \
  --output-md /tmp/inferedge_agent_runtime_registry.md
```

Use the fixture-only remote fallback registry smoke when you want to verify the
entrypoint registry markers without starting the local HTTP fallback worker:

```bash
bash scripts/smoke_remote_fallback_registry_marker.sh
```

This smoke confirms that the generated evidence index and registry preserve
`remote_execution_recovered_by_fallback` and
`lab=Remote fallback starter evidence` from local files only.

The entrypoint smoke now also verifies that Lab preserves Orchestrator operation
context, including queue state, worker health, runtime event summary, and
timeline samples in JSON/Markdown reports.
It also verifies the current AIGuard -> Lab operation-evidence handoff:
AIGuard can emit `worker_health_degradation`, `scheduler_delay_pattern`,
`queue_pressure_context`, `worker_operation_risk_summary`,
`runtime_operation_health`, and, for device-local runs,
`device_local_operation_context` from Orchestrator and Runtime telemetry.
Lab surfaces those signals in operation context sections with queue pressure
reasons, worker risk summaries, Runtime operation summary actions, producer
context, and policy/drop reason counts.
Lab remains the final deployment decision owner.
With `--remote-dispatch`, the same script also writes Orchestrator's
file-based remote worker selection result and runs AIGuard remote-dispatch
diagnosis on that artifact. Add `--remote-execute-plan` to explicitly request
the Orchestrator HTTP/SSH starter execution path when the selected worker
registry entry supports it. File-contract workers remain selection-only and are
recorded as skipped starter evidence. This is remote dispatch starter evidence,
not production SSH/HTTP remote execution. The smoke validation also checks that
the remote dispatch runtime event summary role and starter boundary are
preserved through AIGuard, Lab JSON/Markdown, and the generated evidence index.
With `--edgeenv-run-evidence`, the script writes `08_edgeenv_run_show.json` and
`08_edgeenv/.edgeenv/runs.db`. This is EdgeEnv local evidence preservation for
the Runtime operation summary, not cloud monitoring or Lab deployment decision
ownership.
The `examples/remote_fallback` fixtures intentionally point the primary worker
at an unavailable HTTP endpoint and the fallback worker at a local starter
server. When the fallback worker is running, the same entrypoint smoke records
`remote_execution_failed`, `fallback_execution_result.final_status=succeeded`,
AIGuard `remote_execution_recovered_by_fallback`, and Lab's `Remote fallback
starter evidence` section. This proves bounded recovery evidence propagation,
not production-grade retry control.
The Orchestrator source-side sample for this path is tracked as supporting
reference `654e0ab27b383317ec816d054b293bfa3061cf32`
(`examples/telemetry/remote_fallback_recovery_sample.json`) rather than as a
Core `repos.lock` entry.

The current extension smoke uses the latest Orchestrator producer-backed
sustained path: Vision reads a local image fixture, Voice-Command replays a
FastAPI-style request burst fixture, and Safety-Monitor reads resource snapshot
telemetry. It checks queue-depth, policy decision reason,
`multi_workload_sustained_summary`, producer source markers, optional
`tegrastats_timeline`, AIGuard `profiled_workload_pressure` /
`thermal_resource_pressure`, and Lab `sustained_overload_review` evidence
before live device-local sustained validation is added. Use `--device-local` to
replay the committed local image, request, and resource snapshot producers in
Orchestrator `scenario_mode=device_local`.
For local device experiments, keep `--device-local` and pass
`--vision-input`, optional `--vision-onnx-model`, `--voice-ingress-payload`, and
either `--resource-snapshot` or `--capture-process-resource-snapshot` to reuse
the same entrypoint script with runtime input overrides. The ONNX option records
provider, input/output shapes, and probe latency as lightweight Vision producer
evidence; `--tegrastats-log` can carry a captured Jetson/resource log through
the Orchestrator `tegrastats_timeline`; `--capture-tegrastats` captures Jetson
telemetry during the Orchestrator run when the `tegrastats` command is
available. These options do not claim a full live YOLO/Whisper/FastAPI
sustained service. See
[`docs/agent_runtime_e2e_demo.md`](docs/agent_runtime_e2e_demo.md) for the
minimum committed sample paths and a resource-snapshot variant.
Use `--generate-vision-detector-probe` when you want a reproducible detector-like
ONNX probe without committing a model artifact.

Recent Jetson starter validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with live `tegrastats` log |
| Frames | 64 |
| Max queue depth | 6 |
| Dropped / fallback count | 61 / 61 |
| Deadline misses | 0 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | 39.625 C |
| Max RAM used | 1783 MB |
| Lab decision | `blocked` from runtime reliability review rules |

This record proves the starter path can carry live Jetson resource telemetry
through Orchestrator, AIGuard, and Lab reports. It is still a device-local
starter smoke, not a claim of full live YOLO/Whisper/FastAPI sustained
validation.

Recent Jetson ONNX probe validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with Vision ONNX Runtime probe |
| Frames | 16 |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision probe output shape | `[1, 2]` |
| Vision probe latency | 1.255 ms |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline misses | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This second record validates that the entrypoint can pass a local ONNX model
into the Jetson device-local Vision producer and preserve ONNX Runtime probe
evidence through Orchestrator, AIGuard, and Lab reports. The probe used a tiny
identity ONNX model, so it should be described as device-local ONNX probe
evidence rather than full live YOLO validation.

Recent captured tegrastats handoff validation:

| Evidence | Value |
|---|---:|
| Device mode | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with `--tegrastats-log` |
| Captured log duration | ~12 seconds |
| Parsed `tegrastats` samples | 11 |
| Frames | 16 |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline misses | 1 |
| Max temperature | 41.5 C |
| Max RAM used | 830 MB |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the new `--tegrastats-log` entrypoint option with a
captured Jetson log. It is telemetry handoff evidence, not a full thermal
endurance or live workload validation.

Recent generated detector probe validation:

| Evidence | Value |
|---|---:|
| Scenario | local `device_local` starter with generated detector-like ONNX probe |
| Generated model | `generated_models/detector_tiny.onnx` |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 8 |
| Max queue depth | 6 |
| Dropped / fallback count | 5 / 5 |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates a reproducible detector-like ONNX probe generated at run
time. It is closer to image-shaped perception work than the identity probe, but
it is still not full live YOLO validation.

Recent Jetson generated detector probe smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Scenario | `device_local` starter with generated detector-like ONNX probe |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the same entrypoint chain on Jetson using a generated
detector-like probe. It is device-local smoke evidence, not full live YOLO or
thermal endurance validation.

Recent Jetson YOLOv8n ONNX probe smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with real ONNX model probe |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped / fallback count | 13 / 13 |
| Deadline missed count | 10 |
| Vision probe elapsed range | `120.147-146.878 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record validates the entrypoint chain with a real YOLOv8n ONNX model on
Jetson. It is still an ONNX Runtime probe inside the device-local orchestration
smoke, not a full live camera or decoded detection validation.

Recent Jetson YOLOv8n ONNX probe with live tegrastats capture:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with `--capture-tegrastats` |
| Vision probe backend | `onnxruntime` / `CPUExecutionProvider` |
| Vision input/output shape | `[1, 3, 640, 640]` -> `[1, 84, 8400]` |
| Frames | 32 |
| Max queue depth | 6 |
| Dropped / fallback count | 29 / 29 |
| Deadline missed count | 18 |
| Parsed `tegrastats` samples | 4 |
| Max temperature / RAM | 43.937 C / 966 MB |
| Vision probe elapsed range | `119.912-137.729 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This record ties a real YOLOv8n ONNX probe and live Jetson telemetry capture
into the same entrypoint evidence chain. It remains a device-local smoke, not
thermal endurance or live camera validation.

Latest Jetson device-local replay:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano 25W |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with real ONNX model + live `tegrastats` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped / fallback count | 93 / 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Max temperature / RAM | 39.0 C / 979 MB |
| Vision mean / p95 latency | 156.43 ms / 159.629 ms |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This replay was run from the entrypoint script with `--device-local`,
`--vision-onnx-model`, `--capture-process-resource-snapshot`, and
`--capture-tegrastats`. It confirms the latest main branch still carries real
Jetson ONNX probe and live telemetry evidence through Orchestrator, AIGuard,
and Lab over a longer 96-frame starter replay. The Lab report also preserves
Runtime operation guard evidence
(`runtime_latency_budget_overrun`, `runtime_error_classification`) and
retryable Runtime-side failure context (`runtime_error_retryable`,
`runtime_error_retry_hint`, `runtime_retryable_error_review`) when Runtime
reports a retryable timeout or skipped execution. AIGuard preserves the
deterministic retry hint as evidence, while Lab remains the deployment decision
owner. The same report preserves
Orchestrator operation guard context such as `worker_health_degradation` when
worker health telemetry indicates degraded runtime loops. It is not a decoded
YOLO accuracy validation or sustained thermal endurance claim.
For the clean Jetson replay procedure that avoids touching dirty local Forge or
Runtime worktrees, see
[`Clean Jetson Replay Runbook`](docs/agent_runtime_e2e_demo.md#clean-jetson-replay-runbook).
For a submission-facing snapshot of the generated Lab evidence, see
[`Jetson Device-Local Agent Runtime Evidence Report`](docs/evidence/jetson_device_local_agent_runtime_report.md).

Latest Jetson EdgeEnv preservation smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano 25W |
| Scenario | `device_local` starter with real ONNX model + live `tegrastats` + EdgeEnv registry preservation |
| Output bundle | `/tmp/inferedge_agent_runtime_jetson_edgeenv_label_gate_20260531T090600Z` |
| Entrypoint commit | `0b05af8` |
| Operation path | `device_local_starter` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped / fallback count | 93 / 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Device-local / producer events | 99 / 99 |
| Max temperature / RAM | 44.437 C / 991 MB |
| Vision mean / p95 latency | 155.947 ms / 155.625 ms |
| EdgeEnv run evidence | `run-20260531-090621-22900f06` with `runtime_operation_summary` stored |
| Lab preservation context | `lab_report_preservation_context_present=true`; `preservation_identity` / `preservation_details` present |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

This latest replay confirms that the updated entrypoint can still carry
device-local runtime operation evidence into EdgeEnv's local run registry and
Lab-owned preservation context after the cross-repo smoke started gating the
split `preservation_identity` / `preservation_details` labels. It remains
device-local starter smoke, not decoded YOLO
accuracy validation, live camera operation, production remote execution, or
thermal endurance validation.

Latest 5-minute-class Jetson sustained smoke:

| Evidence | Value |
|---|---:|
| Device | Jetson Orin Nano 25W |
| Model | user-provided `yolov8n.onnx` |
| Scenario | `device_local` starter with real ONNX model + live `tegrastats` + EdgeEnv registry preservation |
| Output bundle | `/tmp/inferedge_agent_runtime_jetson_sustained_5min_edgeenv_20260531T091654Z` |
| Entrypoint commit | `4417fbb` |
| Runtime window | 5-minute-class |
| Frames | 3600 |
| Max queue depth | 6 |
| Dropped / fallback count | 3597 / 3597 |
| Deadline missed count | 1802 |
| Parsed `tegrastats` samples | 281 |
| Max temperature / RAM | 50.375 C / 1038 MB |
| Vision mean / p95 latency | 152.77 ms / 156.948 ms |
| EdgeEnv run evidence | `run-20260531-092158-c3323ba9` with `runtime_operation_summary` stored |
| Preservation labels | `preservation_identity` / `preservation_details` present |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` from runtime reliability review rules |

The latest repeat run was captured after the Agent Runtime EdgeEnv label gate
landed and passed the entrypoint schema-marker validation. It carries
5-minute-class queue pressure, drop/fallback, deadline miss, live Jetson
telemetry, derived `operation_risk_summary`, EdgeEnv registry preservation,
AIGuard `queue_pressure_context` / `worker_operation_risk_summary`, and
Lab-owned deployment decision evidence through the same bundle. It remains
device-local smoke evidence, not decoded YOLO accuracy validation, live camera
operation, Whisper/FastAPI service execution, production remote execution, or
sustained thermal endurance validation. See
[`Jetson Device-Local 5-Minute Sustained Smoke Report`](docs/evidence/jetson_device_local_5min_sustained_report.md)
and its
[`HTML report`](docs/evidence/jetson_device_local_5min_sustained_report.html).

Reproduce the same class of Jetson smoke with the convenience runner:

```bash
bash scripts/demo_jetson_5min_sustained.sh

# Optional: also preserve Runtime operation summary through EdgeEnv.
bash scripts/demo_jetson_5min_sustained.sh --edgeenv-run-evidence
```

Before starting a repeat Jetson run from a development machine, use the
readiness preflight to catch SSH, `tegrastats`, clean Forge fixture, input, and
model-path issues without creating new evidence:

```bash
bash scripts/check_jetson_sustained_readiness.sh

# Optional: include the EdgeEnv repo/CLI preflight for registry preservation.
bash scripts/check_jetson_sustained_readiness.sh --edgeenv-run-evidence
```

If the target is offline or SSH is blocked, keep the existing committed Jetson
evidence as the latest confirmed record and rerun the preflight before
attempting another sustained smoke. Do not describe a failed preflight as new
Jetson runtime evidence.

Open the Local Studio demo:

```bash
cd repos/InferEdgeLab
poetry run inferedgelab serve --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/studio
```

Click `Load Demo Evidence` to replay the bundled ONNX Runtime CPU vs TensorRT
Jetson evidence, compare view, deployment decision context, and optional
AIGuard diagnosis cases.

## Reproducible Clone Modes

Use the verified lock file:

```bash
bash scripts/clone_all.sh --locked
```

Use the latest `main` branch from each repo:

```bash
bash scripts/clone_all.sh --latest
```

Update existing clones:

```bash
bash scripts/update_all.sh --latest
```

or return to the locked portfolio snapshot:

```bash
bash scripts/update_all.sh --locked
```

## Entrypoint Files

| File | Purpose |
|---|---|
| `repos.yaml` | Human-readable repository map |
| `repos.lock` | Verified commit snapshot used by `--locked` |
| `scripts/clone_all.sh` | Clone all InferEdge Core repositories |
| `scripts/update_all.sh` | Update existing clones to latest or locked state |
| `scripts/smoke_all.sh` | Run cross-repo portfolio smoke checks |
| `scripts/demo_agent_runtime_e2e.sh` | Replay the Reliable Edge Agent Runtime extension smoke |
| `docs/ecosystem_1page.md` | Submission-ready ecosystem diagram and three-question layer map |
| `docs/assets/inferedge_ecosystem_diagram.svg` | Reusable ecosystem diagram asset for README, portfolio pages, and slides |
| `docs/agent_runtime_e2e_demo.md` | Agent runtime contract-chain demo guide |
| `docs/portfolio_summary.md` | 30-second portfolio summary and one-line repository role map |
| `docs/interview_narrative.md` | Interview-ready narrative for explaining the ecosystem and Jetson evidence role |
| `docs/final_submission_rehearsal.md` | Clean-clone submission gate rehearsal and results |
| `docs/pipeline_map.md` | Pipeline map and repository responsibility guide |

## Current Demo Evidence

The canonical Local Studio demo evidence is maintained in InferEdgeLab and
InferEdge-Runtime:

| Evidence | Value |
|---|---:|
| TensorRT Jetson FP16 25W mean | 10.066401 ms |
| TensorRT Jetson FP16 25W p99 | 15.548438 ms |
| TensorRT Jetson FP16 25W FPS | 99.340373 |
| ONNX Runtime CPU mean | 45.4299 ms |
| ONNX Runtime CPU p99 | 49.2128 ms |
| ONNX Runtime CPU FPS | 22.0119 |
| Local Studio speedup | about 4.51x |
| YOLOv8 subset | 10 images / 89 ground-truth boxes |
| simplified mAP@50 | 0.1410 |
| precision / recall | 0.2941 / 0.1685 |

## Scope Boundary

Included:

- local-first validation workflow
- repository clone/update entrypoint
- Core 4 contract smoke orchestration
- Local Studio demo entrypoint
- README and documentation map

Not included:

- production SaaS infrastructure
- DB/Redis queue persistence
- auth/billing/upload flow
- cloud dashboard deployment
- automatic evaluation for arbitrary model families

## Primary Review Path

For a reviewer or interviewer, start here:

1. `docs/portfolio_summary.md`
2. `docs/interview_narrative.md`
3. `docs/final_submission_rehearsal.md`
4. This README
5. `docs/pipeline_map.md`
6. `repos/InferEdgeLab/README.md`
7. `repos/InferEdgeLab/docs/portfolio/inferedge_portfolio_submission.md`
8. `repos/InferEdge-Runtime/docs/reports/jetson_evidence_summary.md`
9. `repos/InferEdgeAIGuard/docs/detector_validation_matrix.md`
