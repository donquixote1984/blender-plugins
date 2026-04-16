#!/usr/bin/env python3
"""Build script to package the Blender addon into a zip file."""

import os
import zipfile
from pathlib import Path


def create_release_zip():
    """Create a zip file of the addon in the release folder."""

    # Define paths
    src_dir = Path("src")
    release_dir = Path("release")

    # Create release directory if it doesn't exist
    release_dir.mkdir(exist_ok=True)

    # Use fixed zip filename
    zip_name = "multi_uv_management.zip"
    zip_path = release_dir / zip_name

    # Create the zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from src directory
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                # Calculate the archive name (relative path from src)
                arcname = Path("multi_uv_management") / file_path.relative_to(src_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nRelease created: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    create_release_zip()
