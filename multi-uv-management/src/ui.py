"""
UI Panel for Multi UV Management addon.

This module defines the main panel that appears in the UV Editor sidebar.
It handles the display of UV tabs, buttons, and dynamic UI states based on
selected objects and their UV layers.
"""

import bpy
from .utils import get_uv_status, get_uv_name_for_tab, has_different_active_uv, has_locked_uv_in_selection


class MULTIUV_PT_MainPanel(bpy.types.Panel):
    """
    Main panel for Multi UV Management.

    Displays in UV Editor and Shader Editor sidebar with tabs for up to 4 UV layers
    and buttons for managing UV data across multiple objects.
    """
    bl_label = "Multi UV"
    bl_idname = "MULTIUV_PT_main_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Multi UV'

    @classmethod
    def poll(cls, context):
        # Show in Shader Editor (Shading view)
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout

        # Check if selected objects have different active UVs
        has_diff_active = has_different_active_uv(context)

        # Get active tab from scene property
        active_tab = context.scene.multiuv_active_tab
        uv_index = int(active_tab[-1]) - 1

        # Get UV status for current tab
        uv_status = get_uv_status(context, uv_index)

        # Get lock state for current UV
        lock_prop_name = f"multiuv_lock_uv{uv_index + 1}"
        is_locked = getattr(context.scene, lock_prop_name, False)

        # Check if any selected object has this UV locked
        has_locked = has_locked_uv_in_selection(context, uv_index)

        # Get selected mesh count
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        selected_count = len(selected_meshes)

        # Warning message area
        if has_diff_active:
            # Different active UVs warning
            box = layout.box()
            box.label(text="Selected objects have different active UV", icon='ERROR')
        elif uv_status == 'partial' and not has_diff_active:
            # Not all objects have this UV
            box = layout.box()
            box.label(text=f"Not all selected objects have {active_tab}, click Create to unify the UV slots", icon='INFO')

        # Create tabs row
        row = layout.row(align=True)

        # Determine which UV is actually active in the objects
        actual_active_uv = -1
        has_selection = False
        if selected_meshes:
            has_selection = True
            for obj in selected_meshes:
                if obj.data.uv_layers:
                    actual_active_uv = obj.data.uv_layers.active_index
                    break

        # Draw UV tab buttons (UV1, UV2, UV3, UV4)
        for i in range(1, 5):
            tab_name = f"UV{i}"
            tab_uv_index = i - 1
            tab_uv_status = get_uv_status(context, tab_uv_index)

            col = row.column(align=True)

            # Determine button state
            is_selected_tab = (tab_name == active_tab)
            is_active_uv = (tab_uv_index == actual_active_uv)

            # Disable tabs that don't exist on all selected objects when there's different active UVs
            if has_diff_active and tab_uv_status != 'all':
                col.enabled = False

            # Set color based on state
            if has_selection and not has_diff_active:
                # Has selected objects and all have same active UV
                if is_selected_tab and tab_uv_status in ('none', 'partial'):
                    # Selected tab but no/partial UV data - red alert
                    col.alert = True
                elif is_active_uv and tab_uv_status != 'none':
                    # This UV is actually active - blue (depress state)
                    pass
            # else: no selection or different active UVs - all tabs remain default gray

            # Draw tab button with appropriate visual state
            depress = has_selection and not has_diff_active and is_active_uv and tab_uv_status != 'none'
            op = col.operator("multiuv.switch_tab", text=tab_name, depress=depress)
            op.tab_name = tab_name

        # First row of action buttons
        layout.separator()
        row = layout.row(align=True)

        # Create button (only for UV2, UV3, UV4 - UV1 always exists)
        if uv_index > 0:
            col = row.column(align=True)
            if uv_status in ('none', 'partial'):
                # No UV or partial - Create is enabled unless locked
                if has_locked:
                    col.enabled = False
                else:
                    col.enabled = True
            else:
                # UV exists on all - Create is disabled
                col.enabled = False
            op = col.operator("multiuv.create_uv", text="Create")
            op.uv_index = uv_index

        # Rename button
        col = row.column(align=True)
        if uv_status in ('none', 'partial') or is_locked:
            # Disabled if no UV, partial UV, or locked
            col.enabled = False
        else:
            col.enabled = True
        op = col.operator("multiuv.rename_uv", text="Rename")
        op.uv_index = uv_index

        # Delete button (only for UV2, UV3, UV4 - UV1 cannot be deleted)
        if uv_index > 0:
            col = row.column(align=True)
            if uv_status in ('none', 'partial') or is_locked:
                # Disabled if no UV, partial UV, or locked
                col.enabled = False
            else:
                col.enabled = True
            op = col.operator("multiuv.delete_uv", text="Delete")
            op.uv_index = uv_index

        # Lock toggle button (last position in row)
        col = row.column(align=True)
        if uv_status == 'none':
            # No UV - lock button disabled
            col.enabled = False
        elif uv_status == 'partial':
            # Partial UV - lock button enabled and highlighted if locked
            col.enabled = True
            if has_locked:
                # Highlight lock button when some objects have locked UV
                col.alert = True
        else:
            # All have UV - normal state
            col.enabled = True
        icon = 'LOCKED' if is_locked else 'UNLOCKED'
        col.prop(context.scene, lock_prop_name, text="Lock", icon=icon, toggle=True)

        # Second row: Copy/Paste/Restore buttons
        layout.separator()
        row = layout.row(align=True)

        # Copy button
        col = row.column(align=True)
        if uv_status == 'none':
            # No UV to copy
            col.enabled = False
        else:
            col.enabled = True
        op = col.operator("multiuv.copy_uv", text="Copy", icon='COPYDOWN')
        op.uv_index = uv_index

        # Paste button - only enabled when clipboard has data and not locked
        col = row.column(align=True)
        from . import _clipboard_data
        has_clipboard_data = len(_clipboard_data) > 0
        if not has_clipboard_data or is_locked:
            # No clipboard data or locked - disable paste
            col.enabled = False
        else:
            col.enabled = True
        op = col.operator("multiuv.paste_uv", text="Paste", icon='PASTEDOWN')
        op.uv_index = uv_index

        # Restore button
        col = row.column(align=True)
        # Restore is always enabled if there's backup data
        op = col.operator("multiuv.restore_uv", text="Restore", icon='LOOP_BACK')
        op.uv_index = uv_index

        # Display UV Name
        layout.separator()
        box = layout.box()
        row = box.row()
        row.label(text="UV Name:")

        # Check if in rename mode for this UV index
        if context.scene.multiuv_rename_mode and context.scene.multiuv_rename_index == uv_index:
            # Show input field
            row.prop(context.scene, "multiuv_rename_value", text="")
            # Show confirm and cancel buttons
            row.operator("multiuv.confirm_rename", text="", icon='CHECKMARK')
            row.operator("multiuv.cancel_rename", text="", icon='CANCEL')
        else:
            # Show UV name as label
            uv_name = get_uv_name_for_tab(context, uv_index)
            row.label(text=uv_name)

        # Show selected object count below UV name
        if selected_count > 0:
            row = box.row()
            row.label(text=f"{selected_count} objects selected")

        # Create Texture button (only in Shading view with shader nodes)
        layout.separator()

        # Get UV name to check if unified
        uv_name = get_uv_name_for_tab(context, uv_index)
        is_unified = uv_name and uv_name != "multiple names" and uv_name != ""

        row = layout.row()
        if is_unified:
            op = row.operator("multiuv.create_texture", text="Create Texture", icon='TEXTURE')
            op.uv_index = uv_index
        else:
            row.enabled = False
            op = row.operator("multiuv.create_texture", text="Create Texture", icon='TEXTURE')
            op.uv_index = uv_index
            row = layout.row()
            row.label(text="Need unify the UV name", icon='ERROR')


class MULTIUV_PT_BatchOperationPanel(bpy.types.Panel):
    """
    Batch Operation panel for Multi UV Management.

    Provides batch operations for copying UV layer structure from active object.
    """
    bl_label = "Batch Operation"
    bl_idname = "MULTIUV_PT_batch_operation_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Multi UV'
    bl_options = {'DEFAULT_CLOSED'}  # Collapsed by default

    @classmethod
    def poll(cls, context):
        # Show in Shader Editor (Shading view)
        return context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'ShaderNodeTree'

    def draw(self, context):
        layout = self.layout

        # Check if we have multiple objects with one active
        active_obj = context.active_object
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        has_active_mesh = active_obj and active_obj.type == 'MESH' and active_obj in selected_meshes
        has_multiple_objects = len(selected_meshes) > 1

        # Enable buttons only when there's an active mesh and multiple objects selected
        buttons_enabled = has_active_mesh and has_multiple_objects

        # Copy UV Layers From Active button
        row = layout.row()
        row.enabled = buttons_enabled
        row.operator("multiuv.copy_uv_layers_from_active", text="Copy UV Layers From Active", icon='DUPLICATE')

        # Force UV Layers From Active button (with danger indication)
        row = layout.row()
        row.enabled = buttons_enabled
        row.alert = True  # Red/danger indication
        row.operator("multiuv.force_uv_layers_from_active", text="Force UV Layers From Active", icon='ERROR')
