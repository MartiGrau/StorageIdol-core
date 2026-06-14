"""
storageidol-whatsapp — WhatsApp Cloud API client.

Usage:
    from storageidol_whatsapp import WhatsAppClient, parse_webhook

    client = WhatsAppClient(phone_number_id="123", access_token="...")
    await client.send_text(to="+34600000000", text="Hola!")
    await client.send_template(to="+34600000000", name="retras_debt_d3", language="es")

    # In webhook handler:
    event = parse_webhook(raw_body)
    if event.type == "message":
        print(event.message.text)
"""

from .client import WhatsAppClient
from .types import (
    InboundMessage,
    MessageStatus,
    ParsedWebhookEvent,
    TemplateComponent,
    WebhookEventType,
    parse_webhook,
)

__all__ = [
    "WhatsAppClient",
    "parse_webhook",
    "InboundMessage",
    "MessageStatus",
    "ParsedWebhookEvent",
    "TemplateComponent",
    "WebhookEventType",
]
