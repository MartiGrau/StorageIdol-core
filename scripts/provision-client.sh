#!/usr/bin/env bash
# scripts/provision-client.sh <client-id>
#
# Bootstraps a new client deployment directory from the _template.
# Called by the /new-client Claude skill and by CI.
#
# Steps:
#   1. Validate client profile exists (clients/<id>/profile.md)
#   2. Copy _template structure into clients/<id>/ (skip existing files)
#   3. Substitute <CLIENT_ID> placeholder in all generated files
#   4. Generate deploy/clients/<id>/docker-compose.yml and .env.example
#   5. Create clients/<id>/feedback/ directory with schema CSV
#
# The Claude /new-client agent handles the intelligent parts (config.yaml,
# graph.py, MCP tools). This script handles the mechanical file scaffolding.

set -euo pipefail

CLIENT_ID="${1:?Usage: $0 <client-id>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$REPO_ROOT/clients/_template"
CLIENT_DIR="$REPO_ROOT/clients/$CLIENT_ID"
DEPLOY_TEMPLATE="$REPO_ROOT/deploy/_template"
DEPLOY_CLIENT_DIR="$REPO_ROOT/deploy/clients/$CLIENT_ID"

# ── 1. Validate ───────────────────────────────────────────────────────────────
if [[ ! -d "$CLIENT_DIR" ]]; then
  echo "ERROR: clients/$CLIENT_ID/ does not exist."
  echo "Create clients/$CLIENT_ID/profile.md from clients/_template/profile.md first."
  exit 1
fi

echo "→ Provisioning client: $CLIENT_ID"

# ── 2. Copy template structure (skip existing files) ─────────────────────────
echo "→ Scaffolding client directory from _template..."
rsync -a --ignore-existing --exclude='.gitkeep' "$TEMPLATE_DIR/" "$CLIENT_DIR/"

# ── 3. Substitute placeholder in copies (not in _template itself) ─────────────
echo "→ Substituting CLIENT_ID placeholder..."
find "$CLIENT_DIR" -type f \( -name "*.yaml" -o -name "*.md" -o -name "*.ts" \) | \
  xargs sed -i.bak "s/<CLIENT_ID>/$CLIENT_ID/g"
find "$CLIENT_DIR" -name "*.bak" -delete

# ── 4. Generate deploy config ─────────────────────────────────────────────────
echo "→ Generating deploy/clients/$CLIENT_ID/..."
mkdir -p "$DEPLOY_CLIENT_DIR"
cp "$DEPLOY_TEMPLATE/docker-compose.yml" "$DEPLOY_CLIENT_DIR/docker-compose.yml"
cp "$DEPLOY_TEMPLATE/.env.example" "$DEPLOY_CLIENT_DIR/.env.example"
sed -i.bak "s/<CLIENT_ID>/$CLIENT_ID/g" "$DEPLOY_CLIENT_DIR/docker-compose.yml"
sed -i.bak "s/<VERSION>/latest/g" "$DEPLOY_CLIENT_DIR/docker-compose.yml"
find "$DEPLOY_CLIENT_DIR" -name "*.bak" -delete
echo "  → Remember to pin <VERSION> before going to production."

# ── 5. Feedback directory ─────────────────────────────────────────────────────
mkdir -p "$CLIENT_DIR/feedback"
if [[ ! -f "$CLIENT_DIR/feedback/feedback.csv" ]]; then
  cat > "$CLIENT_DIR/feedback/feedback.csv" <<CSV
conversation_id,environment,date,category,description,expected_behavior,actual_behavior,priority,resolved
# category: wrong_intent | wrong_auth | wrong_response | missing_escalation | hallucination | voice_quality | other
# priority: low | medium | high
# environment: dev | prod
CSV
  echo "→ Created clients/$CLIENT_ID/feedback/feedback.csv"
fi

echo ""
echo "✓ Client $CLIENT_ID provisioned."
echo ""
echo "Next steps:"
echo "  1. Fill in clients/$CLIENT_ID/config.yaml (all <PLACEHOLDER> values)"
echo "  2. Run: /build-mcp $CLIENT_ID   (generate the MCP server)"
echo "  3. Run: /simulate $CLIENT_ID    (validate graph with mock MCP)"
echo "  4. Fill in deploy/clients/$CLIENT_ID/.env.example → .env on the server"
echo "  5. Run: scripts/build-image.sh $CLIENT_ID"
