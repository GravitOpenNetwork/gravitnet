#!/bin/bash
# verify_local.sh — runs the same checks as the CI workflow, locally.
# Assumes scripts/start_testnet.sh has already been run and node-1 is on
# localhost:8000, node-2 on localhost:8001.

set -e
FAILED=0

check() {
  local desc="$1"
  shift
  if "$@"; then
    echo "✅ $desc"
  else
    echo "❌ $desc"
    FAILED=1
  fi
}

echo "--- 1. Discovery endpoint (root-level, RFC 8615) ---"
curl -sf http://localhost:8000/.well-known/vcp | jq '.'
check "discovery reachable" curl -sf -o /dev/null http://localhost:8000/.well-known/vcp

echo "--- 2. Submit claim to node-1 ---"
RESP=$(curl -sf -X POST http://localhost:8000/v1/claim \
  -H "Content-Type: application/json" \
  -d '{"content":"test claim","provenance":[{"type":"url","src":"https://example.com"}],"method":"grover"}')
echo "$RESP" | jq '.'
CLAIM_ID=$(echo "$RESP" | jq -r '.claim_id')
[ -n "$CLAIM_ID" ] && [ "$CLAIM_ID" != "null" ]
check "claim_id returned" test -n "$CLAIM_ID"

echo "--- 3. Cross-node isolation check (expected: node-2 does NOT know this claim) ---"
if curl -sf http://localhost:8001/v1/claim/"$CLAIM_ID" > /dev/null 2>&1; then
  echo "❌ UNEXPECTED: node-2 knows about node-1's claim — Implementation Status §9 is stale, update the draft."
  FAILED=1
else
  echo "✅ Expected: no cross-node state sync yet (matches §9)."
fi

echo "--- 4. Verify action (default confidence 0.85 >= threshold 0.7 -> ACCEPTED) ---"
VRESP=$(curl -sf -X POST http://localhost:8000/v1/action/verify \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"test\",\"params\":{},\"basis\":[\"$CLAIM_ID\"],\"stake\":100,\"proposed_by\":\"did:test\"}")
echo "$VRESP" | jq '.'
STATUS=$(echo "$VRESP" | jq -r '.status')
[ "$STATUS" = "ACCEPTED" ]
check "action ACCEPTED as expected" test "$STATUS" = "ACCEPTED"
TRACE_ID=$(echo "$VRESP" | jq -r '.trace_id')

echo "--- 5. Retrieve trace ---"
curl -sf http://localhost:8000/v1/trace/"$TRACE_ID" | jq '.'
check "trace retrievable" curl -sf -o /dev/null http://localhost:8000/v1/trace/"$TRACE_ID"

echo "---"
if [ "$FAILED" -eq 0 ]; then
  echo "✅ All local checks passed."
else
  echo "❌ One or more checks failed — see above before relying on this for the draft's Implementation Status section."
  exit 1
fi
