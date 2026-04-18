# Bevel 2 UV - Blender Plugin

## Description

A Blender plugin that performs 2-segment bevel operations on selected edges while automatically preserving UV seam marks on the middle edges.

## Core Algorithm

The plugin leverages Blender's bevel behavior to identify middle edges:

1. **Blender's Automatic Behavior**: When beveling seam edges, Blender automatically marks the outer edges (1st and 3rd) as seams, while the middle edge (2nd) remains unmarked
2. **Identifying Middle Edges**:
   - Find edges in bevel-generated faces that are NOT seams
   - Exclude edges whose vertices belong to non-bevel faces (these are connecting edges, not middle edges)
   - Verify direction matches original seam edges (direction_match > 0.85)
3. **Mark Seams**: Mark identified middle edges as seams
4. **Clear Outer Edge Seams**: Remove seam marks from edges in non-bevel faces that match the original seam edge directions

## Advantages

- No reliance on geometric distance calculations
- Uses topological relationships (face membership)
- Automatically handles complex cases (Y-junctions, 4-edge intersections, etc.)
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
- Direction matching uses vector dot product

