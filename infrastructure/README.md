# Infrastructure

Docker, cloud configuration, CI/CD, and client provisioning resources.

## Structure

```
infrastructure/
├── docker/
│   ├── docker-compose.dev.yml      # Local dev stack (Postgres, Redis)
│   └── docker-compose.prod.yml     # Production baseline
├── clients/
│   └── <client-id>/
│       └── config.yaml             # Per-client configuration
├── k8s/                            # Kubernetes manifests (when ready)
└── scripts/                        # Infra-specific scripts
```

## Client configs

Each client gets a dedicated directory under `infrastructure/clients/<client-id>/`. The `config.yaml` file is the single source of truth for all client-specific settings. See `context/architecture/core-vs-config.md` for the full list of configurable keys.

Never put secrets in `config.yaml` — use environment variable references instead.
