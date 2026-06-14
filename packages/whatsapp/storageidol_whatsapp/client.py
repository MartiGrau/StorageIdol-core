"""
WhatsApp Cloud API HTTP client.

Wraps the Meta Graph API for sending messages.
HMAC signature validation is handled in core/api (webhook layer).
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .types import TemplateComponent

logger = logging.getLogger(__name__)

_API_VERSION = "v20.0"
_BASE_URL = f"https://graph.facebook.com/{_API_VERSION}"


class WhatsAppClient:
    """
    Async WhatsApp Cloud API client.

    Args:
        phone_number_id: The WhatsApp Business phone number ID.
        access_token:    The long-lived access token from Meta Business Manager.
    """

    def __init__(self, phone_number_id: str, access_token: str) -> None:
        self._phone_number_id = phone_number_id
        self._client = httpx.AsyncClient(
            base_url=_BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def send_text(self, to: str, text: str) -> dict[str, Any]:
        """
        Send a free-form text message within a 24-hour session window.

        Args:
            to:   Recipient E.164 phone number (e.g. "+34600000000").
            text: Message body (max 4096 chars).
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
        response = await self._client.post(
            f"/{self._phone_number_id}/messages", json=payload
        )
        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def send_template(
        self,
        to: str,
        name: str,
        language: str = "es",
        components: list[TemplateComponent] | None = None,
    ) -> dict[str, Any]:
        """
        Send an approved Meta template message (e.g. debt-collection D+N messages).

        Args:
            to:         Recipient E.164 phone number.
            name:       Template name (must be Meta-approved, e.g. "retras_debt_d3").
            language:   BCP-47 language code (default "es").
            components: Template components with variable substitutions.
        """
        template_payload: dict[str, Any] = {
            "name": name,
            "language": {"code": language},
        }
        if components:
            template_payload["components"] = [c.model_dump() for c in components]

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template_payload,
        }
        response = await self._client.post(
            f"/{self._phone_number_id}/messages", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def send_reaction(self, to: str, message_id: str, emoji: str) -> dict[str, Any]:
        """React to an inbound message with an emoji."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "reaction",
            "reaction": {"message_id": message_id, "emoji": emoji},
        }
        response = await self._client.post(
            f"/{self._phone_number_id}/messages", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """Mark an inbound message as read (shows double blue tick)."""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        response = await self._client.post(
            f"/{self._phone_number_id}/messages", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "WhatsAppClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    @staticmethod
    def verify_signature(body: bytes, signature: str, app_secret: str) -> bool:
        """
        Verify the X-Hub-Signature-256 header from Meta.

        Should be called in the webhook handler before processing any payload.
        """
        expected = "sha256=" + hmac.new(
            app_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
