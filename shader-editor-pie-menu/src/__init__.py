bl_info = {
    "name": "Shader Editor Pie Menu",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Shader Editor > Tab Key",
    "description": "Pie menu with quick shortcuts in Shader Editor",
    "category": "Node",
}

import bpy
import os
from bpy.types import Menu, Operator
from bpy.props import CollectionProperty
from bpy_extras.io_utils import ImportHelper


class SHADEREDITOR_OT_sd_texture_import(Operator, ImportHelper):
    bl_idname = "shader_editor.sd_texture_import"
    bl_label = "SD Texture Import"
    bl_description = "Import Substance Designer PBR textures and connect to Principled BSDF"

    files: CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    filter_glob: bpy.props.StringProperty(
        default='*.png;*.jpg;*.jpeg;*.tga;*.tiff;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files selected")
            return {'CANCELLED'}

        # Get file paths
        file_paths = [os.path.join(self.directory, f.name) for f in self.files]

        # Categorize textures
        textures = {
            'basecolor': None,
            'normal': None,
            'roughness': None,
            'ao': None,
            'metallic': None,
            'opacity': None
        }

        for path in file_paths:
            filename_lower = os.path.basename(path).lower()

            if any(x in filename_lower for x in ['basecolor', 'diffuse', 'albedo', 'base_color']):
                textures['basecolor'] = path
            elif 'normal' in filename_lower:
                textures['normal'] = path
            elif 'roughness' in filename_lower or 'rough' in filename_lower:
                textures['roughness'] = path
            elif 'ao' in filename_lower or 'ambient' in filename_lower or 'occlusion' in filename_lower:
                textures['ao'] = path
            elif 'metallic' in filename_lower or 'metalness' in filename_lower or 'metal' in filename_lower:
                textures['metallic'] = path
            elif 'opacity' in filename_lower or 'alpha' in filename_lower:
                textures['opacity'] = path

        # Get or create Principled BSDF
        node_tree = context.space_data.edit_tree
        if not node_tree:
            self.report({'WARNING'}, "No active node tree")
            return {'CANCELLED'}

        principled = None
        # Check selected nodes first
        for node in context.selected_nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break

        # If no selected Principled BSDF, find first one
        if not principled:
            for node in node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled = node
                    break

        # Create if not found
        if not principled:
            principled = node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            principled.location = (0, 0)

        # Create Texture Coordinate and Mapping nodes
        tex_coord = node_tree.nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (principled.location.x - 800, principled.location.y)

        mapping = node_tree.nodes.new('ShaderNodeMapping')
        mapping.location = (principled.location.x - 600, principled.location.y)

        # Connect Texture Coordinate to Mapping
        node_tree.links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        # Track Y position for image texture nodes
        y_offset = principled.location.y + 300

        # Create image texture nodes and connect them
        image_nodes = []

        # Base Color
        if textures['basecolor']:
            img_node = node_tree.nodes.new('ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(textures['basecolor'])
            img_node.image.colorspace_settings.name = 'sRGB'
            img_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], img_node.inputs['Vector'])
            image_nodes.append(img_node)
            y_offset -= 300

            # Store for AO mixing
            basecolor_node = img_node

        # AO (needs special handling with Mix Color)
        if textures['ao']:
            ao_node = node_tree.nodes.new('ShaderNodeTexImage')
            ao_node.image = bpy.data.images.load(textures['ao'])
            ao_node.image.colorspace_settings.name = 'Non-Color'
            ao_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], ao_node.inputs['Vector'])
            image_nodes.append(ao_node)
            y_offset -= 300

            # Create Mix Color node
            if textures['basecolor']:
                mix_node = node_tree.nodes.new('ShaderNodeMix')
                mix_node.data_type = 'RGBA'
                mix_node.blend_type = 'MULTIPLY'
                mix_node.location = (principled.location.x - 200, principled.location.y + 200)

                # Connect: Base Color -> A, AO -> B, Mix -> Principled Base Color
                node_tree.links.new(basecolor_node.outputs['Color'], mix_node.inputs[6])  # A
                node_tree.links.new(ao_node.outputs['Color'], mix_node.inputs[7])  # B
                mix_node.inputs[0].default_value = 0.5  # Factor
                node_tree.links.new(mix_node.outputs[2], principled.inputs['Base Color'])
            else:
                # If no base color, just connect AO directly
                node_tree.links.new(ao_node.outputs['Color'], principled.inputs['Base Color'])
        elif textures['basecolor']:
            # No AO, connect base color directly
            node_tree.links.new(basecolor_node.outputs['Color'], principled.inputs['Base Color'])

        # Normal
        if textures['normal']:
            img_node = node_tree.nodes.new('ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(textures['normal'])
            img_node.image.colorspace_settings.name = 'Non-Color'
            img_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], img_node.inputs['Vector'])
            image_nodes.append(img_node)

            # Create Normal Map node
            normal_map = node_tree.nodes.new('ShaderNodeNormalMap')
            normal_map.location = (principled.location.x - 200, y_offset)
            node_tree.links.new(img_node.outputs['Color'], normal_map.inputs['Color'])
            node_tree.links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
            y_offset -= 300

        # Roughness
        if textures['roughness']:
            img_node = node_tree.nodes.new('ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(textures['roughness'])
            img_node.image.colorspace_settings.name = 'Non-Color'
            img_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], img_node.inputs['Vector'])
            node_tree.links.new(img_node.outputs['Color'], principled.inputs['Roughness'])
            image_nodes.append(img_node)
            y_offset -= 300

        # Metallic
        if textures['metallic']:
            img_node = node_tree.nodes.new('ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(textures['metallic'])
            img_node.image.colorspace_settings.name = 'Non-Color'
            img_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], img_node.inputs['Vector'])
            node_tree.links.new(img_node.outputs['Color'], principled.inputs['Metallic'])
            image_nodes.append(img_node)
            y_offset -= 300

        # Opacity
        if textures['opacity']:
            img_node = node_tree.nodes.new('ShaderNodeTexImage')
            img_node.image = bpy.data.images.load(textures['opacity'])
            img_node.image.colorspace_settings.name = 'Non-Color'
            img_node.location = (principled.location.x - 400, y_offset)
            node_tree.links.new(mapping.outputs['Vector'], img_node.inputs['Vector'])
            node_tree.links.new(img_node.outputs['Color'], principled.inputs['Alpha'])
            image_nodes.append(img_node)

        self.report({'INFO'}, f"Imported {len([t for t in textures.values() if t])} textures")
        return {'FINISHED'}


class SHADEREDITOR_OT_mix_color(Operator):
    bl_idname = "shader_editor.mix_color"
    bl_label = "Mix Color"
    bl_description = "Create Mix Color node and connect selected nodes"

    @classmethod
    def poll(cls, context):
        if context.space_data.type != 'NODE_EDITOR':
            return False
        if not context.space_data.edit_tree:
            return False

        # Check if any selected node has color output
        selected_nodes = context.selected_nodes
        if not selected_nodes:
            return True  # Allow creation even with no selection

        for node in selected_nodes:
            if hasattr(node, 'outputs'):
                for output in node.outputs:
                    if output.type == 'RGBA':
                        return True
        return False

    def invoke(self, context, event):
        # Store selected nodes before execution
        self.stored_selected = [node for node in context.selected_nodes]
        self.stored_active = context.active_node
        return self.execute(context)

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        if not node_tree:
            return {'CANCELLED'}

        # Get cursor location (pie menu location)
        cursor_loc = context.space_data.cursor_location

        # Create Mix Color node
        mix_node = node_tree.nodes.new('ShaderNodeMix')
        mix_node.data_type = 'RGBA'
        mix_node.blend_type = 'MULTIPLY'
        mix_node.location = cursor_loc
        mix_node.inputs[0].default_value = 1.0  # Factor

        # Use stored selection if available
        if hasattr(self, 'stored_selected'):
            selected_nodes = self.stored_selected
            active_node = self.stored_active
        else:
            selected_nodes = context.selected_nodes
            active_node = context.active_node

        if len(selected_nodes) == 2 and active_node in selected_nodes:
            # Two nodes selected, one is active
            secondary_node = None
            for node in selected_nodes:
                if node != active_node:
                    secondary_node = node
                    break

            # Find color outputs
            active_color_output = None
            secondary_color_output = None

            if hasattr(active_node, 'outputs'):
                for output in active_node.outputs:
                    if output.type == 'RGBA':
                        active_color_output = output
                        break

            if hasattr(secondary_node, 'outputs'):
                for output in secondary_node.outputs:
                    if output.type == 'RGBA':
                        secondary_color_output = output
                        break

            # Connect A (active) and B (secondary)
            if active_color_output:
                node_tree.links.new(active_color_output, mix_node.inputs[6])  # A
            if secondary_color_output:
                node_tree.links.new(secondary_color_output, mix_node.inputs[7])  # B

        elif len(selected_nodes) == 1:
            # One node selected
            node = selected_nodes[0]
            if hasattr(node, 'outputs'):
                for output in node.outputs:
                    if output.type == 'RGBA':
                        node_tree.links.new(output, mix_node.inputs[6])  # A
                        break

        # If no nodes selected or other cases, just create empty Mix Color node

        # Select the new mix node
        for node in node_tree.nodes:
            node.select = False
        mix_node.select = True
        node_tree.nodes.active = mix_node

        return {'FINISHED'}


class SHADEREDITOR_OT_test_button(Operator):
    bl_idname = "shader_editor.test_button"
    bl_label = "Test Button"
    bl_description = "A test button"

    def execute(self, context):
        self.report({'INFO'}, "Test button clicked!")
        return {'FINISHED'}


class SHADEREDITOR_MT_pie_menu(Menu):
    bl_label = "Shader Editor Pie Menu"
    bl_idname = "SHADEREDITOR_MT_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Top
        pie.operator("shader_editor.sd_texture_import", text="SD Texture Import", icon='TEXTURE')
        # Right
        pie.operator("shader_editor.mix_color", text="Mix Color", icon='NODE_COMPOSITING')
        # Left
        # Bottom


addon_keymaps = []


def register():
    bpy.utils.register_class(SHADEREDITOR_OT_sd_texture_import)
    bpy.utils.register_class(SHADEREDITOR_OT_mix_color)
    bpy.utils.register_class(SHADEREDITOR_OT_test_button)
    bpy.utils.register_class(SHADEREDITOR_MT_pie_menu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'TAB', 'PRESS')
        kmi.properties.name = "SHADEREDITOR_MT_pie_menu"
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(SHADEREDITOR_MT_pie_menu)
    bpy.utils.unregister_class(SHADEREDITOR_OT_test_button)
    bpy.utils.unregister_class(SHADEREDITOR_OT_mix_color)
    bpy.utils.unregister_class(SHADEREDITOR_OT_sd_texture_import)


if __name__ == "__main__":
    register()
