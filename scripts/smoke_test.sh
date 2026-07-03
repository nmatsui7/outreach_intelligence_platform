#!/usr/bin/env bash
# AI Feature Smoke Test
# Usage: bash scripts/smoke_test.sh [base_url]
BASE="${1:-http://127.0.0.1:8000}"
PASS=0
FAIL=0

check() {
  local label="$1" method="$2" url="$3" expect="${4:-200}"
  local args=(-s -o /tmp/smoke_test_resp.txt -w "%{http_code}")
  if [ "$method" = "POST" ]; then args+=(-X POST); fi
  code=$(curl "${args[@]}" "$BASE$url" 2>/dev/null)
  if [ "$code" = "$expect" ]; then
    echo "  PASS [$code] $label"
    ((PASS++))
  else
    echo "  FAIL [$code] $label (expected $expect)"
    head -c 200 /tmp/smoke_test_resp.txt 2>/dev/null
    echo
    ((FAIL++))
  fi
}

echo "=== AI Feature Smoke Test ==="
echo ""

check "Health check"          GET  /api/health
check "Organizations list"    GET  /api/organizations
check "Org detail (WPL)"      GET  /api/organizations/1
check "AI Summary"            GET  /api/organizations/1/summary
check "AI Opportunity Analysis" GET /api/organizations/1/opportunities
check "AI Readiness Assessment" POST /api/organizations/1/readiness-assessment
check "Meeting Brief"         GET  /api/organizations/1/meeting-brief
check "Outreach Recommendation" GET /api/organizations/1/outreach-recommendation
check "Interactions"          GET  /api/organizations/1/interactions
check "Knowledge Summary"     GET  /api/organizations/1/knowledge-summary
check "Workflow Opportunities" GET /api/organizations/1/workflow-opportunities
check "Knowledge Sources"     GET  /api/organizations/1/knowledge-sources
check "Failure Cases"         GET  /api/organizations/1/failure-cases
check "Adoption Risk Notes"   GET  /api/organizations/1/adoption-risk-notes
check "Adoption Principles"   GET  /api/adoption-principles
check "Adoption Plan"         GET  /api/organizations/1/adoption-plan
check "Pilot Plans"           GET  /api/organizations/1/pilot-plans
check "Success Metrics"       GET  /api/organizations/1/success-metrics
check "Global Pilot Plans"    GET  /api/pilot-plans
check "Global Success Metrics" GET  /api/success-metrics
check "Outbox"                GET  /api/outbox
check "Analytics Summary"     GET  /api/analytics/summary
check "Knowledge Search"      GET  '/api/knowledge/search?q=follow-up'

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
