#!/bin/bash
# start_testnet_vps.sh — VPS variant of scripts/start_testnet.sh
#
# Difference from the local/CI version: on a public VPS, opening 50
# unauthenticated write-capable API ports to the entire internet is a
# needless attack surface, especially since /v1/claim and
# /v1/action/verify have no auth in this reference implementation
# (see §7 Security Considerations, draft-gravit-vcp-00).
#
# Default behavior: only node-1 (port 8000) binds to 0.0.0.0, reachable
# publicly via Caddy's HTTPS reverse proxy on the domain. Nodes 2-50
# bind to 127.0.0.1 only — still fully usable for local demonstration
# and for any future gossip logic running on the same host, but not
# exposed to the open internet.
#
# Set PUBLIC_ALL_NODES=true to expose all 50 (e.g. if you deliberately
# want external parties to poke individual nodes during a review).

set -e

PUBLIC_ALL_NODES="${PUBLIC_ALL_NODES:-false}"

echo "🚀 Starting 50 EES VCP Testnet nodes (VPS mode, PUBLIC_ALL_NODES=$PUBLIC_ALL_NODES)..."

for i in {1..50}; do
  NODE_ID="node-$i"
  PORT=$((8000 + i - 1))

  if [ "$i" -eq 1 ] || [ "$PUBLIC_ALL_NODES" = "true" ]; then
    BIND="0.0.0.0:$PORT:8000"
  else
    BIND="127.0.0.1:$PORT:8000"
  fi

  docker compose run -d \
    --name "gravit-node-$i" \
    --publish "$BIND" \
    --env NODE_ID="$NODE_ID" \
    --env GRAVIT_ETA=0.2 \
    --env GRAVIT_GAMMA=1.5 \
    --env GRAVIT_EPSILON=0.1 \
    node
done

echo "✅ Testnet with 50 nodes deployed."
echo "Public (via Caddy HTTPS): https://<your-domain>/.well-known/vcp -> node-1"
echo "Local-only nodes: http://127.0.0.1:8001 through http://127.0.0.1:8049"
echo "Set PUBLIC_ALL_NODES=true before running this script to expose all 50."
