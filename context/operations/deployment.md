# Deployment

## Environments

| Environment | Purpose | Branch |
|---|---|---|
| `dev` | Local development | any |
| `staging` | Integration testing, client demos | `develop` |
| `production` | Live client traffic | `main` |

## CI/CD

GitHub Actions runs on every push. Pipelines are defined in `.github/workflows/`.

Standard pipeline per service:
1. Lint + type check
2. Unit tests
3. Build Docker image
4. Push to container registry
5. Deploy to target environment (staging on `develop`, production on `main`)

## Deploying a new service version

```bash
# Trigger manually if needed
gh workflow run deploy.yml --field service=api --field env=staging
```

Deployments to production require a passing staging run and a manual approval step in GitHub Actions.

## Client provisioning

See `context/architecture/core-vs-config.md` for the conceptual split.

```bash
# Provision a new client environment
scripts/provision-client.sh <client-id>

# Deprovision (removes DB schema and config, does not delete data)
scripts/deprovision-client.sh <client-id>
```

Client configs live in `infrastructure/clients/<client-id>/config.yaml`.

## Rollback

```bash
# Roll back API to previous image tag
gh workflow run rollback.yml --field service=api --field tag=<previous-tag>
```

All rollbacks are logged. Notify the team in the ops channel before rolling back production.

## Health checks

Each service exposes `GET /health` returning `{"status": "ok"}`. Infrastructure monitors this endpoint and alerts on failure.
