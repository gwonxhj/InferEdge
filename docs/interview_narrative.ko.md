# InferEdge 인터뷰 내러티브

언어: [English](interview_narrative.md) | 한국어

이 문서는 한국어 빠른 안내서입니다. 대표/canonical 문서는
[InferEdge Interview Narrative](interview_narrative.md)입니다.

## 45초 답변

InferEdge는 ONNX 모델을 build provenance, real runtime evidence, structured
comparison/evaluation, optional deterministic diagnosis, Lab-owned deployment
decision으로 연결하는 local-first Edge AI inference validation portfolio입니다.

핵심 질문은 세 가지입니다.

| 질문 | 담당 흐름 |
|---|---|
| 이 모델을 배포해도 되는가? | Forge -> Runtime -> Lab (+ optional AIGuard) |
| 이 benchmark evidence를 믿고 비교할 수 있는가? | InferEdgeEnv |
| 배포된 workload가 부하 상황에서도 안정적인가? | InferEdgeOrchestrator |

강점은 단일 benchmark 숫자가 아니라 build identity부터 runtime behavior,
report, deterministic warning, deployment decision ownership까지 evidence chain을
보존한다는 점입니다.

## 먼저 말할 evidence

| Evidence | 현재 기록 | 말하는 방식 |
|---|---|---|
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS | 실제 Jetson runtime evidence |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS | Local Studio demo baseline |
| Speedup | ONNX Runtime CPU 대비 약 4.51x FPS | backend comparison evidence |
| Jetson device-local replay | 96 frames, 155.86 ms mean, 156.877 ms p95, 45.5 C, 1000 MB RAM | ONNX probe + telemetry handoff evidence |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, p95 156.948 ms, 50.375 C, 1038 MB RAM | Smoke/Starter sustained operation evidence |
| Jetson quick-scan registry | 96-frame / 5-minute rows, `Operation Quick Scan Summary` | queue/deadline/fallback pressure를 먼저 보는 reviewer navigation evidence |

demo / evidence report와 같은 Jetson evidence 용어를 사용합니다.

| 용어 | 인터뷰 표현 |
|---|---|
| Representative snapshot | 96-frame / 5-minute Markdown/HTML report는 submission-facing metric snapshot이며, 최신 registry 자체가 아닙니다. |
| Latest registry | `c04abc9` operation-summary registry는 96-frame / 5-minute row를 비교하는 최신 local navigation record입니다. |
| Quick-scan navigation | `Duration Comparison Summary`와 `Operation Quick Scan Summary`는 full report를 열기 전에 duration과 queue/deadline/fallback pressure를 훑어보는 reviewer navigation입니다. |

## 역할 설명

| Repository | 인터뷰 표현 | 경계 |
|---|---|---|
| InferEdgeForge | artifact가 어떻게 만들어졌는지 기록합니다. | inference 실행이나 deployment decision을 소유하지 않습니다. |
| InferEdge-Runtime | model artifact를 execution evidence로 바꿉니다. | comparison policy나 scheduling을 소유하지 않습니다. |
| InferEdgeLab | evidence를 report와 deployment decision으로 해석합니다. | final deployment decision owner입니다. |
| InferEdgeAIGuard | deterministic warning/diagnosis evidence를 추가합니다. | LLM guessing이나 final decision owner가 아닙니다. |
| InferEdgeEnv | run evidence를 보존하고 comparability를 판정합니다. | production DB/cloud telemetry store가 아닙니다. |
| InferEdgeOrchestrator | queue/deadline/fallback operation context를 기록합니다. | Kubernetes, Triton, completed production scheduler가 아닙니다. |

## 문제 정의

이 프로젝트는 단순히 다음 질문을 답하려는 것이 아닙니다.

```text
Can this model run fast?
```

더 중요한 질문은 아래입니다.

```text
Can we trust the evidence behind this runtime result?
Why was this deployment decision made?
```

그래서 InferEdge는 artifact identity, backend/provider condition, latency/p95/p99,
FPS, resource evidence, comparability context, operation context, deterministic
warning evidence, Lab-owned deployment decision을 함께 보존합니다.

## Jetson / Runtime Operation 설명

Jetson evidence는 workflow가 desktop simulation에 머무르지 않고 constrained
real device까지 이어진다는 점을 보여줍니다. 다만 현재 Jetson/device-local
기록은 runtime evidence와 operation smoke로 설명해야 하며, broad accuracy,
service-readiness, endurance claim으로 말하면 안 됩니다.

좋은 표현:

- "real-device runtime and telemetry handoff evidence"
- "device-local ONNX probe inside the operation evidence chain"
- "Lab report preserves risk context and remains the decision owner"
- "5-minute-class replay is sustained Smoke/Starter evidence"
- "quick-scan registry shows queue/deadline/fallback pressure before opening
  the full report"
- "registry는 quick-scan navigation metadata이며 production runtime operation
  proof가 아니다"

피해야 할 표현:

- production remote execution
- live camera / Whisper / FastAPI service readiness
- full YOLO accuracy benchmark
- production scheduler

## Deep-Dive 답변

### 왜 하나의 repo가 아닌가?

Build provenance, runtime execution, comparison policy, diagnosis evidence,
comparability, operation control은 바뀌는 이유가 다릅니다. repo를 나누면
contract ownership이 명확하고 smoke test도 각 역할에 맞게 유지됩니다.

### 왜 Lab이 decision owner인가?

Runtime과 Orchestrator는 evidence를 만들고, AIGuard는 deterministic warning을
제공하며, EdgeEnv는 comparability를 판정합니다. 이 신호를 deployment
decision으로 묶는 책임은 Lab 하나에 두어야 decision policy가 producer layer에
흩어지지 않습니다.

### 왜 EdgeEnv가 별도인가?

결과가 비교 가능하지 않으면 regression 계산은 위험합니다. EdgeEnv는 model,
input, benchmark protocol, telemetry context를 먼저 확인하고, 비교 가능한 경우에만
runtime regression evidence를 해석합니다.

### 왜 Orchestrator가 별도인가?

Validation은 모델을 배포해도 되는지 묻고, Operation은 queue pressure,
deadline, fallback, constrained device resource 아래 workload가 안정적인지 묻습니다.
두 역할을 분리해야 operation evidence가 hidden deployment shortcut처럼 보이지
않습니다.

## 주장하지 말아야 할 것

- production SaaS dashboard
- production observability platform
- GitLab / CI runtime control plane
- Kubernetes-style orchestration
- production SSH/HTTP remote execution
- long-lived worker daemon readiness
- public leaderboard
- LLM root-cause diagnosis
- smoke input 기반 full YOLO/Whisper accuracy validation
- Smoke/Starter run 기반 thermal endurance validation

## 마무리 답변

InferEdge의 가치는 edge AI deployment evidence를 명시적으로 남긴다는 점입니다.
누가 build하고, 누가 실행하고, 누가 비교하고, 누가 진단하고, 누가 comparability를
보존하고, 누가 operation context를 기록하고, 누가 deployment decision을 소유하는지
분리합니다. quick-scan registry는 queue/deadline/fallback pressure를 full report
전에 보여주는 reviewer navigation evidence입니다. 그래서 이 포트폴리오는 "모델을
한 번 돌렸다"가 아니라 edge runtime reliability를 판단하기 위한 evidence chain을
보여줍니다.
