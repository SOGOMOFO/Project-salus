# Investor Intelligence Directorate v1

Investor Intelligence Directorate (IID) is the permanent Economics and Finance decision-support capability inside Project Salus.

## Mission
Deliver educational, evidence-driven investment analysis that improves decision quality without presenting certainty.

## Doctrine
- Evidence first, narrative second.
- Protect downside before pursuing upside.
- Confidence thresholds enforce discipline.
- Recommendations are decision support, not personalized financial advice.

## Pipeline
1. Ingest thesis, bear/bull cases, and assumptions.
2. Score nine core factors on a 0-100 scale.
3. Run expert panel interpretation.
4. Run scenario engine and portfolio model synthesis.
5. Apply recommendation engine with confidence and risk/reward policy.
6. Emit structured recommendation with disclaimer.

## Expert Panel
- Value Analyst
- Growth Analyst
- Macro Strategist
- Behavioral Economist
- Risk Officer
- Portfolio Manager

## Scoring Model
IID scores these factors on 0-100:
- valuation
- financial_strength
- growth
- competitive_moat
- management
- macro_environment
- technical_trend
- risk
- conviction

## Confidence Rules
Evidence quality grades:
- A+
- A
- B
- C
- D

Confidence bands:
- 99
- 95
- 90
- 80
- 70
- 60
- below_60

Rule:
- If confidence is below 80, default recommendation is `Monitor` unless `risk_reward` is exceptional.

## Risk Policy
- Recommendation outputs: `Buy`, `Hold`, `Monitor`, `Avoid`.
- Elevated risk or weak evidence should avoid aggressive recommendations.
- No brokerage execution or account connectivity is enabled in v1.

## Scenario Engine
Scenario engine outputs directional states for:
- recession
- inflation_shock
- market_crash
- interest_rate_change
- geopolitical_conflict
- ai_adoption_acceleration

## Portfolio Model
Portfolio model output includes:
- fit_summary
- suggested_sizing
- risk_budget_used
- rebalance_trigger

## Recommendation Engine
Recommendation engine returns one of:
- Buy
- Hold
- Monitor
- Avoid

Policy guardrail remains active:
- Confidence below 80 defaults to `Monitor` unless risk/reward is exceptional.

## AI Investment Categories
- infrastructure
- foundation_models
- enterprise_ai_software
- robotics
- cybersecurity
- healthcare_ai
- defense_ai
- industrial_automation
- edge_ai
- ai_enabled_services

## Portfolio Health Placeholder
IID includes a placeholder model for:
- cash_allocation
- equity_allocation
- crypto_allocation
- bonds
- precious_metals
- private_investments
- real_estate
- business_ownership
- emergency_liquidity
- debt
- tax_exposure

## Scenario Placeholders
- recession
- inflation_shock
- market_crash
- interest_rate_change
- geopolitical_conflict
- ai_adoption_acceleration

## API Endpoints
- `GET /investor-intelligence/status`
- `GET /investor-intelligence/framework`
- `POST /investor-intelligence/analyze`

## Future: Investment Digital Twin
Planned future capability is an Investment Digital Twin that simulates portfolio resilience, scenario transitions, and adaptive thesis updates under changing macro and market regimes.

## Disclaimer
"This is decision-support analysis, not personalized financial advice."
