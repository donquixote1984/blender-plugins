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

        seam_edges_data = []
        for edge in selected_edges:
            if edge.seam:
                v1, v2 = edge.verts[0], edge.verts[1]
                seam_edges_data.append({
                    'direction': ((v2.co - v1.co).normalized()).copy(),
                })

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

        # Collect all edges in bevel faces
        bevel_edges = set()
        for face in bevel_faces:
            for edge in face.edges:
                bevel_edges.add(edge)

        # Clear seam on outer edges
        non_bevel_faces = set(bm.faces) - bevel_faces
        non_bevel_edges = set()
        for face in non_bevel_faces:
            for edge in face.edges:
                non_bevel_edges.add(edge)

        # Find middle edges: edges in bevel faces that are NOT seam
        # (Blender auto-marks outer edges as seam, middle edges are not seam)
        middle_edges = []
        for edge in bevel_edges:
            if not edge.seam:
                # Check if edge vertices belong to non-bevel faces
                v1, v2 = edge.verts[0], edge.verts[1]
                v1_in_non_bevel = any(face in non_bevel_faces for face in v1.link_faces)
                v2_in_non_bevel = any(face in non_bevel_faces for face in v2.link_faces)

                # Skip if either vertex is in non-bevel faces
                if v1_in_non_bevel or v2_in_non_bevel:
                    continue

                # Verify it's aligned with one of the original seam edges
                for seam_data in seam_edges_data:
                    original_direction = seam_data['direction']
                    edge_direction = (v2.co - v1.co).normalized()
                    direction_match = abs(edge_direction.dot(original_direction))

                    if direction_match > 0.85:
                        middle_edges.append(edge)
                        edge.seam = True
                        break

        for edge in non_bevel_edges:
            if edge.seam:
                for seam_data in seam_edges_data:
                    original_direction = seam_data['direction']
                    v1, v2 = edge.verts[0], edge.verts[1]
                    edge_direction = (v2.co - v1.co).normalized()
                    direction_match = abs(edge_direction.dot(original_direction))

                    if direction_match > 0.85:
                        edge.seam = False
                        break

        bmesh.update_edit_mesh(mesh)

        seam_count = len(seam_edges_data)
        found_count = len(middle_edges)
        self.report({'INFO'}, f"Beveled {len(selected_edges)} edges, marked {found_count}/{seam_count} middle edges as seam")

        return {'FINISHED'}


def menu_func(self, context):
    """Add operator to edge menu."""
    self.layout.operator(BEVEL2UV_OT_BevelWithSeam.bl_idname)
