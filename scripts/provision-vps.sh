#!/usr/bin/env bash
# scripts/provision-vps.sh <client-id> [provider]
#
# Provisions a dedicated VPS for clients who don't have their own server.
# StorageIdol manages the infrastructure; cost is billed through.
#
# Prerequisites:
#   - clients/<client-id>/profile.md has "hosting: storageidol"
#   - hcloud CLI (Hetzner) or doctl (DigitalOcean) authenticated
#   - deploy/clients/<client-id>/ exists (run provision-client.sh first)
#
# What it does:
#   1. Create a VPS (Hetzner CX32 or equivalent)
#   2. Configure SSH, firewall, Docker, Docker Compose
#   3. Push deploy/clients/<client-id>/ to the server
#   4. Pull images and start the stack
#   5. Register the watchdog with ops.storageidol.com

set -euo pipefail

CLIENT_ID="${1:?Usage: $0 <client-id> [hetzner|digitalocean]}"
PROVIDER="${2:-hetzner}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$REPO_ROOT/deploy/clients/$CLIENT_ID"

# ── Validate ──────────────────────────────────────────────────────────────────
if [[ ! -d "$DEPLOY_DIR" ]]; then
  echo "ERROR: deploy/clients/$CLIENT_ID/ not found."
  echo "Run scripts/provision-client.sh $CLIENT_ID first."
  exit 1
fi

PROFILE="$REPO_ROOT/clients/$CLIENT_ID/profile.md"
if ! grep -q "hosting: storageidol" "$PROFILE" 2>/dev/null; then
  echo "WARNING: clients/$CLIENT_ID/profile.md does not specify 'hosting: storageidol'."
  echo "This script is for StorageIdol-managed VPS only. Client-managed servers"
  echo "should receive deploy/clients/$CLIENT_ID/ and run it themselves."
  read -rp "Continue anyway? [y/N] " confirm
  [[ "$confirm" == "y" ]] || exit 1
fi

echo "→ Provisioning VPS for client: $CLIENT_ID  provider: $PROVIDER"

# ── Create server ─────────────────────────────────────────────────────────────
case "$PROVIDER" in
  hetzner)
    SERVER_NAME="storageidol-$CLIENT_ID"
    SERVER_TYPE="cx32"     # 4 vCPU, 8 GB RAM — adequate for single-client stack
    IMAGE="ubuntu-24.04"
    echo "→ Creating Hetzner server: $SERVER_NAME ($SERVER_TYPE, $IMAGE)"
    # hcloud server create \
    #   --name "$SERVER_NAME" \
    #   --type "$SERVER_TYPE" \
    #   --image "$IMAGE" \
    #   --ssh-key storageidol-ops \
    #   --location nbg1 \
    #   --label client="$CLIENT_ID"
    echo "  [DRY RUN] hcloud server create ..."
    ;;
  digitalocean)
    echo "→ Creating DigitalOcean droplet for $CLIENT_ID"
    # doctl compute droplet create "storageidol-$CLIENT_ID" \
    #   --size s-2vcpu-4gb \
    #   --image ubuntu-24-04-x64 \
    #   --region ams3 \
    #   --ssh-keys <fingerprint>
    echo "  [DRY RUN] doctl compute droplet create ..."
    ;;
  *)
    echo "ERROR: Unknown provider '$PROVIDER'. Supported: hetzner, digitalocean"
    exit 1
    ;;
esac

# ── Bootstrap Docker on the server ───────────────────────────────────────────
# SERVER_IP=$(hcloud server describe "$SERVER_NAME" -o json | jq -r '.public_net.ipv4.ip')
# ssh root@$SERVER_IP 'apt-get update && apt-get install -y docker.io docker-compose-plugin'

echo "→ [STUB] Bootstrap Docker + Docker Compose on server"

# ── Push deploy config ────────────────────────────────────────────────────────
# scp "$DEPLOY_DIR/docker-compose.yml" root@$SERVER_IP:/opt/storageidol/
# scp "$DEPLOY_DIR/.env" root@$SERVER_IP:/opt/storageidol/  # .env must exist!

echo "→ [STUB] Push deploy/clients/$CLIENT_ID/ to server"
echo "  NOTE: .env must be created from .env.example with real secrets before this step."

# ── Start the stack ───────────────────────────────────────────────────────────
# ssh root@$SERVER_IP 'cd /opt/storageidol && docker compose pull && docker compose up -d'

echo "→ [STUB] docker compose pull && up -d"

echo ""
echo "✓ VPS provisioning stub complete for $CLIENT_ID."
echo "  This script contains dry-run stubs. Uncomment the real commands after"
echo "  creating SSH key 'storageidol-ops' and authenticating the provider CLI."
