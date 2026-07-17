# Deploying VCP Testnet on AWS EC2

Uses the same concept as the Hetzner/DigitalOcean setup: `cloud-init` on first boot + `systemd` for process persistence. The difference on AWS is that firewall configurations are handled via Security Groups rather than `ufw` (you can leave the internal `ufw` configuration in the cloud-init file as an extra security layer; they do not conflict).

## 1. Cloud-init Configuration

Use [patches/vps/cloud-init.yaml](file:///root/gravit/gravitnet/patches/vps/cloud-init.yaml) without structural changes — replace `REPLACE_ME_DOMAIN` and `REPLACE_ME_REPO` as described previously. AWS accepts this file as "User data" during instance configuration; the format is identical.

## 2. Security Group Configuration (Analogous to UFW rules, but at AWS level)

```bash
aws ec2 create-security-group \
  --group-name gravit-testnet-sg \
  --description "VCP testnet - public 22/80/443 only"

SG_ID=$(aws ec2 describe-security-groups \
  --group-names gravit-testnet-sg \
  --query 'SecurityGroups[0].GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
  --protocol tcp --port 22 --cidr <your-IP>/32

aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

Ports 8001–8049 are intentionally left closed in the Security Group — using the same design as a standard VPS setup: `/v1/claim` and `/v1/action/verify` have no authentication enabled, meaning only `node-1` is exposed publicly via Caddy on port 443. SSH access (port 22) should ideally be restricted to your personal IP rather than open to `0.0.0.0/0`.

## 3. Instance Creation

```bash
aws ec2 run-instances \
  --image-id <ami-ubuntu-24.04-in-your-region> \
  --instance-type t3.medium \
  --key-name <your-ssh-key> \
  --security-group-ids "$SG_ID" \
  --user-data file://patches/vps/cloud-init.yaml \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=40,VolumeType=gp3}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=gravit-testnet}]'
```

`t3.medium` (2 vCPUs, 4 GB RAM) is the minimum recommended size in `DEPLOY_VPS.md`. For a comfortable buffer during image builds, `t3.large` (2 vCPUs, 8 GB RAM) is preferred.

Query the latest AMI ID for Ubuntu 24.04 in your target region:
```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text
```

## 4. Elastic IP & DNS setup

```bash
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id <instance-id> --allocation-id <alloc-id>
```

Point your A-record `testnet.gravit.space` to the allocated Elastic IP before Caddy starts for the first time (otherwise Caddy's automatic SSL certificate issuance will fail, as detailed in the general VPS setup).

## 5. Verification Commands (Same as general VPS guide)

```bash
ssh -i <key>.pem ubuntu@<Elastic-IP>
systemctl status gravitnet-testnet.service
docker ps --filter "name=gravit-node-"
curl https://testnet.gravit.space/.well-known/vcp | jq '.'
```

## 6. Budget Considerations (Non-Production Scale)

A `t3.medium` or `t3.large` running on-demand is intended as a short-lived testnet for demonstration/review, not a production-scale GON consensus setup. If this testnet is meant to be run continuously for months, explore AWS Savings Plans or Reserved Instances after the initial I-D review phase is complete.
