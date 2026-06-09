# Client Onboarding

## Overview

Onboarding a new client takes 3–5 business days from signed contract to go-live.

## Steps

### 1. Kickoff call (Day 0)

Collect from client:
- CRM type and API credentials
- WhatsApp Business Account ID and phone number
- Twilio phone number (or provide one via StorageIdol account)
- ElevenLabs voice preference (language, tone, speed)
- Approved WhatsApp message templates
- Knowledge base documents (FAQs, property list, policies)
- Escalation contacts (name, phone, availability hours)
- Debt staging thresholds (D+N values, amounts per stage)

### 2. Configuration (Days 1–2)

- Create `infrastructure/clients/<client-id>/config.yaml` from template
- Fill all keys from kickoff call outputs
- Load knowledge base into vector store
- Submit WhatsApp templates to Meta for approval (24–72h, start early)
- Configure CRM webhook or polling adapter
- Run `scripts/provision-client.sh <client-id>`

### 3. Staging tests (Days 2–3)

- Test all conversation flows end-to-end in staging with real WhatsApp / Twilio test creds
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
