"""Gateway routes — webhook endpoints for Telegram, Slack, WhatsApp."""

import json
import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional

from services.gateway import get_gateway, GatewayConfig, OutgoingMessage

logger = logging.getLogger(__name__)


class GatewayConfigUpdate(BaseModel):
    telegram_token: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    whatsapp_token: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_from: Optional[str] = None
    default_model: Optional[str] = None
    default_provider: Optional[str] = None
    default_api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    webhook_base: Optional[str] = None
    rate_limit_per_min: Optional[int] = None


def setup_gateway_routes():
    router = APIRouter(prefix="/api/gateway", tags=["gateway"])

    def gw() -> GatewayService:
        return get_gateway()

    # ── Telegram ──────────────────────────────────────────

    @router.post("/telegram")
    async def telegram_webhook(request: Request):
        """Receive Telegram Bot API updates."""
        if not gw().check_rate_limit("telegram"):
            return {"ok": True, "error": "rate_limited"}
        body = await request.json()
        msg = gw().parse_telegram(body)
        if not msg:
            return {"ok": True}
        reply = await gw().route_to_llm(msg)
        gw().send_telegram(OutgoingMessage(
            platform="telegram", channel_id=msg.channel_id, text=reply,
        ))
        return {"ok": True}

    # ── Slack ─────────────────────────────────────────────

    @router.post("/slack")
    async def slack_webhook(request: Request):
        """Receive Slack Events API / slash commands."""
        body_raw = await request.body()
        body = await request.json()

        # URL verification handshake
        if body.get("type") == "url_verification":
            return JSONResponse(content={"challenge": body.get("challenge", "")})
        if not gw().check_rate_limit("slack"):
            return {"ok": True, "error": "rate_limited"}

        # Verify Slack signature
        sig = request.headers.get("X-Slack-Signature", "")
        ts = request.headers.get("X-Slack-Request-Timestamp", "")
        if sig and ts and gw().config.slack_signing_secret:
            if not gw().verify_slack_signature(body_raw, ts, sig):
                raise HTTPException(status_code=401, detail="Invalid Slack signature")

        msg = gw().parse_slack(body, dict(request.headers))
        if not msg:
            return {"ok": True}

        # Slash commands need immediate 200 response
        if "command" in body:
            reply = await gw().route_to_llm(msg)
            gw().send_slack(OutgoingMessage(
                platform="slack", channel_id=msg.channel_id, text=reply,
            ))
            return {"response_type": "ephemeral", "text": "Processing..."}

        # Events API
        reply = await gw().route_to_llm(msg)
        # Need to verify Slack event
        if body.get("event", {}).get("type") == "message" and not body.get("event", {}).get("subtype"):
            gw().send_slack(OutgoingMessage(
                platform="slack", channel_id=msg.channel_id, text=reply,
            ))
        return {"ok": True}

    # ── WhatsApp ──────────────────────────────────────────

    @router.post("/whatsapp")
    async def whatsapp_webhook(request: Request):
        """Receive WhatsApp Business API webhook."""
        if not gw().check_rate_limit("whatsapp"):
            return {"ok": True, "error": "rate_limited"}
        body = await request.json()
        msg = gw().parse_whatsapp(body)
        if not msg:
            return {"ok": True}
        reply = await gw().route_to_llm(msg)
        gw().send_whatsapp(OutgoingMessage(
            platform="whatsapp", channel_id=msg.channel_id, text=reply,
        ))
        return {"ok": True}

    @router.get("/whatsapp")
    async def whatsapp_verify(request: Request, hub_mode: str = "", hub_verify_token: str = "", hub_challenge: str = ""):
        """WhatsApp Business API webhook verification."""
        if hub_mode == "subscribe" and hub_verify_token:
            expected = gw().config.whatsapp_verify_token or "honeybadger_verify"
            if hub_verify_token == expected:
                return PlainTextResponse(hub_challenge)
        return PlainTextResponse("Verification failed", status_code=403)

    # ── Twilio (WhatsApp/SMS) ─────────────────────────────

    @router.post("/twilio")
    async def twilio_webhook(request: Request):
        """Receive Twilio webhook for WhatsApp or SMS."""
        if not gw().check_rate_limit("whatsapp"):
            return PlainTextResponse("""<?xml version="1.0" encoding="UTF-8"?><Response/>""")
        form = await request.form()
        body = dict(form)
        msg = gw().parse_whatsapp(body)
        if not msg:
            return PlainTextResponse("")  # Twilio expects TwiML
        reply = await gw().route_to_llm(msg)
        gw().send_whatsapp(OutgoingMessage(
            platform="whatsapp", channel_id=msg.channel_id, text=reply,
        ))
        # Return TwiML for Twilio
        return PlainTextResponse(f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>""",
            media_type="application/xml")

    # ── Config ────────────────────────────────────────────

    @router.get("/config")
    async def get_config():
        """Get gateway configuration (tokens masked)."""
        c = gw().config
        def mask(val: str) -> str:
            if not val or len(val) < 8: return val
            return val[:4] + "****" + val[-4:]
        return {
            "telegram_token": mask(c.telegram_token) if c.telegram_token else "",
            "slack_bot_token": mask(c.slack_bot_token) if c.slack_bot_token else "",
            "whatsapp_token": mask(c.whatsapp_token) if c.whatsapp_token else "",
            "twilio_account_sid": mask(c.twilio_account_sid) if c.twilio_account_sid else "",
            "twilio_whatsapp_from": c.twilio_whatsapp_from or "",
            "default_model": c.default_model or "",
            "default_provider": c.default_provider or "groq",
            "system_prompt": c.system_prompt[:80] + "..." if c.system_prompt and len(c.system_prompt) > 80 else (c.system_prompt or ""),
            "webhook_base": c.webhook_base or "",
            "rate_limit_per_min": c.rate_limit_per_min,
            "telegram_webhook_set": bool(c.telegram_token),
            "slack_configured": bool(c.slack_bot_token and c.slack_signing_secret),
            "whatsapp_configured": bool(c.whatsapp_token or c.twilio_account_sid),
        }

    @router.post("/config")
    async def set_config(update: GatewayConfigUpdate):
        """Update gateway configuration."""
        svc = gw()
        for k, v in update.dict(exclude_none=True).items():
            if hasattr(svc.config, k):
                setattr(svc.config, k, v)
        svc.save_config()
        return {"ok": True, "message": "Gateway configuration updated"}

    @router.post("/telegram/set-webhook")
    async def set_telegram_webhook():
        """Register webhook URL with Telegram Bot API."""
        base = gw().config.webhook_base
        if not base:
            raise HTTPException(status_code=400, detail="Set webhook_base in config first")
        url = f"{base.rstrip('/')}/api/gateway/telegram"
        ok = gw().set_telegram_webhook(url)
        if ok:
            return {"ok": True, "webhook_url": url}
        raise HTTPException(status_code=502, detail="Failed to set Telegram webhook")

    @router.post("/test-llm")
    async def test_llm_route():
        """Test LLM connection with a simple ping."""
        svc = gw()
        test_msg = IncomingMessage(
            platform="test", channel_id="", user_id="", user_name="Tester",
            text="Reply with exactly: OK",
        )
        import time as _time
        t0 = _time.time()
        try:
            reply = await svc.route_to_llm(test_msg)
            elapsed = round(_time.time() - t0, 2)
            return {"ok": True, "model": svc.config.default_model, "reply": reply[:200], "time": f"{elapsed}s"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @router.get("/status")
    async def gateway_status():
        """Get gateway status summary."""
        from services.litellm_proxy import litellm_proxy_service
        litellm = {"running": False}
        try:
            s = litellm_proxy_service.detect(timeout=2.0)
            litellm = {"running": s.running, "models": len(s.models)}
        except Exception:
            pass
        return {
            "gateway": "active",
            "telegram": bool(gw().config.telegram_token),
            "slack": bool(gw().config.slack_bot_token),
            "whatsapp": bool(gw().config.whatsapp_token or gw().config.twilio_account_sid),
            "litellm": litellm,
            "routes": {
                "telegram": "/api/gateway/telegram",
                "slack": "/api/gateway/slack",
                "whatsapp": "/api/gateway/whatsapp",
                "twilio": "/api/gateway/twilio",
            },
        }

    return router
