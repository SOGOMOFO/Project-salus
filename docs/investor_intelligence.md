# Investor Intelligence Directorate v1

Project Salus includes a permanent Economics and Finance directorate focused on educational investment decision support.

## Agent panel
- Value Analyst
- Growth Analyst
- Macro Strategist
- Behavioral Economist
- Risk Officer
- Portfolio Manager

## Scoring model
The framework uses the following normalized factors (0-100):
- valuation
- financial_strength
- growth
- moat
- management
- macro
- technical
- risk
- conviction

## Recommendation statuses
- Buy
- Hold
- Monitor
- Avoid

## Core decision rule
When confidence is below 80%, recommendation defaults to `Monitor` unless risk/reward is exceptional.

## API endpoints
- `GET /investor-intelligence/status`
- `POST /investor-intelligence/analyze`
- `GET /investor-intelligence/framework`

## Safety constraints
- No real brokerage account connectivity in v1.
- Output language remains educational and decision-support focused.
- Results do not claim certainty or guaranteed outcomes.

## Example analyze payload
```json
{
  "ticker": "MSFT",
  "confidence": 76,
  "scores": {
    "valuation": 68,
    "financial_strength": 85,
    "growth": 82,
    "moat": 88,
    "management": 83,
    "macro": 64,
    "technical": 71,
    "risk": 52,
    "conviction": 79
  }
}
```
