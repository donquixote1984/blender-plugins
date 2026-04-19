"""Bevel operator that preserves UV seams."""

import bpy
import bmesh
from mathutils import Vector


class BEVEL2UV_OT_BevelWithSeam(bpy.types.Operator):
    """Bevel selected edges with 2 segments and preserve UV seams on middle edge"""

    bl_idname = "bevel2uv.bevel_with_seam"
    bl_label = "Bevel 2 Segments with UV Seam"
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Bevel offset distance",
        default=0.1,
        min=0.0,
        soft_max=1.0
    )

    @classmethod
    def poll(cls, context):
        """Check if operator can run."""
        return (context.mode == 'EDIT_MESH' and
                context.edit_object and
                context.edit_object.type == 'MESH')

    def execute(self, context):
        """Execute the bevel operation."""
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        selected_edges = [e for e in bm.edges if e.select]

        if not selected_edges:
            self.report({'WARNING'}, "No edges selected")
            return {'CANCELLED'}

        # Record which edges were originally seam
        original_seam_edges = set(e for e in selected_edges if e.seam)
        seam_count = len(original_seam_edges)

        result = bmesh.ops.bevel(
            bm,
            geom=selected_edges,
            offset=self.offset,
            offset_type='OFFSET',
            segments=2,
            profile=0.5,
            affect='EDGES'
        )

        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        bevel_faces = set(f for f in result['faces'] if isinstance(f, bmesh.types.BMFace))
        non_bevel_faces = set(bm.faces) - bevel_faces

        # Deselect all
        for edge in bm.edges:
            edge.select = False

        # Collect all edges in bevel faces
        bevel_edges = set()
        for face in bevel_faces:
            for edge in face.edges:
                bevel_edges.add(edge)

        # Find outer seam edges (from original seam edges)
        outer_seam_edges = set()
        for edge in bevel_edges:
            if edge.seam:
                v1, v2 = edge.verts[0], edge.verts[1]
                v1_in_non_bevel = any(f in non_bevel_faces for f in v1.link_faces)
                v2_in_non_bevel = any(f in non_bevel_faces for f in v2.link_faces)

                # Outer edges connect to non-bevel faces
                if v1_in_non_bevel or v2_in_non_bevel:
                    outer_seam_edges.add(edge)

        # Find middle edges: only in faces that contain outer seam edges
        middle_edges = []
        for face in bevel_faces:
            # Check if this face has outer seam edges
            face_has_outer_seam = any(e in outer_seam_edges for e in face.edges)

            if face_has_outer_seam:
                for edge in face.edges:
                    if not edge.seam:
                        v1, v2 = edge.verts[0], edge.verts[1]
                        v1_in_non_bevel = any(f in non_bevel_faces for f in v1.link_faces)
                        v2_in_non_bevel = any(f in non_bevel_faces for f in v2.link_faces)

                        # Middle edge vertices should not touch non-bevel faces
                        if not v1_in_non_bevel and not v2_in_non_bevel:
                            middle_edges.append(edge)

        # For each middle edge, get its edge loop
        all_loop_edges = set()

        for edge in middle_edges:
            if edge not in all_loop_edges:
                # Deselect all
                for e in bm.edges:
                    e.select = False

                # Select this edge
                edge.select = True

                # Update mesh to apply selection
                bmesh.update_edit_mesh(mesh)

                # Use Blender's edge loop select
                bpy.ops.mesh.loop_multi_select(ring=False)

                # Get selected edges (the edge loop)
                edge_loop = [e for e in bm.edges if e.select]
                all_loop_edges.update(edge_loop)

        # Clear all seams
        for edge in bm.edges:
            edge.seam = False

        # Mark all loop edges as seam
        for edge in all_loop_edges:
            edge.seam = True

        bmesh.update_edit_mesh(mesh)

        self.report({'INFO'}, f"Marked {len(all_loop_edges)} edges as seam from {len(middle_edges)} middle edges")

        return {'FINISHED'}


def menu_func(self, context):
    """Add operator to edge menu."""
    self.layout.operator(BEVEL2UV_OT_BevelWithSeam.bl_idname)
