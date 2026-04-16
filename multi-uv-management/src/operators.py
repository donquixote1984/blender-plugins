"""
Operators for Multi UV Management addon.

This module contains all operator classes that handle user interactions:
- Tab switching and UV activation
- UV layer creation, deletion, and renaming
- UV data copy/paste/restore operations
"""

import bpy
from .utils import get_uv_name_for_tab


def get_clipboard():
    """Get the global clipboard data."""
    from . import _clipboard_data
    return _clipboard_data


def get_backup():
    """Get the global backup data."""
    from . import _backup_data
    return _backup_data


class MULTIUV_OT_SwitchTab(bpy.types.Operator):
    """
    Switch to a UV tab and activate the corresponding UV layer.

    When switching tabs, this operator automatically activates the UV layer
    at the corresponding index for all selected mesh objects.
    """
    bl_idname = "multiuv.switch_tab"
    bl_label = "Switch Tab"
    bl_options = {'REGISTER', 'UNDO'}

    tab_name: bpy.props.StringProperty()

    def execute(self, context):
        # Update the active tab in the UI
        context.scene.multiuv_active_tab = self.tab_name

        # Convert tab name to UV index (UV1 -> 0, UV2 -> 1, etc.)
        uv_index = int(self.tab_name[-1]) - 1

        # Check UV status before activating
        from .utils import get_uv_status
        uv_status = get_uv_status(context, uv_index)

        # Only activate UV if all selected objects have it
        # This prevents creating "different active UV" state when some objects don't have the UV
        if uv_status == 'all':
            # Activate the UV layer for all selected mesh objects
            selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            for obj in selected_meshes:
                if len(obj.data.uv_layers) > uv_index:
                    obj.data.uv_layers.active_index = uv_index

        # Force UI refresh in UV Editor
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()

        return {'FINISHED'}


class MULTIUV_OT_CreateUV(bpy.types.Operator):
    """
    Create UV layer at specified index for all selected objects.

    Creates UV layers up to the target index if they don't exist.
    Naming convention: UV1 = "UVMap", UV2+ = "UVMap__NEW__N"
    """
    bl_idname = "multiuv.create_uv"
    bl_label = "Create UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        for obj in selected_meshes:
            # Only create UV layers for objects that don't have enough
            # This allows "unifying" UV slots across multiple objects
            while len(obj.data.uv_layers) <= self.uv_index:
                current_index = len(obj.data.uv_layers)
                # UV1 gets "UVMap", UV2+ get "UVMap__NEW__N" where N is the tab number
                uv_name = "UVMap" if current_index == 0 else f"UVMap__NEW__{current_index + 1}"
                obj.data.uv_layers.new(name=uv_name)

        # After creating UVs, activate the target UV layer for all objects
        for obj in selected_meshes:
            if len(obj.data.uv_layers) > self.uv_index:
                obj.data.uv_layers.active_index = self.uv_index

        return {'FINISHED'}


class MULTIUV_OT_RenameUV(bpy.types.Operator):
    """
    Enter rename mode for UV layer.

    Displays a text input field to rename the UV layer for all selected objects.
    """
    bl_idname = "multiuv.rename_uv"
    bl_label = "Rename UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        # Enter rename mode
        context.scene.multiuv_rename_mode = True
        context.scene.multiuv_rename_index = self.uv_index

        # Set default name from current UV layer
        uv_name = get_uv_name_for_tab(context, self.uv_index)
        if uv_name == "multiple names" or not uv_name:
            # Multiple objects with different names - use default
            context.scene.multiuv_rename_value = f"UVMap__NEW__{self.uv_index + 1}"
        else:
            # Use existing name
            context.scene.multiuv_rename_value = uv_name

        return {'FINISHED'}


class MULTIUV_OT_ConfirmRename(bpy.types.Operator):
    """
    Confirm UV rename operation.

    Applies the new name to the UV layer for all selected objects.
    """
    bl_idname = "multiuv.confirm_rename"
    bl_label = "Confirm"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        new_name = context.scene.multiuv_rename_value
        uv_index = context.scene.multiuv_rename_index

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        # Apply new name to all selected objects
        for obj in selected_meshes:
            if len(obj.data.uv_layers) > uv_index:
                obj.data.uv_layers[uv_index].name = new_name

        # Exit rename mode
        context.scene.multiuv_rename_mode = False

        return {'FINISHED'}


class MULTIUV_OT_CancelRename(bpy.types.Operator):
    """
    Cancel UV rename operation.

    Exits rename mode without applying changes.
    """
    bl_idname = "multiuv.cancel_rename"
    bl_label = "Cancel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Exit rename mode without saving
        context.scene.multiuv_rename_mode = False
        return {'FINISHED'}


class MULTIUV_OT_DeleteUV(bpy.types.Operator):
    """
    Delete UV layer at specified index.

    Removes the UV layer from all selected objects. Protected by lock state.
    Shows confirmation dialog before deletion.
    """
    bl_idname = "multiuv.delete_uv"
    bl_label = "Delete UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def invoke(self, context, event):
        # Show confirmation dialog
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        # Remove UV layer from each object
        for obj in selected_meshes:
            if len(obj.data.uv_layers) > self.uv_index:
                uv_layer = obj.data.uv_layers[self.uv_index]
                obj.data.uv_layers.remove(uv_layer)

        # Force UI refresh in UV Editor
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.tag_redraw()

        return {'FINISHED'}


class MULTIUV_OT_CopyUV(bpy.types.Operator):
    """
    Copy UV data from selected objects.

    Stores UV coordinates for each object in the clipboard, indexed by object name.
    This allows pasting UV data back to the same objects later.
    """
    bl_idname = "multiuv.copy_uv"
    bl_label = "Copy UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        # Clear clipboard and store UV data for each object
        clipboard = get_clipboard()
        clipboard.clear()

        for obj in selected_meshes:
            if len(obj.data.uv_layers) > self.uv_index:
                uv_layer = obj.data.uv_layers[self.uv_index]

                # Store UV coordinates for each loop (vertex in a face)
                uv_data = []
                for loop in obj.data.loops:
                    uv = uv_layer.data[loop.index].uv
                    uv_data.append((uv.x, uv.y))

                # Store in clipboard with object name as key
                clipboard[obj.name] = {
                    'uv_data': uv_data,
                    'uv_index': self.uv_index,
                    'loop_count': len(obj.data.loops)  # For validation
                }

        self.report({'INFO'}, f"Copied UV data from {len(clipboard)} objects")
        return {'FINISHED'}


class MULTIUV_OT_PasteUV(bpy.types.Operator):
    """
    Paste UV data to selected objects.

    Matches objects by name and pastes UV data from clipboard.
    Automatically backs up current UV data before pasting for restore functionality.
    Validates mesh topology hasn't changed by checking loop count.
    """
    bl_idname = "multiuv.paste_uv"
    bl_label = "Paste UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        clipboard = get_clipboard()
        if not clipboard:
            self.report({'WARNING'}, "No UV data in clipboard")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        # Backup current UV data before pasting (for restore functionality)
        backup = get_backup()
        backup.clear()

        pasted_count = 0
        for obj in selected_meshes:
            # Backup current UV data if it exists
            if len(obj.data.uv_layers) > self.uv_index:
                uv_layer = obj.data.uv_layers[self.uv_index]
                uv_data = []
                for loop in obj.data.loops:
                    uv = uv_layer.data[loop.index].uv
                    uv_data.append((uv.x, uv.y))

                backup[obj.name] = {
                    'uv_data': uv_data,
                    'uv_index': self.uv_index,
                    'loop_count': len(obj.data.loops)
                }

            # Check if we have clipboard data for this object (match by name)
            if obj.name in clipboard:
                clipboard_data = clipboard[obj.name]

                # Verify loop count matches (mesh topology validation)
                if clipboard_data['loop_count'] != len(obj.data.loops):
                    self.report({'WARNING'}, f"Skipping {obj.name}: mesh topology changed")
                    continue

                # Ensure UV layer exists (create if necessary)
                while len(obj.data.uv_layers) <= self.uv_index:
                    current_index = len(obj.data.uv_layers)
                    uv_name = "UVMap" if current_index == 0 else f"UVMap__NEW__{current_index + 1}"
                    obj.data.uv_layers.new(name=uv_name)

                # Paste UV data from clipboard
                uv_layer = obj.data.uv_layers[self.uv_index]
                uv_data = clipboard_data['uv_data']

                for loop_idx, loop in enumerate(obj.data.loops):
                    if loop_idx < len(uv_data):
                        uv_layer.data[loop.index].uv = uv_data[loop_idx]

                pasted_count += 1

        # Clear clipboard after paste (force single-use copy/paste)
        clipboard.clear()

        if pasted_count > 0:
            self.report({'INFO'}, f"Pasted UV data to {pasted_count} objects")
        else:
            self.report({'WARNING'}, "No matching objects found in clipboard")

        return {'FINISHED'}


class MULTIUV_OT_RestoreUV(bpy.types.Operator):
    """
    Restore previous UV data before paste.

    Restores UV data from the backup created during the last paste operation.
    Useful when you realize you pasted the wrong UV data.
    """
    bl_idname = "multiuv.restore_uv"
    bl_label = "Restore Previous UV"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        backup = get_backup()
        if not backup:
            self.report({'WARNING'}, "No backup data available")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        restored_count = 0
        for obj in selected_meshes:
            # Check if we have backup data for this object
            if obj.name in backup:
                backup_data = backup[obj.name]

                # Verify loop count matches (mesh topology validation)
                if backup_data['loop_count'] != len(obj.data.loops):
                    self.report({'WARNING'}, f"Skipping {obj.name}: mesh topology changed")
                    continue

                # Ensure UV layer exists
                if len(obj.data.uv_layers) > self.uv_index:
                    # Restore UV data from backup
                    uv_layer = obj.data.uv_layers[self.uv_index]
                    uv_data = backup_data['uv_data']

                    for loop_idx, loop in enumerate(obj.data.loops):
                        if loop_idx < len(uv_data):
                            uv_layer.data[loop.index].uv = uv_data[loop_idx]

                    restored_count += 1

        if restored_count > 0:
            self.report({'INFO'}, f"Restored UV data for {restored_count} objects")
        else:
            self.report({'WARNING'}, "No matching objects found in backup")

        return {'FINISHED'}


class MULTIUV_OT_CopyUVLayersFromActive(bpy.types.Operator):
    """
    Copy UV layer structure from active object to other selected objects.

    Creates missing UV layers on other objects to match active object's layer count.
    Does not modify existing UV layers or copy UV data.
    """
    bl_idname = "multiuv.copy_uv_layers_from_active"
    bl_label = "Copy UV Layers From Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "No active mesh object")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH' and obj != active_obj]

        if not selected_meshes:
            self.report({'WARNING'}, "No other mesh objects selected")
            return {'CANCELLED'}

        # Get active object's UV layer count
        active_uv_count = len(active_obj.data.uv_layers)

        modified_count = 0
        for obj in selected_meshes:
            current_uv_count = len(obj.data.uv_layers)

            # Only create missing UV layers (don't delete extra ones)
            if current_uv_count < active_uv_count:
                while len(obj.data.uv_layers) < active_uv_count:
                    current_index = len(obj.data.uv_layers)
                    uv_name = "UVMap" if current_index == 0 else f"UVMap__NEW__{current_index + 1}"
                    obj.data.uv_layers.new(name=uv_name)
                modified_count += 1

        if modified_count > 0:
            self.report({'INFO'}, f"Created UV layers for {modified_count} objects")
        else:
            self.report({'INFO'}, "All objects already have sufficient UV layers")

        return {'FINISHED'}


class MULTIUV_OT_ForceUVLayersFromActive(bpy.types.Operator):
    """
    Force UV layer structure from active object to other selected objects.

    Creates or deletes UV layers to exactly match active object's layer count.
    WARNING: This will delete extra UV layers and their data!
    """
    bl_idname = "multiuv.force_uv_layers_from_active"
    bl_label = "Force UV Layers From Active"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Show confirmation dialog with warning
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        active_obj = context.active_object
        if not active_obj or active_obj.type != 'MESH':
            self.report({'WARNING'}, "No active mesh object")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH' and obj != active_obj]

        if not selected_meshes:
            self.report({'WARNING'}, "No other mesh objects selected")
            return {'CANCELLED'}

        # Get active object's UV layer count
        active_uv_count = len(active_obj.data.uv_layers)

        modified_count = 0
        for obj in selected_meshes:
            current_uv_count = len(obj.data.uv_layers)

            if current_uv_count < active_uv_count:
                # Create missing UV layers
                while len(obj.data.uv_layers) < active_uv_count:
                    current_index = len(obj.data.uv_layers)
                    uv_name = "UVMap" if current_index == 0 else f"UVMap__NEW__{current_index + 1}"
                    obj.data.uv_layers.new(name=uv_name)
                modified_count += 1
            elif current_uv_count > active_uv_count:
                # Delete extra UV layers
                while len(obj.data.uv_layers) > active_uv_count:
                    uv_layer = obj.data.uv_layers[-1]  # Remove last layer
                    obj.data.uv_layers.remove(uv_layer)
                modified_count += 1

        if modified_count > 0:
            self.report({'INFO'}, f"Forced UV layer structure for {modified_count} objects")
        else:
            self.report({'INFO'}, "All objects already match active object's UV structure")

        return {'FINISHED'}


class MULTIUV_OT_CreateTexture(bpy.types.Operator):
    """
    Create texture nodes for current UV layer.

    Creates UV Map, Mapping, and Image Texture nodes in material,
    connected and configured for the current active UV layer.
    """
    bl_idname = "multiuv.create_texture"
    bl_label = "Create Texture"
    bl_options = {'REGISTER', 'UNDO'}

    uv_index: bpy.props.IntProperty()

    def execute(self, context):
        from .utils import get_uv_name_for_tab

        # Get UV name for current index
        uv_name = get_uv_name_for_tab(context, self.uv_index)

        if not uv_name or uv_name == "multiple names":
            self.report({'WARNING'}, "UV names are not unified")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected")
            return {'CANCELLED'}

        created_count = 0
        for obj in selected_meshes:
            # Check if object has the UV layer
            if len(obj.data.uv_layers) <= self.uv_index:
                self.report({'WARNING'}, f"Skipping {obj.name}: UV layer does not exist")
                continue

            # Ensure object has a material
            if not obj.data.materials:
                mat = bpy.data.materials.new(name=f"{obj.name}_Material")
                mat.use_nodes = True
                obj.data.materials.append(mat)
            else:
                mat = obj.data.materials[0]
                if not mat.use_nodes:
                    mat.use_nodes = True

            # Get material node tree
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Create UV Map node
            uv_map_node = nodes.new(type='ShaderNodeUVMap')
            uv_map_node.uv_map = uv_name
            uv_map_node.location = (-600, 0)

            # Create Mapping node
            mapping_node = nodes.new(type='ShaderNodeMapping')
            mapping_node.location = (-400, 0)

            # Create Image Texture node
            image_texture_node = nodes.new(type='ShaderNodeTexImage')
            image_texture_node.location = (-200, 0)

            # Connect nodes: UV Map -> Mapping -> Image Texture
            links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
            links.new(mapping_node.outputs['Vector'], image_texture_node.inputs['Vector'])

            created_count += 1

        self.report({'INFO'}, f"Created texture nodes for {created_count} objects")
        return {'FINISHED'}
