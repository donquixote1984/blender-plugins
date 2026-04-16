"""
Utility functions for Multi UV Management addon.

This module provides helper functions for checking UV layer status,
names, and active states across multiple selected objects.
"""


def get_uv_status(context, uv_index):
    """
    Check UV status for selected objects at the specified index.

    Args:
        context: Blender context
        uv_index: UV layer index to check (0-3 for UV1-UV4)

    Returns:
        str: 'all' if all objects have UV at this index,
             'none' if no objects have UV at this index,
             'partial' if some objects have UV at this index
    """
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

    if not selected_meshes:
        return 'none'

    has_uv_count = 0
    for obj in selected_meshes:
        if len(obj.data.uv_layers) > uv_index:
            has_uv_count += 1

    if has_uv_count == len(selected_meshes):
        return 'all'
    elif has_uv_count == 0:
        return 'none'
    else:
        return 'partial'


def get_uv_name_for_tab(context, uv_index):
    """
    Get UV name for the specified UV index from selected objects.

    Args:
        context: Blender context
        uv_index: UV layer index to check (0-3 for UV1-UV4)

    Returns:
        str: UV layer name if all objects have the same name,
             "multiple names" if objects have different names,
             "" if no UV layer exists at this index
    """
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH' and obj.data.uv_layers]

    if not selected_meshes:
        return ""

    uv_names = set()
    for obj in selected_meshes:
        if len(obj.data.uv_layers) > uv_index:
            uv_names.add(obj.data.uv_layers[uv_index].name)

    if len(uv_names) == 0:
        return ""
    elif len(uv_names) == 1:
        return uv_names.pop()
    else:
        return "multiple names"


def is_uv_active(context, uv_index):
    """
    Check if the UV at the specified index is active for all selected objects.

    Args:
        context: Blender context
        uv_index: UV layer index to check (0-3 for UV1-UV4)

    Returns:
        bool: True if all selected objects have this UV as active,
              False otherwise
    """
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

    if not selected_meshes:
        return False

    all_active = True
    for obj in selected_meshes:
        if len(obj.data.uv_layers) > uv_index:
            if obj.data.uv_layers.active_index != uv_index:
                all_active = False
                break
        else:
            all_active = False
            break

    return all_active


def has_different_active_uv(context):
    """
    Check if selected objects have different active UV indices.

    This is used to detect when multiple objects are selected with
    different UV layers active, which requires special UI handling.

    Args:
        context: Blender context

    Returns:
        bool: True if selected objects have different active UV indices,
              False if all have the same active UV or no objects selected
    """
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

    if not selected_meshes:
        return False

    active_indices = set()
    for obj in selected_meshes:
        if obj.data.uv_layers:
            active_indices.add(obj.data.uv_layers.active_index)

    # If more than one different active index, they have different active UVs
    return len(active_indices) > 1


def has_locked_uv_in_selection(context, uv_index):
    """
    Check if any selected object has the specified UV layer locked.

    Args:
        context: Blender context
        uv_index: UV layer index to check (0-3 for UV1-UV4)

    Returns:
        bool: True if any object has this UV locked, False otherwise
    """
    selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

    if not selected_meshes:
        return False

    lock_prop_name = f"multiuv_lock_uv{uv_index + 1}"

    # Check if any object has this UV and it's locked
    for obj in selected_meshes:
        if len(obj.data.uv_layers) > uv_index:
            # If this object has the UV layer, check if it's locked
            # Note: Lock is a scene-level property, so we check the scene
            if getattr(context.scene, lock_prop_name, False):
                return True

    return False
