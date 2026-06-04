#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#   HONEY BADGER KERNEL OS — Uninstaller
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="${HOME}/honeybadger"

echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
echo -e "${RED}  HONEY BADGER KERNEL — Uninstaller${NC}"
echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Stop service
if systemctl is-active --quiet honeybadger 2>/dev/null; then
    echo "Stopping service..."
    sudo systemctl stop honeybadger
    sudo systemctl disable honeybadger
    sudo rm -f /etc/systemd/system/honeybadger.service
    sudo systemctl daemon-reload
    echo -e "${GREEN}✓ Service removed${NC}"
fi

# Stop Docker
if [ -d "$INSTALL_DIR" ] && command -v docker &> /dev/null; then
    cd "$INSTALL_DIR" 2>/dev/null && docker compose down 2>/dev/null || true
fi

# Remove directory
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    read -p "Delete installation directory ($INSTALL_DIR)? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo -e "${GREEN}✓ Removed $INSTALL_DIR${NC}"
    else
        echo -e "${YELLOW}! Kept $INSTALL_DIR${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✓ Uninstallation complete${NC}"
