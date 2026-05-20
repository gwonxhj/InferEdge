# Jetson Device-Local Agent Runtime Evidence Report

This document captures the submission-facing summary of the Lab report generated
by the clean Jetson replay runbook.

Scope:

- Device: Jetson Orin Nano 25W
- Entrypoint: `InferEdge/scripts/demo_agent_runtime_e2e.sh`
- Scenario: `device_local`
- Model: user-provided `yolov8n.onnx`
- Vision backend: ONNX Runtime `CPUExecutionProvider`
- Telemetry: live `tegrastats` capture during the Orchestrator run
- Output bundle: `/tmp/inferedge_agent_runtime_jetson_sustained_96_main`

This is device-local runtime reliability smoke evidence. It is not decoded YOLO
accuracy validation, live camera operation, Whisper/FastAPI service execution,
production remote execution, or sustained thermal endurance validation.

## Replay Command

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
  --capture-tegrastats
```

## Runtime Reliability Metrics

| Metric | Value |
|---|---:|
| Frames | 96 |
| Executed count | 99 |
| Dropped count | 93 |
| Fallback count | 93 |
| Deadline missed count | 50 |
| Max queue depth | 6 |
| Queue pressure state | overloaded |
| Policy decision reason | queue_backlog_threshold_exceeded |
| Parsed `tegrastats` samples | 9 |
| Max temperature | 39.0 C |
| Max RAM used | 979 MB |

## Workload Summary

| Agent | Type | Executed | Dropped | Deadline Missed | Fallback | Mean Latency ms | P95 Latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| safety_monitor_agent | safety | 48 | 0 | 0 | 0 | 3.196 | 3.282 |
| vision_agent | vision | 50 | 46 | 50 | 46 | 156.43 | 159.629 |
| voice_command_agent | voice | 1 | 47 | 0 | 47 | 38.826 | 38.826 |

## Runtime Operation Evidence

| Field | Value |
|---|---|
| runtime_result_schema | `inferedge-runtime-result-v1` |
| compare_key | `vision_agent__b1__h224w224__fp32` |
| backend_key | `onnxruntime__cpu` |
| runtime_status | `degraded` |
| runtime_error_category | `runtime_timeout_observed` |
| timeout_policy | `latency_threshold` |
| timeout_budget_ms | 20 |
| runtime_timeout_observed | `true` |

## AIGuard Evidence

| Evidence | Metric | Status | Severity |
|---|---|---|---|
| repeated_deadline_miss | deadline_miss_rate=0.505051 | failed | high |
| excessive_drop_rate | drop_rate=0.484375 | failed | medium |
| fallback_overuse | fallback_rate=0.484375 | failed | medium |
| queue_backlog_risk | queue_backlog_policy_decision_count=93 | warning | medium |
| sustained_overload_risk | max_total_queue_depth=6 | failed | medium |
| runtime_latency_budget_overrun | latency_budget_exceeded=1 | failed | medium |
| runtime_error_classification | runtime_error_severity=medium | failed | medium |
| profiled_workload_pressure | profiled_workload_risk_count=3 | failed | high |
| thermal_resource_pressure | max_temperature_c=39.0 | passed | low |

AIGuard verdict:

- guard_verdict: `blocked`
- severity: `high`
- primary_reason: `deadline_miss_rate indicates runtime reliability risk under orchestrated multi-agent load.`

## Lab Deployment Decision

| Field | Value |
|---|---|
| policy_version | `inferedge-lab-agent-runtime-policy-v1` |
| decision | `blocked` |
| reason | Agent runtime reliability evidence indicates blocked deployment risk. |
| recommended_action | Do not deploy until deadline, drop, fallback, and guard evidence are reviewed. |

Triggered rules:

- `guard_blocked_runtime_block`
- `deadline_miss_block`
- `drop_rate_review`
- `fallback_rate_review`
- `queue_backlog_review`
- `sustained_overload_review`
- `runtime_timeout_observed_review`
- `runtime_operation_guard_block`

## Interpretation

The replay demonstrates that the entrypoint can carry device-local workload
pressure, live Jetson telemetry, Runtime operation evidence, AIGuard reliability
signals, and a Lab-owned deployment decision through one evidence chain.

The result is intentionally `blocked`: the Vision workload exceeded its latency
budget under the orchestrated device-local starter scenario, queue backlog
triggered repeated drop/fallback policy decisions, and AIGuard escalated the
runtime reliability evidence. This is useful as reliability evidence because it
shows how the pipeline handles unsafe runtime conditions rather than only
reporting a successful benchmark.

InferEdgeLab remains the final deployment decision owner. Orchestrator and
AIGuard provide evidence; they do not overwrite Lab policy.
