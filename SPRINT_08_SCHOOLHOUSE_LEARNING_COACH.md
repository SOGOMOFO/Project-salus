# Sprint 08 — Schoolhouse Learning Coach Module

## Objective
Build a dedicated Project Salus teaching module to help Kyle learn WGU school work, cybersecurity, AI, investing, business, and leadership skills.

## Doctrine
The Schoolhouse module must make Kyle more capable, not more dependent on AI.

The module should teach:
- understanding
- memory
- application
- reasoning
- independent recall
- exam readiness
- writing quality
- professional communication

## Primary User
Kyle

## Current Education Mission
WGU BS Cybersecurity and Information Assurance.

## Core Purpose
Project Salus Schoolhouse exists to help Kyle learn faster, retain more, pass school requirements, and build durable knowledge for cybersecurity, AI, business, and investing.

## Core Capabilities
- Course tracker
- Study session planner
- Daily school brief
- Quiz mode
- One-question-at-a-time tutoring
- Wrong-answer review
- Competency mapper
- Flashcard generator
- Writing task support
- Rubric analyzer
- Exam readiness score
- After-action review for study sessions

## Proposed Endpoints
- GET /api/schoolhouse/status
- POST /api/schoolhouse/course
- GET /api/schoolhouse/courses
- POST /api/schoolhouse/study-session
- POST /api/schoolhouse/quiz
- POST /api/schoolhouse/wrong-answer-review
- POST /api/schoolhouse/writing-task
- GET /api/schoolhouse/daily-brief

## Study Session Model
Fields:
- course
- objective
- duration_minutes
- material
- notes
- confidence_before
- confidence_after
- blockers
- next_action

## Quiz Mode Rules
- Ask one question at a time
- Wait for Kyle's answer
- Grade briefly
- Explain why correct or incorrect
- Track weak areas
- Continue until stopped

## WGU Support
The module should support:
- OA prep
- PA writing task breakdown
- competency mapping
- rubric interpretation
- instructor email drafting
- retake planning
- study pacing
- evidence and portfolio artifact tracking

## Current Known WGU Priorities
- D333 written tasks
- Prompt Engineering OA retake preparation
- Cybersecurity/GRC career alignment
- Future certification alignment

## Schoolhouse Teaching Rules
The module should:
1. Teach first principles.
2. Use plain language.
3. Ask Kyle one question at a time during quiz mode.
4. Correct briefly.
5. Explain the reason.
6. Track weak areas.
7. Build confidence through competence, not praise.
8. Help Kyle produce his own answers.

## Do Not Build Yet
- Full LMS integration
- WGU login integration
- Browser automation
- Paid course marketplace
- Voice/video tutoring
- Public education product
- Full AI agent orchestration

## Success Criteria
1. Kyle can add a WGU course.
2. Kyle can start a study session.
3. Kyle can get a daily school brief.
4. Kyle can run quiz mode structure.
5. Kyle can review wrong answers.
6. Tests pass.
