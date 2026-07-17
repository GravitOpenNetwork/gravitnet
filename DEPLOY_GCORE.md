# Deploying VCP Testnet on Gcore Cloud

Verified against Gcore documentation (gcore.com/docs): Gcore Cloud VM supports native `cloud-init` via the **User data** field in both the Customer Portal and API. Since this mechanism is identical to the Hetzner/DO/AWS cloud-config implementation, the [patches/vps/cloud-init.yaml](file:///root/gravit/gravitnet/patches/vps/cloud-init.yaml) template can be reused without adjustments.

## 1. Via Gcore Customer Portal (Faster for Manual Launches)

1. Log in to the Gcore Customer Portal → Instances → Create Instance.
2. Select a Region (Core or Edge regions; Edge regions are suitable for this testnet, resource requirements are minimal).
3. Select Architecture — `x86-64`, Image — `Ubuntu 24.04 LTS`.
4. Choose Flavors — 2 vCPUs / 4 GB RAM minimum (see specifications in `DEPLOY_VPS.md`, but 4 vCPUs / 8 GB RAM is recommended for optimal performance during docker builds).
5. Locate the **Additional options** section → Enable **User data** → Insert the contents of [patches/vps/cloud-init.yaml](file:///root/gravit/gravitnet/patches/vps/cloud-init.yaml) (after updating `REPLACE_ME_DOMAIN` and `REPLACE_ME_REPO`).
6. Configure the subnet: if your region already has a routed network, use it; if creating a new subnet, select a CIDR block in private range (e.g. 10.0.0.0/24) with DHCP enabled.
7. Attach your SSH key and click Create Instance.

## 2. Via Gcore Cloud API (For CI/CD Pipelines & Automation)

Gcore Cloud is managed via a REST API using an API token generated in the Customer Portal (Profile → API Tokens). The exact JSON payload structure depends on the API version active in your region; verify the latest payload format at docs.gcore.com. Example structure:

```bash
curl -X POST \
  "https://api.gcore.com/cloud/v1/instances/<project_id>/<region_id>" \
  -H "Authorization: APIKey <your-token>" \
  -H "Content-Type: application/json" \
  -d @instance-create.json
```

Where `instance-create.json` defines flavor, image, networks, SSH keys, and a `user_data` property containing the **base64-encoded** content of `cloud-init.yaml` (this is required for the REST API; the Customer Portal UI does this conversion automatically).

```bash
# Encode cloud-init config before inserting it in the JSON payload
base64 -w0 patches/vps/cloud-init.yaml
```

## 3. Firewall Settings

Gcore Cloud uses Security Groups at the subnet layer, matching AWS. The same security parameters apply: open ports 22 (restricted to your SSH IP where possible), 80, and 443. Keep ports 8001–8049 closed as they are bound to localhost (`127.0.0.1`) in `start_testnet_vps.sh` and are not exposed.

## 4. DNS and Verification

Follow the general verification instructions: point your subdomain `testnet.gravit.space` A-record to your instance's public IP prior to first Caddy launch, then run:

```bash
ssh <user>@<gcore-instance-ip>
systemctl status gravitnet-testnet.service
docker ps --filter "name=gravit-node-"
curl https://testnet.gravit.space/.well-known/vcp | jq '.'
```

## 5. Why Choose Gcore Cloud

If region/data center location proximity is important for GON (Gcore provides extensive Edge and Core regions across Europe, offering closer coverage to EU/CH audiences than some AWS regions), it can serve as a primary deployment option. For basic verification/review of the Internet-Draft, select the provider you currently hold an active account with to avoid verification delays.
