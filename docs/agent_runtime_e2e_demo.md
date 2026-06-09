# Reliable Edge Agent Runtime E2E Demo

Language: English | [한국어](agent_runtime_e2e_demo.ko.md)

This document describes the local extension smoke that connects the Reliable
Edge Agent Runtime contracts across the InferEdge ecosystem.

The demo is intentionally local-first and file-based. It is not a production
orchestration service, cloud dashboard, or general AI OS.

The current smoke uses the latest Orchestrator producer-backed sustained
path: Vision reads a local image fixture, Voice-Command replays a FastAPI-style
request burst fixture, and Safety-Monitor reads resource snapshot telemetry.
It verifies that queue-depth timeline evidence, policy decision reasons,
`multi_workload_sustained_summary`, producer source markers, optional
`tegrastats_timeline`, AIGuard `profiled_workload_pressure` /
`thermal_resource_pressure`, and Lab `sustained_overload_review` are preserved
across the chain before live device-local sustained validation is added. It also
checks that Lab preserves Orchestrator operation context, including queue state,
worker health, runtime event summary, and timeline samples in report output. The
current chain also preserves AIGuard Orchestrator operation evidence:
`worker_health_degradation` and `scheduler_delay_pattern` are surfaced in the
Lab report when Orchestrator worker health or scheduler-delay telemetry
provides those deterministic warning signals. The
optional `--device-local` mode uses committed local image, request, and resource
snapshot producers in Orchestrator `scenario_mode=device_local`.

## Status Boundary

| Path | Status | Meaning |
|---|---|---|
| Default e2e chain | Implemented | `agent_manifest -> Runtime result.agent -> Orchestrator -> AIGuard -> Lab` contract is reproducible |
| Producer-backed sustained workload path | Smoke/Starter | Queue/drop/fallback/deadline evidence is generated from committed fixtures |
| Device-local override path | Smoke/Starter | Local image, optional ONNX model, request payload, resource snapshot, and `tegrastats` input can be routed through the same chain |
| Jetson ONNX + live `tegrastats` replay | Smoke/Starter | Real device telemetry handoff is validated through the report path |
| Live camera, Whisper/FastAPI service, thermal endurance, production remote execution | Future Work | Not completed and should not be described as current functionality |

## Contract Chain

```text
Forge agent_manifest
-> Runtime result.agent
-> Orchestrator orchestration_summary
-> AIGuard guard_analysis
-> Lab agent-runtime-report
```

## Smoke Gate Split

The entrypoint e2e smoke and the Runtime Intelligence artifact smoke validate
different parts of the ecosystem.

| Gate | Command | What it proves | What it does not prove |
|---|---|---|---|
| Agent runtime operation smoke | `bash scripts/demo_agent_runtime_e2e.sh` or the Agent Runtime EdgeEnv stage inside `bash scripts/smoke_all.sh` | File-based agent manifest, Runtime `result.agent`, Orchestrator operation evidence, AIGuard runtime warning evidence, Lab agent-runtime report, optional remote-dispatch starter markers, optional EdgeEnv run preservation identity/details labels, and duration-class navigation labels are connected in one generated bundle | Runtime regression comparability, telemetry-history replay, or CI artifact bundle completeness |
| Runtime Intelligence artifact smoke | `bash scripts/smoke_all.sh` or Lab's `bash scripts/smoke_runtime_intelligence_chain.sh --output-dir <dir>` | The committed Orchestrator -> EdgeEnv -> AIGuard -> Lab Runtime Intelligence bundle keeps manifest alignment, telemetry-history coverage, Runtime Intelligence Risk Summary rows, EdgeEnv-preserved `operation_risk_summary` navigation context, AIGuard `edgeenv_orchestrator_operation_risk_summary` evidence, remote-dispatch boundary rows, report gates, and optional CI artifact outputs | Production observability, GitLab as a control plane, live remote execution, or a production scheduler |
| Operation quick-scan registry smoke | `bash scripts/smoke_quick_scan_registry_summary.sh` | A fixture-only device-local preservation bundle rebuilds the evidence index and run registry with `Operation Quick Scan Summary` before `## Runs`, `Reviewer operation quick scan`, queue/deadline/fallback markers, and Lab-owner boundary wording | Live Jetson execution, thermal endurance validation, production scheduling, or Lab ownership transfer |

Keep these gates local-first. The agent runtime smoke is the operational
scenario replay; the Runtime Intelligence smoke is the regression/anomaly
artifact-bundle gate; the quick-scan registry smoke is a reviewer-navigation
marker gate. No path makes Orchestrator or AIGuard the final deployment
decision owner; Lab remains the report and decision owner.

Runtime Intelligence smoke writes these reviewer-facing artifacts under the
configured output directory:

| Artifact | Purpose |
|---|---|
| `runtime_intelligence_bundle_manifest_gate_summary.md` | Confirms the committed bundle manifest, EdgeEnv handoff alignment, artifact roles, owner boundaries, and source repository mapping |
| `edgeenv_runtime_regression.md` / `.html` | Shows same-condition EdgeEnv runtime regression evidence without AIGuard enrichment |
| `runtime_anomaly_summary.md` / `.html` | Shows the Lab-owned Runtime Intelligence Risk Summary with EdgeEnv regression, AIGuard deterministic runtime evidence, telemetry coverage, promoted `Operation quick scan` reviewer focus, preserved `operation_risk_summary` markers, AIGuard operation-risk summary evidence, and remote-dispatch boundary rows |
| `runtime_anomaly_gate_summary.md` | Confirms the generated Markdown/HTML report still contains required Runtime Intelligence rows, Lab ownership wording, `Validated Duration Traceability`, and `Validated Reviewer Focus` with `reviewer_focus_operation_quick_scan` reviewer context |
| `runtime_intelligence_ci_artifact_gate_summary.md` | Confirms the optional CI artifact bundle shape, including the copied `Validated Reviewer Focus` marker, without making CI a production control plane |
| `aiguard_edgeenv_handoff_alignment.json` / `.md` | Preserves the precomputed AIGuard/EdgeEnv handoff alignment fixture used by the smoke |

Use this output list when reviewing Runtime Intelligence evidence. Use
`00_evidence_index.*` from the agent runtime smoke when reviewing generated
operation scenario bundles.

The current CI artifact gate also validates Lab-owned report marker context in
the copied AIGuard/EdgeEnv alignment artifact. The expected context is:
`lab_expected_report_markers`, `report_marker_context_role` set to
`lab_report_contract_context`, and
`aiguard_validates_expected_report_markers=false`. This keeps marker
enforcement in Lab's bundle/report gates while AIGuard remains an external
deterministic evidence provider.

## Run

From the InferEdge entrypoint repository:

```bash
bash scripts/demo_agent_runtime_e2e.sh
```

Run the explicit device-local starter path when you want the Orchestrator
`scenario_mode=device_local` config:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local
```

Replace the committed device-local fixtures with local inputs from the
entrypoint script:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --voice-ingress-payload /path/to/requests.json \
  --capture-process-resource-snapshot
```

If optional ONNX Runtime dependencies are installed in the Orchestrator
environment, add a lightweight Vision producer probe:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --vision-onnx-model /path/to/vision_model.onnx
```

This verifies that the entrypoint can pass an ONNX model path into the
Orchestrator device-local Vision producer and preserve
`vision_inference_backend`, input/output shapes, and probe latency through the
e2e smoke outputs. It is not a full live YOLO service.

Add the remote dispatch starter when you want the entrypoint smoke to include
remote worker selection evidence:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch
```

By default this uses Orchestrator's committed remote worker registry and task
request examples. It writes `06_remote_dispatch_result.json`, including
`selected_worker_id`, `decision_reason`, worker health snapshot,
`worker_selection`, `retry_fallback_plan`, `remote_execution_plan`, and
`remote_execution_result`. It also writes
`07_remote_dispatch_guard_analysis.json` so AIGuard can explain whether the
remote dispatch starter stayed selection-only, skipped execution, failed, or
completed the explicit starter path. The smoke gate also checks that AIGuard,
Lab JSON/Markdown, and the generated evidence index preserve the
`remote_dispatch_runtime_event_compact_summary` role, `operation_boundary`, and
`production_remote_execution=false` marker from the Orchestrator artifact.

Explicit HTTP/SSH starter execution is opt-in:

```bash
bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch --remote-execute-plan
```

The committed file-contract worker examples are selection-only, so the
execution result is recorded as skipped starter evidence. A registry entry with
an `http_request` or `ssh_command` endpoint can use the same option to record
starter execution status, transport, and error category. This is remote dispatch
starter evidence, not production SSH/HTTP execution.

Preserve Runtime operation summary through EdgeEnv when you want the entrypoint
bundle to include local registry evidence:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local --edgeenv-run-evidence
```

This writes `08_edgeenv_run_show.json` and `08_edgeenv/.edgeenv/runs.db`.
EdgeEnv stores the Runtime operation summary as supplemental run evidence; it
does not become a deployment decision owner, cloud monitoring path, or
same-condition comparability gate.

To reproduce bounded remote fallback recovery, run only the fallback HTTP
starter worker and leave the primary endpoint unavailable:

```bash
# Terminal A
python3 ../InferEdgeOrchestrator/scripts/remote_http_worker.py \
  --host 127.0.0.1 \
  --port 8765 \
  --worker-id fallback-http-worker

# Terminal B
bash scripts/demo_agent_runtime_e2e.sh \
  --output-dir /tmp/inferedge_agent_runtime_fallback_e2e \
  --frames 8 \
  --remote-dispatch \
  --remote-execute-plan \
  --remote-timeout-sec 1 \
  --remote-worker-registry examples/remote_fallback/remote_worker_registry_fallback.json \
  --remote-task-request examples/remote_fallback/remote_task_request_fallback.json
```

The fallback fixture selects `primary-http-worker` first, where
`http://127.0.0.1:9876/execute` is intentionally unavailable. The retry policy
allows one fallback attempt on `connection_error`, and the local
`fallback-http-worker` listens on `http://127.0.0.1:8765/execute`. A successful
starter replay should include:

- `06_remote_dispatch_result.json` with `fallback_execution_result.final_status`
  set to `succeeded`
- `07_remote_dispatch_guard_analysis.json` with
  `remote_execution_recovered_by_fallback`
- `05_lab_agent_runtime_report.md` with `Remote fallback starter evidence`

This is a bounded starter recovery smoke. It does not provide production retry
control, auth, heartbeat, or a long-lived remote worker.

The Orchestrator source-side fixture for this recovery path is recorded in
`repos.yaml` as supporting reference
`654e0ab27b383317ec816d054b293bfa3061cf32`
(`examples/telemetry/remote_fallback_recovery_sample.json`). It is not part of
the Core `repos.lock` clone/update contract.

When you do not have a local ONNX file but want a detector-like probe instead
of the tiny identity model, generate one under the output directory:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --generate-vision-detector-probe
```

This calls the Orchestrator synthetic detector ONNX generator and uses the
generated `detector_tiny.onnx` as the Vision probe. The generated model is a
local artifact and is not committed. It is closer to image-shaped perception
work than the identity probe, but it still should not be described as full live
YOLO validation.

If you already captured a Jetson `tegrastats` log, pass it through the same
entrypoint smoke:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --tegrastats-log /path/to/tegrastats.log
```

The script copies the provided log into the generated evidence directory and
routes it through the Orchestrator `tegrastats_timeline`, AIGuard reliability
analysis, and Lab report. This is telemetry handoff evidence, not a full
thermal endurance validation.

On Jetson, use `--capture-tegrastats` when you want the entrypoint smoke to
capture `tegrastats` during the Orchestrator sustained run:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --vision-input /path/to/frame.ppm \
  --vision-onnx-model /path/to/model.onnx \
  --capture-tegrastats
```

This starts `tegrastats` for the duration of the Orchestrator run and routes the
captured log through the same `tegrastats_timeline`. It is still a device-local
smoke path, not thermal endurance validation.

Use `--resource-snapshot /path/to/resources.json` instead of
`--capture-process-resource-snapshot` when you already have a resource snapshot
fixture. These overrides intentionally require `--device-local` so the default
producer-backed smoke remains stable and dependency-light.

## Minimum Sample Inputs

If `InferEdgeOrchestrator` is cloned next to this entrypoint repo, the smallest
committed input set is:

| Workload | Path | Source marker |
|---|---|---|
| Vision | `../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm` | `image_file` |
| Voice / Command | `../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json` | `fastapi_request_fixture` |
| Safety / Monitor | `../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json` | `resource_snapshot_fixture` |

Concrete replay command:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_inputs \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --resource-snapshot ../InferEdgeOrchestrator/examples/inputs/safety_resource_snapshots.json
```

Concrete process-snapshot variant:

```bash
bash scripts/demo_agent_runtime_e2e.sh --device-local \
  --output-dir /tmp/inferedge_agent_runtime_device_local_process \
  --frames 8 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --voice-ingress-payload ../InferEdgeOrchestrator/examples/inputs/voice_ingress_requests.json \
  --capture-process-resource-snapshot
```

This remains a device-local starter path. It validates that local producer
inputs flow through Orchestrator, AIGuard, and Lab report contracts. It does not
claim full live YOLO/Whisper/FastAPI/Jetson sustained validation.

## Jetson Starter Validation Record

The same device-local starter path was replayed on a Jetson Orin Nano with a
live `tegrastats` capture. This validates the telemetry handoff path without
claiming full live workload validation.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Frames | 64 |
| Max queue depth | 6 |
| Dropped count | 61 |
| Fallback count | 61 |
| Deadline missed count | 0 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | 39.625 C |
| Max RAM used | 1783 MB |
| Max GPU percent | 0 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

The generated Orchestrator summary preserved `image_file`,
`fastapi_request_fixture`, and `process_resource_snapshot` producer sources.
The Lab report preserved `queue_state_summary`, `worker_health_snapshot`,
`runtime_event_summary`, and `runtime_event_timeline_sample` under
`agent_runtime_summary.operation_context`.

## Jetson ONNX Probe Validation Record

The device-local entrypoint path was also replayed on the same Jetson Orin Nano
with `--vision-onnx-model`. This validates that a local ONNX model can be passed
into the Orchestrator Vision producer and preserved as lightweight inference
probe evidence across Orchestrator, AIGuard, and Lab reports.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Frames | 16 |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision output shape | `[1, 2]` |
| Vision probe latency | 1.255 ms |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

The ONNX model used for this validation was a tiny identity probe model. This
record should be described as device-local ONNX Runtime probe evidence, not as
full live YOLO/Whisper/FastAPI sustained validation.

## Captured Tegrastats Log Option Validation

The entrypoint `--tegrastats-log` option was validated with a separately
captured Jetson Orin Nano `tegrastats` log. The log was captured for about
12 seconds and then passed into the local entrypoint smoke, which copied it into
the evidence bundle and routed it through Orchestrator, AIGuard, and Lab.

| Field | Observed value |
|---|---:|
| Power mode | 25W |
| Scenario mode | `device_local` |
| Captured log duration | ~12 seconds |
| Parsed `tegrastats` samples | 11 |
| Frames | 16 |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| Max temperature | 41.5 C |
| Max RAM used | 830 MB |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates the captured-log telemetry handoff path. It should not be
described as thermal endurance validation or full live YOLO/Whisper/FastAPI
sustained validation.

## Generated Detector Probe Validation

The entrypoint `--generate-vision-detector-probe` option was validated with the
Orchestrator synthetic detector ONNX generator. The generated model stayed under
the temporary output directory and was used only as local probe evidence. The
Lab report step uses `poetry run inferedgelab` when Poetry is available, and
falls back to an installed `inferedgelab` CLI when running on a device image
without Poetry. If neither command is available, the entrypoint invokes the
local Lab repo as `python -m inferedgelab.cli` so Jetson smoke runs can use the
checked-out Lab source without installing a global console script.

| Field | Observed value |
|---|---:|
| Scenario mode | `device_local` |
| Generated model | `generated_models/detector_tiny.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 8 |
| Max queue depth | 6 |
| Dropped count | 5 |
| Fallback count | 5 |
| Lab decision | `blocked` |

This validates the generated detector-like ONNX probe path. It should be
described as a reproducible lightweight vision probe, not as full live YOLO
validation.

The same path was also replayed on Jetson Orin Nano with the generated detector
probe and process resource snapshot enabled.

| Field | Jetson observed value |
|---|---:|
| Scenario mode | `device_local` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 16, 16]` |
| Vision output shape | `[1, 6]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 1 |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This is Jetson device-local smoke evidence for the entrypoint contract chain.
It should not be described as full live YOLO/Whisper/FastAPI sustained
validation or thermal endurance validation.

The same device-local entrypoint path was also replayed with a user-provided
YOLOv8n ONNX model copied to the Jetson temporary directory and passed through
`--vision-onnx-model`.

| Field | Jetson YOLOv8n observed value |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 16 |
| Max queue depth | 6 |
| Dropped count | 13 |
| Fallback count | 13 |
| Deadline missed count | 10 |
| Vision probe elapsed range | `120.147-146.878 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates a real ONNX model probe through the entrypoint contract chain on
Jetson. It should not be described as decoded YOLO accuracy validation, live
camera operation, or full thermal endurance validation.

The real YOLOv8n ONNX probe was then replayed with `--capture-tegrastats` so
that live Jetson telemetry was captured during the Orchestrator sustained run
and routed through AIGuard and the Lab report.

| Field | Jetson YOLOv8n + live tegrastats value |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Vision input shape | `[1, 3, 640, 640]` |
| Vision output shape | `[1, 84, 8400]` |
| Frames | 32 |
| Max queue depth | 6 |
| Dropped count | 29 |
| Fallback count | 29 |
| Deadline missed count | 18 |
| Parsed `tegrastats` samples | 4 |
| Max temperature | `43.937 C` |
| Max RAM used | `966 MB` |
| Vision probe elapsed range | `119.912-137.729 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates the live Jetson telemetry capture path and a real ONNX model
probe in one evidence bundle. It is still not decoded YOLO accuracy validation,
live camera operation, or thermal endurance validation.

The latest main-branch replay was run again on Jetson Orin Nano 25W with the
same entrypoint path, a user-provided `yolov8n.onnx`, local image input,
process resource snapshot capture, and live `tegrastats` capture.

| Field | Latest Jetson device-local replay |
|---|---:|
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped count | 93 |
| Fallback count | 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Max temperature | `39.0 C` |
| Max RAM used | `979 MB` |
| Vision mean / p95 latency | `156.43 ms / 159.629 ms` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This latest replay confirms that the current main branches still carry real
Jetson ONNX probe and live telemetry evidence through Orchestrator, AIGuard,
and Lab over a longer 96-frame starter replay. It also confirms the Lab report
preserves Runtime operation guard evidence (`runtime_latency_budget_overrun`,
`runtime_error_classification`).
It remains a device-local smoke record, not decoded YOLO accuracy, live camera,
Whisper/FastAPI, or sustained thermal endurance validation.
A submission-facing snapshot of the generated Lab evidence is captured in
[`Jetson Device-Local Agent Runtime Evidence Report`](evidence/jetson_device_local_agent_runtime_report.md)
([한국어: Jetson 디바이스 로컬 에이전트 런타임 증거 보고서](evidence/jetson_device_local_agent_runtime_report.ko.md)).

The longer 5-minute-class Jetson replay used the same path with `--frames 3600`
and a 420-second guard timeout.

| Field | 5-minute-class Jetson sustained smoke |
|---|---:|
| Runtime window | 5-minute-class |
| Scenario mode | `device_local` |
| Model | `yolov8n.onnx` |
| Vision inference backend | `onnxruntime` |
| Vision provider | `CPUExecutionProvider` |
| Frames | 3600 |
| Max queue depth | 6 |
| Dropped count | 3597 |
| Fallback count | 3597 |
| Deadline missed count | 1802 |
| Parsed `tegrastats` samples | 281 |
| Max temperature | `50.375 C` |
| Max RAM used | `1038 MB` |
| Vision mean / p95 latency | `152.77 ms / 156.948 ms` |
| EdgeEnv run ID | `run-20260531-092158-c3323ba9` |
| Preservation labels | `preservation_identity` and `preservation_details` present |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

The latest repeat run was captured under
`/tmp/inferedge_agent_runtime_jetson_sustained_5min_edgeenv_20260531T091654Z`
and passed the final schema-marker validation. The bundle preserves derived
`operation_risk_summary` markers, EdgeEnv `runtime_operation_summary`,
AIGuard `queue_pressure_context`, AIGuard `worker_operation_risk_summary`, and
the Lab-owned blocked deployment decision. The Lab report and evidence index
also preserve `preservation_identity` / `preservation_details`. The
submission-facing snapshot is captured as
[`Jetson Device-Local 5-Minute Sustained Smoke Report`](evidence/jetson_device_local_5min_sustained_report.md)
([한국어: Jetson 디바이스 로컬 5분급 지속 스모크 보고서](evidence/jetson_device_local_5min_sustained_report.ko.md))
and
[`HTML report`](evidence/jetson_device_local_5min_sustained_report.html)
([한국어: HTML 보고서](evidence/jetson_device_local_5min_sustained_report.html)).
It is still runtime-operation smoke evidence, not decoded YOLO accuracy
validation, live camera operation, Whisper/FastAPI service execution, production
remote execution, or sustained thermal endurance validation.

For repeat runs on Jetson, use the convenience wrapper:

```bash
bash scripts/demo_jetson_5min_sustained.sh
```

The wrapper calls `scripts/demo_agent_runtime_e2e.sh` with the documented
`device_local`, ONNX Runtime probe, process resource snapshot, and live
`tegrastats` capture options. Use `--help` to override output directory,
frame count, timeout, ONNX model, or clean Forge repo path.

From a development machine, run the readiness preflight before starting a
repeat Jetson smoke:

```bash
bash scripts/check_jetson_sustained_readiness.sh
```

The preflight checks SSH reachability, `tegrastats`, the clean Forge fixture
repo, the Vision input, the ONNX model path, and the sustained runner. It does
not run inference, capture `tegrastats`, or produce new evidence. If it fails,
fix the target connectivity or input setup first and continue treating the
latest committed Jetson report as the latest confirmed evidence.

The script writes generated evidence under:

```text
reports/agent_runtime_e2e/
```

Use a temporary output directory for clean validation:

```bash
bash scripts/demo_agent_runtime_e2e.sh --output-dir /tmp/inferedge_agent_runtime_e2e
bash scripts/demo_agent_runtime_e2e.sh --device-local --output-dir /tmp/inferedge_agent_runtime_e2e_device_local
```

## Clean Jetson Replay Runbook

Use this runbook when the Jetson has local Forge or Runtime worktrees with
experimental builds, untracked artifacts, or branch-specific changes. Do not
delete or reset those worktrees just to reproduce the entrypoint smoke. Instead,
use a temporary clean Forge clone for the fixture contract and keep the evidence
bundle under `/tmp`.

Prepare a clean Forge fixture source:

```bash
rm -rf /tmp/inferedge_clean_repos
mkdir -p /tmp/inferedge_clean_repos
git clone --depth 1 https://github.com/gwonxhj/InferEdgeForge.git \
  /tmp/inferedge_clean_repos/InferEdgeForge
test -f /tmp/inferedge_clean_repos/InferEdgeForge/tests/fixtures/agent_manifest_vision.json
```

For the optional EdgeEnv registry preservation path, make sure the existing
InferEdgeEnv repo is cloned next to the entrypoint repo:

```bash
test -d ~/InferEdgeEnv/.git
```

Replay the 96-frame Jetson device-local path from the entrypoint repo:

```bash
cd ~/InferEdge
PATH=$HOME/miniconda3/envs/yolo_env/bin:$PATH \
INFEREDGE_FORGE_REPO=/tmp/inferedge_clean_repos/InferEdgeForge \
bash scripts/demo_agent_runtime_e2e.sh \
  --device-local \
  --output-dir /tmp/inferedge_agent_runtime_jetson_sustained_96_main \
  --frames 96 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model ~/InferEdge_device_local_inputs/models/yolov8n.onnx \
  --capture-process-resource-snapshot \
  --capture-tegrastats \
  --edgeenv-run-evidence
```

Expected output files:

- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/00_evidence_index.md`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/00_evidence_index.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/03_orchestration_summary.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/04_aiguard_guard_analysis.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/05_lab_agent_runtime_report.json`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/05_lab_agent_runtime_report.md`
- `/tmp/inferedge_agent_runtime_jetson_sustained_96_main/08_edgeenv_run_show.json`

The `00_evidence_index.*` files are generated after the Lab report and provide
a compact navigation layer over the bundle. They summarize scenario label,
scenario category, scenario mode, queue pressure, deadline/drop/fallback counts,
AIGuard verdict, Lab decision, and optional remote-dispatch status without
replacing the source JSON contracts.
When `--edgeenv-run-evidence` is used, the same index also records whether the
Lab Markdown report rendered `Runtime Intelligence EdgeEnv Preservation`, so
the EdgeEnv run ID can be traced from the navigation index into Lab-owned
deployment context.
The index also carries the Lab report marker contract vocabulary, including
`Operation quick scan`, `Reviewer operation quick scan`, `lab_expected_report_markers`,
`lab_report_contract_context`, and
`aiguard_validates_expected_report_markers=false`. These are reviewer
navigation markers only; they do not make the entrypoint, AIGuard, or CI the
Lab report owner.

The EdgeEnv preservation marker path was replayed on Jetson with the latest
entrypoint/Lab main branches and an existing `~/InferEdgeEnv` clone. The
latest 96-frame smoke used the user-provided `yolov8n.onnx`, live
`tegrastats`, process resource snapshot capture, and `--edgeenv-run-evidence`
after the split Jetson preservation report-row and reviewer duration label
gates landed.

| Field | Jetson observed value |
|---|---:|
| Output bundle | `/tmp/inferedge_agent_runtime_jetson_reviewer_duration_96_20260531T102218Z` |
| Entrypoint commit | `c212ea6` |
| Operation path | `device_local_starter` |
| Reviewer duration label | `short 96-frame-class replay (96 frames)` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped / fallback count | 93 / 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Device-local / producer events | 99 / 99 |
| Max temperature / RAM | 45.5 C / 1000 MB |
| Vision mean / p95 latency | 155.86 ms / 156.877 ms |
| EdgeEnv run ID | `run-20260531-102243-4afc19d6` |
| EdgeEnv summary | `runtime_operation_summary` stored |
| Lab preservation section | present |
| Evidence index Lab context | `lab_report_preservation_context_present=true` |
| Preservation labels | `preservation_identity` and `preservation_details` present |
| Reviewer duration row | `Reviewer Duration Label` present in `00_evidence_index.md` |
| Run registry EdgeEnv cell | `lab_preservation=present`, `lab_context=present` |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This validates the local registry preservation bridge. EdgeEnv stores
supplemental Runtime operation evidence; it does not become the Lab deployment
decision owner or a production telemetry database. The latest replay also
confirms the real-device path still renders the preservation identity/details
and reviewer duration label rows now gated by `scripts/smoke_all.sh`.

### Latest Jetson Quick-Scan Registry

The same 96-frame EdgeEnv preservation path was replayed again on Jetson after
the Runtime Intelligence quick-scan marker gate landed. This run verifies that
the live device-local bundle carries the Lab report marker contract vocabulary
inside `00_evidence_index.*`.

| Field | Jetson quick-scan marker replay |
|---|---:|
| Output bundle | `/tmp/inferedge_agent_runtime_jetson_quick_scan_96_20260608T105418Z` |
| Entrypoint commit | `16a2ef0` |
| Operation path | `device_local_starter` |
| Reviewer operation marker | `Reviewer operation quick scan` |
| Reviewer operation label | `queue_pressure_reason=queue_backlog_threshold_exceeded; max_total_queue_depth=6; deadline_missed_count=50; fallback_count=93` |
| Report marker context | `lab_report_contract_context` |
| AIGuard marker ownership | `aiguard_validates_expected_report_markers=false` |
| Frames | 96 |
| Duration label | `short 96-frame-class replay (96 frames)` |
| Max queue depth | 6 |
| Dropped / fallback count | 93 / 93 |
| Deadline missed count | 50 |
| Parsed `tegrastats` samples | 9 |
| Device-local / producer events | 99 / 99 |
| EdgeEnv run ID | `run-20260608-105430-f8841ef4` |
| Lab preservation section | present |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

This record is a live marker-preservation smoke for reviewer navigation. It
does not change Lab ownership, EdgeEnv comparability ownership, AIGuard
diagnosis ownership, or the starter-only boundary of the device-local path.

A newer reviewer-focus validation was run on 2026-06-09 KST
(`20260608T232814Z` UTC) after the entrypoint started gating Lab's
`Validated Reviewer Focus` summary marker. This rerun does not replace the
5-minute-class evidence above; it confirms that the current Jetson checkout and
the current Lab Runtime Intelligence artifact gate both preserve the
reviewer-facing quick-scan markers.

| Field | Jetson reviewer-focus validation |
|---|---:|
| Readiness preflight | `passed` with `--edgeenv-run-evidence` |
| Entrypoint commit | `06e4ab9` |
| Lab commit | `3a7a464` |
| Device-local output bundle | `/tmp/inferedge_agent_runtime_jetson_reviewer_focus_96_20260608T232814Z` |
| Lab Runtime Intelligence smoke | `/tmp/inferedgelab_runtime_intelligence_reviewer_focus_jetson_20260608T232927Z` |
| Registry Markdown | `/tmp/inferedge_agent_runtime_jetson_reviewer_focus_96_registry_20260608T232814Z.md` |
| Runtime Intelligence summary marker | `Validated Reviewer Focus` |
| Reviewer focus marker | `reviewer_focus_operation_quick_scan` |
| Agent runtime preservation marker | `Runtime Intelligence EdgeEnv Preservation` |
| Operation quick-scan registry section | `Operation Quick Scan Summary` |
| EdgeEnv run ID | `run-20260608-232827-e584af13` |
| Frames | 96 |
| Max queue depth | 6 |
| Dropped / fallback count | 93 / 93 |
| Deadline missed count | 50 |
| Lab decision | `blocked` |

The first Lab smoke attempt used Jetson's system `python3` and failed because
`typer` was not installed in that interpreter. Re-running the same Lab smoke
with `PATH=$HOME/miniconda3/envs/yolo_env/bin:$PATH` passed and produced the
`Validated Reviewer Focus` and `reviewer_focus_operation_quick_scan` markers in
both `runtime_anomaly_gate_summary.md` and
`runtime_intelligence_ci_artifact_gate_summary.md`. This is an environment
selection note, not a contract change.

The 96-frame quick-scan bundle was then indexed together with a fresh
5-minute-class Jetson replay so reviewers can compare duration and operation
context without opening each full report first. The older documented
5-minute-class bundle lived under Jetson `/tmp`, so the comparison uses a new
3600-frame replay generated on the same current entrypoint branch.

| Field | Jetson duration registry replay |
|---|---:|
| 96-frame bundle | `/tmp/inferedge_agent_runtime_jetson_quick_scan_96_20260608T105418Z` |
| 5-minute-class bundle | `/tmp/inferedge_agent_runtime_jetson_sustained_5min_quick_scan_compare_20260608T110341Z` |
| Registry Markdown | `/tmp/inferedge_agent_runtime_jetson_duration_quick_scan_registry_summary_20260608T115310Z.md` |
| Registry JSON | `/tmp/inferedge_agent_runtime_jetson_duration_quick_scan_registry_summary_20260608T115310Z.json` |
| Duration rows | `short 96-frame-class replay (96 frames)` and `5-minute-class sustained replay (3600 frames)` |
| 96-frame queue/drop/fallback/deadline | `6 / 93 / 93 / 50` |
| 5-minute queue/drop/fallback/deadline | `6 / 3597 / 3597 / 1802` |
| Parsed `tegrastats` samples | `9` and `309` |
| EdgeEnv run IDs | `run-20260608-105430-f8841ef4`, `run-20260608-110905-0d126ea1` |
| Lab preservation registry cell | `lab_preservation=present`, `lab_context=present` |
| Operation quick-scan registry section | `Operation Quick Scan Summary` before `## Runs` |
| Operation quick-scan registry column | `Reviewer operation quick scan: queue_pressure_reason=...; max_total_queue_depth=...; deadline_missed_count=...; fallback_count=...` |
| AIGuard / Lab status | `blocked/high`, `blocked` for both rows |

This registry is still a local-first review navigation artifact. It separates
the short replay and 5-minute-class replay by duration metadata while preserving
both as Smoke/Starter evidence, not thermal endurance validation or production
runtime operation proof. The `Operation Quick Scan` column mirrors Lab report
marker context from each run's EdgeEnv summary for reviewer navigation only; it
does not make the registry a Lab report owner. The regenerated Markdown registry
now shows both rows in `Operation Quick Scan Summary` before the full `## Runs`
table, and keeps the detailed `Reviewer operation quick scan` labels before the
longer EdgeEnv cell. Reviewers can identify queue/deadline/fallback pressure
without opening each bundle first.

To compare multiple generated run bundles, build a local entrypoint navigation
registry from their indexes:

```bash
python3 scripts/build_agent_runtime_run_registry.py \
  --run-dir /tmp/inferedge_agent_runtime_e2e \
  --run-dir /tmp/inferedge_agent_runtime_e2e_device_local \
  --output-json /tmp/inferedge_agent_runtime_registry.json \
  --output-md /tmp/inferedge_agent_runtime_registry.md
```

The registry is derived from `00_evidence_index.json` files and is only a
navigation layer. It does not replace the Orchestrator, AIGuard, Lab, remote
dispatch source contracts, or InferEdgeEnv's SQLite run evidence registry and
comparability checker. Registry tables preserve scenario label and category when
Orchestrator emits them, while keeping scenario mode for backward compatibility
with older bundles. Each index also records an additive `duration_class` /
`duration_label`, so reviewers can distinguish short 96-frame-class replay,
5-minute-class sustained replay, quick starter smoke, and custom sustained
smoke without opening every Orchestrator JSON first. The Markdown index mirrors
those values in a dedicated `Reviewer Duration Label` table before the detailed
run summary, so short replay and sustained replay bundles are easier to
separate during review. The same table now preserves `duration_source` and
`duration_scope_label`, including `source=entrypoint_requested_frames` when the
entrypoint CLI supplied the frame count, so replay-duration metadata remains
traceable without changing source contracts. Each index also records an
`operation_path` such as
`device_local_starter`, `producer_backed_starter`, `remote_dispatch_starter`,
or `remote_dispatch_with_fallback`. When remote dispatch evidence is present,
the registry table preserves selected worker, remote execution status, and
fallback final status as starter evidence rather than production remote
execution proof. It also preserves `production_remote_execution` and
`operation_boundary` when Orchestrator emits them so the starter boundary stays
visible in the navigation layer. When EdgeEnv preservation evidence carries
Lab report quick-scan marker context, the registry also renders an
`Operation Quick Scan Summary` before the detailed run table and keeps the
same compact label in the `Operation Quick Scan` column, so reviewers can see
queue/deadline/fallback pressure before opening the full run report. The entrypoint smoke now fails if the
downstream AIGuard, Lab, or evidence-index artifacts drop the compact remote
runtime event role or starter-only boundary marker.
For a local-only gate that does not start the fallback HTTP worker, run
`bash scripts/smoke_remote_fallback_registry_marker.sh`. It creates a synthetic
remote fallback bundle, rebuilds the evidence index and registry, and requires
`aiguard=remote_execution_recovered_by_fallback` plus
`lab=Remote fallback starter evidence` in the registry Markdown.

For a fixture-only quick-scan registry gate, run
`bash scripts/smoke_quick_scan_registry_summary.sh`. It creates a synthetic
device-local EdgeEnv preservation bundle, rebuilds the evidence index and run
registry, and requires `Operation Quick Scan Summary` before `## Runs` with
`Reviewer operation quick scan`, queue/deadline/fallback markers, reviewer
navigation metadata, and the Lab-owner boundary wording. This gate does not
need a live Jetson or Orchestrator worker.

For a focused runtime-operation comparison, generate one device-local
probe/process bundle and one remote fallback bundle, then build a registry from
those two output directories:

```bash
python3 scripts/build_agent_runtime_run_registry.py \
  --run-dir /tmp/inferedge_agent_runtime_device_local_probe_process \
  --run-dir /tmp/inferedge_agent_runtime_fallback_e2e \
  --output-json /tmp/inferedge_agent_runtime_compare_registry.json \
  --output-md /tmp/inferedge_agent_runtime_compare_registry.md
```

This lets reviewers compare the device-local input/probe path and the bounded
remote fallback path in one table while still drilling back into each run's
Orchestrator, AIGuard, Lab, and remote-dispatch source artifacts.
When multiple Jetson device-local bundles are indexed together, the duration
columns keep the 96-frame replay and 5-minute-class sustained replay visibly
separate while preserving both as Smoke/Starter evidence.
For the latest Jetson pair, run the registry builder on the Jetson because the
generated bundles are stored under that device's `/tmp`:

```bash
python3 scripts/build_agent_runtime_run_registry.py \
  --run-dir /tmp/inferedge_agent_runtime_jetson_quick_scan_96_20260608T105418Z \
  --run-dir /tmp/inferedge_agent_runtime_jetson_sustained_5min_quick_scan_compare_20260608T110341Z \
  --output-json /tmp/inferedge_agent_runtime_jetson_duration_quick_scan_registry_summary_20260608T115310Z.json \
  --output-md /tmp/inferedge_agent_runtime_jetson_duration_quick_scan_registry_summary_20260608T115310Z.md
```

The generated registry keeps both rows under the same navigation table while
the `Duration Label` column separates
`short 96-frame-class replay (96 frames)` from
`5-minute-class sustained replay (3600 frames)`. This comparison is for review
navigation and evidence traceability; it does not upgrade either bundle to
thermal endurance validation.
The Markdown registry now also renders a `Duration Comparison Summary` before
the detailed run table, grouping those duration labels so reviewers can choose
the right bundle before scanning the wider operation/EdgeEnv columns.
The summary includes `Duration Sources`, preserving whether duration scope came
from `entrypoint_requested_frames` or Orchestrator artifact metadata.
For device-local input override runs, the generated `00_evidence_index.json`
and run registry now include `producer_sources`, `device_local_producer_count`,
and `producer_stages`. In the override path these fields should show
`image_file`, `fastapi_request_fixture`, `resource_snapshot_fixture`, and
`device_local_cli_override`, which confirms that the entrypoint passed local
inputs through Orchestrator before the AIGuard and Lab reports were generated.
When EdgeEnv evidence is present, the registry EdgeEnv cell also marks
`lab_preservation=present` after Lab renders the preservation section, keeping
the reviewer path aligned with the Lab report without changing source
contracts.

Expected evidence markers:

- `multi_workload_sustained_summary`
- `tegrastats_timeline`
- `profiled_workload_pressure`
- `thermal_resource_pressure`
- `runtime_latency_budget_overrun`
- `runtime_error_classification`
- `runtime_error_retryable`
- `runtime_error_retry_hint`
- `runtime_retryable_error_review`
- `worker_health_degradation`
- `scheduler_delay_pattern` when scheduler delay events are observed
- `agent_deployment_decision`

The observed timing and resource values can vary slightly by Jetson mode,
current load, and thermal state. This runbook validates a clean replay of the
device-local ONNX probe and live telemetry handoff path. It is not decoded YOLO
accuracy validation, live camera operation, Whisper/FastAPI service execution,
or sustained thermal endurance validation.

## Inputs

The script resolves repositories from `./repos`, sibling directories, or
`/Users/GwonHyeokJun/Documents/GitHub`.

Override paths when needed:

```bash
INFEREDGE_FORGE_REPO=/path/to/InferEdgeForge \
INFEREDGE_RUNTIME_REPO=/path/to/InferEdge-Runtime \
INFEREDGE_ORCHESTRATOR_REPO=/path/to/InferEdgeOrchestrator \
INFEREDGE_AIGUARD_REPO=/path/to/InferEdgeAIGuard \
INFEREDGE_LAB_REPO=/path/to/InferEdgeLab \
bash scripts/demo_agent_runtime_e2e.sh
```

## Outputs

| Output | Purpose |
|---|---|
| `00_evidence_index.json` | Compact machine-readable navigation index for generated evidence files |
| `00_evidence_index.md` | Human-readable evidence bundle index and decision summary |
| `01_forge_agent_manifest_vision.json` | Agent workload handoff contract example |
| `02_runtime_result_agent.json` | Runtime result with backward-compatible `agent` block |
| `03_orchestration_summary.json` | Profiled multi-workload scheduler policy decision evidence |
| `03_tegrastats_sample.log` | Local tegrastats-style sample, copied captured log, or live captured Jetson log for thermal/resource evidence |
| `generated_models/detector_tiny.onnx` | Optional local artifact written only when `--generate-vision-detector-probe` is used |
| `04_aiguard_guard_analysis.json` | Deterministic runtime reliability diagnosis evidence |
| `04_aiguard_guard_analysis.md` | Human-readable AIGuard report |
| `05_lab_agent_runtime_report.json` | Lab-owned agent runtime reliability report |
| `05_lab_agent_runtime_report.md` | Human-readable Lab deployment decision context |
| `06_remote_dispatch_result.json` | Optional file-based remote worker selection evidence when `--remote-dispatch` is used |
| `07_remote_dispatch_guard_analysis.json` | Optional AIGuard diagnosis for remote dispatch starter evidence |
| `07_remote_dispatch_guard_analysis.md` | Optional human-readable remote dispatch diagnosis |
| `08_edgeenv_run_show.json` | Optional EdgeEnv run evidence when `--edgeenv-run-evidence` is used |
| `08_edgeenv/.edgeenv/runs.db` | Optional EdgeEnv local registry for the Runtime operation evidence run |

Expected sustained evidence markers:

- `sustained_high_load` in Orchestrator output
- `multi_workload_sustained_summary` and `tegrastats_timeline` in Orchestrator output
- `image_file`, `fastapi_request_fixture`, `resource_snapshot_fixture`, and `resource_degradation_score` in Orchestrator output
- `producer_sources` and `device_local_producer_count` in Orchestrator output when `--device-local` is used
- `sustained_overload_risk` in AIGuard output
- `profiled_workload_pressure` and `thermal_resource_pressure` in AIGuard output
- `worker_health_degradation` in AIGuard output when Orchestrator worker health
  marks degraded or constrained runtime loops
- `scheduler_delay_pattern` in AIGuard output when scheduler delay events are
  observed
- `queue_pressure_context` in AIGuard output when Orchestrator reports elevated
  or threshold-exceeded queue pressure reasons
- `worker_operation_risk_summary` in AIGuard output when Orchestrator records
  non-healthy worker operation risk labels
- `device_local_operation_context` in AIGuard and Lab output when
  `--device-local` records producer source and runtime event coverage
- `runtime_retryable_error` and `runtime_error_retryable` when Runtime marks a
  timeout or skipped execution as retryable evidence
- `runtime_operation_summary` in Runtime and Orchestrator-bundled Runtime
  result evidence, plus `runtime_operation_health` in AIGuard output when
  Runtime provides summary risk labels or a review action
- `runtime_retryable_error_review` in the Lab report when retryable Runtime
  failure-handling evidence requires deployment review
- `runtime_operation_summary_review` in the Lab report when Runtime summary
  evidence is carried into Lab-owned decision context
- `max_total_queue_depth` in Lab report metrics
- `profiled_workload_pressure` and `thermal_resource_pressure` preserved in Lab report evidence
- `AIGuard Orchestrator Operation Evidence` in the Lab Markdown report,
  including worker reason summaries plus policy/drop reason counts
- `operation_context`, `queue_state_summary`, `worker_health_snapshot`,
  `runtime_event_summary`, and `runtime_event_timeline_sample` preserved in
  the Lab report
- `queue_pressure_reason`, `max_pressure_task`, `operation_risk_summary`, and
  producer context preserved in Lab JSON/Markdown reports
- `operation_summary_recommended_action`, Runtime risk labels, and Runtime
  evidence gaps visible in Lab Markdown and the generated evidence index
- `Orchestrator Operation Context`, `Worker Health`, and
  `Runtime Event Summary` visible in the Lab Markdown report, including worker
  operation risk and queue pressure reason tables
- `sustained_overload_review` in Lab decision rules
- `inferedge-remote-dispatch-result-v1`, `file_contract_starter`, and
  `selected_worker_id` in `06_remote_dispatch_result.json` when
  `--remote-dispatch` is used
- `remote_execution_plan`, `worker_selection`, and `retry_fallback_plan` in
  `06_remote_dispatch_result.json` when `--remote-dispatch` is used
- `remote_execution_result` in `06_remote_dispatch_result.json` and
  `Remote execution starter evidence` in the Lab Markdown report when
  `--remote-dispatch` is used
- `07_remote_dispatch_guard_analysis.json` with deterministic AIGuard evidence
  for the remote dispatch starter when `--remote-dispatch` is used
- `remote_dispatch_runtime_event_compact_summary` and
  `remote dispatch starter evidence only` in AIGuard, Lab, and
  `00_evidence_index.*` artifacts when `--remote-dispatch` is used
- `runtime_operation_summary` in `08_edgeenv_run_show.json` and
  `edgeenv_summary` in `00_evidence_index.json` when
  `--edgeenv-run-evidence` is used
- `Runtime Intelligence EdgeEnv Preservation` in the Lab Markdown report when
  `--edgeenv-run-evidence` is used, so the EdgeEnv run ID and Runtime operation
  summary remain visible in Lab-owned deployment context
- `preservation_identity` / `preservation_details` in `00_evidence_index.*`
  when `--edgeenv-run-evidence` is used, matching the Lab Agent Runtime report
  split between short identity and detailed navigation markers
- `Reviewer operation quick scan` and `lab_expected_report_markers` in
  `00_evidence_index.*`, keeping the entrypoint navigation index aligned with
  the Lab-owned Runtime Intelligence report marker contract
- `lab_report_preservation_section_present` in `00_evidence_index.*` and
  `lab_preservation=present` in the run registry when Lab preserves the same
  EdgeEnv context

## Scope Boundary

Included:

- Vision / Voice-Command / Safety-Monitor workload contracts
- priority/deadline scheduling evidence
- drop/fallback/deadline signal propagation
- lightweight producer-backed sustained workload summary
- Vision local image fixture, Voice FastAPI-style request fixture, and Safety resource snapshot fixture propagation
- optional `--device-local` replay for the explicit Orchestrator device-local starter config
- optional device-local input overrides through `--vision-input`,
  `--voice-ingress-payload`, `--resource-snapshot`, or
  `--capture-process-resource-snapshot`
- optional generated detector-like ONNX probe through
  `--generate-vision-detector-probe`
- local tegrastats-style thermal/resource sample propagation
- optional captured `tegrastats` log propagation through `--tegrastats-log`
- optional live Jetson `tegrastats` capture through `--capture-tegrastats`
- optional file-based remote worker selection evidence through
  `--remote-dispatch`
- optional EdgeEnv local run registry evidence through
  `--edgeenv-run-evidence`
- AIGuard runtime reliability interpretation
- Lab-owned report and deployment decision context

Not included:

- production SaaS infrastructure
- DB/queue persistence
- cloud orchestration
- production remote worker execution, SSH/HTTP dispatch, or secure tunnel
  operation
- LLM agent framework implementation
- universal AI OS claims
