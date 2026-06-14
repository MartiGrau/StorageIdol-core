# Client Onboarding

## Overview

Onboarding a new client requires **3–5 days of StorageIdol engineering effort**, but is gated by external approvals that typically add **1–3 weeks of calendar time**:

- **Meta WABA verification** — 2–10 business days (can run in parallel with config)
- **WhatsApp template approval** — 24–72 hours per template batch
- **Telnyx ES DID provisioning** — 1–5 business days for Spanish +34 numbers

Plan for a minimum of **2 weeks** from kickoff to go-live when Spanish voice numbers or new Meta accounts are involved.

## Steps

### 1. Kickoff call (Day 0)

Collect from client:
- CRM type and API credentials
- WhatsApp Business Account ID and phone number
- Spanish +34 phone number for voice (provisioned via Telnyx — start request on Day 0, takes 1–5 business days)
- ElevenLabs voice preference (language, tone, speed)
- Approved WhatsApp message templates (submit to Meta Day 1 — approval takes 24–72h)
- Knowledge base documents (FAQs, property list, policies)
- Escalation contacts (name, phone, availability hours)
- Debt staging thresholds (D+N values, amounts per stage)

### 2. Configuration (Days 1–2)

- Run `scripts/provision-client.sh <client-id>` (creates `clients/<client-id>/` from template)
- Fill all keys in `clients/<client-id>/config.yaml` from kickoff call outputs
- Load knowledge base into vector store
- Submit WhatsApp templates to Meta for approval (24–72h, start early)
- Configure CRM webhook or polling adapter
- Build and push the client MCP image: `scripts/build-image.sh <client-id>` (requires human review — MCP code handles real CRM credentials and PII)

### 3. Staging tests (Days 2–3)

- Test all conversation flows end-to-end in staging with real WhatsApp + LiveKit dev credentials
- Validate debt scheduler triggers from a dummy CRM entry
- Test human escalation handoff
- Review voice quality with client on a test call
- Confirm payment link generation and tracking

### 4. Go-live (Days 3–5)

- Switch to production credentials in client config
- Set DNS for client subdomain
- Monitor first 48h of live traffic closely
- Deliver handover doc with admin access and escalation runbook

## Post go-live

- 30-day check-in call: review conversion rates, missed escalations, call quality
- 60-day upsell review: present usage data, propose additional modules
