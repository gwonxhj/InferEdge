# Jetson Device-Local 5-Minute Sustained Smoke Report 한국어 Quick Guide

언어: [English](jetson_device_local_5min_sustained_report.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[Jetson Device-Local 5-Minute Sustained Smoke Report](jetson_device_local_5min_sustained_report.md)입니다.

이 report는 Jetson device-local starter를 5-minute-class로 반복 실행한
runtime-operation evidence 요약입니다. 목적은 장시간 production service를
증명하는 것이 아니라, device-local overload 상황의 queue/drop/fallback,
telemetry, EdgeEnv preservation, AIGuard warning, Lab-owned deployment
decision 흐름을 재현하는 것입니다.

## 최신 registry와의 관계

이 문서는 submission-facing 5-minute-class Jetson evidence snapshot입니다.
최신 reviewer navigation 기록은
[`docs/agent_runtime_e2e_demo.ko.md`](../agent_runtime_e2e_demo.ko.md#최근-jetson-quick-scan-marker-재현)에
정리된 operation-summary quick-scan registry입니다.
해당 section의 용어 표를 기준으로 `representative snapshot`,
`latest registry`, `quick-scan navigation` 의미를 96-frame report와 맞춰
읽습니다.

최신 registry cross-check:

| 항목 | 값 |
|---|---|
| Entrypoint commit | `c04abc9` |
| 최신 5-minute-class bundle | `/tmp/inferedge_agent_runtime_jetson_sustained_5min_operation_summary_latest_20260609T121700Z` |
| 최신 registry Markdown | `/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.md` |
| 최신 registry JSON | `/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.json` |
| 최신 5-minute EdgeEnv run ID | `run-20260609-122009-c17a030b` |
| Duration row | `5-minute-class sustained replay (3600 frames)` |
| Operation summary labels | `operation_summary: mode=device_local_starter` / `operation_summary: mode=timeout_threshold_exceeded` |

이 registry는 96-frame replay와 5-minute-class replay를 하나의 navigation
table에서 비교하게 해줍니다. 두 run을 thermal endurance validation으로
격상하거나, 이 문서의 metric snapshot을 대체하거나, registry를 Lab report
owner로 만들지 않습니다.

## Scope

| 항목 | 값 |
|---|---|
| Device | Jetson Orin Nano 25W |
| Scenario | `device_local` |
| Model | user-provided `yolov8n.onnx` |
| Vision backend | ONNX Runtime `CPUExecutionProvider` |
| Telemetry | Orchestrator run 중 live `tegrastats` capture |
| Replay length | 3600 frames |
| EdgeEnv run ID | `run-20260531-092158-c3323ba9` |

## 핵심 수치

| Metric | Value |
|---|---:|
| Frames | 3600 |
| Executed count | 3603 |
| Dropped count | 3597 |
| Fallback count | 3597 |
| Deadline missed count | 1802 |
| Overload event count | 3597 |
| Max queue depth | 6 |
| Queue pressure reason | queue_backlog_threshold_exceeded |
| Parsed `tegrastats` samples | 281 |
| Max temperature | 50.375 C |
| Max RAM used | 1038 MB |
| Vision mean latency | 152.77 ms |
| Vision p95 latency | 156.948 ms |

## Evidence chain 해석

```text
Jetson 5-minute-class device-local starter
-> Orchestrator sustained queue/drop/fallback evidence
-> EdgeEnv runtime_operation_summary preservation
-> AIGuard deterministic runtime reliability warning evidence
-> Lab-owned blocked deployment decision
```

이 run은 5-minute-class smoke/starter evidence입니다. Vision workload가
latency budget을 넘고, queue backlog가 긴 구간에서 반복적으로
drop/fallback policy를 발생시키며, 그 context가 Lab report까지 보존되는지
확인합니다.

## Lab deployment decision

| Field | Value |
|---|---|
| policy_version | `inferedge-lab-agent-runtime-policy-v1` |
| decision | `blocked` |
| reason | Agent runtime reliability evidence indicates blocked deployment risk. |

Lab-owned deployment decision은 InferEdgeLab이 소유합니다. Orchestrator와
AIGuard는 각각 operation context와 deterministic evidence를 제공하지만,
최종 deployment policy owner가 아닙니다.

## 주장하지 않는 것

- decoded YOLO accuracy validation
- live camera operation
- Whisper/FastAPI service execution
- production remote execution
- sustained thermal endurance validation
- production worker daemon
- production observability platform
- Kubernetes-style orchestration

## Jetson 필요 여부

이 문서를 읽거나 링크를 검증하는 작업에는 Jetson 기기가 필요 없습니다.
새로운 5-minute-class replay, live `tegrastats` capture, SSH readiness
preflight를 수행할 때만 Jetson 기기가 필요합니다.
