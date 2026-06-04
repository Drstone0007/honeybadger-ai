# PRODUCTION DEPLOYMENT GUIDE
## Honey Badger Kernel OS v1.0 — TITAN BUILD

```
═══════════════════════════════════════════════════════════════════
  HONEY BADGER KERNEL — PRODUCTION DEPLOYMENT
  Elite Tech Conglomerate | Zero Compromise
═══════════════════════════════════════════════════════════════════
```

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Native Deployment](#native-deployment)
5. [pip install (PyPI)](#pip-install-pypi)
6. [Snap Package](#snap-package)
7. [Nix/NixOS](#nixnixos)
8. [Ansible](#ansible)
9. [Vagrant](#vagrant)
10. [Podman (Rootless)](#podman-rootless)
11. [Cloud Deployment](#cloud-deployment)
12. [Environment Configuration](#environment-configuration)
13. [Security Hardening](#security-hardening)
14. [SSL/TLS Setup](#ssltls-setup)
15. [Reverse Proxy Configuration](#reverse-proxy-configuration)
16. [Monitoring & Observability](#monitoring--observability)
17. [Backup & Recovery](#backup--recovery)
18. [Scaling Considerations](#scaling-considerations)
19. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Storage** | 20 GB | 50+ GB SSD |
| **OS** | Linux, macOS, Windows | Ubuntu 22.04+ / Debian 12+ |
| **Python** | 3.11+ | 3.12+ |
| **Docker** | 24.0+ | 25.0+ (with Compose v2) |

### GPU Requirements (Optional)

| GPU | VRAM | Use Case |
|-----|------|----------|
| NVIDIA RTX 3060+ | 8+ GB | Local model serving |
| AMD RX 6700+ | 8+ GB | ROCm acceleration |
| Apple M1+ | 8+ GB | Metal acceleration |

### Network Requirements

| Port | Protocol | Purpose |
|------|----------|---------|
| 7000 | TCP | HTTP (Odysseus/Honey Badger) |
| 8080 | TCP | SearXNG (internal) |
| 8091 | TCP | ntfy (internal) |
| 8100 | TCP | ChromaDB (internal) |
| 11434 | TCP | Ollama (if using) |

---

## Quick Install (One-Liner)

```bash
curl -fsSL https://raw.githubusercontent.com/honeybadger-ai/honeybadger/main/install.sh | bash
```

With options:

```bash
curl -fsSL https://raw.githubusercontent.com/honeybadger-ai/honeybadger/main/install.sh | bash -s -- --dir /opt/honeybadger --port 7000
```

Uninstall:

```bash
~/honeybadger/uninstall.sh
```

---

## Deployment Options

### Option 1: Docker (Recommended)

**Pros:** Isolated, reproducible, GPU support, easy updates
**Cons:** ~500MB disk overhead, Docker dependency

### Option 2: Native

**Pros:** Direct GPU access, lower overhead, full control
**Cons:** Manual dependency management, environment differences

### Option 3: Kubernetes

**Pros:** Scalable, orchestrated, production-grade
**Cons:** Complex setup, resource overhead

### Option 4: pip install (PyPI)

**Pros:** Simple, integrates with Python ecosystem
**Cons:** Requires Python, no container isolation

### Option 5: Snap Package

**Pros:** Auto-updates, sandboxed, cross-distro
**Cons:** Larger size, limited host access

### Option 6: Nix/NixOS

**Pros:** Reproducible, declarative, rollbacks
**Cons:** Steep learning curve

### Option 7: Ansible

**Pros:** Idempotent, multi-server, documented
**Cons:** Requires Ansible control node

### Option 8: Vagrant

**Pros:** Consistent dev/prod, portable VMs
**Cons:** VM overhead, slower I/O

### Option 9: Podman (Rootless)

**Pros:** No daemon, rootless, Docker-compatible
**Cons:** Smaller ecosystem

### Option 10: Cloud (AWS/GCP/Azure)

**Pros:** Managed, scalable, global
**Cons:** Cost, vendor lock-in

### Option 11: Docker Swarm

**Pros:** Simpler than K8s, built-in Docker
**Cons:** Less features than K8s

### Option 12: macOS App Bundle

**Pros:** Native macOS experience, menubar app
**Cons:** macOS only

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/honeybadger-ai/honeybadger.git
cd honeybadger

# Create environment file
cp .env.example .env

# Start services
docker compose up -d --build

# Check status
docker compose ps
docker compose logs -f honeybadger
```

### Docker Compose Services

| Service | Port | Purpose |
|---------|------|---------|
| `honeybadger` | 7000 | Main application |
| `chromadb` | 8100 | Vector database |
| `searxng` | 8080 | Web search |
| `ntfy` | 8091 | Push notifications |

### Docker GPU Support

#### NVIDIA GPU

```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Enable GPU passthrough
./scripts/check-docker-gpu.sh --install-nvidia-toolkit --enable-nvidia-overlay

# Verify
docker compose exec honeybadger nvidia-smi -L
```

#### AMD GPU

```bash
# Check AMD GPU passthrough
./scripts/check-docker-amd-gpu.sh

# Add to .env
echo "COMPOSE_FILE=docker-compose.yml:docker/gpu.amd.yml" >> .env
echo "RENDER_GID=$(stat -c '%g' /dev/dri/renderD128)" >> .env

# Restart
docker compose up -d
```

### Docker Networking

By default, services bind to `127.0.0.1`. To expose to LAN:

```bash
# .env
APP_BIND=0.0.0.0
APP_PORT=7000
```

**Security Warning:** Never expose directly to the internet without HTTPS.

### Docker Data Persistence

Data volumes are mounted to `./data/`:

```
data/
├── app.db              # SQLite database
├── settings.json       # System settings
├── memory.json         # User memory
├── uploads/            # File uploads
├── personal_docs/      # User documents
├── chroma/             # Vector database
├── huggingface/        # Model cache
└── logs/               # Application logs
```

### Docker Commands Reference

```bash
# Start/Stop
docker compose up -d                    # Start in background
docker compose down                     # Stop and remove
docker compose restart honeybadger      # Restart main service

# Logs
docker compose logs -f honeybadger      # Follow logs
docker compose logs --tail=100          # Last 100 lines
docker compose logs | grep ERROR        # Filter errors

# Shell access
docker compose exec honeybadger bash    # Shell into container
docker compose exec honeybadger python  # Python REPL

# Database
docker compose exec honeybadger sqlite3 data/app.db

# Updates
git pull
docker compose build --no-cache
docker compose up -d
```

---

## Native Deployment

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip \
  git tmux curl wget build-essential

# Clone and setup
git clone https://github.com/honeybadger-ai/honeybadger.git
cd honeybadger

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Start the server
python -m uvicorn app:app --host 127.0.0.1 --port 7000

# Or use the CLI
./scripts/honeybadger
```

### macOS

```bash
# Install Homebrew dependencies
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Clone and setup
git clone https://github.com/honeybadger-ai/honeybadger.git
cd honeybadger

# One-command launcher
./start-macos.sh
```

### Windows

```powershell
# Prerequisites
# 1. Python 3.11+ (from python.org)
# 2. Git for Windows (from git-scm.com)

# Clone and setup
git clone https://github.com/honeybadger-ai/honeybadger.git
cd honeybadger

# One-command launcher
powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
```

### Systemd Service (Linux)

```bash
# Install service
sudo ./install-service.sh

# Start service
sudo systemctl start honeybadger-ui

# Enable on boot
sudo systemctl enable honeybadger-ui

# Check status
sudo systemctl status honeybadger-ui

# View logs
sudo journalctl -u honeybadger-ui -f
```

---

## pip install (PyPI)

```bash
# Install from PyPI
pip install honeybadger-kernel

# Or install from source
pip install git+https://github.com/honeybadger-ai/honeybadger.git

# Run
honeybadger-kernel

# Or with Python
python -m honeybadger_kernel
```

### pip + Virtual Environment (Recommended)

```bash
# Create isolated environment
python3.12 -m venv ~/.honeybadger
source ~/.honeybadger/bin/activate

# Install
pip install honeybadger-kernel

# Run
honeybadger-kernel

# Exit venv
deactivate
```

---

## Snap Package

```bash
# Install from Snap Store
sudo snap install honeybadger-kernel

# Or install from local file
sudo snap install --dangerous honeybadger-kernel_1.0_amd64.snap

# Run
honeybadger-kernel

# Permissions
sudo snap connect honeybadger-kernel:removable-media
sudo snap connect honeybadger-kernel:network

# Auto-updates
sudo snap refresh honeybadger-kernel
```

---

## Nix/NixOS

### NixOS Module

```nix
# configuration.nix
{ config, pkgs, ... }:
{
  imports = [
    <nixpkgs/nixos/modules/services/misc/honeybadger-kernel.nix>
  ];

  services.honeybadger-kernel = {
    enable = true;
    port = 7000;
    bindAddress = "127.0.0.1";
    environmentFile = "/etc/honeybadger/.env";
  };
}
```

### Nix Flake

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    honeybadger.url = "github:honeybadger-ai/honeybadger";
  };

  outputs = { self, nixpkgs, honeybadger }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        honeybadger.nixosModules.honeybadger-kernel
        {
          services.honeybadger-kernel.enable = true;
        }
      ];
    };
  };
}
```

### nix-shell (Temporary)

```bash
# Run without installing
nix-shell -p honeybadger-kernel

# Or from flakes
nix run github:honeybadger-ai/honeybadger
```

---

## Ansible

### Playbook

```yaml
# playbook.yml
---
- hosts: honeybadger_servers
  become: yes
  vars:
    honeybadger_version: "1.0.0"
    honeybadger_port: 7000
    honeybadger_admin_password: "{{ vault_honeybadger_password }}"

  tasks:
    - name: Install Docker
      apt:
        name: [docker.io, docker-compose-plugin]
        state: present
        update_cache: yes

    - name: Clone repository
      git:
        repo: "https://github.com/honeybadger-ai/honeybadger.git"
        dest: "/opt/honeybadger"
        version: "v{{ honeybadger_version }}"

    - name: Create .env file
      template:
        src: templates/env.j2
        dest: "/opt/honeybadger/.env"
        mode: '0600'

    - name: Start services
      community.docker.docker_compose:
        project_src: "/opt/honeybadger"
        state: present
```

### Inventory

```ini
# inventory.ini
[honeybadger_servers]
server1 ansible_host=192.168.1.100
server2 ansible_host=192.168.1.101

[honeybadger_servers:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### Run

```bash
# Install Ansible
pip install ansible

# Run playbook
ansible-playbook -i inventory.ini playbook.yml --ask-vault-pass
```

---

## Vagrant

```ruby
# Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "honeybadger"

  # Port forwarding
  config.vm.network "forwarded_port", guest: 7000, host: 7000

  # VM resources
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
  end

  # Provisioning
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3.12 python3.12-venv docker.io docker-compose

    cd /vagrant
    cp .env.example .env
    docker compose up -d --build
  SHELL
end
```

```bash
# Start VM
vagrant up

# SSH into VM
vagrant ssh

# Stop VM
vagrant halt

# Destroy VM
vagrant destroy
```

---

## Podman (Rootless)

```bash
# Install Podman
sudo apt install podman podman-compose

# Run with Podman
podman-compose up -d --build

# Or build and run manually
podman build -t honeybadger-kernel .
podman run -d \
  --name honeybadger \
  -p 7000:7000 \
  -v ./data:/app/data \
  --env-file .env \
  honeybadger-kernel

# Auto-start on login
podman generate systemd --new --name honeybadger > ~/.config/systemd/user/honeybadger.service
systemctl --user enable honeybadger
```

---

## Cloud Deployment

### AWS (EC2 + Docker)

```bash
# Launch EC2 instance (Ubuntu 22.04)
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type t3.large \
  --key-name mykey \
  --security-group-ids sg-xxx \
  --user-data '#!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose-plugin
    git clone https://github.com/honeybadger-ai/honeybadger.git /opt/honeybadger
    cd /opt/honeybadger
    cp .env.example .env
    docker compose up -d --build'
```

### GCP (Compute Engine)

```bash
# Create instance
gcloud compute instances create honeybadger \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose-plugin
    git clone https://github.com/honeybadger-ai/honeybadger.git /opt/honeybadger
    cd /opt/honeybadger
    cp .env.example .env
    docker compose up -d --build'
```

### Azure (VM)

```bash
# Create VM
az vm create \
  --resource-group myResourceGroup \
  --name honeybadger \
  --image Ubuntu2204 \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --custom-data '#!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose-plugin
    git clone https://github.com/honeybadger-ai/honeybadger.git /opt/honeybadger
    cd /opt/honeybadger
    cp .env.example .env
    docker compose up -d --build'
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml honeybadger

# Check services
docker service ls

# Scale service
docker service scale honeybadger_honeybadger=3

# Remove stack
docker stack rm honeybadger
```

### Kubernetes (Helm)

```yaml
# Chart.yaml
apiVersion: v2
name: honeybadger-kernel
version: 1.0.0
description: Honey Badger Kernel OS
```

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Add repo
helm repo add honeybadger https://honeybadger-ai.github.io/charts
helm repo update

# Install
helm install honeybadger honeybadger/honeybadger-kernel \
  --set replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.host=honeybadger.yourdomain.com
```

---

## Environment Configuration

### Core Settings

```bash
# .env file

# Network
APP_BIND=127.0.0.1          # Bind address (0.0.0.0 for LAN)
APP_PORT=7000               # HTTP port

# Authentication
AUTH_ENABLED=true           # Enable login
LOCALHOST_BYPASS=false      # Dev bypass for localhost
SECURE_COOKIES=true         # HTTPS-only cookies

# Database
DATABASE_URL=sqlite:///./data/app.db

# LLM Providers
LLM_HOST=localhost          # Local LLM server
LLM_HOSTS=host1:8000,host2:8000  # Multiple hosts
OPENAI_API_KEY=sk-...       # OpenAI API key

# Search
SEARXNG_INSTANCE=http://localhost:8080

# Vector Database
CHROMADB_HOST=localhost
CHROMADB_PORT=8100

# Admin
HONEYBADGER_ADMIN_USER=admin
HONEYBADGER_ADMIN_PASSWORD=changeme
```

### Feature Flags

```bash
# .env or data/features.json

web_search=true
web_fetch=true
deep_research=false
memory=true
document_editor=true
rag=true
sensitive_filter=true
gallery=true
```

### Model Configuration

```bash
# Model endpoints
DEFAULT_ENDPOINT_ID=local-ollama
DEFAULT_MODEL=llama3:8b

# Fallbacks
DEFAULT_MODEL_FALLBACKS=[
  {"endpoint_id": "openai", "model": "gpt-4"},
  {"endpoint_id": "anthropic", "model": "claude-3-sonnet"}
]

# Research
RESEARCH_ENDPOINT_ID=local-vllm
RESEARCH_MODEL=llama3:70b
```

---

## Security Hardening

### 1. Authentication

```bash
# Strong admin password
HONEYBADGER_ADMIN_PASSWORD=$(openssl rand -base64 32)

# Enable 2FA
# Navigate to Settings → Security → Enable 2FA

# Disable open signup
# Navigate to Settings → Auth → Open Signup: OFF
```

### 2. Network Security

```bash
# Bind to localhost only
APP_BIND=127.0.0.1

# Enable secure cookies (requires HTTPS)
SECURE_COOKIES=true

# Disable localhost bypass in production
LOCALHOST_BYPASS=false
```

### 3. API Keys

```bash
# Rotate API keys regularly
# Store in .env, never in code

# Disable unused features
HONEYBADGER_DISABLE_MCP=true  # If not using MCP
```

### 4. File System

```bash
# Set proper permissions
chmod 600 .env
chmod 700 data/
chown -R honeybadger:honeybadger data/

# Enable file integrity monitoring
# Use tools like AIDE or Tripwire
```

### 5. Container Security

```bash
# Run as non-root
# Docker Compose already handles this

# Limit resources
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G

# Read-only filesystem (where possible)
read_only: true
tmpfs:
  - /tmp
  - /run
```

### 6. Audit Logging

```bash
# Enable audit logs
# In data/settings.json:
{
  "audit_logging": true,
  "audit_retention_days": 90
}
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 2: Self-Signed (Development)

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/honeybadger.key \
  -out /etc/ssl/certs/honeybadger.crt

# Update permissions
chmod 600 /etc/ssl/private/honeybadger.key
chmod 644 /etc/ssl/certs/honeybadger.crt
```

### Option 3: Cloudflare Tunnel

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Run tunnel
cloudflared tunnel --url http://localhost:7000
```

---

## Reverse Proxy Configuration

### Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/honeybadger.crt;
    ssl_certificate_key /etc/ssl/private/honeybadger.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://127.0.0.1:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Static files caching
    location /static/ {
        proxy_pass http://127.0.0.1:7000;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Caddy

```Caddyfile
yourdomain.com {
    reverse_proxy localhost:7000
    
    header {
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
}
```

### Traefik

```yaml
# docker-compose.yml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.honeybadger.rule=Host(`yourdomain.com`)"
  - "traefik.http.routers.honeybadger.entrypoints=websecure"
  - "traefik.http.routers.honeybadger.tls.certresolver=letsencrypt"
  - "traefik.http.services.honeybadger.loadbalancer.server.port=7000"
```

---

## Monitoring & Observability

### Health Checks

```bash
# Application health
curl -s http://localhost:7000/health | jq .

# Docker health
docker compose ps
docker compose logs --tail=50 honeybadger
```

### Metrics Collection

```bash
# Enable metrics endpoint
# In data/settings.json:
{
  "metrics_enabled": true,
  "metrics_port": 9090
}

# Prometheus scrape config
scrape_configs:
  - job_name: 'honeybadger'
    static_configs:
      - targets: ['localhost:9090']
```

### Log Aggregation

```bash
# Docker logs to file
docker compose logs -f honeybadger >> /var/log/honeybadger/app.log 2>&1

# Log rotation
cat > /etc/logrotate.d/honeybadger << EOF
/var/log/honeybadger/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0640 honeybadger honeybadger
}
EOF
```

### Alerting

```bash
# Health check script
#!/bin/bash
if ! curl -sf http://localhost:7000/health > /dev/null; then
    echo "Honey Badger is down!" | mail -s "Alert: Honey Badger" admin@yourdomain.com
    systemctl restart honeybadger-ui
fi

# Cron job
*/5 * * * * /opt/honeybadger/healthcheck.sh
```

---

## Backup & Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/honeybadger/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Stop services
docker compose stop honeybadger

# Backup data
cp -r data/ $BACKUP_DIR/

# Backup database
sqlite3 data/app.db ".backup '$BACKUP_DIR/app.db'"

# Backup settings
cp .env $BACKUP_DIR/
cp data/settings.json $BACKUP_DIR/
cp data/features.json $BACKUP_DIR/

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Start services
docker compose start honeybadger

# Cleanup old backups (keep 30 days)
find /backup/honeybadger -name "*.tar.gz" -mtime +30 -delete
```

### Recovery

```bash
# Stop services
docker compose stop

# Restore data
tar -xzf /backup/honeybadger/20240101.tar.gz -C /

# Restart
docker compose up -d
```

### Database Migration

```bash
# Export data
sqlite3 data/app.db ".dump" > backup.sql

# Import data
sqlite3 data/app.db < backup.sql
```

---

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  honeybadger:
    deploy:
      replicas: 3
      
  # Load balancer
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
```

### Vertical Scaling

```yaml
# docker-compose.yml
services:
  honeybadger:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
```

### Database Scaling

```bash
# Switch to PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/honeybadger

# Or MySQL
DATABASE_URL=mysql://user:pass@localhost:3306/honeybadger
```

### Cache Scaling

```bash
# Add Redis cache
REDIS_URL=redis://localhost:6379/0

# Docker Compose
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :7000
netstat -tlnp | grep 7000

# Kill process
kill -9 <PID>
```

#### 2. Database Locked

```bash
# Check for stale locks
ls -la data/app.db*
rm -f data/app.db-wal data/app.db-shm

# Restart
docker compose restart honeybadger
```

#### 3. Out of Memory

```bash
# Check memory usage
docker stats
free -h

# Increase limits
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 16G
```

#### 4. GPU Not Detected

```bash
# NVIDIA
docker compose exec honeybadger nvidia-smi

# Check CUDA
docker compose exec honeybadger nvidia-smi -L

# Reinstall CUDA support
docker compose exec honeybadger pip install nvidia-cuda-runtime-cu12
```

#### 5. Search Not Working

```bash
# Check SearXNG
curl http://localhost:8080/search?q=test&format=json

# Restart SearXNG
docker compose restart searxng

# Check logs
docker compose logs searxng
```

#### 6. Vector Database Issues

```bash
# Check ChromaDB
curl http://localhost:8100/api/v1/heartbeat

# Reset ChromaDB
rm -rf data/chrom/
docker compose restart
```

### Debug Mode

```bash
# Enable debug logging
# .env
LOG_LEVEL=DEBUG

# Or in settings.json
{
  "debug": true,
  "verbose_logging": true
}
```

### Performance Profiling

```bash
# Enable profiling
# .env
PROFILING_ENABLED=true

# Access profiler at
http://localhost:7000/debug/profiler
```

---

## Support

- **Documentation:** https://docs.honeybadger.ai
- **Issues:** https://github.com/honeybadger-ai/honeybadger/issues
- **Discord:** https://discord.gg/honeybadger
- **Email:** support@honeybadger.ai

---

```
═══════════════════════════════════════════════════════════════════
  HONEY BADGER KERNEL — PRODUCTION READY
  All systems operational | Build TITAN
═══════════════════════════════════════════════════════════════════
```
