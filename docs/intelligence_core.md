# Salus Intelligence Core v1

Salus Intelligence Core v1 is the central reasoning and coordination layer for directorates.

## Mission
Provide consistent decision evaluation, evidence grading, recommendation generation, and multi-agent reconciliation.

## Core Functions
- evaluate_decision()
- score_evidence()
- reconcile_agent_outputs()
- generate_recommendation()
- create_decision_record()

## Decision Scoring Model
Each decision includes:
- strategic_fit
- evidence_quality
- roi
- difficulty
- risk
- opportunity_cost
- timeline
- recommendation

## Recommendations
- Pursue
- Pause
- Delegate
- Discard
- Monitor

## Evidence Grades
- A+
- A
- B
- C
- D

## Confidence Bands
- 99
- 95
- 90
- 80
- 70
- 60
- below_60

## API Endpoints
- GET /intelligence/status
- POST /intelligence/evaluate
- POST /intelligence/reconcile

## Integration Behavior
- Decision records are stored to memory when available.
- Memory write failures are best-effort and do not fail requests.
- Intelligence evaluation audit logging is best-effort when Security Core audit logging is available.
- Audit write failures do not fail requests.
