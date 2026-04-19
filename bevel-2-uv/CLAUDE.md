# Bevel 2 UV - Blender Plugin

## Description

A Blender plugin that performs 2-segment bevel operations on selected edges while automatically preserving UV seam marks on the middle edges.

## Core Algorithm

The plugin uses a combination of topological analysis and Blender's built-in edge loop selection:

1. **Identify Original Seam Edges**: Record which selected edges are marked as seams before beveling
2. **Perform Bevel Operation**: Execute 2-segment bevel with specified offset
3. **Find Outer Edges**: Locate seam edges in bevel faces that connect to non-bevel faces (these are the 1st and 3rd edges from original seam)
4. **Identify Middle Edges**: In bevel faces containing outer edges, find edges that:
   - Are NOT seam edges
   - Have vertices that do NOT belong to non-bevel faces
5. **Get Edge Loops**: For each middle edge, use `bpy.ops.mesh.loop_multi_select(ring=False)` to get the complete edge loop (simulates Alt+Click)
6. **Mark Seams**: Clear all seams, then mark all edges in the collected edge loops as seams

## Key Insights

- **Topological Approach**: Uses face membership rather than geometric calculations (distance, direction)
- **Blender's Edge Loop**: Leverages built-in edge loop selection instead of manual traversal
- **Automatic Handling**: Works correctly for complex cases (Y-junctions, 4-edge intersections, parallel edges on cubes)

## Advantages

- No reliance on geometric distance or direction matching thresholds
- Uses topological relationships (face membership)
- Leverages Blender's robust edge loop selection
- Automatically handles complex topology
- Simple and reliable algorithm

## Usage

1. Enter Edit mode
2. Select edges to bevel (recommended: edges already marked as UV seams)
3. Execute: Edge menu > Bevel 2 Segments with UV Seam, or search "Bevel 2 Segments with UV Seam"
4. Adjust offset parameter

## File Structure

```
bevel-2-uv/
├── src/
│   ├── __init__.py      # Plugin entry and registration
│   └── operator.py      # Core bevel operator
├── build.py             # Build script
└── release/             # Generated zip files
```

## Development Notes

- Uses bmesh API for mesh operations
- Retrieves bevel-generated faces via result['faces']
- Determines edge types using face membership relationships
- Uses `bpy.ops.mesh.loop_multi_select(ring=False)` for edge loop selection
- Requires updating edit mesh between bmesh operations and bpy.ops calls

