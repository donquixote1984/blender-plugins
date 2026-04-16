"""
Multi UV Management Addon for Blender

This addon provides a comprehensive interface for managing multiple UV layers
across multiple objects simultaneously. It supports up to 4 UV layers with
features like copy/paste, lock protection, and batch operations.
"""

bl_info = {
    "name": "Multi UV Management",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "UV Editor > Sidebar > Multi UV",
    "description": "Multi UV Management Tools",
    "category": "UV",
}

import bpy
from . import i18n
from .operators import (
    MULTIUV_OT_SwitchTab,
    MULTIUV_OT_CreateUV,
    MULTIUV_OT_RenameUV,
    MULTIUV_OT_ConfirmRename,
    MULTIUV_OT_CancelRename,
    MULTIUV_OT_DeleteUV,
    MULTIUV_OT_CopyUV,
    MULTIUV_OT_PasteUV,
    MULTIUV_OT_RestoreUV,
    MULTIUV_OT_CopyUVLayersFromActive,
    MULTIUV_OT_ForceUVLayersFromActive,
    MULTIUV_OT_CreateTexture,
)
from .ui import MULTIUV_PT_MainPanel, MULTIUV_PT_BatchOperationPanel


# Global storage for clipboard and backup data
# These cannot be stored as Scene properties because they contain complex data structures
_clipboard_data = {}
_backup_data = {}


# All classes to be registered
classes = (
    MULTIUV_OT_SwitchTab,
    MULTIUV_OT_CreateUV,
    MULTIUV_OT_RenameUV,
    MULTIUV_OT_ConfirmRename,
    MULTIUV_OT_CancelRename,
    MULTIUV_OT_DeleteUV,
    MULTIUV_OT_CopyUV,
    MULTIUV_OT_PasteUV,
    MULTIUV_OT_RestoreUV,
    MULTIUV_OT_CopyUVLayersFromActive,
    MULTIUV_OT_ForceUVLayersFromActive,
    MULTIUV_OT_CreateTexture,
    MULTIUV_PT_MainPanel,
    MULTIUV_PT_BatchOperationPanel,
)


def register():
    """Register addon classes and properties."""
    from bpy.props import EnumProperty, BoolProperty, IntProperty, StringProperty

    # Active tab selection (UV1, UV2, UV3, UV4)
    bpy.types.Scene.multiuv_active_tab = EnumProperty(
        name="Active Tab",
        items=[
            ('UV1', "UV1", "UV1 Tab"),
            ('UV2', "UV2", "UV2 Tab"),
            ('UV3', "UV3", "UV3 Tab"),
            ('UV4', "UV4", "UV4 Tab"),
        ],
        default='UV1'
    )

    # Rename mode state
    bpy.types.Scene.multiuv_rename_mode = BoolProperty(
        name="Rename Mode",
        default=False
    )

    # Index of UV being renamed
    bpy.types.Scene.multiuv_rename_index = IntProperty(
        name="Rename Index",
        default=0
    )

    # New name value during rename
    bpy.types.Scene.multiuv_rename_value = StringProperty(
        name="New UV Name",
        default=""
    )

    # Lock states for each UV layer (prevents Delete/Rename operations)
    bpy.types.Scene.multiuv_lock_uv1 = BoolProperty(
        name="Lock UV1",
        default=False
    )

    bpy.types.Scene.multiuv_lock_uv2 = BoolProperty(
        name="Lock UV2",
        default=False
    )

    bpy.types.Scene.multiuv_lock_uv3 = BoolProperty(
        name="Lock UV3",
        default=False
    )

    bpy.types.Scene.multiuv_lock_uv4 = BoolProperty(
        name="Lock UV4",
        default=False
    )

    # Note: Clipboard and backup data are stored in module-level globals
    # (_clipboard_data and _backup_data) because Scene properties cannot store
    # complex nested dictionaries

    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register internationalization
    i18n.register()


def unregister():
    """Unregister addon classes and properties."""
    # Unregister internationalization
    i18n.unregister()

    # Unregister all classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Delete all scene properties
    del bpy.types.Scene.multiuv_active_tab
    del bpy.types.Scene.multiuv_rename_mode
    del bpy.types.Scene.multiuv_rename_index
    del bpy.types.Scene.multiuv_rename_value
    del bpy.types.Scene.multiuv_lock_uv1
    del bpy.types.Scene.multiuv_lock_uv2
    del bpy.types.Scene.multiuv_lock_uv3
    del bpy.types.Scene.multiuv_lock_uv4


if __name__ == "__main__":
    register()
