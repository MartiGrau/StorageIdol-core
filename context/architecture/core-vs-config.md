# Core vs Configuration

Understanding this distinction is essential before making any architectural decision.

## The rule

**Never put client-specific logic in the Core layer. Never put reusable platform logic in a client config.**

## Core layer

Lives in: `apps/agents/`, `apps/api/`, `packages/`

- The LangGraph graph definitions (nodes, edges, conditional routing)
- Agent prompts that are client-agnostic (system prompts, output parsers)
- The debt scheduler engine and its D+N state machine
- The human escalation mechanism
- All third-party SDK wrappers (ElevenLabs, Twilio, WhatsApp, Stripe)
- Shared data models (contact, conversation, event, payment)
- The audit log writer

Changes here affect every client simultaneously. Treat changes to Core with the same care as a library release — breaking changes require a migration plan.

## Configuration layer

Lives in: `infrastructure/clients/<client-id>/` or a per-client DB schema

- WhatsApp message templates (text, variables, language)
- Conversational flow scripts and tone instructions
- Knowledge base documents (FAQs, property info, policies)
- CRM endpoint and auth credentials
- ElevenLabs voice ID and language settings
- D+N threshold values and escalation conditions
- Payment gateway credentials and link templates
- Notification endpoints (webhooks, Slack, email)

Changes here affect only that client. A misconfiguration cannot crash another client's environment.

## How a new client deployment works

1. Create `infrastructure/clients/<client-id>/config.yaml` from the template
2. Fill in all configuration keys (CRM, voice, templates, thresholds)
3. Run `scripts/provision-client.sh <client-id>` — creates DB schema, deploys config, runs smoke test
4. QA the flows in staging with real WhatsApp / Twilio test credentials
5. Flip DNS to client's subdomain → live

No code changes required for a standard client deployment.
