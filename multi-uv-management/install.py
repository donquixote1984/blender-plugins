#!/usr/bin/env python3
"""Install script for Multi UV Management addon to Blender 5.0."""

import shutil
from pathlib import Path

# Blender 5.0 user extensions path
BLENDER_ADDONS_PATH = Path(r"C:\Users\wuguoxu\AppData\Roaming\Blender Foundation\Blender\5.0\extensions\user_default")

# Source and target paths
SRC_DIR = Path("src")
TARGET_DIR = BLENDER_ADDONS_PATH / "multi_uv_management"

def install_addon():
    """Install the addon to Blender's extensions directory."""

    # Check if Blender extensions directory exists
    if not BLENDER_ADDONS_PATH.exists():
        print(f"Error: Blender extensions directory not found: {BLENDER_ADDONS_PATH}")
        return False

    # Remove old installation if exists
    if TARGET_DIR.exists():
        print(f"Removing old installation: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR)

    # Copy addon files
    print(f"Installing addon to: {TARGET_DIR}")
    shutil.copytree(SRC_DIR, TARGET_DIR)

    print("\nInstallation complete!")
    print("\nNext steps:")
    print("1. Restart Blender")
    print("2. Go to Edit > Preferences > Add-ons")
    print("3. Search for 'Multi UV Management'")
    print("4. Enable the addon")

    return True

if __name__ == "__main__":
    install_addon()
