# Package: whatsapp

WhatsApp Cloud API client.

**Language:** Python | **Key dependency:** `httpx`

## What it provides

- `WhatsAppClient(phone_number_id, access_token)` 
- `send_text(to, body)` — Session message (within 24h window)
- `send_template(to, template_name, language, components)` — Template message (outside 24h window or first contact)
- `send_media(to, media_type, url, caption)` — Image, document, audio
- `mark_read(message_id)` — Mark incoming message as read
- `parse_webhook(payload, signature, secret) -> WebhookEvent` — Validate + parse inbound webhook

## Important constraint

Template messages must be pre-approved by Meta. Templates are stored per client in `clients/<id>/debt-templates.yaml` and `clients/<id>/config.yaml`. This client never hard-codes template names — they are always loaded from config.
