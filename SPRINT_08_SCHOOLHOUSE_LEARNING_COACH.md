# Sprint 08 — Schoolhouse Learning Coach Module

## Objective
Build a dedicated Project Salus teaching module to help Kyle learn WGU school work, cybersecurity, AI, investing, and business skills.

## Doctrine
The Schoolhouse module must make Kyle more capable, not more dependent on AI.

It should teach:
- understanding
- memory
- application
- reasoning
- exam readiness
- writing quality
- independent recall

## Primary User
Kyle

## Current Education Mission
WGU BS Cybersecurity and Information Assurance.

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

## Do Not Build Yet
- Full LMS integration
- WGU login integration
- Browser automation
- Paid course marketplace
- Voice/video tutoring
- Public education product

## Success Criteria
1. Kyle can add a WGU course.
2. Kyle can start a study session.
3. Kyle can get a daily school brief.
4. Kyle can run quiz mode structure.
5. Kyle can review wrong answers.
6. Tests pass.
