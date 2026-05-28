# Jetson Device-Local 5-Minute Sustained Smoke Report

This document captures a longer device-local sustained smoke replay of the
InferEdge runtime-operation evidence chain.

Scope:

- Device: Jetson Orin Nano 25W
- Entrypoint: `InferEdge/scripts/demo_agent_runtime_e2e.sh`
- Scenario: `device_local`
- Model: user-provided `yolov8n.onnx`
- Vision backend: ONNX Runtime `CPUExecutionProvider`
- Telemetry: live `tegrastats` capture during the Orchestrator run
- Output bundle: `/tmp/inferedge_agent_runtime_jetson_sustained_5min_operation_risk_summary_v2`

This is 5-minute-class device-local runtime reliability smoke evidence. It is
not decoded YOLO accuracy validation, live camera operation, Whisper/FastAPI
service execution, production remote execution, or sustained thermal endurance
validation.

## Replay Command

```bash
cd ~/InferEdge
PATH=$HOME/miniconda3/envs/yolo_env/bin:$PATH \
INFEREDGE_FORGE_REPO=/tmp/inferedge_clean_repos/InferEdgeForge \
timeout 420 bash scripts/demo_agent_runtime_e2e.sh \
  --device-local \
  --output-dir /tmp/inferedge_agent_runtime_jetson_sustained_5min_operation_risk_summary_v2 \
  --frames 3600 \
  --vision-input ../InferEdgeOrchestrator/examples/inputs/vision_frame.ppm \
  --vision-onnx-model ~/InferEdge_device_local_inputs/models/yolov8n.onnx \
  --capture-process-resource-snapshot \
  --capture-tegrastats
```

Latest confirmed run:

- Captured after Runtime Intelligence CI artifact gate hardening
- Entrypoint schema-marker validation: `passed`
- AIGuard operation context markers: `queue_pressure_context`, `worker_operation_risk_summary`

## Runtime Reliability Metrics

| Metric | Value |
|---|---:|
| Frames | 3600 |
| Executed count | 3603 |
| Dropped count | 3597 |
| Fallback count | 3597 |
| Deadline missed count | 1802 |
| Overload event count | 3597 |
| Policy decision count | 3597 |
| Max queue depth | 6 |
| Queue pressure state | overloaded |
| Queue pressure reason | queue_backlog_threshold_exceeded |
| Max pressure task | vision_agent |
| Queue depth samples | 7206 |
| Parsed `tegrastats` samples | 294 |
| Max temperature | 49.843 C |
| Max RAM used | 1155 MB |

## Workload Summary

| Agent | Type | Executed | Dropped | Deadline Missed | Fallback | Mean Latency ms | P95 Latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| safety_monitor_agent | safety | 1800 | 0 | 0 | 0 | 3.097 | 3.247 |
| vision_agent | vision | 1802 | 1798 | 1802 | 1798 | 160.021 | 158.415 |
| voice_command_agent | voice | 1 | 1799 | 0 | 1799 | 39.023 | 39.023 |

## Runtime Operation Evidence

| Field | Value |
|---|---|
| runtime_result_schema | `inferedge-runtime-result-v1` |
| scenario_mode | `device_local` |
| vision_inference_backend | `onnxruntime` |
| vision_model_path | `/home/risenano01/InferEdge_device_local_inputs/models/yolov8n.onnx` |
| queue_pressure_state | `overloaded` |
| runtime_error_category | `runtime_timeout_observed` |
| runtime_error_severity | `medium` |

## AIGuard Evidence

| Evidence | Metric | Status | Severity |
|---|---|---|---|
| repeated_deadline_miss | deadline_miss_rate | failed | high |
| excessive_drop_rate | drop_rate | failed | medium |
| fallback_overuse | fallback_rate | failed | medium |
| queue_backlog_risk | queue_backlog_policy_decision_count | warning | medium |
| sustained_overload_risk | max_total_queue_depth | failed | medium |
| runtime_latency_budget_overrun | latency_budget_exceeded | failed | medium |
| runtime_error_classification | runtime_error_severity | failed | medium |
| profiled_workload_pressure | profiled_workload_risk_count | failed | high |
| thermal_resource_pressure | max_temperature_c=49.843 | passed | low |
| worker_health_degradation | degraded_or_constrained_worker_count | warning | medium |
| queue_pressure_context | queue_pressure_reason_count | warning | medium |
| worker_operation_risk_summary | worker_operation_risk_count | warning | medium |
| device_local_operation_context | device_local_event_count | passed | low |

AIGuard verdict:

- guard_verdict: `blocked`
- severity: `high`
- confidence: `0.88`
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

This replay intentionally shows an unsafe runtime condition rather than a
successful benchmark-only path. The Vision workload exceeded its latency budget
under a longer device-local starter run, queue backlog caused repeated
drop/fallback policy decisions, and AIGuard escalated the runtime reliability
evidence. Lab correctly preserved the evidence and produced a blocked
deployment decision.

This strengthens the portfolio evidence because it demonstrates that InferEdge
does not only report fast runs. It also records longer runtime-operation
pressure and carries that evidence through Orchestrator, AIGuard, and the
Lab-owned deployment decision.

InferEdgeLab remains the final deployment decision owner. Orchestrator and
AIGuard provide evidence; they do not overwrite Lab policy.
