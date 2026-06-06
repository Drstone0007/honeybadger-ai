"""Messaging gateway — Telegram, Slack, WhatsApp through Honey Badger."""

import json
import logging
import hmac
import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory sliding-window rate limiter per platform."""

    def __init__(self, default_max_per_min: int = 30):
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._default_max = default_max_per_min

    def check(self, key: str, max_per_min: int = 0) -> bool:
        now = time.time()
        window = now - 60
        bucket = self._buckets[key]
        bucket[:] = [t for t in bucket if t > window]
        limit = max_per_min or self._default_max
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True


@dataclass
class GatewayConfig:
    telegram_token: str = ""
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    whatsapp_token: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_phone_id: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    default_model: str = ""
    default_provider: str = "groq"
    default_api_key: str = ""
    system_prompt: str = "You are the IWAS Gateway Agent — routing messages through Honey Badger. Reply concisely and helpfully."
    webhook_base: str = ""
    rate_limit_per_min: int = 30


@dataclass
class IncomingMessage:
    platform: str            # "telegram" | "slack" | "whatsapp"
    channel_id: str          # chat/room/phone identifier for reply
    user_id: str             # sender identifier
    user_name: str           # display name
    text: str                # message text
    raw: dict = field(default_factory=dict)


@dataclass
class OutgoingMessage:
    platform: str
    channel_id: str
    text: str
    raw: Optional[dict] = None


class GatewayService:

    def __init__(self, config: Optional[GatewayConfig] = None):
        self.config = config or GatewayConfig()
        self._http = httpx.Client(timeout=30)
        self._rate_limiter = RateLimiter(default_max_per_min=30)

    def check_rate_limit(self, platform: str) -> bool:
        """Check if a platform has exceeded its rate limit."""
        return self._rate_limiter.check(platform, self.config.rate_limit_per_min)

    # ── Telegram ──────────────────────────────────────────

    def parse_telegram(self, body: dict) -> Optional[IncomingMessage]:
        """Parse a Telegram Update into an IncomingMessage."""
        msg = body.get("message") or body.get("callback_query", {}).get("message") or {}
        chat = msg.get("chat", {})
        text = msg.get("text", "") or body.get("callback_query", {}).get("data", "")
        user = msg.get("from", {})
        if not chat.get("id"):
            return None
        return IncomingMessage(
            platform="telegram",
            channel_id=str(chat["id"]),
            user_id=str(user.get("id", "")),
            user_name=user.get("first_name", "Telegram User"),
            text=text,
            raw=body,
        )

    def send_telegram(self, msg: OutgoingMessage) -> bool:
        """Send a message to Telegram via Bot API."""
        token = self.config.telegram_token
        if not token:
            logger.warning("Telegram: no bot token configured")
            return False
        try:
            r = self._http.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": msg.channel_id, "text": msg.text, "parse_mode": "Markdown"},
            )
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

    def set_telegram_webhook(self, url: str) -> bool:
        """Register webhook URL with Telegram Bot API."""
        token = self.config.telegram_token
        if not token:
            return False
        try:
            r = self._http.post(
                f"https://api.telegram.org/bot{token}/setWebhook",
                json={"url": url},
            )
            r.raise_for_status()
            data = r.json()
            return data.get("ok", False)
        except Exception as e:
            logger.error(f"Telegram webhook set error: {e}")
            return False

    # ── Slack ─────────────────────────────────────────────

    def parse_slack(self, body: dict, headers: dict) -> Optional[IncomingMessage]:
        """Parse a Slack Events API or slash command payload."""
        # Slash command
        if "command" in body and "text" in body:
            return IncomingMessage(
                platform="slack",
                channel_id=body.get("channel_id", ""),
                user_id=body.get("user_id", ""),
                user_name=body.get("user_name", "Slack User"),
                text=body.get("text", ""),
                raw=body,
            )
        # Events API — URL verification
        if body.get("type") == "url_verification":
            return None  # Handled at route level
        # Events API — message event
        event = body.get("event", {})
        if event.get("type") == "message" and "subtype" not in event:
            return IncomingMessage(
                platform="slack",
                channel_id=event.get("channel", ""),
                user_id=event.get("user", ""),
                user_name=event.get("user", "Slack User"),
                text=event.get("text", ""),
                raw=body,
            )
        return None

    def verify_slack_signature(self, body: bytes, timestamp: str, signature: str) -> bool:
        """Verify Slack's HMAC-SHA256 signing secret."""
        secret = self.config.slack_signing_secret
        if not secret:
            return True
        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        expected = "v0=" + hmac.new(
            secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def send_slack(self, msg: OutgoingMessage) -> bool:
        """Send a message to Slack via chat.postMessage."""
        token = self.config.slack_bot_token
        if not token:
            logger.warning("Slack: no bot token configured")
            return False
        try:
            r = self._http.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json={"channel": msg.channel_id, "text": msg.text, "mrkdwn": True},
            )
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Slack send error: {e}")
            return False

    # ── WhatsApp / Twilio ─────────────────────────────────

    def parse_whatsapp(self, body: dict) -> Optional[IncomingMessage]:
        """Parse a WhatsApp Business API or Twilio webhook."""
        # WhatsApp Business API (Graph API)
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "text":
                        text = msg["text"].get("body", "")
                        return IncomingMessage(
                            platform="whatsapp",
                            channel_id=value.get("metadata", {}).get("phone_number_id", "")
                                or msg.get("from", ""),
                            user_id=msg.get("from", ""),
                            user_name=msg.get("from", "WhatsApp User"),
                            text=text,
                            raw=body,
                        )
        # Twilio webhook format
        if body.get("Body") and body.get("From"):
            return IncomingMessage(
                platform="whatsapp",
                channel_id=body.get("To", ""),
                user_id=body.get("From", ""),
                user_name=body.get("From", "WhatsApp User"),
                text=body.get("Body", ""),
                raw=body,
            )
        return None

    def send_whatsapp(self, msg: OutgoingMessage) -> bool:
        """Send a WhatsApp message via Twilio or WhatsApp Business API."""
        # Prefer Twilio (simpler)
        if self.config.twilio_account_sid and self.config.twilio_auth_token:
            try:
                r = self._http.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.config.twilio_account_sid}/Messages.json",
                    auth=(self.config.twilio_account_sid, self.config.twilio_auth_token),
                    data={"To": msg.channel_id, "From": self.config.twilio_whatsapp_from or "whatsapp:+14155238886", "Body": msg.text},
                )
                r.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Twilio WhatsApp send error: {e}")
                return False
        # WhatsApp Business API fallback
        if self.config.whatsapp_token and self.config.whatsapp_phone_id:
            try:
                r = self._http.post(
                    f"https://graph.facebook.com/v18.0/{self.config.whatsapp_phone_id}/messages",
                    headers={"Authorization": f"Bearer {self.config.whatsapp_token}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": msg.channel_id,
                        "type": "text",
                        "text": {"body": msg.text},
                    },
                )
                r.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"WhatsApp Business send error: {e}")
                return False
        logger.warning("WhatsApp: no credentials configured")
        return False

    # ── LLM Routing ───────────────────────────────────────

    @staticmethod
    def _extract_model_override(text: str) -> tuple[str, str]:
        """Parse 'model:provider/model-name rest of message' from text."""
        for prefix in ("model:", "mdl:"):
            if text.startswith(prefix):
                rest = text[len(prefix):].lstrip()
                parts = rest.split(None, 1)
                if parts:
                    model_spec = parts[0]
                    remaining = parts[1] if len(parts) > 1 else ""
                    return remaining, model_spec
        return text, ""

    async def route_to_llm(self, msg: IncomingMessage) -> str:
        """Route a message through the IWAS/Honey Badger LLM."""
        text, model_override = self._extract_model_override(msg.text)

        model = model_override or self.config.default_model
        provider = self.config.default_provider
        api_key = self.config.default_api_key

        if not model:
            return "Gateway: no default model configured. Set via /api/gateway/config."
        msg.text = text

        from services.litellm_proxy import litellm_proxy_service
        try:
            status = litellm_proxy_service.detect(timeout=2.0)
            if status.running and status.models:
                # Use LiteLLM
                async with httpx.AsyncClient(timeout=60) as client:
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": self.config.system_prompt},
                            {"role": "user", "content": f"[{msg.platform}] {msg.user_name}: {msg.text}"},
                        ],
                        "max_tokens": 1024,
                    }
                    r = await client.post(
                        f"{status.url}/v1/chat/completions",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                    )
                    r.raise_for_status()
                    data = r.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
        except Exception:
            pass

        # Fallback: direct provider call
        if provider and api_key:
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.config.system_prompt},
                        {"role": "user", "content": f"[{msg.platform}] {msg.user_name}: {msg.text}"},
                    ],
                    "max_tokens": 1024,
                }
                urls = {
                    "groq": ("https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {api_key}"}),
                    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {api_key}"}),
                }
                if provider in urls:
                    url, headers = urls[provider]
                    headers["Content-Type"] = "application/json"
                    try:
                        r = await client.post(url, headers=headers, json=payload)
                        r.raise_for_status()
                        data = r.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
                    except Exception as e:
                        logger.error(f"Gateway LLM fallback error: {e}")

        return f"Received your message: \"{msg.text}\" — IWAS Gateway active. Configure LLM routing via /api/gateway/config."

    # ── Config Persistence ────────────────────────────────

    def load_config(self):
        """Load gateway config from JSON file."""
        from pathlib import Path
        config_file = Path("data/gateway_config.json")
        if config_file.exists():
            try:
                data = json.loads(config_file.read_text())
                for k, v in data.items():
                    if hasattr(self.config, k):
                        setattr(self.config, k, v)
            except Exception as e:
                logger.warning(f"Failed to load gateway config: {e}")

    def save_config(self) -> dict:
        """Save gateway config to JSON file."""
        from pathlib import Path
        config_file = Path("data/gateway_config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {k: getattr(self.config, k) for k in dir(self.config) if not k.startswith("_")}
        config_file.write_text(json.dumps(data, indent=2))
        return data


_gateway_service: Optional[GatewayService] = None


def get_gateway() -> GatewayService:
    global _gateway_service
    if _gateway_service is None:
        _gateway_service = GatewayService()
        _gateway_service.load_config()
    return _gateway_service
