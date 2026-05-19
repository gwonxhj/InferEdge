# Reliable Edge Agent Runtime E2E Demo

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
optional `--device-local` mode uses committed local image, request, and resource
snapshot producers in Orchestrator `scenario_mode=device_local`.

## Contract Chain

```text
Forge agent_manifest
-> Runtime result.agent
-> Orchestrator orchestration_summary
-> AIGuard guard_analysis
-> Lab agent-runtime-report
```

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
without Poetry.

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

The script writes generated evidence under:

```text
reports/agent_runtime_e2e/
```

Use a temporary output directory for clean validation:

```bash
bash scripts/demo_agent_runtime_e2e.sh --output-dir /tmp/inferedge_agent_runtime_e2e
bash scripts/demo_agent_runtime_e2e.sh --device-local --output-dir /tmp/inferedge_agent_runtime_e2e_device_local
```

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
| `01_forge_agent_manifest_vision.json` | Agent workload handoff contract example |
| `02_runtime_result_agent.json` | Runtime result with backward-compatible `agent` block |
| `03_orchestration_summary.json` | Profiled multi-workload scheduler policy decision evidence |
| `03_tegrastats_sample.log` | Local tegrastats-style sample, copied captured log, or live captured Jetson log for thermal/resource evidence |
| `generated_models/detector_tiny.onnx` | Optional local artifact written only when `--generate-vision-detector-probe` is used |
| `04_aiguard_guard_analysis.json` | Deterministic runtime reliability diagnosis evidence |
| `04_aiguard_guard_analysis.md` | Human-readable AIGuard report |
| `05_lab_agent_runtime_report.json` | Lab-owned agent runtime reliability report |
| `05_lab_agent_runtime_report.md` | Human-readable Lab deployment decision context |

Expected sustained evidence markers:

- `sustained_high_load` in Orchestrator output
- `multi_workload_sustained_summary` and `tegrastats_timeline` in Orchestrator output
- `image_file`, `fastapi_request_fixture`, `resource_snapshot_fixture`, and `resource_degradation_score` in Orchestrator output
- `producer_sources` and `device_local_producer_count` in Orchestrator output when `--device-local` is used
- `sustained_overload_risk` in AIGuard output
- `profiled_workload_pressure` and `thermal_resource_pressure` in AIGuard output
- `max_total_queue_depth` in Lab report metrics
- `profiled_workload_pressure` and `thermal_resource_pressure` preserved in Lab report evidence
- `operation_context`, `queue_state_summary`, `worker_health_snapshot`,
  `runtime_event_summary`, and `runtime_event_timeline_sample` preserved in
  the Lab report
- `Orchestrator Operation Context`, `Worker Health`, and
  `Runtime Event Summary` visible in the Lab Markdown report
- `sustained_overload_review` in Lab decision rules

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
- AIGuard runtime reliability interpretation
- Lab-owned report and deployment decision context

Not included:

- production SaaS infrastructure
- DB/queue persistence
- cloud orchestration
- LLM agent framework implementation
- universal AI OS claims
