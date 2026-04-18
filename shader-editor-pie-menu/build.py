import os
import zipfile
import shutil
from pathlib import Path

def build_addon():
    """Build Blender addon as zip file"""

    # Define paths
    src_dir = Path("src")
    release_dir = Path("release")
    addon_name = "shader-editor-pie-menu"

    # Ensure release directory exists
    release_dir.mkdir(exist_ok=True)

    # Output zip file path
    zip_path = release_dir / f"{addon_name}.zip"

    # Remove old zip file
    if zip_path.exists():
        zip_path.unlink()

    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Iterate all files in src directory
        for file_path in src_dir.rglob('*'):
            if file_path.is_file():
                # Path in zip: addon_name/relative_path
                arcname = Path(addon_name) / file_path.relative_to(src_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nAddon build complete: {zip_path}")
    print(f"File size: {zip_path.stat().st_size} bytes")

if __name__ == "__main__":
    build_addon()
