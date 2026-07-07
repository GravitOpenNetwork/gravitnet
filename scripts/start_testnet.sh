#!/bin/bash
# EES VCP Testnet Launcher v0.1
# Starts 50 Docker containers simulating the EES nodes.

set -e

echo "🚀 Starting 50 EES VCP Testnet nodes..."
for i in {1..50}; do
  NODE_ID="node-$i"
  PORT=$((8000 + i))
  
  # Run the node container detached
  # Map external port $PORT to internal FastAPI port 8000
  NODE_ID="$NODE_ID" docker compose run -d \
    --name "gravit-node-$i" \
    --publish "$PORT:8000" \
    --env NODE_ID="$NODE_ID" \
    node
done

echo "✅ Testnet with 50 nodes successfully deployed."
echo "Nodes are accessible on http://localhost:8001 through http://localhost:8050"
