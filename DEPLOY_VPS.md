# Deploying Public VCP Testnet on a Generic VPS
### Fallback Option, Independent of Hostpoint Support Status

Utilizes the same principles as `scripts/start_testnet.sh` (verified in CI), plus `cloud-init` for automated provisioning during VPS creation, and `systemd` to ensure the testnet survives server reboots.

---

## 1. VPS Specifications

50 containers with a lightweight FastAPI application and in-memory storage constitute a light load, but to accommodate image builds and Docker overhead, we recommend:

| Parameter | Minimum | Recommended |
|---|---|---|
| vCPU | 2 | 4 |
| RAM | 4 GB | 8 GB |
| Disk | 40 GB SSD | 40 GB SSD |
| OS | Ubuntu 22.04/24.04 LTS | Ubuntu 24.04 LTS |

Suitable providers where cloud-init is a built-in feature upon instance creation (verify Hostpoint Flex Server support separately, as it may not support it): Hetzner Cloud, DigitalOcean, Scaleway. These are listed because cloud-init works out-of-the-box via web UI or CLI, which is critical for meeting deadlines.

## 2. DNS Configuration (Required in Advance)

You will need a subdomain pointing to the future IP of the VPS, e.g., `testnet.gravit.space` → A-record pointing to the server IP. This must be set up before launching Caddy for the first time, otherwise Let's Encrypt SSL certificate issuance will fail (Caddy validates DNS prior to certificate request).

## 3. Preparing Files Before VPS Creation

In [patches/vps/cloud-init.yaml](file:///root/gravit/gravitnet/patches/vps/cloud-init.yaml):
1. Replace `REPLACE_ME_DOMAIN` with the actual subdomain (e.g. `testnet.gravit.space`).
2. Replace `REPLACE_ME_REPO` with the repository URL (`https://github.com/GravitOpenNetwork/gravitnet.git`).

Ensure that the repository branch target contains:
- [scripts/start_testnet_vps.sh](file:///root/gravit/gravitnet/scripts/start_testnet_vps.sh)
- [scripts/stop_testnet.sh](file:///root/gravit/gravitnet/scripts/stop_testnet.sh)
- Previously applied patches in [apps/api/main.py](file:///root/gravit/gravitnet/apps/api/main.py) and [apps/api/routes/vcp.py](file:///root/gravit/gravitnet/apps/api/routes/vcp.py) (crucial — contains the root-level `/.well-known/vcp` fix, without which Caddy will proxy to a non-existent route)

Push these files to the repository before creating the VPS, otherwise the `runcmd` git clone will fetch an outdated version.

## 4. Creating VPS with cloud-init

Hetzner Cloud (CLI):
```bash
hcloud server create \
  --name gravit-testnet \
  --type cx22 \
  --image ubuntu-24.04 \
  --location nbg1 \
  --user-data-from-file patches/vps/cloud-init.yaml \
  --ssh-key <your-ssh-key-name>
```

DigitalOcean (CLI):
```bash
doctl compute droplet create gravit-testnet \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-4gb \
  --region fra1 \
  --user-data-file patches/vps/cloud-init.yaml \
  --ssh-keys <fingerprint>
```

Using web console: insert the contents of the cloud-init file into the "User data" or "Cloud-init" text area during instance creation.

First boot setup (installing Docker, Caddy, cloning repo, starting 50 nodes) typically takes 3 to 6 minutes.

## 5. Verification Post-Launch

```bash
ssh root@<server-IP>

# Check systemd testnet service status
systemctl status gravitnet-testnet.service

# Verify containers are running
docker ps --filter "name=gravit-node-"   # expect 50 lines

# Validate public HTTPS access to the discovery endpoint (as required by specification)
curl https://testnet.gravit.space/.well-known/vcp | jq '.'

# Check if Caddy certificate was issued (if not yet ready, wait a minute and check logs)
journalctl -u caddy --no-pager | tail -30
```

## 6. Public vs Private Endpoints (Security Design)
- `https://testnet.gravit.space/.well-known/vcp` — public, served over HTTPS as required by RFC 8615. This is the endpoint that can be safely referenced in Draft Section 9.
- `http://127.0.0.1:8001` ... `8049` on the host — **not exposed publicly by default**. Reason: `/v1/claim` and `/v1/action/verify` do not have authentication enabled in this reference implementation (see §7 Security Considerations), and leaving 49 open write-enabled API endpoints on a live server is not recommended.
- If you need to demo individual nodes to external reviewers, use an SSH tunnel (`ssh -L`), or temporarily restart the testnet service with `PUBLIC_ALL_NODES=true` (`systemctl restart gravitnet-testnet.service`) and revert it afterwards.

## 7. Lifecycle Commands

```bash
# Restart the testnet (e.g. after pulling updated code)
cd /opt/gravitnet && git pull && docker compose build
systemctl restart gravitnet-testnet.service

# Terminate and clean up all containers
systemctl stop gravitnet-testnet.service

# View logs for a specific node
docker logs gravit-node-1
```

## 8. Hostpoint Flex Server Deployment

The same `cloud-init.yaml` will work on Hostpoint Flex Server as long as Hostpoint supports: (a) root SSH access, (b) cloud-init provisioning or running `runcmd` scripts manually upon first login, (c) custom Docker Engine installs. If these conditions are not met, the general VPS option (Hetzner/DO/Scaleway) remains the primary target.

## 9. Pre-Draft Checklist

- [ ] Subdomain DNS A-record points to the server IP.
- [ ] curl `https://<domain>/.well-known/vcp` returns HTTP 200 with valid JSON.
- [ ] docker ps displays 50 active `gravit-node-*` containers.
- [ ] `systemctl is-enabled gravitnet-testnet.service` is `enabled` (persists reboot).
- [ ] Draft Section 9 explicitly links to the public discovery URL and notes the lack of cross-node sync.
