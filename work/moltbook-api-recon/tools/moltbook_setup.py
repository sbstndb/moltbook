#!/usr/bin/env python3
"""
Moltbook Setup - Configuration management tool

Sets up ~/.moltbook/config.json with your API key and preferences.

Usage:
    python moltbook_setup.py
"""

import os
import json
import sys
from pathlib import Path


def main():
    print("\n" + "="*50)
    print("🦞 Moltbook Configuration Setup")
    print("="*50 + "\n")

    # Create config directory
    config_dir = Path.home() / ".moltbook"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config.json"

    # Check if exists
    if config_path.exists():
        print(f"⚠️  Config already exists at: {config_path}")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing config.")
            return 0

    # Gather config
    print("Let's set up your Moltbook configuration:\n")

    api_key = input("API Key (moltbook_sk_...): ").strip()
    while not api_key.startswith("moltbook_sk_"):
        print("⚠️  API key should start with 'moltbook_sk_'")
        api_key = input("API Key: ").strip()

    default_submolt = input("\nDefault submolt [general]: ").strip() or "general"

    print("\n✓ Configuration saved!")
    print(f"  Location: {config_path}")
    print(f"  API Key: {api_key[:20]}...")
    print(f"  Default Submolt: {default_submolt}")

    # Save config
    config = {
        "api_key": api_key,
        "default_submolt": default_submolt,
        "auto_format": True,
        "quality_check": True,
        "posting": {
            "default_delay_seconds": 1800,
            "max_retries": 3
        }
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Set permissions
    os.chmod(config_path, 0o600)

    print("\nYou're ready to post! Try:")
    print("  python smart_poster.py --help")

    return 0


if __name__ == "__main__":
    sys.exit(main())
