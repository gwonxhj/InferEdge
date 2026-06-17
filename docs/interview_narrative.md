# InferEdge Interview Narrative

Language: English | [한국어](interview_narrative.ko.md)

Use this as a speaking guide. The goal is to explain InferEdge as a
local-first Edge AI inference validation and runtime-evidence ecosystem without
overclaiming production readiness.

## 45-Second Answer

InferEdge is a local-first Edge AI inference validation portfolio. It turns an
ONNX model into traceable build provenance, real runtime evidence, structured
comparison/evaluation, optional deterministic diagnosis, and a Lab-owned
deployment decision.

The ecosystem separates three questions:

| Question | Owner path |
|---|---|
| Can we deploy this model? | Forge -> Runtime -> Lab (+ optional AIGuard) |
| Can this benchmark evidence be trusted and compared? | InferEdgeEnv |
| Can deployed workloads stay stable under load? | InferEdgeOrchestrator |

The strongest signal is not one benchmark number. The signal is that the
portfolio preserves evidence from build identity to runtime behavior, report
generation, deterministic warnings, and deployment decision ownership.

## Evidence To Mention First

| Evidence | Current record | How to phrase it |
|---|---|---|
| TensorRT Jetson FP16 | 10.066 ms mean, 15.548 ms p99, 99.34 FPS | Real Jetson runtime evidence |
| ONNX Runtime CPU baseline | 45.430 ms mean, 49.213 ms p99, 22.01 FPS | Baseline for the Local Studio demo |
| Speedup | about 4.51x FPS over ONNX Runtime CPU | Backend comparison evidence, not a universal benchmark claim |
| Jetson device-local replay | 96 frames, 155.86 ms mean, 156.877 ms p95, 45.5 C, 1000 MB RAM | ONNX probe + telemetry handoff evidence |
| Jetson 5-minute-class replay | 3600 frames, Vision mean 152.77 ms, p95 156.948 ms, 50.375 C, 1038 MB RAM | Smoke/Starter sustained operation evidence |
| Jetson quick-scan registry | 96-frame and 5-minute rows with linked metric snapshots and `Operation Quick Scan Summary` | Reviewer navigation for queue/deadline/fallback pressure, not production control evidence |

Use the same Jetson evidence terms as the demo and evidence reports:

| Term | Interview phrasing |
|---|---|
| Representative snapshot | The 96-frame and 5-minute Markdown/HTML reports are submission-facing metric snapshots, not the latest registry itself. |
| Latest registry | The `c04abc9` operation-summary registry is the latest local navigation record for comparing the 96-frame and 5-minute rows, including linked metric snapshot values (`155.86` / `156.877` ms, `45.5 C` / `1000 MB`; `152.77` / `156.948` ms, `50.375 C` / `1038 MB`) without replacing the source reports. |
| Quick-scan navigation | `Duration Comparison Summary` and `Operation Quick Scan Summary` help reviewers scan duration and queue/deadline/fallback pressure before opening full reports. |

For shared reviewer marker-gate details across the Lab report summary, copied CI
artifact summary, and generated `00_evidence_index.*` artifacts, point reviewers
to [Agent Runtime E2E Demo](agent_runtime_e2e_demo.md). This interview narrative
stays at speaking-guide level and is not the detailed marker vocabulary owner.
The short interview phrasing is: the smoke-gated evidence-index boundary keeps
`00_evidence_index.md` as reviewer navigation, not a Lab report owner or source
contract.

## Architecture Explanation

```text
ONNX model
-> InferEdgeForge
-> InferEdge-Runtime
-> InferEdgeLab
-> optional InferEdgeAIGuard
-> Deployment Decision Report / Local Studio

Runtime operation extension:
InferEdgeOrchestrator
-> InferEdgeEnv
-> optional InferEdgeAIGuard
-> InferEdgeLab Runtime Intelligence Risk Summary
```

The split is intentional. Each repository owns one contract and avoids silently
taking responsibility for another layer.

| Repository | Interview phrasing | Boundary |
|---|---|---|
| InferEdgeForge | Records how an artifact was built. | Does not run inference or decide deployment. |
| InferEdge-Runtime | Turns model artifacts into execution evidence. | Does not own comparison policy or scheduling. |
| InferEdgeLab | Interprets evidence into reports and deployment decisions. | Final deployment decision owner. |
| InferEdgeAIGuard | Adds deterministic warning/diagnosis evidence. | Does not use LLM guessing and does not own final decisions. |
| InferEdgeEnv | Preserves run evidence and judges comparability. | Not a production DB or cloud telemetry store. |
| InferEdgeOrchestrator | Records queue/deadline/fallback operation context. | Not Kubernetes, Triton, or a completed production scheduler. |

## Problem Framing

Do not frame the project as:

```text
Can this model run fast?
```

Frame it as:

```text
Can we trust the evidence behind this runtime result, and can reviewers see
why a deployment decision was made?
```

That means preserving:

- artifact identity
- runtime/backend/provider condition
- latency, p95/p99, FPS, and resource evidence
- benchmark comparability context
- runtime operation context
- deterministic warning evidence
- Lab-owned deployment decision
- reproducible commands and reports

## Runtime Operation / Jetson Story

Jetson evidence makes the portfolio stronger because the workflow reaches a
constrained real device instead of staying at desktop simulation. The current
Jetson and device-local records should be described as runtime evidence and
operation smoke, not as broad accuracy, service-readiness, or endurance claims.

Good phrasing:

- "This shows real-device runtime and telemetry handoff."
- "This is a device-local ONNX probe inside the operation evidence chain."
- "The Lab report preserves the risk context and remains the decision owner."
- "The 5-minute-class replay is sustained Smoke/Starter evidence, not thermal
  endurance validation."
- "The quick-scan registry lets reviewers see queue/deadline/fallback pressure
  before opening the full report."
- "The registry is quick-scan navigation metadata, not production runtime
  operation proof."

Avoid phrasing:

- "This is production remote execution."
- "This proves live camera / Whisper / FastAPI service readiness."
- "This is a full YOLO accuracy benchmark."
- "This is a production scheduler."

## Deep-Dive Answers

### Why not one repository?

One repository would blur contracts. Build provenance, runtime execution,
comparison policy, diagnosis evidence, comparability, and operation control
change for different reasons. Splitting them makes ownership inspectable and
keeps smoke tests targeted.

### Why is Lab the decision owner?

Runtime and Orchestrator produce evidence. AIGuard produces deterministic
warnings. EdgeEnv judges comparability. Lab is the layer that combines those
signals into a report and deployment decision, so decision policy does not leak
into every producer.

### Why is EdgeEnv separate?

Regression analysis is dangerous when results are not comparable. EdgeEnv
checks run identity, benchmark protocol, model/input conditions, and telemetry
context before treating runtime deltas as regression evidence.

### Why is Orchestrator separate?

Validation asks whether a model can deploy. Operation asks whether workloads
remain stable under queue pressure, deadlines, fallback, and constrained device
resources. Keeping Orchestrator separate prevents runtime-operation evidence
from becoming a hidden deployment shortcut.

### What does the current portfolio prove?

It proves a reproducible local-first evidence chain:

```text
build provenance
-> runtime result
-> comparison/evaluation
-> deterministic warning evidence
-> local registry / comparability context
-> reviewer quick-scan registry for queue/deadline/fallback pressure
-> operation-risk report context
-> Lab-owned deployment decision
```

It does not prove production SaaS readiness, Kubernetes-style orchestration,
general monitoring, production remote execution, or broad model quality.

## What Not To Claim

- production SaaS dashboard
- production observability platform
- GitLab or CI as a runtime control plane
- Kubernetes-style orchestration
- production SSH/HTTP remote execution
- long-lived worker daemon readiness
- public leaderboard
- LLM root-cause diagnosis
- full YOLO/Whisper accuracy validation from smoke inputs
- thermal endurance validation from Smoke/Starter runs

## Closing Answer

InferEdge is valuable because it makes edge AI deployment evidence explicit. It
separates who builds, who runs, who compares, who diagnoses, who preserves
comparability, who records operation context, and who owns the deployment
decision. That makes the portfolio more than "I ran a model"; it shows the
evidence needed to reason about edge runtime reliability.
