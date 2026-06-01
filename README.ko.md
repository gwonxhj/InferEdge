# InferEdge

언어: [English](README.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표 README와 가장 최신 상세 설명은
[English README](README.md)를 기준으로 유지합니다.

InferEdge는 Edge AI 모델을 단순 benchmark 숫자로만 비교하지 않고, build
provenance, 실제 Runtime 실행 결과, validation evidence, optional deterministic
diagnosis, Lab-owned deployment decision을 하나의 local-first 검증 흐름으로
연결하는 multi-repository entrypoint입니다.

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
| [InferEdge-Runtime](https://github.com/gwonxhj/InferEdge-Runtime) | C++ inference execution, Lab-compatible result JSON, Jetson evidence |
| [InferEdgeLab](https://github.com/gwonxhj/InferEdgeLab) | compare, evaluate, report, API, Local Studio, deployment decision owner |
| [InferEdgeAIGuard](https://github.com/gwonxhj/InferEdgeAIGuard) | optional deterministic diagnosis evidence provider |
| [InferEdgeEnv](https://github.com/gwonxhj/InferEdgeEnv) | local run evidence registry, comparability checker, runtime regression evidence |
| [InferEdgeOrchestrator](https://github.com/gwonxhj/InferEdgeOrchestrator) | queue/deadline/fallback/worker health operation context provider |

## 현재 말할 수 있는 것

- Core Forge -> Runtime -> Lab -> optional AIGuard validation pipeline은 구현되어 있습니다.
- Local Studio는 local-first evidence replay와 deployment decision 확인용 UI입니다.
- Runtime Intelligence artifact gate는 Orchestrator -> EdgeEnv -> AIGuard -> Lab
  evidence chain의 report marker와 owner boundary를 검증합니다.
- Jetson/device-local smoke는 실제 device-local starter evidence를 보존하지만,
  decoded YOLO accuracy, live camera service, production remote execution, thermal
  endurance validation을 의미하지 않습니다.

## 중요한 경계

InferEdge는 현재 범위에서 다음을 완료 기능처럼 주장하지 않습니다.

- production SaaS dashboard
- production observability platform
- Kubernetes-style orchestration
- production remote execution / long-lived worker daemon
- AIGuard 또는 Orchestrator의 최종 deployment decision ownership

최종 deployment decision owner는 InferEdgeLab입니다. AIGuard는 deterministic
evidence provider이고, Orchestrator는 operation context provider이며, EdgeEnv는
registry / comparability / regression evidence owner입니다.

## 먼저 볼 문서

| 문서 | 용도 |
|---|---|
| [InferEdge Ecosystem 1-Page Summary](docs/ecosystem_1page.md) | ecosystem diagram과 layer split |
| [Portfolio Summary](docs/portfolio_summary.md) | 포트폴리오용 30초 요약 |
| [Pipeline Map](docs/pipeline_map.md) | 레포별 책임과 contract boundary |
| [Agent Runtime E2E Demo](docs/agent_runtime_e2e_demo.md) | Runtime Operation / Agent Runtime smoke 흐름 |

영어 README가 대표 문서이므로, 전체 명령어와 최신 세부 evidence는
[README.md](README.md)에서 확인하세요.
