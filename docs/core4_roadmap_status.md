# InferEdge Core4 Roadmap Status

Date: 2026-06-19

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

## Current Status

| Roadmap item | Current evidence | Status |
|---|---|---|
| Core 4 Contract Conformance Suite | InferEdgeLab PR #374 strengthens `core4_conformance` coverage for compare bundles, rendered report aliases, comparison mode, and Lab decision surface | Complete for the current contract snapshot |
| Lab Decision Policy Versioning | InferEdgeLab PR #375 documents the Lab decision policy rule surface and guards docs/code alignment | Complete for documented policy rules |
| Runtime Real-Device Evidence Depth | InferEdge-Runtime PR #67 adds a Jetson evidence depth audit for current 15W/25W fixtures, p95/p99, thermal/memory/power starter evidence, and sustained evidence criteria | Complete as an audit; fresh sustained capture still requires Jetson hardware |
| AIGuard Detector Matrix Depth | InferEdgeAIGuard PR #107 adds deterministic detection disappearance evidence for candidate zero detections against non-empty baseline evidence; PR #108 adds per-class detection drift evidence for class-specific disappearance with stable total counts; PR #109 bounds the calibration drift policy before implementation | Complete for disappearance and per-class drift; calibration drift is policy-gated but not implemented |
| Documentation Cleanup | This entrypoint preserves local-first validation wording, production SaaS/AI OS boundaries, Lab decision ownership, and deterministic AIGuard wording across reviewer-facing docs | In progress through small bounded cleanup passes |

## Portfolio Impact

The completed work improves the portfolio in the current direction because it
turns reviewer claims into contract-aware checks:

- Lab conformance makes the validation report and decision surface easier to
  trust.
- Lab policy documentation explains why a decision was made without moving the
  decision owner.
- Runtime evidence depth separates short smoke evidence from sustained Jetson
  evidence requirements.
- AIGuard disappearance and per-class drift evidence add deterministic failure
  modes without LLM root-cause guessing.
- AIGuard calibration drift now has a bounded future policy for fixed-bin
  score histogram, mean score, std score, and saturation deltas before any
  implementation claim.
- Documentation cleanup keeps the project framed as a local-first validation
  workflow, not a production SaaS, AI OS, or generic monitoring stack.

## Deferred Improvement Candidates

These directions may improve the portfolio later, but they should stay separate
from the completed Core4 cleanup so the current evidence remains clear:

| Candidate | Why it could help | Why defer |
|---|---|---|
| Fresh Jetson sustained capture | Upgrades Runtime evidence from audit/starter evidence to new sustained device evidence | Requires Jetson hardware and should not be implied from existing fixtures |
| AIGuard calibration drift implementation | Explains confidence distribution shifts | Policy is now bounded, but implementation still needs fixture-gated additive evidence and must not replace Lab deployment decision rules |
| Runtime Operation v2 polish | Shows constrained edge workload reliability under queue/deadline/fallback pressure | Must remain an operation evidence extension, not a new production orchestration product |

## Boundaries

- This status document is not a source contract.
- This status document is not a Lab report, deployment decision, or AIGuard
  verdict.
- No new benchmark, Jetson run, or sustained evidence is claimed here.
- Jetson hardware is required for fresh sustained Runtime evidence collection.
- Lab remains the final deployment decision owner.
