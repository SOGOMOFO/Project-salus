#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${SALUS_BASE_URL:-http://127.0.0.1:8010}"
TOKEN="${SALUS_LOCAL_TOKEN:-salus-local-token}"

echo "Smoke checking Project Salus at ${BASE_URL}"

curl -fsS "${BASE_URL}/api/mission-control/auth/status" | python3 -m json.tool >/dev/null
echo "OK auth status"

curl -fsS "${BASE_URL}/api/mission-control/dashboard" | python3 -m json.tool >/dev/null
echo "OK dashboard API"

curl -fsS "${BASE_URL}/api/mission-control/mvp-readiness" | python3 -m json.tool >/dev/null
echo "OK readiness API"

curl -fsS "${BASE_URL}/mission-control/v1" \
  -H "x-salus-token: ${TOKEN}" \
  | grep -q "Command Center"

echo "OK dashboard HTML"

echo "Smoke check complete"
