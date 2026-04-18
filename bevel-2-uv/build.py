#!/usr/bin/env python3
"""Build script to package the Blender addon into a zip file."""

import zipfile
from pathlib import Path


def create_release_zip():
    """Create a zip file of the addon in the release folder."""

    src_dir = Path("src")
    release_dir = Path("release")

    release_dir.mkdir(exist_ok=True)

    zip_name = "bevel_2_uv.zip"
    zip_path = release_dir / zip_name

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                arcname = Path("bevel_2_uv") / file_path.relative_to(src_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nRelease created: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    create_release_zip()
