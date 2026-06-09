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
| `00_evidence_index.json` / `.md` | generated bundle navigation index. `Operation quick scan`, `Reviewer operation quick scan`, `Validated Reviewer Focus`, `reviewer_focus_operation_quick_scan`, `lab_expected_report_markers`, `lab_report_contract_context` 같은 Lab report marker contract를 reviewer navigation context로 보존 |
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
| Operation quick-scan registry smoke | `bash scripts/smoke_quick_scan_registry_summary.sh`로 fixture-only device-local preservation bundle을 registry까지 재생성하고 `Operation Quick Scan Summary`, `Reviewer operation quick scan`, queue/deadline/fallback marker를 확인 | live Jetson 실행, thermal endurance validation, production scheduling, Lab ownership 이전을 증명하지 않음 |

세 gate 모두 local-first smoke입니다. Orchestrator나 AIGuard가 final deployment
decision owner가 되지 않습니다.
`smoke_quick_scan_registry_summary.sh` 역시 Jetson이 필요 없는 fixture-only
gate이며, reviewer navigation metadata와 Lab-owner boundary wording이 registry에
남는지만 좁게 확인합니다.

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

## 최근 Jetson quick-scan marker 재현

2026-06-08에 같은 96-frame device-local EdgeEnv preservation 경로를 Jetson에서
다시 실행했습니다. 목적은 새 성능 수치 갱신이 아니라, `00_evidence_index.*`
안에 Lab report marker contract가 live device-local bundle에서도 보존되는지
확인하는 것입니다.

| 항목 | 값 |
|---|---:|
| Output bundle | `/tmp/inferedge_agent_runtime_jetson_quick_scan_96_20260608T105418Z` |
| Entrypoint commit | `16a2ef0` |
| Operation path | `device_local_starter` |
| Reviewer operation marker | `Reviewer operation quick scan` |
| Quick-scan label | `queue_pressure_reason=queue_backlog_threshold_exceeded; max_total_queue_depth=6; deadline_missed_count=50; fallback_count=93` |
| Report marker context | `lab_report_contract_context` |
| AIGuard marker ownership | `aiguard_validates_expected_report_markers=false` |
| Frames | 96 |
| Duration label | `short 96-frame-class replay (96 frames)` |
| EdgeEnv run ID | `run-20260608-105430-f8841ef4` |
| Lab preservation section | present |
| AIGuard verdict | `blocked` / `high` |
| Lab decision | `blocked` |

이 기록은 reviewer navigation marker 보존 smoke입니다. Lab final decision
ownership, EdgeEnv comparability ownership, AIGuard deterministic diagnosis
ownership을 바꾸지 않으며, device-local starter를 production operation으로
격상하지 않습니다.

2026-06-09 KST (`20260608T232814Z` UTC)에 entrypoint가 Lab의
`Validated Reviewer Focus` summary marker를 gate하기 시작한 뒤 같은 경로를
한 번 더 확인했습니다. 이 재검증은 기존 5-minute-class evidence를 대체하지
않고, 현재 Jetson checkout과 현재 Lab Runtime Intelligence artifact gate가
reviewer-facing quick-scan marker를 보존하는지 확인하는 기록입니다.

| 항목 | Jetson reviewer-focus validation |
|---|---:|
| Readiness preflight | `--edgeenv-run-evidence` 기준 `passed` |
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

첫 Lab smoke는 Jetson system `python3`에 `typer`가 없어 실패했습니다.
같은 smoke를 `PATH=$HOME/miniconda3/envs/yolo_env/bin:$PATH`로 재실행하면
통과했고, `runtime_anomaly_gate_summary.md`와
`runtime_intelligence_ci_artifact_gate_summary.md` 양쪽에서
`Validated Reviewer Focus`와 `reviewer_focus_operation_quick_scan` marker가
확인되었습니다. 이는 환경 선택 메모이며 contract 변경이 아닙니다.

Jetson entrypoint checkout을 `d38df87`로 동기화한 뒤, 96-frame
reviewer-focus bundle과 2026-06-09 KST (`20260609T001057Z` UTC)에 새로
생성한 5-minute-class Jetson replay를 하나의 registry로 묶었습니다. 이
기록은 최신 reviewer-focus marker gate와 최신 3600-frame sustained smoke를
같은 navigation registry에서 비교하게 해, 각 full report를 열기 전에
duration / operation context를 확인할 수 있게 합니다.

| 항목 | 값 |
|---|---:|
| Entrypoint commit | `d38df87` |
| Lab commit | `3a7a464` |
| 96-frame bundle | `/tmp/inferedge_agent_runtime_jetson_reviewer_focus_96_20260608T232814Z` |
| 5-minute-class bundle | `/tmp/inferedge_agent_runtime_jetson_sustained_5min_reviewer_focus_20260609T001057Z` |
| Registry Markdown | `/tmp/inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.md` |
| Registry JSON | `/tmp/inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.json` |
| Duration rows | `short 96-frame-class replay (96 frames)` / `5-minute-class sustained replay (3600 frames)` |
| 96-frame queue/drop/fallback/deadline | `6 / 93 / 93 / 50` |
| 5-minute queue/drop/fallback/deadline | `6 / 3597 / 3597 / 1802` |
| Parsed `tegrastats` samples | `9` / `281` |
| Device-local / producer events | `99 / 99` / `3603 / 3603` |
| EdgeEnv run IDs | `run-20260608-232827-e584af13`, `run-20260609-001553-51217d1d` |
| Lab preservation registry cell | `lab_preservation=present`, `lab_context=present` |
| Operation quick-scan registry section | `## Runs` 앞의 `Operation Quick Scan Summary` |
| Operation quick-scan registry column | `Reviewer operation quick scan: queue_pressure_reason=...; max_total_queue_depth=...; deadline_missed_count=...; fallback_count=...` |
| AIGuard / Lab status | 두 row 모두 `blocked/high`, `blocked` |

이 registry는 local-first reviewer navigation artifact입니다. short replay와
5-minute-class replay를 duration metadata로 분리해 보여주지만, 둘 다
Smoke/Starter evidence이며 thermal endurance validation이나 production
runtime operation proof로 격상하지 않습니다. `Operation Quick Scan` column은
각 run의 EdgeEnv summary에 보존된 Lab report marker context를 reviewer
navigation 용도로만 보여주며, registry가 Lab report owner가 되는 것은
아닙니다. 재생성된 Markdown registry는 두 row 모두에서
`Operation Quick Scan Summary`를 full `## Runs` table보다 먼저 보여주고,
긴 EdgeEnv cell 앞의 `Operation Quick Scan` column에도 같은 compact label을
유지합니다. 또한 사람이 읽는 `Reviewer operation quick scan` label 옆에
raw `reviewer_focus_operation_quick_scan` marker와
`raw_marker=reviewer_focus_operation_quick_scan` label을 JSON과 Markdown에
함께 보존하므로, source contract를 바꾸지 않고 Lab report gate marker까지
추적할 수 있습니다. 그래서 각 bundle을 열기 전에 queue/deadline/fallback
pressure를 먼저 식별할 수 있습니다.

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
