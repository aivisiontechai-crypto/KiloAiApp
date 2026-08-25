from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Webhook:
    id: str
    url: str
    events: list[str]
    secret: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class WebhookManager:
    def __init__(self) -> None:
        self._webhooks: dict[str, Webhook] = {}
        self._next_id = 1

    def register_webhook(self, url: str, events: list[str], secret: str = "") -> Webhook:
        webhook = Webhook(
            id=str(self._next_id),
            url=url,
            events=events,
            secret=secret or secrets.token_hex(16),
        )
        self._next_id += 1
        self._webhooks[webhook.id] = webhook
        logger.info("Registered webhook %s -> %s", webhook.id, url)
        return webhook

    def unregister_webhook(self, webhook_id: str) -> bool:
        if webhook_id in self._webhooks:
            del self._webhooks[webhook_id]
            return True
        return False

    def get_webhooks(self) -> list[Webhook]:
        return list(self._webhooks.values())

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)

    def sign_payload(self, webhook: Webhook, payload: dict) -> str:
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        if not webhook.secret:
            return ""
        return hmac.new(webhook.secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
