# Reliable Edge Agent Runtime E2E Demo 한국어 Quick Guide

언어: [English](agent_runtime_e2e_demo.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[Reliable Edge Agent Runtime E2E Demo](agent_runtime_e2e_demo.md)입니다.

이 demo는 InferEdge ecosystem에서 agent runtime operation evidence가 어떻게
전달되는지 확인하는 local-first file-based smoke입니다. production orchestration
service, cloud dashboard, general AI OS가 아닙니다.

## 무엇을 검증하는가

```text
Forge agent_manifest
-> Runtime result.agent
-> Orchestrator orchestration_summary
-> AIGuard guard_analysis
-> Lab agent-runtime-report
```

Lab은 report와 deployment decision owner입니다. Orchestrator는 operation
context provider이고, AIGuard는 deterministic evidence provider이며, EdgeEnv는
local run evidence / comparability / registry context를 보존합니다.

## 실행 경로 선택

| 목적 | 명령 | Jetson 필요 여부 | 의미 |
|---|---|---|---|
| 기본 agent runtime chain 확인 | `bash scripts/demo_agent_runtime_e2e.sh` | 필요 없음 | committed fixture 기반 e2e bundle 생성 |
| device-local starter 확인 | `bash scripts/demo_agent_runtime_e2e.sh --device-local` | 필요 없음 | Orchestrator `scenario_mode=device_local` 경로 확인 |
| local input override 확인 | `bash scripts/demo_agent_runtime_e2e.sh --device-local --vision-input <path> --voice-ingress-payload <path> --capture-process-resource-snapshot` | 필요 없음 | local image/request/resource input이 chain을 통과하는지 확인 |
| ONNX probe 추가 | `bash scripts/demo_agent_runtime_e2e.sh --device-local --vision-input <path> --vision-onnx-model <path>` | 필요 없음, Jetson에서도 가능 | lightweight Vision producer probe evidence 생성 |
| remote dispatch starter 확인 | `bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch` | 필요 없음 | file-based worker selection evidence 생성 |
| HTTP/SSH starter 실행 요청 | `bash scripts/demo_agent_runtime_e2e.sh --remote-dispatch --remote-execute-plan` | 필요 없음 | 지원 registry entry가 있을 때 starter execution status 기록 |
| EdgeEnv registry preservation 확인 | `bash scripts/demo_agent_runtime_e2e.sh --device-local --edgeenv-run-evidence` | 필요 없음 | `08_edgeenv_run_show.json`, local runs DB 생성 |
| Jetson live `tegrastats` capture | `bash scripts/demo_agent_runtime_e2e.sh --device-local --vision-input <path> --vision-onnx-model <path> --capture-tegrastats` | 필요함 | live Jetson telemetry handoff smoke |
| 5-minute-class Jetson convenience runner | `bash scripts/demo_jetson_5min_sustained.sh` | 필요함 | longer device-local starter smoke 재현 |
| Jetson readiness preflight | `bash scripts/check_jetson_sustained_readiness.sh` | 필요함 | SSH, `tegrastats`, input path 준비 상태 확인. evidence 생성 안 함 |

## 주요 output

| Output | 용도 |
|---|---|
| `00_evidence_index.json` / `.md` | generated bundle navigation index. `Reviewer operation quick scan`, `lab_expected_report_markers`, `lab_report_contract_context` 같은 Lab report marker contract를 reviewer navigation context로 보존 |
| `01_forge_agent_manifest_vision.json` | Forge agent manifest handoff example |
| `02_runtime_result_agent.json` | Runtime result with backward-compatible `agent` block |
| `03_orchestration_summary.json` | Orchestrator scheduling / queue / policy evidence |
| `04_aiguard_guard_analysis.json` / `.md` | deterministic runtime reliability evidence |
| `05_lab_agent_runtime_report.json` / `.md` | Lab-owned deployment decision context |
| `06_remote_dispatch_result.json` | optional remote worker selection evidence |
| `07_remote_dispatch_guard_analysis.json` / `.md` | optional AIGuard diagnosis for remote dispatch starter |
| `08_edgeenv_run_show.json` | optional EdgeEnv run evidence |
| `08_edgeenv/.edgeenv/runs.db` | optional EdgeEnv local registry |

## Runtime Intelligence artifact smoke와의 차이

| Gate | 용도 | 하지 않는 것 |
|---|---|---|
| Agent runtime operation smoke | generated operation scenario bundle에서 manifest, Runtime result, Orchestrator, AIGuard, Lab report 연결을 확인 | Runtime regression comparability나 CI artifact bundle completeness를 검증하지 않음 |
| Runtime Intelligence artifact smoke | committed Orchestrator -> EdgeEnv -> AIGuard -> Lab bundle의 report rows, owner boundary, CI artifact shape를 검증 | production observability, GitLab control plane, live remote execution을 증명하지 않음 |

둘 다 local-first smoke입니다. Orchestrator나 AIGuard가 final deployment
decision owner가 되지 않습니다.

## Jetson evidence 해석

Jetson 경로는 실제 device-local starter evidence와 telemetry handoff를 보여줍니다.
하지만 아래를 의미하지 않습니다.

- decoded YOLO accuracy validation
- live camera operation
- Whisper/FastAPI service execution
- production remote execution
- sustained thermal endurance validation

Jetson 작업이 필요한 경우는 `--capture-tegrastats`,
`demo_jetson_5min_sustained.sh`, `check_jetson_sustained_readiness.sh`처럼
실제 device telemetry 또는 SSH/device-local input 상태를 확인해야 하는 경로입니다.

## Scope Boundary

포함:

- Vision / Voice-Command / Safety-Monitor workload contracts
- queue/drop/fallback/deadline signal propagation
- local fixture producer replay
- optional device-local input override
- optional remote dispatch starter evidence
- optional EdgeEnv local run registry evidence
- AIGuard runtime reliability interpretation
- Lab-owned report and deployment decision context

포함하지 않음:

- production SaaS infrastructure
- DB/queue persistence
- cloud orchestration
- production remote worker execution
- secure tunnel operation
- LLM agent framework
- universal AI OS claims

세부 command와 최신 Jetson evidence record는
[Reliable Edge Agent Runtime E2E Demo](agent_runtime_e2e_demo.md)를 기준으로 확인하세요.
