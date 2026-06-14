#!/usr/bin/env bash
# scripts/build-image.sh <client-id> [version]
#
# Builds and pushes Docker images for all platform services + the per-client MCP.
#
# Images built:
#   registry.storageidol.com/platform-api:<version>
#   registry.storageidol.com/platform-agents:<version>
#   registry.storageidol.com/platform-voice:<version>
#   registry.storageidol.com/platform-dashboard:<version>
#   registry.storageidol.com/watchdog:<version>
#   registry.storageidol.com/mcp-<client-id>:<version>
#
# Platform images are shared across all clients — building one builds for all.
# Run this after any Core change. The MCP image is client-specific.

set -euo pipefail

CLIENT_ID="${1:?Usage: $0 <client-id> [version]}"
VERSION="${2:-$(git rev-parse --short HEAD)}"
REGISTRY="registry.storageidol.com"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "→ Building images for client: $CLIENT_ID  version: $VERSION"

# ── Platform images (shared across all clients) ───────────────────────────────
build_platform() {
  local service="$1"
  local context="$2"
  local dockerfile="${3:-$context/Dockerfile}"
  echo "→ Building $REGISTRY/$service:$VERSION"
  docker build \
    -t "$REGISTRY/$service:$VERSION" \
    -t "$REGISTRY/$service:latest" \
    -f "$dockerfile" \
    "$context"
  docker push "$REGISTRY/$service:$VERSION"
  docker push "$REGISTRY/$service:latest"
}

build_platform "platform-api"       "$REPO_ROOT/core/api"
build_platform "platform-agents"    "$REPO_ROOT/core/agents"
build_platform "platform-voice"     "$REPO_ROOT/packages/voice"
build_platform "platform-dashboard" "$REPO_ROOT/core/dashboard"
build_platform "watchdog"           "$REPO_ROOT/core/watchdog"

# ── Per-client MCP image ──────────────────────────────────────────────────────
MCP_DIR="$REPO_ROOT/clients/$CLIENT_ID/mcp"
if [[ ! -f "$MCP_DIR/Dockerfile" ]]; then
  echo "ERROR: clients/$CLIENT_ID/mcp/Dockerfile not found."
  echo "Run /build-mcp $CLIENT_ID first to generate the MCP server."
  exit 1
fi

echo "→ Building $REGISTRY/mcp-$CLIENT_ID:$VERSION"
docker build \
  -t "$REGISTRY/mcp-$CLIENT_ID:$VERSION" \
  -t "$REGISTRY/mcp-$CLIENT_ID:latest" \
  "$MCP_DIR"
docker push "$REGISTRY/mcp-$CLIENT_ID:$VERSION"
docker push "$REGISTRY/mcp-$CLIENT_ID:latest"

# ── Update deploy config with pinned version ──────────────────────────────────
DEPLOY_COMPOSE="$REPO_ROOT/deploy/clients/$CLIENT_ID/docker-compose.yml"
if [[ -f "$DEPLOY_COMPOSE" ]]; then
  sed -i.bak "s|:<[^>]*VERSION[^>]*>|:$VERSION|g" "$DEPLOY_COMPOSE"
  rm -f "$DEPLOY_COMPOSE.bak"
  echo "→ Pinned version $VERSION in deploy/clients/$CLIENT_ID/docker-compose.yml"
fi

echo ""
echo "✓ All images built and pushed for $CLIENT_ID @ $VERSION"
