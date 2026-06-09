# Packages

Shared libraries imported by apps. Put code here when two or more apps need it.

## Planned packages

| Package | Language | Description |
|---|---|---|
| `packages/integrations` | Python | Third-party SDK wrappers (WhatsApp, Twilio, ElevenLabs, Stripe, CRM adapters) |
| `packages/models` | Python | Shared Pydantic data models (Contact, Conversation, Event, Payment) |
| `packages/ui` | TypeScript | Shared React components used by dashboard and backoffice |
| `packages/config` | Python | Client configuration loader and validator |

Each package has its own `README.md`, `pyproject.toml` or `package.json`, and `tests/` folder.
