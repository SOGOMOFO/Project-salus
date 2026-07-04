# Sprint 21 Risk Register

## Risk 1 — Breaking working MVP during refactor
Likelihood: Medium
Impact: High
Control: One module per sprint, tests before and after.

## Risk 2 — Route conflicts
Likelihood: Medium
Impact: Medium
Control: Maintain route inventory and test all primary pages.

## Risk 3 — Data loss
Likelihood: Medium
Impact: High
Control: Archive before delete, JSON backup/export before storage migration.

## Risk 4 — Security exposure
Likelihood: Low locally, high if exposed online
Impact: High
Control: Do not expose beyond localhost before authentication and permissions exist.

## Risk 5 — Overbuilding features before hardening
Likelihood: High
Impact: Medium
Control: Pause major feature additions until route modularization begins.
