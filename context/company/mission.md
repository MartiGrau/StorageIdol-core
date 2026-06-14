# Mission

StorageIdol automates high-volume, repetitive client interactions for real estate and financial companies using AI agents — so their human teams focus only on decisions that require judgment.

## Vision

Every company with recurring client communication (rentals, mortgages, debt portfolios) should have access to a 24/7 intelligent agent layer that feels human, speaks any language, and never drops a lead or a payment reminder.

## Product philosophy: Core + Configuration

The system is split into two layers:

**Core (owned by StorageIdol, reusable across all clients)**
- Multi-agent architecture built with LangGraph
- Voice synthesis via ElevenLabs
- Telephony via LiveKit + Telnyx (Spanish +34 SIP numbers)
- WhatsApp messaging via WhatsApp Cloud API
- Debt scheduler engine (D+N staged sequences)
- Human escalation logic
- Payment link integration

**Configuration (per-client, guided deployment)**
- Conversational flows and scripts
- WhatsApp message templates
- FAQ knowledge base and context injection
- CRM integration (per client)
- Voice branding and language settings
- Debt stage thresholds and amounts
- Dedicated subdomain and infrastructure slice

The client pays for the adaptation to their business, not for rebuilding the platform. StorageIdol works from a proven, already-deployed system.
