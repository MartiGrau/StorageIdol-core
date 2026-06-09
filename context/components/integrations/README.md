# Component: Integrations

Adapters for third-party services. Each integration is a thin wrapper that normalizes external APIs into internal interfaces.

**App location:** `packages/integrations/` (shared library, imported by `apps/agents/` and `apps/api/`)

## Included integrations

### WhatsApp Cloud API
- Send template messages (outbound)
- Send session messages (reply within 24h window)
- Receive and parse inbound message webhooks
- Status callbacks (delivered, read, failed)

### Twilio
- Place outbound calls with TwiML instructions
- Receive inbound call webhooks
- Transcription callbacks
- Call recording retrieval

### ElevenLabs
- Text-to-speech synthesis (streaming and buffered)
- Voice profile management
- Language and accent configuration

### Stripe
- Generate payment links with prefilled amount and metadata
- Webhook listener for payment completion events

### CRM adapters
- Generic interface: `get_contact`, `update_contact`, `create_activity`, `get_unpaid_invoices`
- Implementations: HubSpot, Salesforce, custom REST (per client)

**Owned by:** Backend / Platform team
