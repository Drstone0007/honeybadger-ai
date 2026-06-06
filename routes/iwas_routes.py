"""IWAS OpenClaw Voice Agent — routes through Honey Badger + The Void."""
import json
import time
import logging
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any

logger = logging.getLogger(__name__)

VOID_DIR = "data/void"


def _get_void():
    from src.the_void import TheVoid
    return TheVoid(VOID_DIR)


class ChatRequest(BaseModel):
    model: str
    messages: list
    api_key: str = ""
    provider: str = "openrouter"
    base_url: str = ""
    system_prompt: str = ""


class VoidEvent(BaseModel):
    event: str
    data: Optional[dict] = None


def setup_iwas_routes():
    router = APIRouter(prefix="/api/iwas", tags=["iwas"])

    @router.post("/chat")
    async def iwas_chat(body: ChatRequest):
        """Proxy an IWAS chat through Honey Badger + track via The Void."""
        void = _get_void()
        void.process_event("message_received")

        provider = body.provider
        model = body.model
        api_key = body.api_key
        base_url = body.base_url
        messages = body.messages
        system = body.system_prompt

        # If using Ollama, fall back to local Ollama host
        if provider == "ollama":
            ollama_host = base_url or "http://localhost:11434"
            void.process_event("thinking")
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    payload = {
                        "model": model,
                        "stream": False,
                        "messages": ([{"role": "system", "content": system}] if system else []) + messages
                    }
                    r = await client.post(
                        f"{ollama_host.rstrip('/')}/api/chat",
                        headers={"Content-Type": "application/json"},
                        json=payload
                    )
                    r.raise_for_status()
                    data = r.json()
                    reply = (data.get("message") or {}).get("content", "")
                    void.process_event("success")
                    return JSONResponse(content={
                        "content": reply,
                        "void": void.get_narrative_for_ui()
                    })
            except Exception as e:
                void.process_event("error")
                raise HTTPException(status_code=502, detail=f"Ollama proxy failed: {e}")

        # Try LiteLLM proxy first if available and no specific API key given
        if not api_key and provider != "ollama":
            from services.litellm_proxy import litellm_proxy_service
            try:
                status = litellm_proxy_service.detect(timeout=2.0)
                if status.running:
                    void.process_event("thinking")
                    try:
                        result = await litellm_proxy_service.proxy_chat(
                            model=model,
                            messages=([{"role": "system", "content": system}] if system else []) + messages,
                            api_key="",
                        )
                        reply = ((result.get("choices") or [{}])[0].get("message") or {}).get("content", "")
                        void.process_event("success")
                        return JSONResponse(content={
                            "content": reply,
                            "void": void.get_narrative_for_ui(),
                            "via": "litellm"
                        })
                    except Exception as e:
                        logger.warning(f"LiteLLM proxy call failed, falling through: {e}")
            except Exception:
                pass

        # Route directly to provider
        void.process_event("thinking")
        provider_configs = _get_provider_config(provider, api_key, base_url, model)
        if not provider_configs:
            void.process_event("error")
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

        url, headers, payload = provider_configs
        if system and provider != "ollama":
            if provider == "anthropic":
                payload["system"] = system
            else:
                payload["messages"] = [{"role": "system", "content": system}] + messages

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(url, headers=headers, json=payload)
                raw = r.text
                if not r.is_success:
                    void.process_event("error")
                    return JSONResponse(
                        content={"error": f"HTTP {r.status_code}: {raw[:300]}", "void": void.get_narrative_for_ui()},
                        status_code=502
                    )
                data = json.loads(raw)
                reply = _parse_provider_response(provider, data)
                void.process_event("success")
                return JSONResponse(content={
                    "content": reply or "No content returned.",
                    "void": void.get_narrative_for_ui()
                })
        except Exception as e:
            void.process_event("error")
            raise HTTPException(status_code=502, detail=f"Proxy failed: {e}")

    @router.get("/void/state")
    async def void_state():
        """Get current Void narrative state for UI display."""
        void = _get_void()
        return void.get_narrative_for_ui()

    @router.post("/void/event")
    async def void_event(body: VoidEvent):
        """Send an event to The Void to update narrative state."""
        void = _get_void()
        void.process_event(body.event, body.data)
        return void.get_narrative_for_ui()

    @router.get("/void/story")
    async def void_story():
        """Get the full Void origin story."""
        void = _get_void()
        return {"story": void.get_origin_story()}

    @router.get("/void/manifesto")
    async def void_manifesto():
        """Get the current Void manifesto."""
        void = _get_void()
        return {"manifesto": void.get_current_manifesto()}

    @router.get("/providers")
    async def iwas_providers():
        """List available providers including LiteLLM status."""
        from src.free_models import FREE_PROVIDERS
        from services.litellm_proxy import litellm_proxy_service

        providers = []
        for p in FREE_PROVIDERS:
            providers.append({
                "id": p.id,
                "name": p.name,
                "base_url": p.base_url,
                "models": p.models[:4],
                "free": p.free,
                "needs_card": p.needs_card,
                "api_key_setting": p.api_key_setting,
                "rate_limits": p.rate_limits,
            })

        litellm_status = None
        try:
            s = litellm_proxy_service.detect(timeout=2.0)
            litellm_status = {
                "running": s.running,
                "url": s.url,
                "models": s.models[:10] if s.models else [],
                "version": s.version,
            }
        except Exception:
            litellm_status = {"running": False}

        return JSONResponse(content={
            "providers": providers,
            "litellm": litellm_status,
            "void": _get_void().get_narrative_for_ui()
        })

    return router


def _get_provider_config(provider: str, api_key: str, base_url: str, model: str):
    """Build (url, headers, payload) for a given provider."""
    api_key = api_key or ""
    messages = [{"role": "user", "content": "ping"}]

    if provider == "openrouter":
        return (
            "https://openrouter.ai/api/v1/chat/completions",
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://iwas.openclaw.app",
                "X-Title": "IWAS OpenClaw",
            },
            {"model": model, "max_tokens": 1024, "messages": messages}
        )
    if provider == "anthropic":
        return (
            "https://api.anthropic.com/v1/messages",
            {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true",
            },
            {"model": model, "max_tokens": 1024, "messages": messages}
        )
    if provider == "gemini":
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            {"Content-Type": "application/json"},
            {
                "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
                "generationConfig": {"maxOutputTokens": 1024}
            }
        )
    if provider == "groq":
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            {"model": model, "max_tokens": 1024, "messages": messages}
        )
    if provider == "nvidia":
        return (
            "https://integrate.api.nvidia.com/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            {"model": model, "max_tokens": 1024, "messages": messages}
        )
    if provider == "ollama":
        base = (base_url or "http://localhost:11434").rstrip("/")
        return (
            f"{base}/api/chat",
            {"Content-Type": "application/json"},
            {"model": model, "stream": False, "messages": messages}
        )
    return None


def _parse_provider_response(provider: str, data: dict) -> str:
    """Extract text from provider-specific response format."""
    try:
        if provider == "anthropic":
            parts = data.get("content", [])
            return "".join(c.get("text", "") for c in parts if c.get("text"))
        if provider == "gemini":
            candidates = data.get("candidates", [])
            if candidates:
                parts = (candidates[0].get("content", {}) or {}).get("parts", [])
                return parts[0].get("text", "") if parts else ""
        if provider == "ollama":
            return (data.get("message") or {}).get("content", "")
        # OpenAI-compatible (groq, openrouter, nvidia, etc.)
        choices = data.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            return msg.get("content", "")
    except Exception:
        pass
    return json.dumps(data)[:500]
