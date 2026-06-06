#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#   HONEY BADGER KERNEL OS — One-Liner Installer
#   Elite Tech Conglomerate | Zero Compromise
# ═══════════════════════════════════════════════════════════════════
#
#   Usage:
#     curl -fsSL https://raw.githubusercontent.com/Drstone0007/honeybadger-ai/main/install.sh | bash
#
#   Or with options:
#     curl -fsSL https://raw.githubusercontent.com/Drstone0007/honeybadger-ai/main/install.sh | bash -s -- --dir /opt/honeybadger --port 7000
#
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ── Config ──
INSTALL_DIR="${HOME}/honeybadger"
PORT=7000
BRANCH="main"
SKIP_DOCKER=false
SKIP_DEPS=false

# ── Banner ──
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
    ██╗  ██╗██╗███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
    ██║  ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
    ███████║██║███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝
    ██╔══██║██║╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝
    ██║  ██║██║███████║   ██║   ╚██████╔╝██║  ██║   ██║
    ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝
    ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
EOF
    echo -e "${NC}"
    echo -e "${BOLD}  KERNEL OS v1.0 | TITAN BUILD${NC}"
    echo -e "  One-Liner Installer"
    echo ""
}

# ── Logging ──
log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[i]${NC} $1"; }

# ── Parse Arguments ──
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dir) INSTALL_DIR="$2"; shift 2 ;;
            --port) PORT="$2"; shift 2 ;;
            --branch) BRANCH="$2"; shift 2 ;;
            --skip-docker) SKIP_DOCKER=true; shift ;;
            --skip-deps) SKIP_DEPS=true; shift ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --dir DIR         Install directory (default: ~/honeybadger)"
                echo "  --port PORT       HTTP port (default: 7000)"
                echo "  --branch BRANCH   Git branch (default: main)"
                echo "  --skip-docker     Skip Docker installation"
                echo "  --skip-deps       Skip system dependencies"
                echo "  --help            Show this help"
                exit 0
                ;;
            *) warn "Unknown option: $1" ;;
        esac
    done
}

# ── Detect OS ──
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            PKG_MANAGER="apt-get"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            PKG_MANAGER="yum"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
            PKG_MANAGER="pacman"
        else
            OS="linux"
            PKG_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        PKG_MANAGER="choco"
    else
        OS="unknown"
        PKG_MANAGER="unknown"
    fi
    info "Detected OS: ${OS}"
}

# ── Check Dependencies ──
check_deps() {
    if [ "$SKIP_DEPS" = true ]; then
        warn "Skipping dependency check"
        return
    fi

    echo -e "${BOLD}Checking dependencies...${NC}"

    # Git
    if ! command -v git &> /dev/null; then
        warn "Git not found. Installing..."
        install_pkg git
    fi
    log "Git $(git --version | cut -d' ' -f3)"

    # Python
    PYTHON_CMD=""
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" &> /dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        warn "Python 3 not found. Installing..."
        install_pkg python3
        PYTHON_CMD="python3"
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log "Python ${PYTHON_VERSION}"

    # pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        warn "pip not found. Installing..."
        $PYTHON_CMD -m ensurepip --upgrade 2>/dev/null || install_pkg python3-pip
    fi
    log "pip available"

    # Docker (optional)
    if [ "$SKIP_DOCKER" = false ]; then
        if command -v docker &> /dev/null; then
            log "Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
        else
            warn "Docker not found (optional)"
            info "Install Docker: https://docs.docker.com/get-docker/"
        fi
    fi

    echo ""
}

# ── Install Package ──
install_pkg() {
    local pkg=$1
    case $OS in
        debian) sudo apt-get update -qq && sudo apt-get install -y -qq "$pkg" ;;
        redhat) sudo yum install -y -q "$pkg" ;;
        arch) sudo pacman -S --noconfirm "$pkg" ;;
        macos) brew install "$pkg" ;;
        *) error "Cannot auto-install $pkg. Please install manually." ;;
    esac
}

# ── Clone Repository ──
clone_repo() {
    echo -e "${BOLD}Cloning repository...${NC}"

    if [ -d "$INSTALL_DIR" ]; then
        warn "Directory exists: $INSTALL_DIR"
        read -p "Update existing installation? [Y/n] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            error "Installation cancelled"
        fi
        cd "$INSTALL_DIR"
        git pull origin "$BRANCH" 2>/dev/null || git pull --rebase origin "$BRANCH"
        log "Updated existing installation"
    else
        git clone --depth 1 -b "$BRANCH" https://github.com/Drstone0007/honeybadger-ai.git "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        log "Cloned to $INSTALL_DIR"
    fi
    echo ""
}

# ── Setup Python Environment ──
setup_python() {
    echo -e "${BOLD}Setting up Python environment...${NC}"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        log "Created virtual environment"
    else
        warn "Virtual environment exists"
    fi

    # Activate
    source venv/bin/activate

    # Install dependencies
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    log "Installed Python dependencies"
    echo ""
}

# ── Setup Configuration ──
setup_config() {
    echo -e "${BOLD}Setting up configuration...${NC}"

    # Create .env
    if [ ! -f ".env" ]; then
        cp .env.example .env

        # Generate random admin password
        ADMIN_PASSWORD=$(openssl rand -base64 24 2>/dev/null || head -c 24 /dev/urandom | base64)
        sed -i "s/HONEYBADGER_ADMIN_PASSWORD=.*/HONEYBADGER_ADMIN_PASSWORD=$ADMIN_PASSWORD/" .env 2>/dev/null || \
        sed -i '' "s/HONEYBADGER_ADMIN_PASSWORD=.*/HONEYBADGER_ADMIN_PASSWORD=$ADMIN_PASSWORD/" .env 2>/dev/null

        # Set port
        sed -i "s/APP_PORT=.*/APP_PORT=$PORT/" .env 2>/dev/null || \
        sed -i '' "s/APP_PORT=.*/APP_PORT=$PORT/" .env 2>/dev/null

        log "Created .env with random admin password"
        echo ""
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}  IMPORTANT: Save these credentials!${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo -e "  Admin URL:      ${BOLD}http://localhost:$PORT${NC}"
        echo -e "  Admin User:     ${BOLD}admin${NC}"
        echo -e "  Admin Password: ${BOLD}$ADMIN_PASSWORD${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo ""
    else
        warn ".env already exists, skipping"
    fi

    # Create data directories
    mkdir -p data/{uploads,personal_docs,logs,chroma,huggingface}
    log "Created data directories"
    echo ""
}

# ── Install Systemd Service (Linux) ──
install_service() {
    if [ "$OS" != "debian" ] && [ "$OS" != "redhat" ]; then
        return
    fi

    echo -e "${BOLD}Installing systemd service...${NC}"

    sudo tee /etc/systemd/system/honeybadger.service > /dev/null << EOF
[Unit]
Description=Honey Badger Kernel OS
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=always
RestartSec=5
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable honeybadger
    log "Systemd service installed"
    echo ""
}

# ── Docker Setup ──
setup_docker() {
    if [ "$SKIP_DOCKER" = true ] || ! command -v docker &> /dev/null; then
        return
    fi

    echo -e "${BOLD}Setting up Docker...${NC}"

    if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
        docker compose up -d --build
        log "Docker containers started"
        DOCKER_MODE=true
    else
        warn "No docker-compose.yml found"
    fi
    echo ""
}

# ── Print Summary ──
print_summary() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ Installation Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BOLD}Location:${NC}  $INSTALL_DIR"
    echo -e "  ${BOLD}Port:${NC}      $PORT"
    echo ""

    if [ "${DOCKER_MODE:-false}" = true ]; then
        echo -e "  ${BOLD}Start:${NC}     docker compose up -d"
        echo -e "  ${BOLD}Stop:${NC}      docker compose down"
        echo -e "  ${BOLD}Logs:${NC}      docker compose logs -f"
    else
        echo -e "  ${BOLD}Start:${NC}     cd $INSTALL_DIR && source venv/bin/activate && python app.py"
        echo -e "  ${BOLD}Service:${NC}   sudo systemctl start honeybadger"
    fi

    echo ""
    echo -e "  ${BOLD}Open:${NC}      http://localhost:$PORT"
    echo ""
    echo -e "  ${BOLD}Docs:${NC}      docs/production/DEPLOYMENT.md"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ── Main ──
main() {
    print_banner
    parse_args "$@"
    detect_os
    check_deps
    clone_repo
    setup_python
    setup_config
    install_service
    print_summary
}

main "$@"
