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
| _(none yet)_ | — | — | — | — | — |

## Adding a client

When a new client is signed:
1. Add a row to this table
2. Create their folder: `cp -r clients/_template clients/<client-id>`
3. Fill in `clients/<client-id>/profile.md`
4. Create `infrastructure/clients/<client-id>/config.yaml` from the infrastructure template
