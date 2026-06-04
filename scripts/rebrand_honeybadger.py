#!/usr/bin/env python3
"""Honey Badger Rebranding Script — replaces Honey Badger branding.

Usage:
    python3 scripts/rebrand_honeybadger.py              # Dry run (show changes)
    python3 scripts/rebrand_honeybadger.py --apply      # Apply changes
"""

import os
import re
import sys
from pathlib import Path

# ── Branding Map ──
BRAND_MAP = {
    # Core names
    "Honey Badger": "Honey Badger",
    "honeybadger": "honeybadger",
    "HONEYBADGER": "HONEYBADGER",
    
    # Variations
    "honeybadger-ui": "honeybadger-ui",
    "Honey Badger UI": "Honey Badger UI",
    "Honey Badger Chat": "Honey Badger Terminal",
    "Honey Badger Chat Stream": "Honey Badger Stream",
    
    # Env vars
    "HONEYBADGER_ADMIN_USER": "HONEYBADGER_ADMIN_USER",
    "HONEYBADGER_ADMIN_PASSWORD": "HONEYBADGER_ADMIN_PASSWORD",
    "HONEYBADGER_HOST": "HONEYBADGER_HOST",
    "HONEYBADGER_PORT": "HONEYBADGER_PORT",
    "HONEYBADGER_SCRIPT_HOST": "HONEYBADGER_SCRIPT_HOST",
    "HONEYBADGER_DISABLE_MCP": "HONEYBADGER_DISABLE_MCP",
    "HONEYBADGER_INPROCESS_POLLERS": "HONEYBADGER_INPROCESS_POLLERS",
    "HONEYBADGER_INPROCESS_TASKS": "HONEYBADGER_INPROCESS_TASKS",
    "HONEYBADGER_SKIP_RUN_HINT": "HONEYBADGER_SKIP_RUN_HINT",
    "HONEYBADGER_NO_OPEN": "HONEYBADGER_NO_OPEN",
    "HONEYBADGER_AMD_TEST_IMAGE": "HONEYBADGER_AMD_TEST_IMAGE",
    
    # Headers
    "X-Honey Badger-Origin": "X-HoneyBadger-Origin",
    "X-Honey Badger-Kind": "X-HoneyBadger-Kind",
    "X-Honey Badger-Ref": "X-HoneyBadger-Ref",
    "X-Honey Badger-Owner": "X-HoneyBadger-Owner",
    "X-Honey Badger-Internal-Token": "X-HoneyBadger-Internal-Token",
    "X-Honey Badger-Signature": "X-HoneyBadger-Signature",
    "X-Honey Badger-Event": "X-HoneyBadger-Event",
    
    # CSS classes
    ".honeybadger-highlight": ".hb-highlight",
    ".honeybadger-hl-label": ".hb-hl-label",
    
    # localStorage keys (keep prefix for compatibility)
    "honeybadger-theme": "hb-theme",
    "honeybadger-toggles": "hb-toggles",
    "honeybadger-model": "hb-model",
    "honeybadger-sessions": "hb-sessions",
    "honeybadger-notes": "hb-notes",
    "honeybadger-last-user": "hb-last-user",
    "honeybadger-sensitive": "hb-sensitive",
    "honeybadger-integrations": "hb-integrations",
    "honeybadger-custom-themes": "hb-custom-themes",
    "honeybadger-doc-open": "hb-doc-open",
    "honeybadger-folder": "hb-folder",
    "honeybadger-search": "hb-search",
    "honeybadger-incognito": "hb-incognito",
    "honeybadger-rag": "hb-rag",
    "honeybadger-mcp": "hb-mcp",
    "honeybadger-density": "hb-density",
    "honeybadger-research": "hb-research",
    "honeybadger-hidden-presets": "hb-hidden-presets",
    "honeybadger-char-sessions": "hb-char-sessions",
    "honeybadger-tour": "hb-tour",
    "honeybadger-hint": "hb-hint",
    "honeybadger-setup": "hb-setup",
    "honeybadger-prompt": "hb-prompt",
    "honeybadger-toolbar": "hb-toolbar",
    "honeybadger-ui-visibility": "hb-ui-visibility",
    
    # URLs
    "github.com/pewdiepie-archdaemon/honeybadger": "github.com/honeybadger-ai/honeybadger",
    "pewdiepie-archdaemon/honeybadger": "honeybadger-ai/honeybadger",
    
    # Docker
    "honeybadger:": "honeybadger:",
    "container_name: honeybadger": "container_name: honeybadger",
    "docker compose logs honeybadger": "docker compose logs honeybadger",
    "docker compose exec honeybadger": "docker compose exec honeybadger",
    
    # Service
    "honeybadger-ui.service": "honeybadger-ui.service",
    "Description=Honey Badger UI": "Description=Honey Badger UI",
    
    # User
    "useradd -d /app honeybadger": "useradd -d /app honeybadger",
    
    # TOTP
    'issuer_name="Honey Badger"': 'issuer_name="Honey Badger"',
    
    # Cache
    "honeybadger-v": "hb-v",
    
    # Collection names
    "honeybadger_tool_index": "hb_tool_index",
    "honeybadger_memories": "hb_memories",
    "honeybadger_rag": "hb_rag",
    
    # Message IDs
    "@honeybadger.local": "@honeybadger.local",
    
    # Email
    "honeybadger_kind": "hb_kind",
    
    # Preset
    "id: 'honeybadger'": "id: 'honeybadger'",
    "name: 'Honey Badger'": "name: 'Honey Badger'",
    
    # MCP
    '"name": "honeybadger"': '"name": "honeybadger"',
    
    # User-Agent
    "User-Agent: Honey Badger": "User-Agent: HoneyBadger",
    "Honey Badger-Webhook": "HoneyBadger-Webhook",
    
    # OpenRouter
    "X-OpenRouter-Title: Honey Badger": "X-OpenRouter-Title: Honey Badger",
    "HTTP-Referer.*honeybadger": "HTTP-Referer.*honeybadger",
    
    # Copyright
    "Copyright (c) 2025 Honey Badger": "Copyright (c) 2025 Honey Badger",
    "2026 Honey Badger": "2026 Honey Badger",
    
    # App name
    'APP_NAME="Honey Badger"': 'APP_NAME="Honey Badger"',
    "com.honeybadger.launcher": "com.honeybadger.launcher",
    "honeybadger.icns": "honeybadger.icns",
}

# Files to skip (binary, generated, or don't change)
SKIP_FILES = {
    ".git/",
    "node_modules/",
    "venv/",
    "__pycache__/",
    "*.pyc",
    "package-lock.json",
    "*.jpg",
    "*.png",
    "*.gif",
    "*.ico",
    "*.icns",
}

def should_skip(path: Path) -> bool:
    """Check if file should be skipped."""
    path_str = str(path)
    for skip in SKIP_FILES:
        if skip.startswith("*"):
            if path_str.endswith(skip[1:]):
                return True
        elif skip in path_str:
            return True
    return False

def rebrand_file(file_path: Path, apply: bool = False) -> list[str]:
    """Rebrand a single file. Returns list of changes."""
    changes = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return changes
    
    new_content = content
    for old, new in BRAND_MAP.items():
        if old in new_content:
            count = new_content.count(old)
            new_content = new_content.replace(old, new)
            changes.append(f"  {old} → {new} ({count}x)")
    
    if changes and apply:
        file_path.write_text(new_content, encoding="utf-8")
    
    return changes

def main():
    apply = "--apply" in sys.argv
    root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("HONEY BADGER REBRANDING SCRIPT")
    print("=" * 60)
    print(f"Mode: {'APPLY' if apply else 'DRY RUN'}")
    print()
    
    total_changes = 0
    files_changed = 0
    
    for file_path in root.rglob("*"):
        if file_path.is_dir() or should_skip(file_path):
            continue
        
        changes = rebrand_file(file_path, apply)
        if changes:
            files_changed += 1
            total_changes += len(changes)
            rel = file_path.relative_to(root)
            print(f"[{rel}]")
            for change in changes:
                print(change)
            print()
    
    print("=" * 60)
    print(f"Total: {total_changes} changes in {files_changed} files")
    if not apply:
        print("Run with --apply to make changes permanent")
    print("=" * 60)

if __name__ == "__main__":
    main()
