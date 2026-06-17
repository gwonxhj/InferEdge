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
| Remote fallback registry marker smoke | `bash scripts/smoke_remote_fallback_registry_marker.sh`로 fixture-only remote fallback bundle을 만들고 `Remote fallback starter evidence`, `Duration source`, `Duration scope label`, `source=entrypoint_requested_frames`, `Duration Sources`를 확인 | fallback starter가 entrypoint-requested replay scope에 묶여 있음을 보존하며 production remote execution이나 live runtime duration claim을 증명하지 않음 |
| Operation quick-scan registry smoke | `bash scripts/smoke_quick_scan_registry_summary.sh`로 fixture-only device-local preservation bundle을 registry까지 재생성하고 `Operation Quick Scan Summary`, `Reviewer operation quick scan`, queue/deadline/fallback marker를 확인 | live Jetson 실행, thermal endurance validation, production scheduling, Lab ownership 이전을 증명하지 않음 |

Runtime Intelligence smoke는 configured output directory 아래에 다음
reviewer-facing artifact를 같은 순서로 기록합니다.

| Artifact | 용도 |
|---|---|
| EdgeEnv `examples/regression/fixture_matrix.json` | Lab smoke 전에 sibling EdgeEnv repo의 same-condition, runtime-comparison, target-comparison, protocol-mismatch, telemetry-gap, replay-sequence fixture role이 유지되는지 확인 |
| `runtime_intelligence_bundle_manifest_gate_summary.md` | committed bundle manifest, EdgeEnv handoff alignment, artifact role, owner boundary, source repository mapping 확인 |
| `edgeenv_runtime_regression.md` / `edgeenv_runtime_regression.html` | AIGuard enrichment 전의 same-condition EdgeEnv runtime regression evidence 확인 |
| `runtime_anomaly_summary.md` / `runtime_anomaly_summary.html` | EdgeEnv regression, AIGuard deterministic runtime evidence, telemetry coverage, `Operation quick scan`, `operation_risk_summary`, remote-dispatch boundary row를 포함한 Lab-owned Runtime Intelligence Risk Summary 확인 |
| `runtime_anomaly_gate_summary.md` | generated Markdown/HTML report가 Runtime Intelligence row, Lab ownership wording, `Validated Duration Traceability`, `Validated Reviewer Focus`, `Validated Review Path`를 유지하는지 확인 |
| `runtime_intelligence_ci_artifact_gate_summary.md` | optional CI artifact bundle shape와 복사된 `Validated Reviewer Focus` / `Validated Review Path` marker를 확인하되 CI를 production control plane으로 만들지 않음 |
| `aiguard_edgeenv_handoff_alignment.json` / `aiguard_edgeenv_handoff_alignment.md` | smoke에서 사용하는 precomputed AIGuard/EdgeEnv handoff alignment fixture 보존 |

`Validated Review Path` gate summary의 세부 marker vocabulary는 README가
아니라 이 문서에 보존합니다. 더 넓은 Runtime Intelligence report gate가
요구하는 duration / reviewer-focus marker도 여기에 함께 보존합니다.

- `Validated Duration Traceability`
- `duration_handoff_alignment: EdgeEnv/AIGuard report context preserved`
- `duration_source: source=entrypoint_requested_frames`
- `duration_scope_label: scope_label=source=entrypoint_requested_frames`
- `duration_label: short 96-frame-class replay (96 frames)`
- `Validated Reviewer Focus`
- `reviewer_focus_operation_quick_scan: Reviewer Focus / Operation quick scan marker validated`
- `reviewer_focus_operation_quick_scan_raw_marker: raw marker preserved in Lab report`

현재 필수 review-path marker는 다음입니다.

- `review_path_section: short Review Path section rendered`
- `review_path_fast_path: readable Review Path fast path rendered`
- `review_path: Reviewer Focus -> Detailed Evidence Rows guidance validated`
- `review_path_scope: comparable regression / telemetry replay / operation evidence preserved`
- `review_path_artifact_gate_summary: artifact gate summary reference row validated`

세 gate 모두 local-first smoke입니다. Orchestrator나 AIGuard가 final deployment
decision owner가 되지 않습니다.
`smoke_quick_scan_registry_summary.sh` 역시 Jetson이 필요 없는 fixture-only
gate이며, reviewer navigation metadata와 Lab-owner boundary wording이 registry에
남는지만 좁게 확인합니다.

`scripts/smoke_all.sh`는 Lab report summary, 복사된 CI artifact summary,
generated `00_evidence_index.*` artifact가 같은 reviewer marker vocabulary를
보존하는지 공통 marker list로 확인합니다. 즉 duration traceability,
reviewer-focus, EdgeEnv preservation, operation quick-scan marker가 Lab report와
entrypoint evidence index 사이에서 어긋나지 않아야 합니다. JSON/Markdown
format-specific label은 분리하지만, 공통 marker vocabulary는 drift되면 안 됩니다.

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
`Validated Reviewer Focus`, `reviewer_focus_operation_quick_scan`,
`review_path_fast_path` marker가
확인되었습니다. 이는 환경 선택 메모이며 contract 변경이 아닙니다.

상위 `scripts/smoke_all.sh`는 Lab smoke 전에 InferEdgeEnv
`examples/regression/fixture_matrix.json`도 확인합니다. 이 gate는
same-condition, runtime-comparison, target-comparison, protocol-mismatch,
telemetry-gap, replay-sequence fixture role이 유지되는지 검증하며,
production monitoring이나 Lab deployment decision ownership을 의미하지
않습니다.

Jetson entrypoint checkout을 `c04abc9`로 동기화한 뒤, 최신 96-frame
device-local bundle과 2026-06-09 KST (`20260609T122600Z` UTC)에 확인한
5-minute-class Jetson replay를 하나의 registry로 묶었습니다. 이 기록은
최신 reviewer-focus marker gate, 공통 `operation_summary` label vocabulary,
3600-frame sustained smoke를 같은 navigation registry에서 비교하게 해, 각
full report를 열기 전에 duration / operation context를 확인할 수 있게
합니다.

| 항목 | 값 |
|---|---:|
| Entrypoint commit | `c04abc9` |
| Lab commit | `3a7a464` |
| 96-frame bundle | `/tmp/inferedge_agent_runtime_jetson_96_operation_summary_latest_20260609T122600Z` |
| 5-minute-class bundle | `/tmp/inferedge_agent_runtime_jetson_sustained_5min_operation_summary_latest_20260609T121700Z` |
| Registry Markdown | `/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.md` |
| Registry JSON | `/tmp/inferedge_agent_runtime_jetson_operation_summary_duration_registry_20260609T122600Z.json` |
| Duration rows | `short 96-frame-class replay (96 frames)` / `5-minute-class sustained replay (3600 frames)` |
| 연결된 metric snapshot | `96-frame: 155.86 ms mean / 156.877 ms p95, max 45.5 C / 1000 MB RAM`; `5-minute-class: 152.77 ms mean / 156.948 ms p95, max 50.375 C / 1038 MB RAM` |
| 96-frame queue/drop/fallback/deadline | `6 / 93 / 93 / 50` |
| 5-minute queue/drop/fallback/deadline | `6 / 3597 / 3597 / 1802` |
| Parsed `tegrastats` samples | `10` / `281` |
| Device-local / producer events | `99 / 99` / `3603 / 3603` |
| EdgeEnv run IDs | `run-20260609-122450-a262b037`, `run-20260609-122009-c17a030b` |
| Lab preservation registry cell | `lab_preservation=present`, `lab_context=present` |
| Operation summary labels | `operation_summary: mode=device_local_starter` / `operation_summary: mode=timeout_threshold_exceeded` |
| Operation quick-scan registry section | `## Runs` 앞의 `Operation Quick Scan Summary` |
| Operation quick-scan summary row | `queue=...`, `depth=...`, `deadline_miss=...`, `fallback=...`, `preservation=...` |
| AIGuard / Lab status | 두 row 모두 `blocked/high`, `blocked` |

연결된 metric snapshot row는 reviewer navigation을 위해 short/sustained
Jetson evidence report의 값을 복사한 것이며, metric record의 소유권은 해당
report에 남아 있습니다.

연결된 Jetson evidence report에서 사용하는 용어 기준:

| 용어 | 의미 | 경계 |
|---|---|---|
| Representative snapshot | 특정 run class의 metric과 Lab-owned decision context를 보존하는 submission-facing Markdown/HTML report | 최신 registry가 snapshot의 metric record를 대체하지 않음 |
| Latest registry | 생성된 `00_evidence_index.*` 파일에서 다시 만든 최신 local run-navigation 기록 | registry row는 Lab report owner, EdgeEnv comparability gate, deployment decision이 아님 |
| Quick-scan navigation | duration과 queue/deadline/fallback pressure를 빠르게 보는 `Duration Comparison Summary`, `Operation Quick Scan Summary` row | reviewer navigation metadata일 뿐 production runtime operation proof가 아님 |

이 registry는 local-first reviewer navigation artifact입니다. short replay와
5-minute-class replay를 duration metadata로 분리해 보여주지만, 둘 다
Smoke/Starter evidence이며 thermal endurance validation이나 production
runtime operation proof로 격상하지 않습니다. `Duration Comparison Summary`와
`Operation Quick Scan Summary` table은 reviewer navigation 용도로 duration,
compact queue/deadline/fallback, `operation_summary`, preservation label만
먼저 보여주며, registry가 Lab report owner가 되는 것은 아닙니다. raw
`Reviewer operation quick scan` marker context는 detailed `## Runs` table과
registry JSON에 계속 보존되므로, source contract를 바꾸지 않고 Lab report
gate marker까지 추적할 수 있습니다. 그래서 각 bundle을 열기 전에
queue/deadline/fallback pressure를 먼저 식별할 수 있습니다.
fixture-only quick-scan smoke는 이 분리를 강제합니다.
`raw_marker=reviewer_focus_operation_quick_scan` 같은 raw marker label은
compact `Operation Quick Scan Summary`에 새면 안 되고, detailed `## Runs`
table과 registry JSON의 `Raw Marker`, `Raw Marker Label`,
`edgeenv_lab_report_operation_quick_scan_raw_marker`,
`edgeenv_lab_report_operation_quick_scan_raw_marker_label`에 남아야 합니다.

Historical reference: 이전 Jetson duration registry는 entrypoint commit
`d38df87` 기준으로
`/tmp/inferedge_agent_runtime_jetson_reviewer_focus_96_20260608T232814Z`와
`/tmp/inferedge_agent_runtime_jetson_sustained_5min_reviewer_focus_20260609T001057Z`를
묶고,
`/tmp/inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.md`
/
`/tmp/inferedge_agent_runtime_jetson_reviewer_focus_duration_registry_20260609T001057Z.json`을
생성했습니다. 이 registry는 EdgeEnv run ID
`run-20260608-232827-e584af13`, `run-20260609-001553-51217d1d`와 5-minute row
`6 / 3597 / 3597 / 1802`, parsed `tegrastats` samples `281`을 보존한
historical marker-preservation reference입니다. 최신 operation-summary
duration record는 위의 `c04abc9` registry입니다.

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
