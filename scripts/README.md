# Scripts

Utility scripts for development, operations, and client management.

## Planned scripts

| Script | Description |
|---|---|
| `provision-client.sh` | Create DB schema, load config, run smoke test for a new client |
| `deprovision-client.sh` | Remove client config and schema (does not delete historical data) |
| `seed-dev.sh` | Seed local dev database with test data |
| `check-health.sh` | Ping all service health endpoints and report status |
| `rotate-keys.sh` | Rotate API keys for a client environment |

Scripts should be idempotent, log clearly, and exit with a non-zero code on failure.
