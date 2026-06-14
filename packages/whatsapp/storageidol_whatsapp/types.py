"""Pydantic models for WhatsApp Cloud API payloads."""

from __future__ import annotations

import enum
import json
from typing import Any

from pydantic import BaseModel


class WebhookEventType(str, enum.Enum):
    MESSAGE = "message"
    STATUS = "status"
    UNKNOWN = "unknown"


class InboundMessage(BaseModel):
    """A message received from a WhatsApp user."""

    message_id: str
    from_number: str    # E.164 format
    text: str | None = None
    media_type: str | None = None   # image | audio | document | video
    media_id: str | None = None
    timestamp: int      # Unix timestamp


class MessageStatus(BaseModel):
    """Delivery status update for a sent message."""

    message_id: str
    to_number: str
    status: str         # sent | delivered | read | failed
    timestamp: int


class ParsedWebhookEvent(BaseModel):
    """Normalized WhatsApp webhook event."""

    type: WebhookEventType
    phone_number_id: str   # Identifies which WhatsApp number/client received the event
    message: InboundMessage | None = None
    status: MessageStatus | None = None
    raw: dict[str, Any]


class TemplateComponent(BaseModel):
    """A component in a template message (header / body / button)."""

    type: str                        # header | body | button
    parameters: list[dict[str, Any]] = []


def parse_webhook(raw_body: bytes | str) -> ParsedWebhookEvent | None:
    """
    Parse a raw WhatsApp Cloud API webhook body into a typed event.

    Returns None if the payload is not a recognisable event (e.g. a ping).
    """
    try:
        data = json.loads(raw_body) if isinstance(raw_body, bytes) else json.loads(raw_body)
    except json.JSONDecodeError:
        return None

    # Standard Cloud API envelope
    try:
        entry = data["entry"][0]
        change = entry["changes"][0]["value"]
    except (KeyError, IndexError):
        return None

    phone_number_id = change.get("metadata", {}).get("phone_number_id", "")

    if "messages" in change:
        msg_data = change["messages"][0]
        msg_type = msg_data.get("type", "text")
        text_content = msg_data.get("text", {}).get("body") if msg_type == "text" else None

        return ParsedWebhookEvent(
            type=WebhookEventType.MESSAGE,
            phone_number_id=phone_number_id,
            message=InboundMessage(
                message_id=msg_data["id"],
                from_number=msg_data["from"],
                text=text_content,
                media_type=msg_type if msg_type != "text" else None,
                media_id=msg_data.get(msg_type, {}).get("id"),
                timestamp=int(msg_data.get("timestamp", 0)),
            ),
            raw=data,
        )

    if "statuses" in change:
        status_data = change["statuses"][0]
        return ParsedWebhookEvent(
            type=WebhookEventType.STATUS,
            phone_number_id=phone_number_id,
            status=MessageStatus(
                message_id=status_data["id"],
                to_number=status_data["recipient_id"],
                status=status_data["status"],
                timestamp=int(status_data.get("timestamp", 0)),
            ),
            raw=data,
        )

    return ParsedWebhookEvent(
        type=WebhookEventType.UNKNOWN,
        phone_number_id=phone_number_id,
        raw=data,
    )
