# InferEdge 포트폴리오 요약

언어: [English](portfolio_summary.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Portfolio Summary](portfolio_summary.md)입니다.

InferEdge는 ONNX 모델을 traceable build artifact, real runtime evidence,
structured evaluation, optional deterministic diagnosis, Lab-owned deployment
decision으로 연결하는 local-first Edge AI inference validation pipeline입니다.

## 30초 구조

| 질문 | 담당 흐름 |
|---|---|
| 이 모델을 배포해도 되는가? | Forge -> Runtime -> Lab (+ optional AIGuard) |
| 이 benchmark evidence를 믿고 비교할 수 있는가? | InferEdgeEnv comparability layer |
| 배포된 workload가 부하 상황에서도 안정적인가? | InferEdgeOrchestrator operation layer |

## Evidence 스냅샷

| 항목 | 현재 기록 |
|---|---|
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS |
| Jetson device-local replay | 96 frames, 155.86 ms mean, max 45.5 C / 1000 MB RAM |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, max 50.375 C / 1038 MB RAM |
| Jetson operation quick-scan registry | 96-frame / 5-minute rows, `Operation Quick Scan Summary`, queue/deadline/fallback marker. [최근 Jetson quick-scan marker 재현](agent_runtime_e2e_demo.ko.md#최근-jetson-quick-scan-marker-재현) |

## 역할 분리

| Repository | 역할 | 경계 |
|---|---|---|
| InferEdge | multi-repo entrypoint와 clone/smoke map | 각 repo contract를 대체하지 않음 |
| InferEdgeForge | build provenance / artifact handoff | inference 실행이나 deployment decision을 소유하지 않음 |
| InferEdge-Runtime | C++ execution / result export | comparison policy를 소유하지 않음 |
| InferEdgeLab | validation / report / deployment decision | final decision owner |
| InferEdgeAIGuard | optional deterministic diagnosis evidence | final decision owner가 아님 |
| InferEdgeEnv | local evidence registry / comparability checker | deployability validation owner가 아님 |
| InferEdgeOrchestrator | runtime operation context provider | deployment decision owner가 아님 |

## 현재 강조할 수 있는 것

| 영역 | 상태 | 설명 |
|---|---|---|
| Core 4 validation pipeline | 구현됨 | build provenance, Runtime evidence, Lab decision, optional AIGuard evidence 연결 |
| Local Studio | 구현됨 | local-first evidence replay와 deployment decision 확인 |
| Runtime Intelligence artifact gate | 구현됨 | Orchestrator -> EdgeEnv -> AIGuard -> Lab evidence chain의 marker와 ownership boundary 검증 |
| Jetson/device-local smoke | Smoke/Starter | device-local ONNX probe와 live telemetry handoff 보존 |
| Remote dispatch/fallback | Smoke/Starter | file-based starter evidence이며 production remote execution이 아님 |
| Cloudflare / dashboard / production worker services | Future Work | 문서화된 방향만 존재 |

## Runtime Operation Starter Chain

```text
Orchestrator worker selection / fallback starter
-> EdgeEnv local registry and replay context
-> AIGuard deterministic warning evidence
-> Lab Runtime Intelligence / operation-risk report
-> Lab-owned deployment decision
```

이 chain의 가치는 production remote operation 주장이 아니라 repo별 책임 분리입니다.
Lab-owned deployment decision은 계속 InferEdgeLab이 소유합니다.

## Runtime Intelligence 검토 경로

세부 marker vocabulary는 smoke gate와 Agent Runtime demo 문서에 보존합니다.
포트폴리오 요약에서는 reviewer가 먼저 확인할 evidence path만 남깁니다.

| 리뷰 질문 | evidence path |
|---|---|
| evidence chain이 끝까지 이어지는가? | `runtime_intelligence_bundle_manifest_gate_summary.md`의 `Orchestrator -> EdgeEnv -> AIGuard -> Lab` bundle |
| report와 deployment decision은 Lab-owned인가? | `runtime_anomaly_summary.md` / `.html`의 Runtime Intelligence Risk Summary와 Lab decision context |
| operation pressure를 빠르게 볼 수 있는가? | `Operation Quick Scan Summary`, queue pressure, `max_total_queue_depth`, deadline miss, fallback count |
| Jetson/device-local context가 handoff 이후에도 남는가? | `00_evidence_index.*`, `lab_preservation=present`, `identity=jetson_device_local_preservation`, `raw_marker=reviewer_focus_operation_quick_scan` |
| remote fallback은 bounded starter evidence로 남는가? | `Remote fallback starter evidence`, `remote_execution_recovered_by_fallback`; production remote execution 주장은 아님 |

Duration handoff 이력은 `EdgeEnv/AIGuard duration handoff alignment`,
`duration_handoff_alignment_20260601`, EdgeEnv `de64d50` / AIGuard `7289899`
marker로 추적합니다.

## 주장하지 말아야 할 것

- production SaaS dashboard
- production observability platform
- GitLab control plane
- production SSH/HTTP remote execution
- long-lived remote worker daemon
- Cloudflare / secure tunnel operation 완료
- production retry/failover infrastructure
- Kubernetes-style or cloud orchestration

세부 implementation status와 evidence 수치는
[InferEdge Portfolio Summary](portfolio_summary.md)를 기준으로 확인하세요.
