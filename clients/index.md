# Client Index

All active and pipeline clients at a glance. Update this file when a client's status changes.

## Status legend

| Status | Meaning |
|---|---|
| `prospect` | In conversation, not yet signed |
| `onboarding` | Signed, deployment in progress |
| `live` | Production deployment active |
| `churned` | No longer active |

## Clients

| Client ID | Company | Modules | Status | Go-live | Notes |
|---|---|---|---|---|---|
| `redtras` | Retras / Citium | Customer Service, Debt Collection | `onboarding` | TBD | Two brands (Retras + Citium), same PMS platform, separate DBs |

## Adding a client

When a new client is signed:
1. Add a row to this table
2. Run `scripts/provision-client.sh <client-id>` (copies `_template`, substitutes placeholders)
3. Fill in `clients/<client-id>/profile.md`
4. Fill in `clients/<client-id>/config.yaml` with values from the kickoff call
