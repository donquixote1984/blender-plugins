"""
Bevel 2 UV Addon for Blender

This addon provides a one-click bevel operation that automatically preserves
UV seams on the middle edge after beveling with 2 segments.
"""

bl_info = {
    "name": "Bevel 2 UV",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D View > Edge Menu",
    "description": "Bevel edges with 2 segments and preserve UV seams on middle edge",
    "category": "Mesh",
}

import bpy
from .operator import BEVEL2UV_OT_BevelWithSeam, menu_func


classes = (
    BEVEL2UV_OT_BevelWithSeam,
)


def register():
    """Register addon classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func)


def unregister():
    """Unregister addon classes."""
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
