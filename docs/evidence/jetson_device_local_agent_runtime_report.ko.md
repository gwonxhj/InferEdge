# Jetson Device-Local Agent Runtime Evidence Report 한국어 Quick Guide

언어: [English](jetson_device_local_agent_runtime_report.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[Jetson Device-Local Agent Runtime Evidence Report](jetson_device_local_agent_runtime_report.md)입니다.

이 report는 clean Jetson replay runbook으로 생성된 Lab report의
submission-facing 요약입니다. 목적은 Jetson device-local starter에서
Orchestrator -> EdgeEnv -> AIGuard -> Lab evidence chain이 보존되는지
보여주는 것입니다.

## Scope

| 항목 | 값 |
|---|---|
| Device | Jetson Orin Nano 25W |
| Scenario | `device_local` |
| Model | user-provided `yolov8n.onnx` |
| Vision backend | ONNX Runtime `CPUExecutionProvider` |
| Telemetry | Orchestrator run 중 live `tegrastats` capture |
| Replay length | 96 frames |
| Evidence index duration label | `short 96-frame-class replay (96 frames)` |
| EdgeEnv run ID | `run-20260531-102243-4afc19d6` |

## 핵심 수치

| Metric | Value |
|---|---:|
| Executed count | 99 |
| Dropped count | 93 |
| Fallback count | 93 |
| Deadline missed count | 50 |
| Max queue depth | 6 |
| Queue pressure state | overloaded |
| Policy decision reason | queue_backlog_threshold_exceeded |
| Parsed `tegrastats` samples | 9 |
| Max temperature | 45.5 C |
| Max RAM used | 1000 MB |
| Vision mean latency | 155.86 ms |
| Vision p95 latency | 156.877 ms |

## Evidence chain 해석

```text
Jetson device-local starter
-> Orchestrator queue/drop/fallback operation evidence
-> EdgeEnv local registry preservation
-> AIGuard deterministic runtime reliability evidence
-> Lab-owned deployment decision
```

이 run은 성공 benchmark만 보여주기 위한 기록이 아닙니다. Vision workload가
latency budget을 넘고 queue backlog가 drop/fallback을 반복해서 발생시키는
unsafe runtime condition을 Lab report까지 전달하는지 확인하는 evidence입니다.

## Lab deployment decision

| Field | Value |
|---|---|
| policy_version | `inferedge-lab-agent-runtime-policy-v1` |
| decision | `blocked` |
| reason | Agent runtime reliability evidence indicates blocked deployment risk. |

Lab-owned deployment decision은 InferEdgeLab이 소유합니다. Orchestrator는
operation context를 제공하고, AIGuard는 deterministic warning evidence를
제공하며, EdgeEnv는 registry / preservation context를 보존합니다.

## 주장하지 않는 것

- decoded YOLO accuracy validation
- live camera operation
- Whisper/FastAPI service execution
- production remote execution
- sustained thermal endurance validation
- production observability platform
- Kubernetes-style orchestration

## Jetson 필요 여부

이 문서를 읽거나 링크를 검증하는 작업에는 Jetson 기기가 필요 없습니다.
새로운 live `tegrastats` capture나 repeat device-local replay를 수행할 때만
Jetson 기기가 필요합니다.
