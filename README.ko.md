# InferEdge

언어: [English](README.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표 README와 가장 최신 상세 설명은
[English README](README.md)를 기준으로 유지합니다.

InferEdge는 Edge AI 모델을 단순 benchmark 숫자로만 비교하지 않고, build
provenance, 실제 Runtime 실행 결과, validation evidence, optional deterministic
diagnosis, Lab-owned deployment decision을 하나의 local-first 검증 흐름으로
연결하는 multi-repository entrypoint입니다.

핵심 메시지:

| 항목 | 현재 evidence |
|---|---|
| 배포 검증 흐름 | Forge -> Runtime -> Lab -> optional AIGuard |
| 비교 가능성 계층 | EdgeEnv local registry / comparability / runtime regression evidence |
| 운영 계층 | Orchestrator queue/deadline/fallback, worker-health evidence |
| Jetson TensorRT 실측 | YOLOv8n TensorRT FP16: 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| CPU baseline | ONNX Runtime CPU: 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 155.86 ms mean, 156.877 ms p95, 45.5 C, 1000 MB RAM |
| Jetson 5분급 sustained replay | 3600 frames, 152.77 ms mean, 156.948 ms p95, 50.375 C, 1038 MB RAM |

## Quick Start

```bash
git clone https://github.com/gwonxhj/InferEdge.git
cd InferEdge
bash scripts/clone_all.sh --locked
bash scripts/smoke_all.sh
```

`scripts/smoke_all.sh`는 Forge, Runtime, Lab, AIGuard, Orchestrator, Env를
묶어 Core 4와 Runtime Intelligence artifact gate를 함께 확인합니다. 이는
reviewer-facing evidence와 contract boundary 검증이며, production observability
platform 또는 GitLab control plane이 아닙니다.

`bash scripts/smoke_quick_scan_registry_summary.sh`는 Jetson 없이 committed
fixture만으로 `Operation Quick Scan Summary` registry marker와
`Reviewer operation quick scan` navigation row를 확인하는 좁은 gate입니다.

review branch publish 전에는 아래 helper로 원격 상태를 확인합니다.

```bash
bash scripts/check_publish_ready.sh
```

[Publish InferEdge Entrypoint](docs/publish_inferedge.md)는
non-fast-forward와 unrelated-history 차단 상태, branch publish + PR 생성 +
PR merge를 한 단계로 묶는 기준, PR changed-file/status gate, PR `Summary` /
`Tests` 기록, 최종 상태 확인, local checkout safety, stale-main에서 정상 repo
파일이 untracked처럼 보이는 경우의 복구 기준, optional branch cleanup,
diagnostic escape-hatch flag 경계를 설명합니다.
기존 public `main` history 위에 force push하지 않습니다.

## 핵심 흐름

```text
ONNX Model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report
-> Local Studio
```

Runtime Intelligence / Operation 확장은 기존 validation pipeline을 대체하지
않고 아래처럼 evidence를 더 깊게 연결합니다.

```text
InferEdgeOrchestrator operation context
-> InferEdgeEnv registry / comparability / regression evidence
-> optional InferEdgeAIGuard deterministic evidence
-> InferEdgeLab Runtime Intelligence Risk Summary
-> Lab-owned deployment decision
```

## 레포 역할

| 레포 | 역할 |
|---|---|
| [InferEdgeForge](https://github.com/gwonxhj/InferEdgeForge) | build provenance, metadata, manifest, artifact handoff |
| [InferEdge-Runtime](https://github.com/gwonxhj/InferEdge-Runtime) | C++ inference execution, Lab-compatible `result.json`, Jetson/runtime evidence |
| [InferEdgeLab](https://github.com/gwonxhj/InferEdgeLab) | compare, evaluate, report, API, Local Studio, deployment decision owner |
| [InferEdgeAIGuard](https://github.com/gwonxhj/InferEdgeAIGuard) | optional deterministic diagnosis evidence provider |
| [InferEdgeEnv](https://github.com/gwonxhj/InferEdgeEnv) | local run evidence registry, comparability checker, runtime regression owner |
| [InferEdgeOrchestrator](https://github.com/gwonxhj/InferEdgeOrchestrator) | runtime operation context provider, queue/deadline/fallback evidence |

## 실측 evidence 스냅샷

| Evidence | 현재 기록 |
|---|---|
| TensorRT Jetson FP16 | mean 10.066401 ms, p99 15.548438 ms, 99.340373 FPS |
| ONNX Runtime CPU baseline | mean 45.4299 ms, p99 49.2128 ms, 22.0119 FPS |
| TensorRT speedup | ONNX Runtime CPU 대비 약 4.51x FPS |
| YOLOv8 subset validation | 10 images, 89 boxes, simplified mAP@50 0.1410 |
| Jetson device-local replay | 96 frames, 155.86 ms mean, 156.877 ms p95, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class sustained replay | 3600 frames, Vision mean 152.77 ms, p95 156.948 ms, max 50.375 C / 1038 MB RAM |
| Jetson operation-summary quick-scan registry | 최신 `c04abc9` 96-frame / 5-minute rows, 연결된 metric snapshot(`155.86` / `156.877` ms, `45.5 C` / `1000 MB`; `152.77` / `156.948` ms, `50.375 C` / `1038 MB`), `Duration Comparison Summary`, `Operation Quick Scan Summary`, `operation_summary` label, Lab preservation context. [최근 Jetson quick-scan marker 재현](docs/agent_runtime_e2e_demo.ko.md#최근-jetson-quick-scan-marker-재현) |

세부 evidence는 [English README](README.md)의 Evidence Snapshot과
`docs/evidence/` 문서를 기준으로 확인하세요. Jetson 기록만 빠르게 확인하려면
[Jetson 디바이스 로컬 evidence quick guide](docs/evidence/jetson_device_local_agent_runtime_report.ko.md)와
[Jetson 5분급 sustained evidence quick guide](docs/evidence/jetson_device_local_5min_sustained_report.ko.md)를
먼저 보면 됩니다. 대표 스냅샷 HTML은
[Jetson 5-minute-class snapshot HTML report](docs/evidence/jetson_device_local_5min_sustained_report.html)에서
확인할 수 있습니다.

## Cross-Repo Role Boundary Snapshot

아래 표는 reviewer가 각 레포의 ownership을 빠르게 확인하기 위한 기준입니다.
세부 표는 [InferEdge 생태계 1페이지 요약](docs/ecosystem_1page.ko.md)과
[파이프라인 맵](docs/pipeline_map.ko.md)에 있습니다. InferEdge를 production SaaS,
cloud control plane, generic monitoring stack처럼 설명하지 않기 위한 경계입니다.

| Project | Canonical owner role | 소유하는 evidence | 소유하지 않는 것 |
|---|---|---|---|
| InferEdgeForge | build provenance / handoff owner | `metadata.json`, `manifest.json`, source/artifact identity, build summary | Runtime executor, scheduler, deployment decision owner |
| InferEdge-Runtime | execution / result evidence owner | Lab-compatible `result.json`, latency/FPS/backend/device context, runtime health and telemetry seed | artifact builder, registry, anomaly detector, scheduler, deployment decision owner |
| InferEdgeLab | validation report / deployment decision owner | compare/evaluate output, Markdown/HTML report, Local Studio, `deployment_decision` | build system, registry, deterministic diagnosis owner, scheduler, production dashboard |
| InferEdgeAIGuard | optional deterministic diagnosis evidence provider | `guard_analysis`, warning/review evidence, raw-context traceability | final deployment decision owner, LLM root-cause engine, production monitor |
| InferEdgeEnv | local evidence registry / comparability / runtime regression owner | run registry, replay bundle, comparability judgement, regression report | production DB, cloud telemetry store, deployment decision owner, general monitoring SaaS |
| InferEdgeOrchestrator | runtime operation context provider | queue/deadline/fallback evidence, worker health, remote-dispatch starter evidence | Kubernetes replacement, cloud orchestration platform, deployability decision owner, completed production scheduler |

## 현재 말할 수 있는 것

| 영역 | 상태 | reviewer signal |
|---|---|---|
| Core Forge -> Runtime -> Lab -> optional AIGuard validation pipeline | 구현됨 | build provenance, Runtime result, Lab compare/report/decision, AIGuard deterministic evidence 연결 |
| Local Studio demo evidence replay | 구현됨 | local-first evidence replay와 deployment decision 확인 |
| Runtime Intelligence artifact gate | 구현됨 | Cross-repo smoke로 `Orchestrator -> EdgeEnv -> AIGuard -> Lab` bundle marker, policy-pressure alignment, Jetson preservation, remote fallback Lab marker 검증 |
| Jetson/device-local smoke | Smoke/Starter | device-local ONNX probe와 live telemetry handoff 보존 |
| Remote dispatch / fallback starter | Smoke/Starter | file-based worker selection과 bounded fallback evidence |
| Cloudflare / dashboard / production worker services | Future Work | 문서화된 방향만 존재 |

## Runtime Intelligence 검토 경로

세부 marker vocabulary는 smoke gate와
[Agent Runtime E2E Demo](docs/agent_runtime_e2e_demo.ko.md)에 보존하고, README에서는
리뷰어가 먼저 열어볼 순서만 남깁니다.

Curated reviewer sample handoff:

- `examples/telemetry/agent_scheduler_delay_sample.json`은
  `scheduler_delay_pattern` AIGuard evidence path를 보여주는 Orchestrator
  sample input으로만 둡니다.
- `examples/telemetry/remote_fallback_recovery_sample.json`은
  `remote_execution_recovered_by_fallback` AIGuard evidence path를 보여주는
  Orchestrator sample input으로만 둡니다.

이 sample path들은 `Orchestrator -> EdgeEnv -> AIGuard -> Lab` handoff를
따라가기 위한 reviewer anchor입니다. Forge artifact, Runtime benchmark output,
Lab decision-policy input, production remote execution 완료 증거가 아닙니다.
현재 handoff gate는 Lab이 artifact를 소비하기 전에 EdgeEnv handoff context와
AIGuard `guard_analysis` raw context의 policy-pressure summary run ID가
일치하는지도 확인합니다.

| 단계 | 먼저 볼 것 | 의미 |
|---|---|---|
| 1 | `runtime_intelligence_bundle_manifest_gate_summary.md` | `Orchestrator -> EdgeEnv -> AIGuard -> Lab` bundle, owner boundary, policy-pressure handoff alignment가 유지되는지 확인 |
| 2 | EdgeEnv `examples/regression/fixture_matrix.json` | Lab이 evidence를 소비하기 전에 same-condition, runtime-comparison, target-comparison, protocol-mismatch, telemetry-gap, replay-sequence fixture coverage 확인 |
| 3 | `runtime_anomaly_summary.md` / `.html` | Lab-owned Runtime Intelligence Risk Summary, duration traceability, operation quick scan 확인 |
| 4 | Lab `Review Path` section과 `Validated Review Path` gate summary | README -> Lab report -> gate summary 순서를 reviewer가 그대로 따라가게 하되 CI, AIGuard, Orchestrator가 report owner처럼 보이지 않게 유지. 세부 marker vocabulary는 Agent Runtime E2E demo 문서에 둠 |
| 5 | generated registry의 `Operation Quick Scan Summary` | wide table을 열기 전 compact queue pressure, depth(`max_total_queue_depth`), deadline miss, fallback count, preservation label, aggregated `evidence_index_boundary_summary` 확인 |
| 6 | `00_evidence_index.md` / `.json` 및 detailed registry row | Jetson/device-local preservation context, `identity=jetson_device_local_preservation`, `lab_preservation=present`, `raw_marker=reviewer_focus_operation_quick_scan`이 navigation metadata로 남고 Lab report owner나 source contract가 되지 않는지 확인 |
| 7 | Remote fallback rows | `Remote fallback starter evidence`를 보존하되 production remote execution으로 해석하지 않음 |

공통 reviewer marker gate가 Lab report summary, 복사된 CI artifact summary,
generated `00_evidence_index.*` artifact를 어떻게 맞추는지는
[Agent Runtime E2E Demo](docs/agent_runtime_e2e_demo.ko.md)에 설명합니다.
README에는 세부 marker vocabulary를 늘리지 않고 검토 순서만 남깁니다.

## 중요한 경계

InferEdge는 현재 범위에서 다음을 완료 기능처럼 주장하지 않습니다.

- production SaaS dashboard
- production observability platform
- Kubernetes-style orchestration
- production remote execution / long-lived worker daemon
- general monitoring SaaS
- cloud control plane
- AIGuard 또는 Orchestrator의 최종 deployment decision ownership

최종 deployment decision owner는 InferEdgeLab입니다. AIGuard는 deterministic
evidence provider이고, Orchestrator는 operation context provider이며, EdgeEnv는
registry / comparability / regression evidence owner입니다.

## 먼저 볼 문서

| 문서 | 용도 |
|---|---|
| [InferEdge 생태계 1페이지 요약](docs/ecosystem_1page.ko.md) | ecosystem diagram과 layer split |
| [포트폴리오 요약](docs/portfolio_summary.ko.md) | 포트폴리오용 30초 요약 |
| [파이프라인 맵](docs/pipeline_map.ko.md) | 레포별 책임과 contract boundary |
| [Final Submission Rehearsal](docs/final_submission_rehearsal.md) | historical clean-clone rehearsal와 현재 reviewer delta; 최신 clean-clone 재실행 주장 아님 |
| [Publish InferEdge Entrypoint](docs/publish_inferedge.md) | 안전한 branch publish, PR 생성/merge, readiness check |
| [Agent Runtime E2E Demo](docs/agent_runtime_e2e_demo.ko.md) | Runtime Operation / Agent Runtime smoke 흐름과 공통 marker-gate 상세 owner |
| [최근 Jetson quick-scan marker 재현](docs/agent_runtime_e2e_demo.ko.md#최근-jetson-quick-scan-marker-재현) | 연결된 metric snapshot 값과 `Duration Comparison Summary`, `Operation Quick Scan Summary`, `operation_summary` label이 포함된 최신 registry |
| [인터뷰 내러티브](docs/interview_narrative.ko.md) | 면접/리뷰어 설명용 45초 답변과 deep-dive 질문 |
| [Jetson 디바이스 로컬 에이전트 런타임 증거 보고서](docs/evidence/jetson_device_local_agent_runtime_report.ko.md) | 현재 Jetson device-local replay evidence |
| [Jetson 디바이스 로컬 5분급 지속 스모크 보고서](docs/evidence/jetson_device_local_5min_sustained_report.ko.md), [대표 스냅샷 HTML 보고서](docs/evidence/jetson_device_local_5min_sustained_report.html) | 현재 Jetson 5-minute-class sustained evidence |

## Cross-Repo Quick Guide Path

한국어로 ecosystem을 검토할 때는 아래 순서로 보면 Validation -> Evidence ->
Operation Control 경계가 흐려지지 않습니다.

| 단계 | lifecycle 질문 | quick guide |
|---|---|---|
| 1 | artifact가 어떻게 만들어졌는가? | [Forge agent manifest contract](https://github.com/gwonxhj/InferEdgeForge/blob/main/docs/agent_manifest_contract.ko.md) |
| 2 | Runtime은 execution evidence를 어떻게 기록하는가? | [Runtime agent result contract](https://github.com/gwonxhj/InferEdge-Runtime/blob/main/docs/agent_runtime_result_contract.ko.md) |
| 3 | deployment decision은 누가 소유하는가? | [Lab Korean README](https://github.com/gwonxhj/InferEdgeLab/blob/main/README.ko.md) |
| 4 | deterministic diagnosis evidence는 무엇인가? | [AIGuard detector validation matrix](https://github.com/gwonxhj/InferEdgeAIGuard/blob/main/docs/detector_validation_matrix.ko.md) |
| 5 | benchmark evidence를 믿고 비교할 수 있는가? | [EdgeEnv runtime regression monitor](https://github.com/gwonxhj/InferEdgeEnv/blob/main/docs/ko/runtime-regression-monitor.md) |
| 6 | 배포된 workload가 부하 상황에서도 안정적인가? | [Orchestrator operation control guide](https://github.com/gwonxhj/InferEdgeOrchestrator/blob/main/docs/operation_control.ko.md) |

이 경로는 ownership을 바꾸지 않습니다. 최종 deployment decision owner는 Lab입니다.
EdgeEnv는 comparability/regression evidence, AIGuard는 deterministic diagnosis
evidence, Orchestrator는 runtime operation context를 소유합니다.

영어 README가 대표 문서이므로, 전체 명령어와 최신 세부 evidence는
[README.md](README.md)에서 확인하세요.
