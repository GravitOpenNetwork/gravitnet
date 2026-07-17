#!/bin/bash
# stop_testnet.sh — clean teardown, referenced by ExecStop in
# gravitnet-testnet.service.
set -e
echo "Stopping and removing all gravit-node-* containers..."
docker rm -f $(docker ps -aq --filter "name=gravit-node-") 2>/dev/null || true
echo "Done."
