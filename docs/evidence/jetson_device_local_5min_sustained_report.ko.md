# Jetson Device-Local 5-Minute Sustained Smoke Report 한국어 Quick Guide

언어: [English](jetson_device_local_5min_sustained_report.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[Jetson Device-Local 5-Minute Sustained Smoke Report](jetson_device_local_5min_sustained_report.md)입니다.

이 report는 Jetson device-local starter를 5-minute-class로 반복 실행한
runtime-operation evidence 요약입니다. 목적은 장시간 production service를
증명하는 것이 아니라, device-local overload 상황의 queue/drop/fallback,
telemetry, EdgeEnv preservation, AIGuard warning, Lab-owned deployment
decision 흐름을 재현하는 것입니다.

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
