# Local Run and Verification of VCP Testnet

This document describes the procedure for locally running a 50-node VCP testnet cluster and executing the automated API verification script.

---

## Prerequisites

To start and verify the testnet, you will need:
1. **Docker** (with Docker Compose v2 support)
2. **Bash** environment
3. **curl** and **jq** (required for the verification script)

---

## Step 1. Building Docker Images

Build the EES node image:
```bash
docker compose build node
```

---

## Step 2. Starting the 50-Node Testnet

To start 50 containers in a single Docker network, execute:
```bash
chmod +x scripts/start_testnet.sh
./scripts/start_testnet.sh
```

This script will run 50 nodes, mapping their ports sequentially from `8000` (for `node-1`) to `8049` (for `node-50`). All nodes will start inside the shared network `gravitnet_default`.

---

## Step 3. Local API Verification (Testing)

To ensure that all endpoints work and verify that behavior matches the specification in Section 9 of the draft, run:
```bash
chmod +x verify_local.sh
./verify_local.sh
```

The script will automatically check:
1. Discovery endpoint: `GET /.well-known/vcp` on `node-1`.
2. Claim submission: `POST /v1/claim` on `node-1` and verifying the returned `claim_id`.
3. Cross-node state isolation: ensuring that `node-2` **does not** know about the claim submitted to `node-1` (verifying state synchronization is indeed disabled).
4. Action verification: `POST /v1/action/verify` on `node-1` referencing the created claim (expecting `ACCEPTED` status since confidence is 0.85).
5. Action trace lookup: `GET /v1/trace/{trace_id}`.

---

## Troubleshooting and FAQ

### 1. Port is already allocated
If ports in the range 8000–8049 are in use by other processes on your machine, container creation will fail.
* You can terminate the blocking applications.
* To stop previously running nodes of the testnet, see the cleanup section below.

### 2. Cleaning and Stopping All Nodes
To completely stop and remove the testnet containers, run:
```bash
docker rm -f $(docker ps -aq --filter "name=gravit-node-") 2>/dev/null || true
```

### 3. Reviewing Container Logs
You can view logs for any individual node (e.g., `node-1`):
```bash
docker logs gravit-node-1
```

To watch logs in real-time, append the `-f` flag:
```bash
docker logs -f gravit-node-1
```

### 4. Changing GQRVP Parameters
If you need to change GQRVP settings (eta, gamma, epsilon) to test boundary conditions in the API, modify their values in the `environment` section of the `node` service inside `docker-compose.yml` and restart the testnet.
