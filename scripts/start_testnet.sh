#!/bin/bash
# Start 50 nodes in a single network (non-matrix!)
set -e

echo "Starting 50-node VCP testnet..."
for i in {1..50}; do
  PORT=$((8000 + i - 1))
  NODE_ID="node-$i"
  echo "Starting $NODE_ID on port $PORT"
  docker compose run -d \
    --name "gravit-node-$i" \
    --publish "$PORT:8000" \
    --env NODE_ID="$NODE_ID" \
    --env GRAVIT_ETA=0.2 \
    --env GRAVIT_GAMMA=1.5 \
    --env GRAVIT_EPSILON=0.1 \
    node
done

echo "✅ 50 nodes running. First node: http://localhost:8000"
echo "Check /.well-known/vcp: curl http://localhost:8000/.well-known/vcp"
