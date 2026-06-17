# Client: Retras

## Identity

| Field | Value |
|---|---|
| Client ID | `redtras` |
| Company | Retras (and Citium — separate brand, same PMS platform) |
| Sector | Self-storage operator (trasteros), Spain |
| Contact | Jesús Fernandez (CEO), Ariana / Victoria (ops), Iago Salgueiro (tech lead) |
| Hosting | _TBD — likely client-hosted on their own infrastructure_ |
| Status | `onboarding` |
| First meeting | 2026-06-11 |

## Business context

Retras is a **highly automated self-storage operator**: no staff on-site, everything managed remotely via app, kiosks, smart lockers, and electronic locks. They operate two brands:

- **Retras** — owned centres + operated/partner centres, all answered as Retras
- **Citium** — white-label brand for an investment fund; separate phone number, separate PMS, separate DB

Both brands share the same technology platform (custom-built PMS with REST API), but have **separate database instances and separate URLs** — they must be treated as two separate client configurations.

Key services beyond basic storage:
- Smart lockers (Amazon-style parcel pickup/dropoff, 24h)
- Self-checkout kiosks (Redsys payment + digital notary for contracts)
- Access via app or PIN keypad; electronic locks on all units
- Corporate mailbox / domiciliation service

## Current pain points (from first meeting)

1. **Call centre is expensive and low quality** — external call centre does not know trasteros; Retras wants to replace weekend/out-of-hours answering with a WhatsApp + voice agent
2. **Debt collection is manual** — existing system sends SMS + email + app chat at D+0, D+2, D+6, D+30 but WhatsApp integration was never completed; human follow-up is required today
3. **Bank reconciliation is manual** — no automated webhook from bank for payment confirmation; must manually check 40 accounts monthly
4. **No cross-channel conversation history** — CRM notes are added manually; no automated summary from inbound conversations

## Modules to activate

| Module | Priority | Notes |
|---|---|---|
| Customer Service (WhatsApp) | P0 — first delivery | Replace external call centre; handle FAQs, auth, CRM lookup |
| Debt Collection (WhatsApp) | P0 — first delivery | Complete the missing WhatsApp channel in their existing D+N process |
| Voice | P1 — after WhatsApp stable | Outbound debt calls; inbound customer service via phone |
| Lead Management | P2 — future | Leads come in through separate campaigns per brand |

## Technical notes

### CRM / PMS
- Custom-built REST API (Iago is the tech lead)
- All endpoints are REST; new endpoints can be created on request
- Separate base URLs for Retras and Citium (`CLIENT_ID` = `redtras` and `citium`)

### Auth
- **Kiosk (self-service):** phone + DNI
- **Web area de cliente:** email (username) + password
- For agent auth: **phone + DNI** is the safe choice (matches kiosk flow; confirmed in meeting)

### Existing debt workflow
- Triggered when `recibo devuelto` (returned direct debit) is recorded
- Already sends SMS + email + app chat; WhatsApp integration has code but is not operational
- StorageIdol replaces/augments the WhatsApp channel
- D+N: soft first (immediate, D+2), escalating tone (D+6), final warning (~D+30)

### Payment
- **Redsys TPV virtual** (not Stripe) — payment links sent in debt messages
- TPV confirmation webhook available → can be used to auto-close debt cases

### Existing chatbot
- Web-only, out-of-hours only; conversational; still being trained
- Knowledge base can be exported as seed for StorageIdol KB

### Routing: two brands = two separate deployments
- Retras phone/WhatsApp → `CLIENT_ID=redtras`
- Citium phone/WhatsApp → `CLIENT_ID=citium` (separate config, separate deployment)
- Same codebase, same modules — different `config.yaml`, different CRM base URL

## Open questions / next steps

- [ ] Iago to share API documentation and available endpoints
- [ ] Confirm which D+N stage values Retras uses (exact days)
- [ ] Export existing chatbot knowledge base for KB ingestion
- [ ] Retras to provision WhatsApp Business Account + phone number for Retras brand
- [ ] Confirm if Citium brand will be onboarded in parallel or sequentially
- [ ] Confirm server hosting preference (client-hosted vs StorageIdol-hosted)
- [ ] Confirm Redsys webhook availability for payment confirmation
