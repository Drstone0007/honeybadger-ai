# HONEY BADGER
═══════════════════════════════════════════════════════════════════
  KERNEL OS v1.0 | TITAN BUILD | ELITE TECH CONGLOMERATE
═══════════════════════════════════════════════════════════════════

![Honey Badger](docs/honeybadger.jpg)

**Terminal-grade AI infrastructure. Zero compromise.**

A self-hosted AI workspace engineered for operators who demand control.
Local-first. Privacy-first. No cloud dependency. Your hardware, your data, your rules.

> "Honey Badger don't care. Honey Badger takes what it wants."

## CAPABILITIES

```
┌─────────────────────────────────────────────────────────────────┐
│  HONEY BADGER KERNEL OS — CORE MODULES                         │
├─────────────────────────────────────────────────────────────────┤
│  [CORE]      Chat Engine        │  vLLM · llama.cpp · Ollama   │
│  [AGENT]     Task Execution     │  MCP · Shell · Files · Skills │
│  [COOKBOOK]  Model Management   │  VRAM-aware · Auto-deploy    │
│  [RESEARCH]  Deep Investigation │  Multi-source · Synthesis     │
│  [COMPARE]   Blind Testing      │  Multi-model · Side-by-side  │
│  [DOCUMENTS] Editor Suite       │  Markdown · HTML · CSV       │
│  [MEMORY]    Persistence        │  ChromaDB · Vector + BM25    │
│  [EMAIL]     Triage System      │  IMAP/SMTP · AI-powered      │
│  [NOTES]     Task Manager       │  Cron · Reminders · Ntfy     │
│  [CALENDAR]  Time Management    │  CalDAV · .ics · Multi-cal   │
│  [MOBILE]    Responsive UI      │  PWA · Touch · Installable   │
├─────────────────────────────────────────────────────────────────┤
│  v2 NEW MODULES                                                │
├─────────────────────────────────────────────────────────────────┤
│  [BRAIN]     Second Brain       │  Karpaty · Knowledge Graph   │
│  [OBSIDIAN]  Vault Integration  │  Wikilinks · Backlinks       │
│  [PIXEL]     Vision Agent       │  Screenshot · OCR · UI       │
│  [SWARM]     Mirofish Swarm     │  Multi-Agent · Parallel      │
│  [GIT]       Git Intelligence   │  Blame · History · Commit    │
│  [METALAND]  The World Inside   │  Orbs · Cinema · The Void    │
│  [IWAS]      Voice Agent        │  OpenClaw · Preexistentism   │
└─────────────────────────────────────────────────────────────────┘
```

## Demo
A full, hover-to-play tour lives on the landing page (`docs/index.html`).

<details>
<summary>Screenshots / clips</summary>

### Chat & Agents
![Chat & Agents](docs/chat.gif)
### Deep Research
![Deep Research](docs/research.gif)
### Compare
![Compare](docs/compare.gif)
### Documents
![Documents](docs/document.gif)
### Notes & Tasks
![Notes & Tasks](docs/notes.gif)

</details>

## QUICK START

**One command. Everything. Zero questions.**

```bash
curl -fsSL https://raw.githubusercontent.com/Drstone0007/honeybadger-ai/main/install.sh | bash
```

Or for a local repo checkout:

```bash
bash install.sh
```

Installs: Core chat + 6 provider models · Second Brain · Pixel Agent · Seeing Agent (vision + talk) · Mirofish Swarm (8 agents) · Git Agent · Obsidian Vault · Metaland + The Void · IWAS Voice Agent · TTS (Edge/Kokoro/ElevenLabs) · STT (Whisper/Deepgram/Google/ElevenLabs) · LiteRT-LM (on-device LLM) · Document processing.
## DEPLOYMENT

```
┌─────────────────────────────────────────────────────────────────┐
│  INSTALLATION PROTOCOL                                         │
├─────────────────────────────────────────────────────────────────┤
│  1. Awesome repository                                           │
│  2. Configure environment                                      │
│  3. Launch kernel                                              │
│  4. Access via localhost:7000                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Docker (Recommended)

```bash
git clone https://github.com/Drstone0007/honeybadger-ai.git
cd honeybadger-ai
cp .env.example .env
docker compose up -d --build
```

**Default port:** `7000` | **Admin:** `admin` | **Password:** Generated on first boot

### Native Linux / macOS

```bash
git clone https://github.com/Drstone0007/honeybadger-ai.git
cd honeybadger-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py
python -m uvicorn app:app --host 127.0.0.1 --port 7000
```

### Apple Silicon

```bash
git clone https://github.com/Drstone0007/honeybadger-ai.git
cd honeybadger-ai
./start-macos.sh
```

**Port:** `7860` | **GPU:** Metal-accelerated via llama.cpp/Ollama

### Windows

```powershell
git clone https://github.com/Drstone0007/honeybadger-ai.git
cd honeybadger-ai
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

## Security Notes
Honey Badger is a self-hosted workspace with powerful local tools: shell access, file uploads, model downloads, web research, email/calendar integrations, and API tokens. Treat it like an admin console.

- Keep `AUTH_ENABLED=true` for any network-accessible deployment.
- Keep `LOCALHOST_BYPASS=false` outside local development.
- Use `SECURE_COOKIES=true` when Honey Badger is served through HTTPS by a trusted reverse proxy or private access gateway.
- Do not expose it directly to the public internet without HTTPS and a trusted reverse proxy or private access layer.
- Keep `.env`, `data/`, `logs/`, databases, uploads, generated media, backups, auth/session files, API keys, and model/provider tokens out of Git and private shares. They are ignored by default.
- Review `data/auth.json` after first boot: disable open signup unless you intentionally want it, make only your own account admin, and keep demo/test accounts non-admin.
- Non-admin users do not get shell/Python/file read/write by default, and admin-only routes/tools such as MCP management, API tokens, webhooks, model/cookbook serving, backup/vault, and app settings are admin-gated. Other features are controlled by per-user privileges, so review each user's privileges before exposing a deployment.
- Rotate any API keys or tokens that were ever pasted into a shared chat, demo, screenshot, or log.
- If you enable API tokens or webhooks, create separate tokens per integration and delete unused ones.
- Prefer binding manual development runs to `127.0.0.1`; bind to `0.0.0.0` only when you intentionally want LAN/reverse-proxy access.
- Keep ChromaDB, SearXNG, ntfy, Ollama, vLLM, llama.cpp, databases, and raw model/provider APIs internal-only. Expose only the authenticated Honey Badger web/API entrypoint through your trusted proxy or private access layer.
- Before publishing a fork, run `git status --short` and confirm no private files from `.env`, `data/`, `logs/`, uploads, backups, or local databases are staged.

### Private or proxied deployments
Honey Badger serves plain HTTP on its app port. Docker Compose binds Honey Badger and the bundled services to `127.0.0.1` by default, so a typical production/private setup is:

1. Keep Honey Badger on localhost, for example `127.0.0.1:7000`.
2. Terminate HTTPS at a trusted reverse proxy or private access gateway.
3. Put the authenticated Honey Badger web/API entrypoint behind that layer.
4. Keep raw service and model ports internal-only.

Cloudflare Access, Tailscale, Caddy, nginx, and Traefik can all fit this pattern; none are required by Honey Badger. If your access layer reaches Honey Badger on the same host, proxy to `http://127.0.0.1:7000` and keep `AUTH_ENABLED=true`, `LOCALHOST_BYPASS=false`, and `SECURE_COOKIES=true`.

Common internal-only ports from the default docs/compose setup:

| Port | Service |
|---|---|
| `7000` | Honey Badger raw app port |
| `8080` | SearXNG |
| `8091` | ntfy |
| `8100` | ChromaDB host port for manual/compose access |
| `11434` | Ollama |
| `8000-8020` | Common local model/provider APIs |

## Contributing
Help is welcome. The best entry points are fresh-install testing, provider setup
bugs, mobile/editor polish, docs, and small focused refactors. See
[ROADMAP.md](ROADMAP.md) for the current help-wanted list.

## Configuration
Most setup is done inside the app with `/setup` or **Settings**. Use `.env`
for deployment-level defaults and secrets you want present before first boot.
Key settings:

| Variable | Default | Description |
|---|---|---|
| `LLM_HOST` | `localhost` | Your LLM server (e.g. `llm-host.local:8000`) |
| `LLM_HOSTS` | -- | Comma-separated list for model discovery |
| `OPENAI_API_KEY` | -- | Optional OpenAI key. Prefer adding providers in the app unless pre-seeding. |
| `SEARXNG_INSTANCE` | `http://localhost:8080` | SearXNG URL. Docker overrides this to `http://searxng:8080`. |
| `SEARXNG_SECRET` | generated on first Docker boot | Optional SearXNG cookie/CSRF secret. Leave blank unless you need to pin it. |
| `APP_BIND` | `127.0.0.1` | Docker Compose host bind address for the web UI. Use `0.0.0.0` only for intentional LAN/reverse-proxy access. |
| `APP_PORT` | `7000` | Docker Compose host port for the web UI. |
| `AUTH_ENABLED` | `true` | Enable/disable login |
| `LOCALHOST_BYPASS` | `false` | Development-only auth bypass for loopback requests. Keep false for shared/network deployments. |
| `SECURE_COOKIES` | `false` | Set true when serving Honey Badger through HTTPS at a trusted proxy or private access gateway. |
| `DATABASE_URL` | `sqlite:///./data/app.db` | Database connection string |
| `CHROMADB_HOST` | `localhost` | ChromaDB host for vector memory. Docker overrides this to `chromadb`. |
| `CHROMADB_PORT` | `8100` | ChromaDB port for manual host runs. Docker overrides this to `8000`. |
| `EMBEDDING_URL` | -- | OpenAI-compatible embeddings endpoint |

### Built-in MCP servers (optional setup)

Honey Badger auto-registers a few built-in MCP servers at startup. The npx-based ones (currently the browser server, `@playwright/mcp`) only start when their npm package is already in the local npx cache. If a package isn't cached, that server is skipped with a startup log message explaining what to do, so a fresh install does not block on a multi-minute npm download or hang if Playwright system deps are missing.

To enable the browser MCP (page navigation, screenshots, vision), run once:

```bash
npx -y @playwright/mcp@latest --version
```

That installs `@playwright/mcp` plus Playwright (~300MB total). Restart Honey Badger and the server will register at startup.

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│  HONEY BADGER KERNEL — SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│  app.py            │  FastAPI Entry Point                     │
│  core/             │  Auth · Database · Middleware · Crypto    │
│  src/              │  LLM Core · Agent Loop · Tools · Search  │
│  routes/           │  API Endpoints (47 modules)              │
│  services/         │  Business Logic (Docs, Memory, Search)   │
│  static/           │  TUI Frontend (HTML/JS/CSS)              │
│  companion/        │  Companion Bridge                        │
│  mcp_servers/      │  MCP Server Modules                      │
│  scripts/          │  CLI Tools & Automation                  │
└─────────────────────────────────────────────────────────────────┘
```

## DATA LAYER

```
data/
├── app.db              # SQLite — sessions, messages, documents
├── settings.json       # System configuration
├── features.json       # Feature flags
├── memory.json         # User memory store
├── presets.json        # Chat presets
├── uploads/            # File uploads
├── personal_docs/      # User documents
├── chroma/             # Vector database
└── deep_research/      # Research cache
```

## STATUS

```
┌─────────────────────────────────────────────────────────────────┐
│  HONEY BADGER KERNEL v1.0 | BUILD: TITAN                      │
│  STATUS: OPERATIONAL | UPTIME: CONTINUOUS                      │
│  License: MIT | Elite Tech Conglomerate                        │
└─────────────────────────────────────────────────────────────────┘
```

```
                              |
                             |||
                            |||||
              |    |    |   |||||||
             )_)  )_)  )_)   ~|~
            )___))___))___)\  |
          )Elite_Tech--Conglomerate )|
         _tlmon____|____+|____|_____\\\__
         \                             /
   ~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~
           ~^~  ALL SYSTEMS GO  ~^~
   ~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~~^~^~
```
