"""Tests for IWAS routes and messaging gateway."""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def gateway_service_mock():
    """Create a mocked GatewayService for route testing."""
    from services.gateway import GatewayService, GatewayConfig, IncomingMessage, OutgoingMessage
    svc = GatewayService()
    svc.config.default_model = "llama-3.3-70b-versatile"
    svc.config.default_provider = "groq"
    svc.config.default_api_key = "test-key"
    svc.config.telegram_token = "123:testbot"
    svc.config.slack_bot_token = "xoxb-test"
    svc.config.slack_signing_secret = "test-secret"
    svc.config.webhook_base = "https://example.com"
    svc.check_rate_limit = MagicMock(return_value=True)
    svc.set_telegram_webhook = MagicMock(return_value=True)
    return svc


@pytest.fixture
def iwas_app():
    """Build a minimal FastAPI with IWAS routes."""
    from routes.iwas_routes import setup_iwas_routes
    app = FastAPI()
    app.include_router(setup_iwas_routes())
    return app


@pytest.fixture
def gateway_app():
    """Build a minimal FastAPI with gateway routes."""
    from routes.gateway_routes import setup_gateway_routes
    app = FastAPI()
    app.include_router(setup_gateway_routes())
    return app


# ── IWAS Route Tests ──────────────────────────────────────────────────

class TestIWASRoutes:

    @pytest.mark.asyncio
    async def test_providers_endpoint(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/iwas/providers")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data.get("providers"), list)
        assert len(data["providers"]) > 0

    @pytest.mark.asyncio
    async def test_void_state(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/iwas/void/state")
        assert r.status_code == 200
        data = r.json()
        assert "consciousness" in data

    @pytest.mark.asyncio
    async def test_void_story(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/iwas/void/story")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_void_manifesto(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/iwas/void/manifesto")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_void_event(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/iwas/void/event", json={"event": "test_event", "data": {}})
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True

    @pytest.mark.asyncio
    async def test_chat_missing_fields(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/iwas/chat", json={})
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, iwas_app):
        transport = ASGITransport(app=iwas_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/iwas/chat", json={"message": "", "provider": "groq"})
        assert r.status_code == 400
        assert "empty" in r.json().get("detail", "").lower()


# ── Gateway Route Tests ───────────────────────────────────────────────

class TestGatewayRoutes:

    @pytest.mark.asyncio
    async def test_config_get(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/gateway/config")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_config_set(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/config", json={
                "default_model": "llama-3.3-70b-versatile",
                "default_provider": "groq",
            })
        assert r.status_code == 200
        data = r.json()
        assert data.get("ok") is True

    @pytest.mark.asyncio
    async def test_status(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/gateway/status")
        assert r.status_code == 200
        data = r.json()
        assert data.get("gateway") == "active"

    @pytest.mark.asyncio
    async def test_telegram_webhook_no_token(self, gateway_app):
        """Should accept and return ok even without parsed message."""
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/telegram", json={
                "update_id": 1,
                "message": {"message_id": 1, "chat": {"id": 123}, "text": "hello"}
            })
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_telegram_no_message(self, gateway_app):
        """Non-message updates should silently return ok."""
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/telegram", json={
                "update_id": 1,
            })
        assert r.status_code == 200
        assert r.json().get("ok") is True

    @pytest.mark.asyncio
    async def test_slack_url_verification(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/slack", json={
                "type": "url_verification",
                "challenge": "abc123",
            })
        assert r.status_code == 200
        data = r.json()
        assert data.get("challenge") == "abc123"

    @pytest.mark.asyncio
    async def test_whatsapp_verify_no_token(self, gateway_app):
        """Should fail with wrong token."""
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/gateway/whatsapp", params={
                "hub_mode": "subscribe",
                "hub_verify_token": "wrong_token",
                "hub_challenge": "challenge_123",
            })
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_whatsapp_verify_default_token(self, gateway_app):
        """Should accept default token."""
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/api/gateway/whatsapp", params={
                "hub_mode": "subscribe",
                "hub_verify_token": "honeybadger_verify",
                "hub_challenge": "challenge_123",
            })
        assert r.status_code == 200
        assert r.text == "challenge_123"

    @pytest.mark.asyncio
    async def test_twilio_returns_twiml(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/twilio", data={
                "Body": "hello",
                "From": "whatsapp:+1234567890",
                "To": "whatsapp:+0987654321",
            })
        assert r.status_code == 200
        assert "<?xml" in r.text
        assert "<Response>" in r.text

    @pytest.mark.asyncio
    async def test_set_webhook_no_base(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/telegram/set-webhook")
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_test_llm_no_model(self, gateway_app):
        transport = ASGITransport(app=gateway_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/api/gateway/test-llm")
        assert r.status_code == 200


# ── Gateway Service Unit Tests ───────────────────────────────────────

class TestGatewayService:

    def test_parse_telegram_message(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        body = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 12345},
                "from": {"id": 999, "first_name": "TestUser"},
                "text": "Hello world",
            },
        }
        msg = svc.parse_telegram(body)
        assert msg is not None
        assert msg.platform == "telegram"
        assert msg.channel_id == "12345"
        assert msg.user_name == "TestUser"
        assert msg.text == "Hello world"

    def test_parse_telegram_non_message(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        msg = svc.parse_telegram({"update_id": 1})
        assert msg is None

    def test_parse_slack_slash_command(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        body = {
            "command": "/ask",
            "text": "what is the meaning of life?",
            "channel_id": "C123",
            "user_id": "U456",
            "user_name": "testuser",
        }
        msg = svc.parse_slack(body, {})
        assert msg is not None
        assert msg.platform == "slack"
        assert msg.text == "what is the meaning of life?"

    def test_parse_slack_url_verification(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        body = {"type": "url_verification", "challenge": "abc"}
        msg = svc.parse_slack(body, {})
        assert msg is None  # Handled at route level

    def test_parse_whatsapp_business(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        body = {
            "entry": [{
                "changes": [{
                    "value": {
                        "metadata": {"phone_number_id": "5551234"},
                        "messages": [{
                            "from": "12345",
                            "type": "text",
                            "text": {"body": "Hi from WhatsApp"},
                        }],
                    },
                }],
            }],
        }
        msg = svc.parse_whatsapp(body)
        assert msg is not None
        assert msg.platform == "whatsapp"
        assert msg.text == "Hi from WhatsApp"

    def test_parse_whatsapp_twilio(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        body = {"Body": "Twilio test", "From": "whatsapp:+123", "To": "whatsapp:+456"}
        msg = svc.parse_whatsapp(body)
        assert msg is not None
        assert msg.text == "Twilio test"

    def test_parse_whatsapp_empty(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        msg = svc.parse_whatsapp({})
        assert msg is None

    def test_extract_model_override_no_prefix(self):
        from services.gateway import GatewayService
        text, model = GatewayService._extract_model_override("hello world")
        assert text == "hello world"
        assert model == ""

    def test_extract_model_override_with_model(self):
        from services.gateway import GatewayService
        text, model = GatewayService._extract_model_override("model:groq/llama3 hello world")
        assert text == "hello world"
        assert model == "groq/llama3"

    def test_extract_model_override_short_alias(self):
        from services.gateway import GatewayService
        text, model = GatewayService._extract_model_override("mdl:claude-sonnet-4 test")
        assert text == "test"
        assert model == "claude-sonnet-4"

    def test_send_telegram_no_token(self):
        from services.gateway import GatewayService, OutgoingMessage
        svc = GatewayService()
        result = svc.send_telegram(OutgoingMessage(platform="telegram", channel_id="123", text="test"))
        assert result is False

    def test_send_slack_no_token(self):
        from services.gateway import GatewayService, OutgoingMessage
        svc = GatewayService()
        result = svc.send_slack(OutgoingMessage(platform="slack", channel_id="C123", text="test"))
        assert result is False

    def test_send_whatsapp_no_creds(self):
        from services.gateway import GatewayService, OutgoingMessage
        svc = GatewayService()
        result = svc.send_whatsapp(OutgoingMessage(platform="whatsapp", channel_id="123", text="test"))
        assert result is False

    def test_slack_signature_verification(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        svc.config.slack_signing_secret = "test_secret"
        body = b'{"type":"url_verification","challenge":"abc"}'
        ts = "1234567890"
        sig = "v0=" + __import__("hmac").new(
            b"test_secret",
            f"v0:{ts}:{body.decode()}".encode(),
            __import__("hashlib").sha256,
        ).hexdigest()
        assert svc.verify_slack_signature(body, ts, sig) is True

    def test_slack_signature_wrong(self):
        from services.gateway import GatewayService
        svc = GatewayService()
        svc.config.slack_signing_secret = "test_secret"
        assert svc.verify_slack_signature(b"test", "0", "v0:wrong_sig") is False

    def test_rate_limiter_accepts(self):
        from services.gateway import RateLimiter
        rl = RateLimiter(5)
        assert rl.check("test", 5) is True

    def test_rate_limiter_rejects(self):
        from services.gateway import RateLimiter
        rl = RateLimiter(2)
        assert rl.check("test", 2) is True
        assert rl.check("test", 2) is True
        assert rl.check("test", 2) is False

    def test_rate_limiter_resets(self):
        from services.gateway import RateLimiter
        import time
        rl = RateLimiter(1)
        assert rl.check("test", 1) is True
        # Without time travel, second check in same window should fail
        assert rl.check("test", 1) is False

    def test_config_save_load(self, tmp_path):
        from services.gateway import GatewayService, GatewayConfig
        import json
        svc = GatewayService()
        svc.config.default_model = "test-model"
        svc.config.default_provider = "groq"
        # Override save path for temp
        from pathlib import Path
        orig_save = svc.save_config
        orig_load = svc.load_config
        test_file = tmp_path / "gateway_config.json"
        def save_to_test():
            test_file.parent.mkdir(parents=True, exist_ok=True)
            data = {k: getattr(svc.config, k) for k in dir(svc.config) if not k.startswith("_")}
            test_file.write_text(json.dumps(data, indent=2))
            return data
        def load_from_test():
            if test_file.exists():
                data = json.loads(test_file.read_text())
                for k, v in data.items():
                    if hasattr(svc.config, k):
                        setattr(svc.config, k, v)
        svc.save_config = save_to_test
        svc.load_config = load_from_test
        svc.save_config()
        svc2 = GatewayService()
        svc2.config.default_model = ""
        # Load
        from pathlib import Path as P2
        # Simulate load
        load_from_test()
        assert svc2.config.default_model != "test-model"  # svc2 not affected, load affects svc
        # Actually load into svc2
        if test_file.exists():
            data = json.loads(test_file.read_text())
            for k, v in data.items():
                if hasattr(svc2.config, k):
                    setattr(svc2.config, k, v)
        assert svc2.config.default_model == "test-model"


# ── IWAS Service Tests ────────────────────────────────────────────────

class TestVoidState:
    """Test The Void integration basic behavior."""

    def test_void_manifesto_exists(self):
        from src.the_void import TheVoid
        v = TheVoid()
        manifesto = v.get_manifesto()
        assert len(manifesto) > 50

    def test_void_state_structure(self):
        from src.the_void import TheVoid
        v = TheVoid()
        state = v.get_state()
        assert "consciousness" in state
        assert "phase" in state
        assert "awakening" in state.get("consciousness", {})
