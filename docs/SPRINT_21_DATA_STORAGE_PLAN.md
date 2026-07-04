# Sprint 21 Data Storage Plan

## Current State
Project Salus currently uses local in-memory structures and JSON persistence for selected capability data.

## Short-Term Recommendation
Keep JSON for local MVP while refactoring routes.

## Medium-Term Recommendation
Create a persistence abstraction before moving to a database.

## Future Database Candidates
- SQLite for local desktop MVP
- PostgreSQL for cloud/team deployment
- Encrypted local store for sensitive personal/family data

## Required Before Database Migration
- Inventory all record groups
- Define schemas
- Define migration script
- Define backup/export process
- Add tests for persistence behavior
