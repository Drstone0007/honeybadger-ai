#!/usr/bin/env python3
"""Setup script to create the daily LinkedIn AI news task in Honey Badger.

Run this once to register the scheduled task:
    python3 scripts/setup_linkedin_task.py

Then enable it via the Tasks UI in Honey Badger.
"""

import json
import sys
import os
import httpx
from pathlib import Path

# Config
HONEYBADGER_URL = os.environ.get("HONEYBADGER_URL", "http://localhost:7000")
SCRIPT_PATH = str(Path(__file__).parent / "linkedin-post.sh")

TASK_CONFIG = {
    "name": "LinkedIn AI News Daily Post",
    "prompt": f"bash {SCRIPT_PATH}",
    "task_type": "action",
    "action": "run_local",
    "schedule": "daily",
    "scheduled_time": "09:00",  # 9 AM
    "output_target": "session",
    "notifications_enabled": True,
}


def create_task():
    """Create the scheduled task via API."""
    # First, we need to get auth. For simplicity, we'll create via the database directly.
    # In production, you'd use the API with proper auth.

    print(f"Creating scheduled task: {TASK_CONFIG['name']}")
    print(f"Schedule: Daily at {TASK_CONFIG['scheduled_time']}")
    print(f"Script: {SCRIPT_PATH}")
    print()

    # Create task via API (requires auth - for now, print instructions)
    print("To create this task:")
    print("1. Open Honey Badger web UI at http://localhost:7000")
    print("2. Go to Tasks section")
    print("3. Click 'Add Task'")
    print(f"4. Name: {TASK_CONFIG['name']}")
    print(f"5. Type: Action")
    print(f"6. Action: run_local")
    print(f"7. Schedule: Daily at {TASK_CONFIG['scheduled_time']}")
    print(f"8. Script/command: bash {SCRIPT_PATH}")
    print("9. Save")
    print()
    print("Or run with --api flag to create via API (requires auth token):")
    print("  export HONEYBADGER_TOKEN=your_token_here")
    print("  python3 scripts/setup_linkedin_task.py --api")

    if "--api" in sys.argv:
        create_via_api()


def create_via_api():
    """Create task via API (requires HONEYBADGER_TOKEN env var)."""
    token = os.environ.get("HONEYBADGER_TOKEN")
    if not token:
        print("Error: HONEYBADGER_TOKEN environment variable not set")
        print("Get a token from Settings > API Tokens in Honey Badger")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = httpx.post(
            f"{HONEYBADGER_URL}/api/tasks",
            json=TASK_CONFIG,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        task = response.json()
        print(f"Task created successfully! ID: {task.get('id')}")
    except Exception as e:
        print(f"Failed to create task: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_task()
