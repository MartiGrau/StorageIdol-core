# Clients

One folder per client. Each folder is the single source of truth for everything an AI agent needs to understand, configure, and develop that client's deployment.

## Folder purpose

Raw input (meetings, emails) lives in `meetings/` and `communications/` — but agents should not have to read all of it. The distilled, actionable signal lives in `requirements/` and `decisions.md`. Keep those up to date after every client interaction.

## How to start a new client

```bash
cp -r clients/_template clients/<client-id>
# Fill in clients/<client-id>/profile.md first
# Then work through requirements/ as discovery calls happen
```

Client ID convention: lowercase, hyphenated company name. Example: `real-estate-bcn`, `inversiones-sol`.

## Agent workflow for a client task

1. Read `clients/<client-id>/profile.md` — understand who they are and what modules they run
2. Read `clients/<client-id>/requirements/` — get the distilled specs
3. Read `clients/<client-id>/decisions.md` — understand constraints and closed questions
4. If you need raw context: check `meetings/` and `communications/`
5. When you make a new decision, add it to `decisions.md`
6. When you update a requirement, update the relevant file in `requirements/`

## Connecting to infrastructure

Each client's live configuration lives in `infrastructure/clients/<client-id>/config.yaml`. The `requirements/` files in this folder are the human/agent-readable source; `config.yaml` is the deployed output. Keep them in sync.

## Sensitive data

Client folders may contain personal and commercially sensitive information. This repo must remain private. Do not paste client data into public tools, logs, or prompts outside this repo.
