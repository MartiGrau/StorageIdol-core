# EU AI Act — Compliance Guide

## Scope

StorageIdol deploys AI systems that interact directly with consumers (customers of self-storage operators). Under **EU AI Act Article 50**, these systems are classified as **general-purpose AI systems interacting with natural persons** and require specific transparency obligations.

StorageIdol operates as both:
- **Developer** of the AI system (the platform)
- **Deployer** of the AI system (each client deployment)

Clients are also deployers under the Act and must be informed of their obligations during onboarding.

## Article 50 — Mandatory AI disclosure

### Obligation

Any AI system that interacts directly with a natural person must **inform that person, in a clear and timely manner**, that they are interacting with an AI system — unless this is obvious from the context.

### Implementation

This obligation is **baked into Core and cannot be removed** by client configuration:

- **Voice calls**: The AI disclosure is injected as the opening of the first voice turn by `core/agents/storageidol_agents/modules/channel/formatter.py`. The call cannot begin with agent content before the disclosure.
- **WhatsApp**: The disclosure is prepended to the first message of every new conversation.

**The wording is client-configurable** in `clients/<id>/config.yaml` under the `disclosure:` key. The default Spanish wording is:

```yaml
disclosure:
  voice_greeting: "Esta llamada puede ser atendida por un asistente de inteligencia artificial en nombre de {brand_name}. Si prefiere hablar con una persona, dígalo en cualquier momento."
  whatsapp_first_message: "Hola 👋 Soy un asistente de inteligencia artificial de *{brand_name}*. Estoy aquí para ayudarte. ¿En qué puedo ayudarte hoy?"
```

Clients may change the wording but may **not** remove the disclosure. The `channel/formatter` enforces this: if `config.disclosure` is empty, the platform falls back to a hardcoded default.

### What "timely" means in practice

- Voice: before the AI speaks on any substantive topic (i.e., the first thing the caller hears)
- WhatsApp: in the first outbound message, before any question-answering content

## Recording and call monitoring

Under **Spanish LOPD-GDD / GDPR**, recording voice calls requires:
1. Informing the caller that the call may be recorded before recording starts
2. Stating the lawful basis (consent or legitimate interest)
3. Storing recordings no longer than necessary (default: 90 days)

**Implementation**: The voice greeting script must include a recording notice if call recording is enabled. This is configurable per client. If `voice.record_calls: true` in `config.yaml`, the formatter appends the recording notice to the voice_greeting disclosure.

## Debt collection conduct (Spanish law)

Spanish debt collection is regulated by **Circular BdE 5/2012** and general consumer protection law. Key rules:
- No contact before 08:00 or after 21:00 (local time)
- No contact on public holidays
- Cease contact immediately if debtor invokes right-to-silence in writing
- Cannot impersonate legal authorities or suggest legal consequences that are not imminent

**Implementation**: The debt collection scheduler (`core/agents/storageidol_agents/tasks.py`) enforces Spanish business hours before sending any WhatsApp template or initiating any voice call. Clients may configure stricter windows in `config.yaml` but not looser ones.

## GDPR / data protection

| Concern | Implementation |
|---|---|
| Lawful basis | Contract performance (service to debtor) + legitimate interest (contact management) |
| Data minimisation | `AgentState` carries only fields needed for the turn; no free-form PII stored in Redis |
| Retention | Conversation records: 24 months default; configurable per client down to 6 months |
| Right to erasure | `POST /contacts/{id}/erase` endpoint removes all PII; replaces with anonymised placeholders |
| Anthropic data processing | All messages to Claude are subject to Anthropic's DPA. Clients must be informed that conversation content is processed by a sub-processor (Anthropic). This is disclosed in the client contract. |
| Langfuse traces | Contain full conversation text. Access restricted to StorageIdol ops for client-hosted tier. |

## Client onboarding requirements

During client onboarding, StorageIdol must:
1. Provide the client with a **Data Processing Agreement (DPA)** addendum covering Anthropic and Langfuse as sub-processors
2. Confirm the client's privacy policy mentions AI-assisted customer service
3. Confirm WhatsApp terms of service compliance (no spam, approved templates only)
4. For debt collection clients: confirm they hold a valid debt collection mandate from the original creditor

## Adding new channels or interaction types

Any new channel or interaction type that involves natural persons must:
1. Include an AI disclosure at the start of the first interaction
2. Offer a clear opt-out path to human assistance
3. Be documented in this file before go-live
