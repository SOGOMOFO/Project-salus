# Sprint 08 — Charisma and Communication Skill Module

## Objective
Integrate charisma as a trainable human capability inside Project Salus.

## Definition
Charisma is the ability to communicate with presence, clarity, confidence, emotional intelligence, timing, and trust-building behavior while preserving ethics and human agency.

## Doctrine
Charisma in Project Salus is not manipulation.
It is ethical influence, leadership communication, active listening, emotional intelligence, and social calibration.

## Directorate Alignment
- Human Capability Development Directorate
- Influence & Human Behavior Intelligence Agent
- Leadership Development
- Communication Training

## Skill Stack
- Presence
- Voice
- Listening
- Emotional intelligence
- Storytelling
- Rapport
- Framing
- Social calibration
- Leadership communication
- Ethical influence

## Must Ship
- Charisma skill model
- Self-assessment endpoint
- Daily charisma drill endpoint
- Conversation AAR endpoint
- Communication scorecard
- Basic tests

## Proposed Endpoints
- GET /api/skills/charisma
- POST /api/skills/charisma/self-assessment
- GET /api/skills/charisma/daily-drill
- POST /api/skills/charisma/conversation-aar

## Scorecard Fields
- presence
- clarity
- listening
- emotional_control
- confidence
- empathy
- framing
- trust_building
- ethical_alignment

## Daily Drill Examples
- 60-second calm voice drill
- Active listening drill
- Storytelling drill
- Pause-before-answer drill
- Reframe a hard conversation drill
- Compliment without flattery drill
- Ask better questions drill

## Conversation AAR
After important conversations, Salus should ask:
1. What was the objective?
2. Who was the audience?
3. What did I say?
4. How did they respond?
5. Did I listen well?
6. Did I stay calm?
7. Did I build trust?
8. What should I improve next time?

## Do Not Build Yet
- Voice recording analysis
- Video analysis
- Facial expression detection
- Manipulation scoring
- Dating/social gimmick features
- Public charisma coach product

## Success Criteria
1. Kyle can assess his charisma baseline.
2. Kyle can receive one daily communication drill.
3. Kyle can log a conversation AAR.
4. Salus can generate one improvement recommendation.
5. Tests pass.
