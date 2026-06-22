# InferEdge Core4 Roadmap Status

Date: 2026-06-22

This document records the current Core4 six-month completion roadmap status for
reviewers. It is a roadmap/status artifact only. It does not change
`metadata.json`, `manifest.json`, Runtime `result.json`, Lab compare output,
Lab deployment decision output, or AIGuard `guard_analysis`.

## Scope

The Core4 validation path remains:

```text
Forge -> Runtime -> Lab (+ optional AIGuard)
```

Runtime Operation and Runtime Intelligence evidence can strengthen the
portfolio, but they do not replace the Core4 validation contract and do not move
the final deployment decision away from Lab.
InferEdgeOrchestrator PR #115 adds an `operation-risk` first-read line to the
sustained CLI output so reviewers can see queue/deadline/fallback risk level,
primary reasons, and affected tasks before opening the full JSON evidence.
InferEdgeOrchestrator PR #116 adds a supplemental `worker_health_trend` block to
the sustained operation timeline summary so reviewers can inspect health-state
counts, health-state task groups, scheduler-delay/fallback/resource degradation
context, and Lab-owned decision boundaries before downstream consumption.
InferEdgeLab PR #376 preserves the same `first_read` marker in the Lab Runtime
Intelligence Markdown/HTML report so the CLI-first reviewer path carries into
the Lab-owned deployment risk report.
InferEdgeEnv PR #155 carries the operation risk `first_read` marker in the
Runtime Intelligence Lab handoff summary and CLI output so the reviewer path is
visible before opening the raw telemetry feed.
InferEdgeAIGuard PR #114 consumes EdgeEnv-preserved Orchestrator
`worker_health_trend` as deterministic evidence, preserving
`scheduler_owner=orchestrator`, `decision_owner=lab`, and
`not_a_deployment_decision=true` boundary markers in raw context.
InferEdgeLab PR #377 surfaces the same AIGuard
`edgeenv_orchestrator_worker_health_trend` evidence in the Lab-owned Runtime
Intelligence Markdown/HTML report, bundle gate, artifact gate, and chain
fixtures without changing Lab deployment decision ownership.
InferEdgeOrchestrator PR #117 declares
`edgeenv_orchestrator_worker_health_trend` in the source EdgeEnv/AIGuard
evidence candidate list, closing the source-feed alignment gap for the
worker-health trend evidence chain.
InferEdge entrypoint first-read PR series closes the reviewer-facing loop by
aligning README, portfolio summary, ecosystem 1-page, interview narrative,
completion audit, generated evidence indexes/run registries, and the cross-repo
Runtime Intelligence report marker gate around
`first_read=review_operation_risk_context`.
PRs #258-#265 are historical anchors for that alignment, but current completion
is proved by the evidence rows, reviewer completion audit verification snapshot,
marker gates, and tests in this repo rather than by appending every sync-only PR
number to this status document.

## Evidence Maintenance Rule

PR references in this file are traceability anchors. Do not advance them only
because a documentation-only synchronization PR was merged. Update the status
claim only when the reviewer-facing evidence boundary changes, a smoke/test gate
changes, or a new Core4 roadmap item becomes current evidence.

## Current Status

| Roadmap item | Current evidence | Status |
|---|---|---|
| Core 4 Contract Conformance Suite | InferEdgeLab PR #374 strengthens `core4_conformance` coverage for compare bundles, rendered report aliases, comparison mode, and Lab decision surface | Complete for the current contract snapshot |
| Lab Decision Policy Versioning | InferEdgeLab PR #375 documents the Lab decision policy rule surface and guards docs/code alignment | Complete for documented policy rules |
| Runtime Real-Device Evidence Depth | InferEdge-Runtime PR #67 adds a Jetson evidence depth audit for current 15W/25W fixtures, p95/p99, thermal/memory/power starter evidence, and sustained evidence criteria | Complete as an audit; fresh sustained capture still requires Jetson hardware |
| AIGuard Detector Matrix Depth | InferEdgeAIGuard PR #107 adds deterministic detection disappearance evidence for candidate zero detections against non-empty baseline evidence; PR #108 adds per-class detection drift evidence for class-specific disappearance with stable total counts; PR #109 bounds the calibration drift policy before implementation; PR #110 implements calibration drift as additive baseline-comparison evidence; PR #111 adds baseline profile stability audit metadata for saved profile sample count and coverage; PR #112 adds sequence-level disappearance evidence for repeated zero-detection frame streaks; PR #113 adds a temporal profile continuity demo case that combines sequence disappearance, class flip, and bbox jump evidence | Complete for disappearance, per-class drift, review-level calibration drift, baseline profile stability audit metadata, sequence-level disappearance evidence, and the temporal continuity demo case |
| Documentation Cleanup | This entrypoint preserves local-first validation wording, production SaaS/AI OS boundaries, Lab decision ownership, deterministic AIGuard wording, and the operation-risk first-read reviewer path across reviewer-facing docs, generated indexes/registries, and smoke gates | Complete for the current first-read reviewer path; future cleanup remains bounded |

## Portfolio Impact

The completed work improves the portfolio in the current direction because it
turns reviewer claims into contract-aware checks:

- Lab conformance makes the validation report and decision surface easier to
  trust.
- Lab policy documentation explains why a decision was made without moving the
  decision owner.
- Runtime evidence depth separates short smoke evidence from sustained Jetson
  evidence requirements.
- AIGuard disappearance, sequence-level disappearance, per-class drift,
  calibration drift, and baseline profile stability metadata add deterministic
  review/failure context without LLM root-cause guessing.
- AIGuard calibration drift now checks fixed-bin score histogram distance,
  mean score delta, std score delta, and saturation delta as additive
  baseline-comparison evidence before Lab makes the final deployment decision.
- AIGuard saved baseline profiles now expose `profile_stability` audit metadata
  so reviewers can see sample count and histogram/class coverage before
  trusting baseline-comparison evidence.
- AIGuard temporal evidence now preserves `max_zero_detection_streak`,
  first disappearance frame, and `zero_detection_streaks` so repeated
  disappearance is easier to review without adding object tracking.
- AIGuard portfolio demo now includes a temporal profile continuity case that
  shows sequence disappearance, class flip, and bbox jump evidence together in
  one compact reviewer fixture.
- Orchestrator sustained CLI output now surfaces the existing
  `operation_risk_rollup` as an `operation-risk` first-read line, improving
  reviewer scanability without changing Lab ownership or the JSON source
  evidence.
- Lab Runtime Intelligence reports now preserve
  `first_read=review_operation_risk_context` for AIGuard/EdgeEnv operation risk
  rollup evidence, aligning the report review path with the Orchestrator CLI
  first-read signal.
- EdgeEnv Lab handoff now reports
  `candidate:review_operation_risk_context` for preserved Orchestrator
  `operation_risk_rollup` context, keeping the first-read path visible before
  Lab/AIGuard consume the handoff bundle.
- AIGuard now emits `edgeenv_orchestrator_worker_health_trend` when EdgeEnv
  preserves Orchestrator worker-health trend context, making degraded and
  constrained worker state visible as deterministic evidence while Lab remains
  the final deployment decision owner.
- Lab Runtime Intelligence reports now show the same worker-health trend
  evidence row, including degraded/constrained worker labels and boundary
  markers, so the Orchestrator -> EdgeEnv -> AIGuard -> Lab chain is visible in
  the final Lab-owned reviewer surface.
- Orchestrator source feeds now declare that worker-health trend evidence as a
  downstream AIGuard candidate, so the source artifact, EdgeEnv preservation,
  AIGuard deterministic evidence, and Lab report row use the same candidate
  vocabulary.
- InferEdge entrypoint now exposes the same first-read path from README through
  portfolio/ecosystem/interview/audit docs, generated
  `operation_risk_first_read_label` / `operation_risk_rollup_first_reads`
  artifacts, the reviewer completion audit, and the cross-repo Runtime
  Intelligence smoke gate. This improves reviewer scanability without turning
  the index, registry, audit, Orchestrator, EdgeEnv, or AIGuard into a
  deployment decision owner.
- The reviewer completion audit now records the `--log-dir` full verification
  snapshot, so long cross-repo smoke output remains reproducible as per-step
  logs while the Core4 status stays tied to evidence rows and tests instead of
  synchronization PR counting.
- Documentation cleanup keeps the project framed as a local-first validation
  workflow, not a production SaaS, AI OS, or generic monitoring stack.

## Deferred Improvement Candidates

These directions may improve the portfolio later, but they should stay separate
from the completed Core4 cleanup so the current evidence remains clear:

| Candidate | Why it could help | Why defer |
|---|---|---|
| Fresh Jetson sustained capture | Upgrades Runtime evidence from audit/starter evidence to new sustained device evidence | Requires Jetson hardware and should not be implied from existing fixtures |
| Runtime Operation v2 deeper polish | Further strengthens constrained edge workload reliability under queue/deadline/fallback pressure beyond the PR #115 first-read CLI polish, PR #116 Orchestrator worker-health trend source artifact, PR #117 Orchestrator worker-health AIGuard candidate alignment, PR #156 EdgeEnv worker-health trend handoff preservation, PR #114 AIGuard worker-health trend deterministic evidence, PR #377 Lab worker-health trend report evidence, PR #376 Lab report first-read polish, PR #155 EdgeEnv handoff first-read polish, and the current reviewer path / artifact / audit / gate alignment | Must remain an operation evidence extension, not a new production orchestration product |

## Portfolio Improvement Decision Log

Use this section when deciding whether to keep polishing the current evidence
path or split a stronger portfolio direction into a later task.

| Decision point | Current direction | Stronger portfolio direction | Decision |
|---|---|---|---|
| Runtime evidence depth | Keep the committed Jetson fixtures and Runtime evidence-depth audit as the current reviewer evidence | Capture a fresh sustained Jetson run with current main branches, p95/p99, thermal, memory, power, and operation quick-scan registry evidence | Prefer the stronger direction later; it requires Jetson hardware and must be recorded as new evidence, not inferred from existing fixtures |
| Runtime Operation polish | Keep operation-risk first-read as reviewer navigation across Orchestrator, EdgeEnv, Lab, entrypoint artifacts, audit, and smoke gates | Add deeper sustained workload pressure evidence only if it preserves Lab final-decision ownership and stays bounded as operation evidence | Defer as a separate Runtime Operation v2 task; do not mix it into Core4 completion status unless the evidence boundary or smoke gate changes |

Start the fresh Jetson direction only after `scripts/check_jetson_sustained_readiness.sh`
passes against the target device. Start the Runtime Operation v2 direction only
with a scoped plan that names the owner repo and confirms no `metadata.json`,
`manifest.json`, Runtime `result.json`, Lab compare output, Lab deployment
decision, or AIGuard `guard_analysis` contract change is being implied.

### Fresh Jetson Readiness Attempt

On 2026-06-21 KST, the fresh sustained Jetson direction was checked with:

```bash
bash scripts/check_jetson_sustained_readiness.sh --edgeenv-run-evidence
```

The sandboxed run failed with SSH `Operation not permitted`; the approved
network run reached `192.168.35.35:22` but timed out. No new Jetson evidence was
created. Keep the committed Jetson reports as the current reviewer evidence
until the target device is powered on, reachable over SSH with `BatchMode=yes`,
and the readiness preflight passes.

### Runtime Operation v2 Scoped Starter Plan

If Jetson sustained capture remains blocked, the safer portfolio improvement is
to start Runtime Operation v2 as a scoped operation-evidence task, not as a new
product surface.

- Owner repo: `InferEdgeOrchestrator`.
- First evidence target: a fixture-backed sustained workload pressure scenario
  that records queue-depth timeline, worker-health trend, deadline/drop/fallback
  counts, and scheduler decision reasons.
- Supporting repos: `InferEdgeEnv`, `InferEdgeAIGuard`, and `InferEdgeLab` may
  consume the Orchestrator evidence only after the source artifact is stable.
- Required boundary: no `metadata.json`, `manifest.json`, Runtime `result.json`,
  Lab compare output, Lab deployment decision, or AIGuard `guard_analysis`
  contract change is implied by this starter plan.
- Completion rule: do not mark Runtime Operation v2 as implemented until the
  Orchestrator source artifact, EdgeEnv preservation path, AIGuard deterministic
  evidence, Lab-owned report context, and entrypoint smoke/reviewer marker gate
  all pass together.

## Boundaries

- This status document is not a source contract.
- This status document is not a Lab report, deployment decision, or AIGuard
  verdict.
- No new benchmark, Jetson run, or sustained evidence is claimed here.
- Jetson hardware is required for fresh sustained Runtime evidence collection.
- Lab remains the final deployment decision owner.
